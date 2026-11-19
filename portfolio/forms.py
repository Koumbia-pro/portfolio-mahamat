"""
Formulaires du tableau de bord.
"""

from django import forms
from django.core.validators import FileExtensionValidator

from .models import (
    CategorieCompetence,
    Competence,
    Experience,
    Formation,
    Profil,
    Projet,
    Service,
    Statistique,
    Technologie,
)


class StyledModelForm(forms.ModelForm):
    """Ajoute les classes CSS du dashboard à chaque champ."""

    # Champs affichés comme icône Font Awesome avec aperçu
    icon_fields = ("icone",)
    # Champs affichés comme curseur 0–100
    range_fields = ("pourcentage",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            w = field.widget
            if isinstance(w, forms.CheckboxInput):
                w.attrs["class"] = "switch-input"
            elif isinstance(w, (forms.ClearableFileInput, forms.FileInput)):
                w.attrs["class"] = "file-input"
            elif isinstance(w, forms.Select):
                w.attrs["class"] = "input"
            else:
                w.attrs["class"] = "input"
            if isinstance(w, forms.Textarea):
                w.attrs.setdefault("rows", 4)
            if name in self.icon_fields:
                w.attrs["data-icon-input"] = "1"
                w.attrs["placeholder"] = "fa-solid fa-code"
            if name in self.range_fields:
                field.widget = forms.NumberInput(attrs={
                    "type": "range", "min": 0, "max": 100, "step": 5,
                    "class": "range", "data-range": "1",
                })
            if name == "ordre":
                w.attrs["min"] = 0


class ProfilForm(StyledModelForm):
    cv = forms.FileField(
        required=False,
        label="Fichier CV (PDF)",
        validators=[FileExtensionValidator(["pdf"])],
        widget=forms.ClearableFileInput(attrs={"accept": "application/pdf"}),
        help_text="Si vide, le CV fourni avec le site est proposé aux visiteurs.",
    )

    class Meta:
        model = Profil
        fields = [
            "nom", "titre", "photo", "cv",
            "description_courte", "roles_animes", "disponible", "statut",
            "description_longue", "age", "localisation", "langues",
            "email", "telephone", "texte_contact", "texte_footer",
            "github", "linkedin", "twitter",
        ]
        widgets = {
            "description_courte": forms.Textarea(attrs={"rows": 3}),
            "roles_animes": forms.Textarea(attrs={"rows": 4}),
            "description_longue": forms.Textarea(attrs={"rows": 8}),
            "texte_contact": forms.Textarea(attrs={"rows": 3}),
            "photo": forms.ClearableFileInput(attrs={"accept": "image/*"}),
        }

    # Regroupement des champs en cartes
    GROUPES = [
        ("Identité", "fa-id-card", ["nom", "titre", "photo", "cv"]),
        ("Accueil", "fa-house", ["description_courte", "roles_animes", "disponible", "statut"]),
        ("À propos", "fa-user", ["description_longue", "age", "localisation", "langues"]),
        ("Contact", "fa-envelope", ["email", "telephone", "texte_contact", "texte_footer"]),
        ("Réseaux sociaux", "fa-share-nodes", ["github", "linkedin", "twitter"]),
    ]

    def groupes(self):
        return [
            {"titre": t, "icone": i, "champs": [self[n] for n in noms]}
            for t, i, noms in self.GROUPES
        ]


class ProjetForm(StyledModelForm):
    class Meta:
        model = Projet
        fields = ["titre", "categorie", "description", "technologies",
                  "image", "lien", "lien_code", "actif", "ordre"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 5}),
            "image": forms.ClearableFileInput(attrs={"accept": "image/*"}),
        }


class CategorieCompetenceForm(StyledModelForm):
    class Meta:
        model = CategorieCompetence
        fields = ["nom", "ordre"]


class CompetenceForm(StyledModelForm):
    class Meta:
        model = Competence
        fields = ["categorie", "nom", "pourcentage", "ordre"]


class ExperienceForm(StyledModelForm):
    class Meta:
        model = Experience
        fields = ["poste", "entreprise", "date_debut", "date_fin", "description", "ordre"]


class FormationForm(StyledModelForm):
    class Meta:
        model = Formation
        fields = ["diplome", "etablissement", "date_debut", "date_fin", "description", "ordre"]


class ServiceForm(StyledModelForm):
    class Meta:
        model = Service
        fields = ["titre", "icone", "description", "ordre"]


class TechnologieForm(StyledModelForm):
    class Meta:
        model = Technologie
        fields = ["nom", "icone", "afficher_orbite", "ordre"]


class StatistiqueForm(StyledModelForm):
    class Meta:
        model = Statistique
        fields = ["valeur", "label", "icone", "ordre"]
