"""
Vues — Portfolio Mahamat Hassan Oumar
"""

from django.shortcuts import render, redirect
from django.http import JsonResponse, FileResponse
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from django.contrib.staticfiles import finders
from django.contrib.staticfiles.storage import staticfiles_storage
from django.db.models import F
from django.utils import timezone
import logging
import re

from .models import (
    Profil,
    CategorieCompetence,
    Statistique,
    Projet,
    Service,
    Experience,
    Formation,
    MessageContact,
    Technologie,
    VisiteJour,
)

CV_STATIQUE = "cv/CV_Mahamat_Hassan_Oumar.pdf"
ROBOTS = re.compile(r"bot|crawl|spider|slurp|preview|facebookexternalhit|whatsapp|curl|wget|python-requests|headless", re.I)
MOBILE = re.compile(r"mobile|android|iphone|ipad", re.I)

# Logger pour cette application
logger = logging.getLogger("portfolio")


# ─────────────────────────────────────────────
# FONCTION UTILITAIRE — VALIDATION EMAIL
# ─────────────────────────────────────────────
def valider_email(email):
    """Valider le format de l'email."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


# ─────────────────────────────────────────────
# FONCTION UTILITAIRE — STATISTIQUES DE VISITES
# ─────────────────────────────────────────────
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
        logger.warning(f"Statistiques indisponibles : {e}")


# ─────────────────────────────────────────────
# 1. PAGE PRINCIPALE
# ─────────────────────────────────────────────
@require_http_methods(["GET"])
def index(request):
    """
    Vue principale — affiche tout le portfolio.
    """

    profil = Profil.objects.first()

    categories = CategorieCompetence.objects.prefetch_related(
        "competences"
    ).all()

    statistiques = Statistique.objects.all()

    projets = Projet.objects.filter(actif=True)

    services = Service.objects.all()

    experiences = Experience.objects.all()

    formations = Formation.objects.all()

    technologies = Technologie.objects.all()

    # Un visiteur est compté une seule fois par jour
    if est_visiteur_reel(request):
        aujourd_hui = timezone.localdate().isoformat()
        if request.session.get("vu_le") != aujourd_hui:
            request.session["vu_le"] = aujourd_hui
            compter("vues", request)

    context = {
        "profil": profil,
        "categories": categories,
        "statistiques": statistiques,
        "projets": projets,
        "services": services,
        "experiences": experiences,
        "formations": formations,
        "technologies": technologies,
        "technologies_orbite": [t for t in technologies if t.afficher_orbite][:5],
        "categories_projets": sorted({p.categorie for p in projets if p.categorie}),
    }

    return render(
        request,
        "portfolio/index.html",
        context,
    )


# ─────────────────────────────────────────────
# 2. FORMULAIRE DE CONTACT
# ─────────────────────────────────────────────
@csrf_protect
@require_http_methods(["POST"])
def contact(request):
    """
    Traiter le formulaire de contact.
    """

    # Récupérer et nettoyer les données
    # Pas d'échappement ici : Django échappe à l'affichage,
    # et l'email est envoyé en texte brut.
    nom     = request.POST.get("name", "").strip()
    email   = request.POST.get("email", "").strip()
    sujet   = request.POST.get("subject", "").strip()[:200]
    message = request.POST.get("message", "").strip()

    # Validation des champs obligatoires
    if not nom or not email or not message:
        return JsonResponse({
            "status": "error",
            "message": "Veuillez remplir tous les champs obligatoires.",
        }, status=400)

    # Validation de la longueur
    if len(nom) > 100:
        return JsonResponse({
            "status": "error",
            "message": "Le nom est trop long.",
        }, status=400)

    if len(message) > 5000:
        return JsonResponse({
            "status": "error",
            "message": "Le message est trop long (max 5000 caractères).",
        }, status=400)

    # Validation de l'email
    if not valider_email(email):
        return JsonResponse({
            "status": "error",
            "message": "Veuillez entrer une adresse email valide.",
        }, status=400)

    try:
        # Sauvegarder dans la base de données
        MessageContact.objects.create(
            nom=nom,
            email=email,
            sujet=sujet or "Sans sujet",
            message=message,
        )

        # Envoyer l'email
        send_mail(
            subject=f"[Portfolio] {nom} — {sujet}",
            message=f"""
Nouveau message reçu sur ton portfolio.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
De      : {nom}
Email   : {email}
Sujet   : {sujet or 'Sans sujet'}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Message :
{message}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Portfolio Mahamat Hassan Oumar
            """,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[settings.EMAIL_HOST_USER],
            fail_silently=False,
        )

        # Logger le succès
        logger.info(
            f"Nouveau message de {nom} ({email})"
        )

        return JsonResponse({
            "status": "success",
            "message": "Votre message a été envoyé avec succès !",
        })

    except Exception as e:

        # Logger l'erreur
        logger.error(f"Erreur envoi email : {str(e)}")

        return JsonResponse({
            "status": "error",
            "message": "Une erreur est survenue. Veuillez réessayer.",
        }, status=500)


# ─────────────────────────────────────────────
# 3. TÉLÉCHARGEMENT DU CV
# ─────────────────────────────────────────────
@require_http_methods(["GET"])
def telecharger_cv(request):
    """
    Télécharger le CV en PDF.
    """

    profil = Profil.objects.first()

    # 1. CV envoyé depuis l'admin, sinon 2. CV fourni avec le site
    chemin = None
    if profil and profil.cv:
        chemin = profil.cv.path
    else:
        chemin = finders.find(CV_STATIQUE)
        if not chemin and staticfiles_storage.exists(CV_STATIQUE):
            chemin = staticfiles_storage.path(CV_STATIQUE)

    try:
        response = FileResponse(
            open(chemin, "rb"),
            as_attachment=True,
            filename="CV_Mahamat_Hassan_Oumar.pdf",
        )
    except (FileNotFoundError, TypeError):
        logger.error("Fichier CV introuvable")
        return redirect("index")

    if est_visiteur_reel(request):
        compter("telechargements_cv")
    logger.info("CV téléchargé")
    return response