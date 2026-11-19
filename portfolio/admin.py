"""
Administration — Portfolio Mahamat Hassan Oumar
"""

from urllib.parse import quote

from django.contrib import admin, messages
from django.utils.html import format_html

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
    VisiteJour,
)


def apercu(url, taille=56, rond=False):
    rayon = "50%" if rond else "10px"
    return format_html(
        '<img src="{}" style="width:{}px;height:{}px;object-fit:cover;border-radius:{};">',
        url, taille, taille, rayon,
    )


def icone(classe):
    return format_html('<i class="{}" style="font-size:18px;width:22px;text-align:center"></i>', classe)


# ─────────────────────────────────────────────
# 1. PROFIL
# ─────────────────────────────────────────────
@admin.register(Profil)
class ProfilAdmin(admin.ModelAdmin):

    list_display = ["miniature", "nom", "titre", "email", "disponible"]
    list_display_links = ["miniature", "nom"]
    readonly_fields = ["miniature_grande"]

    fieldsets = (
        ("Identité", {
            "fields": ("miniature_grande", "nom", "titre", "photo", "cv"),
        }),
        ("Accueil", {
            "fields": ("description_courte", "roles_animes", "disponible", "statut"),
            "description": "Ce qui s'affiche en premier sur ton site.",
        }),
        ("À propos", {
            "fields": ("description_longue", "age", "localisation", "langues"),
        }),
        ("Contact", {
            "fields": ("email", "telephone", "texte_contact", "texte_footer"),
        }),
        ("Réseaux sociaux", {
            "fields": ("github", "linkedin", "twitter"),
        }),
    )

    def has_add_permission(self, request):
        """Un seul profil."""
        return not Profil.objects.exists()

    @admin.display(description="Photo")
    def miniature(self, obj):
        return apercu(obj.photo.url, 40, rond=True) if obj.photo else "—"

    @admin.display(description="Photo actuelle")
    def miniature_grande(self, obj):
        if obj and obj.photo:
            return apercu(obj.photo.url, 120, rond=True)
        return "Aucune photo envoyée : la photo par défaut du site est utilisée."


# ─────────────────────────────────────────────
# 2. COMPÉTENCES
# ─────────────────────────────────────────────
class CompetenceInline(admin.TabularInline):
    model = Competence
    extra = 1
    fields = ["nom", "pourcentage", "ordre"]


@admin.register(CategorieCompetence)
class CategorieCompetenceAdmin(admin.ModelAdmin):
    list_display = ["nom", "nombre", "ordre"]
    list_editable = ["ordre"]
    inlines = [CompetenceInline]

    @admin.display(description="Compétences")
    def nombre(self, obj):
        return obj.competences.count()


@admin.register(Competence)
class CompetenceAdmin(admin.ModelAdmin):
    list_display = ["nom", "categorie", "afficher_barre", "pourcentage", "ordre"]
    list_editable = ["pourcentage", "ordre"]
    list_filter = ["categorie"]
    search_fields = ["nom"]
    ordering = ["categorie", "ordre"]

    @admin.display(description="Niveau")
    def afficher_barre(self, obj):
        return format_html(
            '<div class="pf-bar"><span style="width:{}%"></span></div>',
            obj.pourcentage,
        )


# ─────────────────────────────────────────────
# 3. TECHNOLOGIES
# ─────────────────────────────────────────────
@admin.register(Technologie)
class TechnologieAdmin(admin.ModelAdmin):
    list_display = ["apercu_icone", "nom", "icone", "afficher_orbite", "ordre"]
    list_display_links = ["apercu_icone", "nom"]
    list_editable = ["icone", "afficher_orbite", "ordre"]

    @admin.display(description="")
    def apercu_icone(self, obj):
        return icone(obj.icone)


# ─────────────────────────────────────────────
# 4. STATISTIQUES (chiffres clés)
# ─────────────────────────────────────────────
@admin.register(Statistique)
class StatistiqueAdmin(admin.ModelAdmin):
    list_display = ["apercu_icone", "valeur", "label", "ordre"]
    list_display_links = ["apercu_icone", "label"]
    list_editable = ["valeur", "ordre"]

    @admin.display(description="")
    def apercu_icone(self, obj):
        return icone(obj.icone)


