"""
Vues — Portfolio Mahamat Hassan Oumar
"""

import json
import logging
import re
from datetime import datetime, time, timedelta

from django.conf import settings
from django.contrib.staticfiles import finders
from django.contrib.staticfiles.storage import staticfiles_storage
from django.core.exceptions import ValidationError
from django.core.mail import EmailMessage
from django.core.validators import validate_email
from django.db.models import F
from django.http import FileResponse, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.templatetags.static import static
from django.urls import reverse
from django.utils import timezone
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe
from django.views.decorators.cache import cache_control
from django.views.decorators.http import require_POST, require_safe

from .models import (
    CategorieCompetence,
    Experience,
    Formation,
    MessageContact,
    Profil,
    Projet,
    Service,
    Statistique,
    Technologie,
    VisiteJour,
)
from .securite import adresse_ip, limite_contact

CV_STATIQUE = "cv/CV_Mahamat_Hassan_Oumar.pdf"
NOM_PAR_DEFAUT = "Mahamat Hassan Oumar"
COOKIE_VISITE = "pf_vu"
ROBOTS = re.compile(r"bot|crawl|spider|slurp|preview|facebookexternalhit|whatsapp|curl|wget|python-requests|headless", re.I)
MOBILE = re.compile(r"mobile|android|iphone|ipad", re.I)
SAUTS_DE_LIGNE = re.compile(r"[\r\n\t]+")

logger = logging.getLogger("portfolio")


# ─────────────────────────────────────────────
# FONCTIONS UTILITAIRES
# ─────────────────────────────────────────────
def une_ligne(texte):
    """Supprimer les retours à la ligne (empêche l'injection d'en-têtes email)."""
    return SAUTS_DE_LIGNE.sub(" ", texte).strip()


def est_visiteur_reel(request):
    """Ignorer les robots et l'administrateur connecté."""
    if request.user.is_authenticated and request.user.is_staff:
        return False
    return not ROBOTS.search(request.META.get("HTTP_USER_AGENT", ""))


def compter(champ, request=None):
    """Incrémenter un compteur du jour sans stocker de donnée personnelle."""
    try:
        aujourd_hui = timezone.localdate()
        VisiteJour.objects.get_or_create(date=aujourd_hui)
        champs = {champ: F(champ) + 1}
        if champ == "vues" and request and MOBILE.search(request.META.get("HTTP_USER_AGENT", "")):
            champs["vues_mobile"] = F("vues_mobile") + 1
        VisiteJour.objects.filter(date=aujourd_hui).update(**champs)
    except Exception as e:  # les statistiques ne doivent jamais casser le site
        logger.warning("Statistiques indisponibles : %s", e)


def secondes_avant_minuit():
    maintenant = timezone.localtime()
    minuit = timezone.make_aware(
        datetime.combine(maintenant.date() + timedelta(days=1), time.min),
        maintenant.tzinfo,
    )
    return max(60, int((minuit - maintenant).total_seconds()))


def donnees_structurees(request, profil):
    """Données JSON-LD (schema.org/Person) pour les moteurs de recherche."""
    if not profil:
        return ""
    data = {
        "@context": "https://schema.org",
        "@type": "Person",
        "name": profil.nom,
        "jobTitle": profil.titre,
        "description": profil.description_courte,
        "url": request.build_absolute_uri("/"),
        "email": f"mailto:{profil.email}" if profil.email else None,
        "address": {"@type": "PostalAddress", "addressLocality": profil.localisation} if profil.localisation else None,
        "sameAs": [u for u in (profil.github, profil.linkedin, profil.twitter) if u] or None,
    }
    data = {k: v for k, v in data.items() if v}
    # Échapper < > & pour qu'aucun texte ne puisse fermer la balise <script>
    texte = json.dumps(data, ensure_ascii=False)
    texte = texte.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    return mark_safe(texte)


# ─────────────────────────────────────────────
# 1. PAGE PRINCIPALE
# ─────────────────────────────────────────────
@require_safe
def index(request):
    """Vue principale — affiche tout le portfolio."""

    profil = Profil.objects.first()
    projets = list(Projet.objects.filter(actif=True))
    technologies = list(Technologie.objects.all())
    formations = list(Formation.objects.all())

    if profil and profil.photo:
        image_partage = request.build_absolute_uri(profil.photo.url)
    else:
        image_partage = request.build_absolute_uri(static("images/profile.jpg"))

    context = {
        "profil": profil,
        "nom": profil.nom if profil and profil.nom else NOM_PAR_DEFAUT,
        "categories": CategorieCompetence.objects.prefetch_related("competences"),
        "statistiques": Statistique.objects.all(),
        "projets": projets,
        "services": Service.objects.all(),
        "experiences": Experience.objects.all(),
        "formations": formations,
        "premiere_formation": formations[0] if formations else None,
        "technologies": technologies,
        "technologies_orbite": [t for t in technologies if t.afficher_orbite][:5],
        "categories_projets": sorted({p.categorie for p in projets if p.categorie}),
        "url_canonique": request.build_absolute_uri(reverse("index")),
        "image_partage": image_partage,
        "json_ld": donnees_structurees(request, profil),
    }
    response = render(request, "portfolio/index.html", context)

    # Un visiteur est compté une seule fois par jour, grâce à un simple cookie
    # (pas de session ni de donnée personnelle enregistrée côté serveur).
    if request.method == "GET" and est_visiteur_reel(request):
        aujourd_hui = timezone.localdate().isoformat()
        if request.COOKIES.get(COOKIE_VISITE) != aujourd_hui:
            compter("vues", request)
            response.set_cookie(
                COOKIE_VISITE, aujourd_hui,
                max_age=secondes_avant_minuit(),
                httponly=True, samesite="Lax",
                secure=request.is_secure(),
            )
    return response


