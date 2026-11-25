"""
Tableau de bord personnel — /dashboard/
"""

from django import forms
from django.contrib import messages
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from . import forms as f
from .models import (
    CategorieCompetence,
    Competence,
    Experience,
    Formation,
    MessageContact,
    Profil,
    Projet,
    Service,
    Statistique,
    Technologie,
)
from .securite import adresse_ip, limite_connexion_ip, limite_connexion_user
from .stats import completion_profil, lire_periode, statistiques


staff_required = user_passes_test(
    lambda u: u.is_active and u.is_staff,
    login_url="dashboard:connexion",
)


# ─────────────────────────────────────────────
# Description de chaque section modifiable
# ─────────────────────────────────────────────
def _carte_projet(o):
    return {
        "titre": o.titre,
        "sous_titre": o.categorie,
        "texte": o.description,
        "image": o.image.url if o.image else None,
        "badges": o.get_technologies_list()[:5],
        "etat": ("En ligne", "Masqué")[0 if o.actif else 1],
        "etat_on": o.actif,
    }


def _carte_competence(o):
    return {"titre": o.nom, "niveau": o.pourcentage}


def _carte_categorie(o):
    n = o.competences.count()
    return {"titre": o.nom, "sous_titre": f"{n} compétence{'s' if n > 1 else ''}"}


def _carte_experience(o):
    return {"titre": o.poste, "sous_titre": o.entreprise,
            "meta": f"{o.date_debut} — {o.date_fin}" if o.date_fin else o.date_debut,
            "texte": o.description}


def _carte_formation(o):
    return {"titre": o.diplome, "sous_titre": o.etablissement,
            "meta": f"{o.date_debut} — {o.date_fin}" if o.date_fin else o.date_debut,
            "texte": o.description}


def _carte_service(o):
    return {"titre": o.titre, "icone": o.icone, "texte": o.description}


def _carte_technologie(o):
    return {"titre": o.nom, "icone": o.icone,
            "etat": "Autour de la photo" if o.afficher_orbite else "Bandeau",
            "etat_on": o.afficher_orbite}


def _carte_chiffre(o):
    return {"titre": o.valeur, "sous_titre": o.label, "icone": o.icone}


SECTIONS = {
    "projets": {
        "model": Projet, "form": f.ProjetForm, "carte": _carte_projet,
        "titre": "Projets", "nouveau": "Nouveau projet", "icone": "fa-folder-open",
        "aide": "Les projets affichés dans la section « Projets » de ton site.",
        "basculer": "actif", "basculer_label": ("Masquer", "Mettre en ligne"),
        "affichage": "grille",
    },
    "competences": {
        "model": Competence, "form": f.CompetenceForm, "carte": _carte_competence,
        "titre": "Compétences", "nouveau": "Nouvelle compétence", "icone": "fa-layer-group",
        "aide": "Regroupées par catégorie. Le niveau s'affiche en barre animée sur ton site.",
        "grouper": "categorie", "affichage": "groupes",
        "lien_secondaire": ("categories", "Gérer les catégories", "fa-folder-tree"),
    },
    "categories": {
        "model": CategorieCompetence, "form": f.CategorieCompetenceForm, "carte": _carte_categorie,
        "titre": "Catégories de compétences", "nouveau": "Nouvelle catégorie", "icone": "fa-folder-tree",
        "aide": "Les blocs qui regroupent tes compétences.",
        "parent": ("competences", "Compétences"),
    },
    "experiences": {
        "model": Experience, "form": f.ExperienceForm, "carte": _carte_experience,
        "titre": "Expériences", "nouveau": "Nouvelle expérience", "icone": "fa-briefcase",
        "aide": "Stages, emplois, responsabilités en projet…",
    },
    "formations": {
        "model": Formation, "form": f.FormationForm, "carte": _carte_formation,
        "titre": "Formations", "nouveau": "Nouvelle formation", "icone": "fa-graduation-cap",
        "aide": "Ton parcours scolaire et universitaire. La première s'affiche à côté de ta photo.",
    },
    "services": {
        "model": Service, "form": f.ServiceForm, "carte": _carte_service,
        "titre": "Services", "nouveau": "Nouveau service", "icone": "fa-handshake",
        "aide": "Ce que tu proposes à tes visiteurs.",
    },
    "technologies": {
        "model": Technologie, "form": f.TechnologieForm, "carte": _carte_technologie,
        "titre": "Technologies", "nouveau": "Nouvelle technologie", "icone": "fa-microchip",
        "aide": "Le bandeau défilant de l'accueil. Jusqu'à 5 peuvent tourner autour de ta photo.",
        "basculer": "afficher_orbite", "basculer_label": ("Retirer de l'orbite", "Mettre en orbite"),
        "affichage": "compact",
    },
    "chiffres": {
        "model": Statistique, "form": f.StatistiqueForm, "carte": _carte_chiffre,
        "titre": "Chiffres clés", "nouveau": "Nouveau chiffre", "icone": "fa-hashtag",
        "aide": "Les compteurs animés de la section « À propos ».",
        "affichage": "compact",
    },
}

