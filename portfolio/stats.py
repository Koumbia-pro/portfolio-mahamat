"""
Calcul des statistiques du tableau de bord.
"""

from datetime import timedelta

from django.db.models import Sum
from django.urls import reverse
from django.utils import timezone

from .models import (
    Competence, MessageContact, Profil, Projet, Technologie, VisiteJour,
)

PERIODES = (7, 30, 90)

MOIS_COURTS = ["janv.", "févr.", "mars", "avr.", "mai", "juin",
               "juil.", "août", "sept.", "oct.", "nov.", "déc."]


def _somme(qs, champ):
    return qs.aggregate(total=Sum(champ))["total"] or 0


def _tendance(actuel, precedent):
    """Variation en % par rapport à la période précédente (None si incalculable)."""
    if precedent == 0:
        return None
    return round((actuel - precedent) * 100 / precedent)


def _format_court(d):
    return f"{d.day} {MOIS_COURTS[d.month - 1]}"


def lire_periode(request):
    try:
        jours = int(request.GET.get("jours", 30))
    except ValueError:
        jours = 30
    return jours if jours in PERIODES else 30


def statistiques(jours):
    """Chiffres clés et série quotidienne sur `jours` jours."""
    aujourd_hui = timezone.localdate()
    debut = aujourd_hui - timedelta(days=jours - 1)
    debut_prec = debut - timedelta(days=jours)

    periode = VisiteJour.objects.filter(date__gte=debut, date__lte=aujourd_hui)
    precedente = VisiteJour.objects.filter(date__gte=debut_prec, date__lt=debut)

    vues, vues_prec = _somme(periode, "vues"), _somme(precedente, "vues")
    cv, cv_prec = _somme(periode, "telechargements_cv"), _somme(precedente, "telechargements_cv")
    mobile = _somme(periode, "vues_mobile")
    msgs = MessageContact.objects.filter(date_envoi__date__gte=debut).count()
    msgs_prec = MessageContact.objects.filter(
        date_envoi__date__gte=debut_prec, date_envoi__date__lt=debut
    ).count()

    # Série du graphique (jours sans visite = 0)
    par_jour = {v.date: v for v in periode}
    serie = []
    for i in range(jours):
        d = debut + timedelta(days=i)
        v = par_jour.get(d)
        serie.append({
            "date": d,
            "label": _format_court(d),
            "vues": v.vues if v else 0,
            "cv": v.telechargements_cv if v else 0,
        })
    maximum = max([p["vues"] for p in serie] + [0])
    echelle = max(4, ((maximum + 3) // 4) * 4)  # graduations entières
    for p in serie:
        p["hauteur"] = round(p["vues"] * 100 / echelle, 2)

    projets_actifs = Projet.objects.filter(actif=True).count()

    return {
        "jours": jours,
        "periodes": PERIODES,
        "debut": debut,
        "fin": aujourd_hui,
        "total_vues": vues,
        "kpis": [
            {"label": "Visiteurs", "valeur": vues, "tendance": _tendance(vues, vues_prec),
             "icone": "fa-eye", "aide": f"{round(mobile * 100 / vues) if vues else 0} % sur mobile"},
            {"label": "CV téléchargés", "valeur": cv, "tendance": _tendance(cv, cv_prec),
             "icone": "fa-file-arrow-down",
             "aide": f"{round(cv * 100 / vues, 1) if vues else 0} % des visiteurs"},
            {"label": "Messages reçus", "valeur": msgs, "tendance": _tendance(msgs, msgs_prec),
             "icone": "fa-envelope", "aide": "via le formulaire de contact"},
            {"label": "Projets en ligne", "valeur": projets_actifs, "tendance": None,
             "icone": "fa-folder-open",
             "aide": f"{Competence.objects.count()} compétences · {Technologie.objects.count()} technologies"},
        ],
        "serie": serie,
        "graduations": [echelle, echelle * 3 // 4, echelle // 2, echelle // 4, 0],
        "meilleur": max(serie, key=lambda p: p["vues"]) if maximum else None,
    }


def completion_profil():
    """Liste de ce qui reste à compléter, avec un lien vers la bonne page du dashboard."""
    profil = Profil.objects.first()
    lien_profil = reverse("dashboard:profil")
    lien_projets = reverse("dashboard:liste", args=["projets"])
    actifs = Projet.objects.filter(actif=True)

    elements = []
    if profil:
        elements += [
            ("Photo de profil", bool(profil.photo), lien_profil),
            ("CV en PDF", bool(profil.cv), lien_profil),
            ("Lien LinkedIn", bool(profil.linkedin), lien_profil),
            ("Lien GitHub", bool(profil.github), lien_profil),
            ("Téléphone", bool(profil.telephone), lien_profil),
            ("Âge", bool(profil.age), lien_profil),
            ("Texte « À propos »", bool(profil.description_longue), lien_profil),
        ]
    else:
        elements.append(("Créer ton profil", False, lien_profil))
    elements += [
        ("Au moins 3 projets", actifs.count() >= 3, lien_projets),
        ("Images des projets", actifs.exists() and not actifs.filter(image="").exists(), lien_projets),
        ("Liens GitHub des projets", actifs.exclude(lien_code="").exists(), lien_projets),
    ]
    checklist = [{"label": l, "ok": ok, "url": u} for l, ok, u in elements]
    faits = sum(1 for c in checklist if c["ok"])
    return {
        "checklist": checklist,
        "completion": round(faits * 100 / len(checklist)) if checklist else 0,
    }