# ─────────────────────────────────────────────
# 5. PROJETS
# ─────────────────────────────────────────────
@admin.register(Projet)
class ProjetAdmin(admin.ModelAdmin):
    list_display = ["apercu_image", "titre", "categorie", "technologies", "actif", "ordre"]
    list_display_links = ["apercu_image", "titre"]
    list_editable = ["actif", "ordre"]
    list_filter = ["actif", "categorie"]
    search_fields = ["titre", "description", "technologies"]
    readonly_fields = ["apercu_grand"]
    actions = ["publier", "masquer"]

    fieldsets = (
        (None, {"fields": ("titre", "categorie", "description", "technologies")}),
        ("Image", {"fields": ("apercu_grand", "image")}),
        ("Liens", {"fields": ("lien", "lien_code")}),
        ("Affichage", {"fields": ("actif", "ordre")}),
    )

    @admin.display(description="Image")
    def apercu_image(self, obj):
        return apercu(obj.image.url, 64) if obj.image else "—"

    @admin.display(description="Aperçu")
    def apercu_grand(self, obj):
        if obj and obj.image:
            return format_html('<img src="{}" style="max-width:420px;border-radius:12px;">', obj.image.url)
        return "Pas d'image : une couverture colorée est générée automatiquement."

    @admin.action(description="Afficher sur le site")
    def publier(self, request, queryset):
        n = queryset.update(actif=True)
        self.message_user(request, f"{n} projet(s) affiché(s).", messages.SUCCESS)

    @admin.action(description="Masquer du site")
    def masquer(self, request, queryset):
        n = queryset.update(actif=False)
        self.message_user(request, f"{n} projet(s) masqué(s).", messages.SUCCESS)


# ─────────────────────────────────────────────
# 6. SERVICES
# ─────────────────────────────────────────────
@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ["apercu_icone", "titre", "ordre"]
    list_display_links = ["apercu_icone", "titre"]
    list_editable = ["ordre"]

    @admin.display(description="")
    def apercu_icone(self, obj):
        return icone(obj.icone)


# ─────────────────────────────────────────────
# 7. EXPÉRIENCE & FORMATION
# ─────────────────────────────────────────────
@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ["poste", "entreprise", "date_debut", "date_fin", "ordre"]
    list_editable = ["ordre"]


@admin.register(Formation)
class FormationAdmin(admin.ModelAdmin):
    list_display = ["diplome", "etablissement", "date_debut", "date_fin", "ordre"]
    list_editable = ["ordre"]


# ─────────────────────────────────────────────
# 8. MESSAGES DE CONTACT
# ─────────────────────────────────────────────
@admin.register(MessageContact)
class MessageContactAdmin(admin.ModelAdmin):
    list_display = ["etat", "nom", "email", "sujet", "date_envoi"]
    list_display_links = ["nom", "sujet"]
    list_filter = ["lu", "date_envoi"]
    search_fields = ["nom", "email", "sujet", "message"]
    date_hierarchy = "date_envoi"
    ordering = ["-date_envoi"]
    readonly_fields = ["nom", "email", "sujet", "message", "date_envoi", "repondre"]
    fields = ["repondre", "nom", "email", "sujet", "date_envoi", "message", "lu"]
    actions = ["marquer_lu", "marquer_non_lu"]

    def has_add_permission(self, request):
        return False

    def change_view(self, request, object_id, form_url="", extra_context=None):
        """Ouvrir un message le marque comme lu."""
        MessageContact.objects.filter(pk=object_id, lu=False).update(lu=True)
        return super().change_view(request, object_id, form_url, extra_context)

    @admin.display(description="", ordering="lu")
    def etat(self, obj):
        if obj.lu:
            return format_html('<span class="pf-pill">Lu</span>')
        return format_html('<span class="pf-pill pf-pill-new">Nouveau</span>')

    @admin.display(description="Répondre")
    def repondre(self, obj):
        return format_html(
            '<a class="button" href="mailto:{}?subject={}">Répondre par email</a>',
            obj.email, quote(f"Re: {obj.sujet}"),
        )

    @admin.action(description="Marquer comme lu")
    def marquer_lu(self, request, queryset):
        queryset.update(lu=True)

    @admin.action(description="Marquer comme non lu")
    def marquer_non_lu(self, request, queryset):
        queryset.update(lu=False)


# ─────────────────────────────────────────────
# 9. STATISTIQUES DE VISITES (lecture seule)
# ─────────────────────────────────────────────
@admin.register(VisiteJour)
class VisiteJourAdmin(admin.ModelAdmin):
    list_display = ["date", "vues", "vues_mobile", "telechargements_cv"]
    date_hierarchy = "date"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