NAVIGATION = [
    ("Tableau de bord", [
        ("accueil", "Vue d'ensemble", "fa-gauge-high"),
        ("messages", "Messages", "fa-inbox"),
    ]),
    ("Mon contenu", [
        ("profil", "Profil", "fa-user"),
        ("projets", "Projets", "fa-folder-open"),
        ("competences", "Compétences", "fa-layer-group"),
        ("experiences", "Expériences", "fa-briefcase"),
        ("formations", "Formations", "fa-graduation-cap"),
        ("services", "Services", "fa-handshake"),
        ("technologies", "Technologies", "fa-microchip"),
        ("chiffres", "Chiffres clés", "fa-hashtag"),
    ]),
]


def _section(nom):
    if nom not in SECTIONS:
        raise Http404("Section inconnue")
    return SECTIONS[nom]


def rendu(request, template, actif, contexte=None):
    """Ajoute ce dont toutes les pages ont besoin (menu, profil, messages non lus)."""
    speciales = {"accueil", "messages", "profil"}
    navigation = [
        (titre, [
            (cle, label, icone,
             reverse(f"dashboard:{cle}") if cle in speciales else reverse("dashboard:liste", args=[cle]))
            for cle, label, icone in liens
        ])
        for titre, liens in NAVIGATION
    ]
    ctx = {
        "navigation": navigation,
        "actif": actif,
        "profil": Profil.objects.first(),
        "non_lus": MessageContact.objects.filter(lu=False).count(),
    }
    ctx.update(contexte or {})
    return render(request, template, ctx)


# ─────────────────────────────────────────────
# Connexion / déconnexion
# ─────────────────────────────────────────────
class ConnexionForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update({"class": "input", "autofocus": True, "placeholder": " "})
        self.fields["password"].widget.attrs.update({"class": "input", "placeholder": " "})

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        if not user.is_staff:
            raise forms.ValidationError("Ce compte n'a pas accès au tableau de bord.", code="no_staff")


class ConnexionView(auth_views.LoginView):
    """
    Connexion avec limitation des tentatives : après trop d'échecs,
    l'adresse IP (ou l'identifiant visé) est bloquée 15 minutes.
    """
    template_name = "dashboard/connexion.html"
    authentication_form = ConnexionForm
    redirect_authenticated_user = True

    def get_default_redirect_url(self):
        return reverse("dashboard:accueil")

    def _cles(self):
        identifiant = self.request.POST.get("username", "").strip().lower()[:150]
        return adresse_ip(self.request), identifiant

    def post(self, request, *args, **kwargs):
        ip, identifiant = self._cles()
        if limite_connexion_ip.depasse(ip) or (identifiant and limite_connexion_user.depasse(identifiant)):
            contexte = self.get_context_data(form=self.get_form_class()(request), bloque=True)
            return self.render_to_response(contexte, status=429)
        return super().post(request, *args, **kwargs)

    def form_invalid(self, form):
        ip, identifiant = self._cles()
        limite_connexion_ip.enregistrer(ip)
        if identifiant:
            limite_connexion_user.enregistrer(identifiant)
        return super().form_invalid(form)

    def form_valid(self, form):
        ip, identifiant = self._cles()
        limite_connexion_ip.reinitialiser(ip)
        limite_connexion_user.reinitialiser(identifiant)
        return super().form_valid(form)


class DeconnexionView(auth_views.LogoutView):
    next_page = "dashboard:connexion"


# ─────────────────────────────────────────────
# Vue d'ensemble
# ─────────────────────────────────────────────
@staff_required
def accueil(request):
    contenu = [
        (cle, SECTIONS[cle]["titre"], SECTIONS[cle]["icone"], SECTIONS[cle]["model"].objects.count())
        for cle in ("projets", "competences", "experiences", "formations", "services", "technologies")
    ]
    return rendu(request, "dashboard/accueil.html", "accueil", {
        "stats": statistiques(lire_periode(request)),
        "profil_info": completion_profil(),
        "derniers_messages": MessageContact.objects.order_by("-date_envoi")[:5],
        "contenu": contenu,
    })


