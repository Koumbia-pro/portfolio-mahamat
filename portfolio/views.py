"""
Vues — Portfolio Mahamat Hassan Oumar
"""

from django.shortcuts import render, redirect
from django.http import JsonResponse, FileResponse
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from django.utils.html import escape
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
)

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

    context = {
        "profil": profil,
        "categories": categories,
        "statistiques": statistiques,
        "projets": projets,
        "services": services,
        "experiences": experiences,
        "formations": formations,
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
    nom     = escape(request.POST.get("name", "").strip())
    email   = escape(request.POST.get("email", "").strip())
    sujet   = escape(request.POST.get("subject", "").strip())
    message = escape(request.POST.get("message", "").strip())

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

    if profil and profil.cv:
        try:
            response = FileResponse(
                open(profil.cv.path, "rb"),
                as_attachment=True,
                filename="CV_Mahamat_Hassan.pdf",
            )
            logger.info("CV téléchargé")
            return response
        except FileNotFoundError:
            logger.error("Fichier CV introuvable")
            return redirect("index")

    return redirect("index")