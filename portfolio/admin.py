"""
Administration — Portfolio Mahamat Hassan Oumar
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Profil,
    CategorieCompetence,
    Competence,
    Statistique,
    Projet,
    Service,
    Experience,
    Formation,
    MessageContact,
)


# ─────────────────────────────────────────────
# 1. PROFIL
# ─────────────────────────────────────────────
@admin.register(Profil)
class ProfilAdmin(admin.ModelAdmin):

    list_display = [
        "nom",
        "titre",
        "email",
        "disponible",
    ]

    fieldsets = (
        ("Informations personnelles", {
            "fields": (
                "nom",
                "titre",
                "age",
                "localisation",
                "email",
                "telephone",
                "langues",
                "disponible",
            )
        }),
        ("Textes", {
            "fields": (
                "description_courte",
                "description_longue",
            )
        }),
        ("Médias", {
            "fields": (
                "photo",
                "cv",
            )
        }),
        ("Réseaux sociaux", {
            "fields": (
                "github",
                "linkedin",
                "twitter",
            )
        }),
    )


# ─────────────────────────────────────────────
# 2. COMPÉTENCES
# ─────────────────────────────────────────────
class CompetenceInline(admin.TabularInline):
    """
    Afficher les compétences directement
    dans la catégorie.
    """
    model = Competence
    extra = 1
    fields = ["nom", "pourcentage", "ordre"]


@admin.register(CategorieCompetence)
class CategorieCompetenceAdmin(admin.ModelAdmin):

    list_display = ["nom", "ordre"]
    ordering = ["ordre"]
    inlines = [CompetenceInline]


@admin.register(Competence)
class CompetenceAdmin(admin.ModelAdmin):

    list_display = [
        "nom",
        "categorie",
        "afficher_barre",
        "ordre",
    ]

    list_filter = ["categorie"]
    ordering = ["categorie", "ordre"]

    def afficher_barre(self, obj):
        """Afficher une barre de progression dans l'admin."""
        couleur = "#8b3dff"
        return format_html(
            '<div style="width:150px;background:#1d2535;'
            'border-radius:99px;height:8px;">'
            '<div style="width:{}%;background:{};'
            'height:100%;border-radius:99px;"></div>'
            '</div> {}%',
            obj.pourcentage,
            couleur,
            obj.pourcentage,
        )

    afficher_barre.short_description = "Niveau"


# ─────────────────────────────────────────────
# 3. STATISTIQUES
# ─────────────────────────────────────────────
@admin.register(Statistique)
class StatistiqueAdmin(admin.ModelAdmin):

    list_display = [
        "valeur",
        "label",
        "icone",
        "ordre",
    ]

    ordering = ["ordre"]


# ─────────────────────────────────────────────
# 4. PROJETS
# ─────────────────────────────────────────────
@admin.register(Projet)
class ProjetAdmin(admin.ModelAdmin):

    list_display = [
        "titre",
        "technologies",
        "actif",
        "ordre",
        "date_creation",
    ]

    list_filter = ["actif"]
    list_editable = ["actif", "ordre"]
    ordering = ["ordre"]

    def apercu_image(self, obj):
        """Afficher un aperçu de l'image."""
        if obj.image:
            return format_html(
                '<img src="{}" width="80" '
                'style="border-radius:6px;">',
                obj.image.url,
            )
        return "Pas d'image"

    apercu_image.short_description = "Aperçu"


# ─────────────────────────────────────────────
# 5. SERVICES
# ─────────────────────────────────────────────
@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):

    list_display = [
        "titre",
        "icone",
        "ordre",
    ]

    ordering = ["ordre"]


# ─────────────────────────────────────────────
# 6. EXPÉRIENCE
# ─────────────────────────────────────────────
@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):

    list_display = [
        "poste",
        "entreprise",
        "date_debut",
        "date_fin",
        "ordre",
    ]

    ordering = ["ordre"]


# ─────────────────────────────────────────────
# 7. FORMATION
# ─────────────────────────────────────────────
@admin.register(Formation)
class FormationAdmin(admin.ModelAdmin):

    list_display = [
        "diplome",
        "etablissement",
        "date_debut",
        "date_fin",
        "ordre",
    ]

    ordering = ["ordre"]


# ─────────────────────────────────────────────
# 8. MESSAGES DE CONTACT
# ─────────────────────────────────────────────
@admin.register(MessageContact)
class MessageContactAdmin(admin.ModelAdmin):

    list_display = [
        "nom",
        "email",
        "sujet",
        "date_envoi",
        "lu",
    ]

    list_filter = ["lu"]
    list_editable = ["lu"]
    ordering = ["-date_envoi"]
    readonly_fields = [
        "nom",
        "email",
        "sujet",
        "message",
        "date_envoi",
    ]

    def has_add_permission(self, request):
        """Interdire l'ajout manuel de messages."""
        return False


# ─────────────────────────────────────────────
# PERSONNALISER L'INTERFACE ADMIN
# ─────────────────────────────────────────────
admin.site.site_header = "Portfolio Mahamat Hassan Oumar"
admin.site.site_title = "Portfolio Admin"
admin.site.index_title = "Tableau de bord"