# ─────────────────────────────────────────────
# Profil
# ─────────────────────────────────────────────
@staff_required
def profil(request):
    instance = Profil.objects.first()
    form = f.ProfilForm(request.POST or None, request.FILES or None, instance=instance)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request, "Profil enregistré. Ton site est à jour ✨")
            return redirect("dashboard:profil")
        messages.error(request, "Certains champs sont à corriger.")
    return rendu(request, "dashboard/profil.html", "profil", {"form": form})


# ─────────────────────────────────────────────
# Sections génériques (liste, ajout, modification, suppression)
# ─────────────────────────────────────────────
@staff_required
def liste(request, section):
    conf = _section(section)
    objets = list(conf["model"].objects.all())
    elements = [{"obj": o, **conf["carte"](o)} for o in objets]

    groupes = None
    if conf.get("grouper") == "categorie":
        groupes = []
        for cat in CategorieCompetence.objects.all():
            groupes.append({
                "categorie": cat,
                "elements": [e for e in elements if e["obj"].categorie_id == cat.pk],
            })

    actif = conf.get("parent", (section,))[0]
    return rendu(request, "dashboard/liste.html", actif, {
        "section": section, "conf": conf, "elements": elements, "groupes": groupes,
    })


def _formulaire(request, section, obj=None):
    conf = _section(section)
    initial = {}
    if obj is None and section == "competences" and request.GET.get("categorie"):
        initial["categorie"] = request.GET["categorie"]
    if obj is None and "ordre" in conf["form"].base_fields:
        initial["ordre"] = conf["model"].objects.count()

    form = conf["form"](request.POST or None, request.FILES or None, instance=obj, initial=initial)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request, "Enregistré. Ton site est à jour ✨")
            if "continuer" in request.POST:
                return redirect("dashboard:creer", section=section)
            return redirect("dashboard:liste", section=section)
        messages.error(request, "Certains champs sont à corriger.")

    actif = conf.get("parent", (section,))[0]
    return rendu(request, "dashboard/formulaire.html", actif, {
        "section": section, "conf": conf, "form": form, "obj": obj,
    })


@staff_required
def creer(request, section):
    return _formulaire(request, section)


@staff_required
def modifier(request, section, pk):
    conf = _section(section)
    return _formulaire(request, section, get_object_or_404(conf["model"], pk=pk))


@staff_required
@require_POST
def supprimer(request, section, pk):
    conf = _section(section)
    obj = get_object_or_404(conf["model"], pk=pk)
    nom = str(obj)
    obj.delete()
    messages.success(request, f"« {nom} » a été supprimé.")
    return redirect("dashboard:liste", section=section)


@staff_required
@require_POST
def basculer(request, section, pk):
    conf = _section(section)
    champ = conf.get("basculer")
    if not champ:
        raise Http404
    obj = get_object_or_404(conf["model"], pk=pk)
    setattr(obj, champ, not getattr(obj, champ))
    obj.save(update_fields=[champ])
    messages.success(request, f"« {obj} » mis à jour.")
    return redirect("dashboard:liste", section=section)


# ─────────────────────────────────────────────
# Messages
# ─────────────────────────────────────────────
@staff_required
def messages_liste(request):
    filtre = request.GET.get("filtre", "tous")
    qs = MessageContact.objects.order_by("-date_envoi")
    if filtre == "non-lus":
        qs = qs.filter(lu=False)
    recherche = request.GET.get("q", "").strip()
    if recherche:
        qs = qs.filter(Q(nom__icontains=recherche) | Q(email__icontains=recherche)
                       | Q(sujet__icontains=recherche) | Q(message__icontains=recherche))
    return rendu(request, "dashboard/messages.html", "messages", {
        "liste": qs[:200], "filtre": filtre, "recherche": recherche,
        "total": MessageContact.objects.count(),
    })


@staff_required
def message_detail(request, pk):
    msg = get_object_or_404(MessageContact, pk=pk)
    if not msg.lu:
        msg.lu = True
        msg.save(update_fields=["lu"])
    return rendu(request, "dashboard/message.html", "messages", {"msg": msg})


@staff_required
@require_POST
def message_action(request, pk):
    msg = get_object_or_404(MessageContact, pk=pk)
    action = request.POST.get("action")
    if action == "supprimer":
        msg.delete()
        messages.success(request, "Message supprimé.")
        return redirect("dashboard:messages")
    if action == "non-lu":
        msg.lu = False
        msg.save(update_fields=["lu"])
        messages.success(request, "Marqué comme non lu.")
        return redirect("dashboard:messages")
    return redirect("dashboard:message", pk=pk)