# ─────────────────────────────────────────────
# 2. FORMULAIRE DE CONTACT
# ─────────────────────────────────────────────
def erreur(message, status=400):
    return JsonResponse({"status": "error", "message": message}, status=status)


@require_POST
def contact(request):
    """Traiter le formulaire de contact (appelé en AJAX)."""

    # Champ invisible : seuls les robots le remplissent.
    # On fait semblant d'accepter pour ne pas les aider à s'adapter.
    if request.POST.get("website", "").strip():
        logger.info("Message de robot ignoré (piège)")
        return JsonResponse({"status": "success", "message": "Votre message a été envoyé avec succès !"})

    ip = adresse_ip(request)
    if limite_contact.depasse(ip):
        return erreur("Vous avez envoyé plusieurs messages récemment. Réessayez dans une heure.", 429)

    nom = une_ligne(strip_tags(request.POST.get("name", "")))
    email = request.POST.get("email", "").strip()
    sujet = une_ligne(strip_tags(request.POST.get("subject", "")))
    message = request.POST.get("message", "").strip()

    if not nom or not email or not message:
        return erreur("Veuillez remplir tous les champs obligatoires.")
    if len(nom) > 100:
        return erreur("Le nom est trop long (100 caractères maximum).")
    if len(sujet) > 200:
        return erreur("Le sujet est trop long (200 caractères maximum).")
    if len(message) > 5000:
        return erreur("Le message est trop long (5000 caractères maximum).")
    if len(message) < 10:
        return erreur("Votre message est un peu court : précisez votre demande.")
    try:
        validate_email(email)
    except ValidationError:
        return erreur("Veuillez entrer une adresse email valide.")

    sujet = sujet or "Sans sujet"
    try:
        MessageContact.objects.create(nom=nom, email=email, sujet=sujet, message=message)
    except Exception:
        logger.exception("Impossible d'enregistrer le message de contact")
        return erreur("Une erreur est survenue. Veuillez réessayer.", 500)

    limite_contact.enregistrer(ip)

    # Le message est enregistré dans le dashboard : l'email n'est qu'une notification.
    # Une panne SMTP ne doit donc pas afficher d'erreur au visiteur.
    if settings.CONTACT_EMAIL:
        try:
            EmailMessage(
                subject=f"[Portfolio] {nom} — {sujet}",
                body=(
                    "Nouveau message reçu sur ton portfolio.\n\n"
                    f"De      : {nom}\n"
                    f"Email   : {email}\n"
                    f"Sujet   : {sujet}\n\n"
                    f"Message :\n{message}\n\n"
                    "— Réponds directement à cet email pour écrire à l'expéditeur."
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[settings.CONTACT_EMAIL],
                reply_to=[email],
            ).send(fail_silently=False)
        except Exception as e:
            logger.error("Notification email non envoyée : %s", e)

    logger.info("Nouveau message de contact reçu")
    return JsonResponse({
        "status": "success",
        "message": "Merci ! Votre message a bien été envoyé, je vous réponds rapidement.",
    })


# ─────────────────────────────────────────────
# 3. TÉLÉCHARGEMENT DU CV
# ─────────────────────────────────────────────
@require_safe
def telecharger_cv(request):
    """Télécharger le CV en PDF."""

    profil = Profil.objects.first()

    # 1. CV envoyé depuis le dashboard, sinon 2. CV fourni avec le site
    chemin = None
    if profil and profil.cv:
        try:
            chemin = profil.cv.path
        except NotImplementedError:
            chemin = None
    if not chemin:
        chemin = finders.find(CV_STATIQUE)
        if not chemin and staticfiles_storage.exists(CV_STATIQUE):
            chemin = staticfiles_storage.path(CV_STATIQUE)

    try:
        response = FileResponse(
            open(chemin, "rb"),
            as_attachment=True,
            filename="CV_Mahamat_Hassan_Oumar.pdf",
            content_type="application/pdf",
        )
    except (FileNotFoundError, TypeError):
        logger.error("Fichier CV introuvable")
        return redirect("index")

    if request.method == "GET" and est_visiteur_reel(request):
        compter("telechargements_cv")
    return response


# ─────────────────────────────────────────────
# 4. SEO : robots.txt, sitemap.xml, favicon
# ─────────────────────────────────────────────
@require_safe
@cache_control(max_age=86400, public=True)
def robots_txt(request):
    lignes = [
        "User-agent: *",
        "Disallow: /dashboard/",
        f"Disallow: /{settings.ADMIN_URL}",
        "Allow: /",
        f"Sitemap: {request.build_absolute_uri(reverse('sitemap'))}",
    ]
    return HttpResponse("\n".join(lignes) + "\n", content_type="text/plain; charset=utf-8")


@require_safe
@cache_control(max_age=86400, public=True)
def sitemap_xml(request):
    url = request.build_absolute_uri(reverse("index"))
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"  <url><loc>{url}</loc><changefreq>monthly</changefreq><priority>1.0</priority></url>\n"
        "</urlset>\n"
    )
    return HttpResponse(xml, content_type="application/xml; charset=utf-8")


@require_safe
def favicon(request):
    return redirect(static("images/favicon.svg"), permanent=True)
