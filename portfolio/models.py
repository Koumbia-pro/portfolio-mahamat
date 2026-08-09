"""
Modèles — Portfolio Mahamat Hassan Oumar
"""

from django.db import models


# ─────────────────────────────────────────────
# 1. PROFIL PRINCIPAL
# ─────────────────────────────────────────────
class Profil(models.Model):
    """
    Informations personnelles principales.
    Un seul profil dans la base de données.
    """

    nom = models.CharField(
        max_length=100,
        verbose_name="Nom complet"
    )

    titre = models.CharField(
        max_length=100,
        verbose_name="Titre professionnel",
        help_text="Ex: Développeur Backend"
    )

    description_courte = models.TextField(
        verbose_name="Description courte (hero)",
        help_text="Texte affiché sur la page d'accueil"
    )

    description_longue = models.TextField(
        verbose_name="Description longue (à propos)",
        blank=True
    )

    photo = models.ImageField(
        upload_to="profile/",
        verbose_name="Photo de profil",
        blank=True,
        null=True
    )

    age = models.PositiveIntegerField(
        verbose_name="Âge",
        blank=True,
        null=True
    )

    localisation = models.CharField(
        max_length=100,
        verbose_name="Localisation",
        help_text="Ex: Ouagadougou, Burkina Faso"
    )

    email = models.EmailField(
        verbose_name="Email"
    )

    telephone = models.CharField(
        max_length=20,
        verbose_name="Téléphone",
        blank=True
    )

    disponible = models.BooleanField(
        default=True,
        verbose_name="Disponible pour des opportunités"
    )

    langues = models.CharField(
        max_length=200,
        verbose_name="Langues",
        help_text="Ex: Français (Natif), Anglais (Intermédiaire)"
    )

    github = models.URLField(
        verbose_name="GitHub",
        blank=True
    )

    linkedin = models.URLField(
        verbose_name="LinkedIn",
        blank=True
    )

    twitter = models.URLField(
        verbose_name="Twitter / X",
        blank=True
    )

    cv = models.FileField(
        upload_to="cv/",
        verbose_name="Fichier CV (PDF)",
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = "Profil"
        verbose_name_plural = "Profil"

    def __str__(self):
        return self.nom


# ─────────────────────────────────────────────
# 2. COMPÉTENCES
# ─────────────────────────────────────────────
class CategorieCompetence(models.Model):
    """
    Catégorie de compétences.
    Ex: Langages, Frameworks, Bases de données
    """

    nom = models.CharField(
        max_length=100,
        verbose_name="Nom de la catégorie"
    )

    ordre = models.PositiveIntegerField(
        default=0,
        verbose_name="Ordre d'affichage"
    )

    class Meta:
        verbose_name = "Catégorie de compétence"
        verbose_name_plural = "Catégories de compétences"
        ordering = ["ordre"]

    def __str__(self):
        return self.nom


class Competence(models.Model):
    """
    Une compétence avec son niveau en pourcentage.
    """

    categorie = models.ForeignKey(
        CategorieCompetence,
        on_delete=models.CASCADE,
        related_name="competences",
        verbose_name="Catégorie"
    )

    nom = models.CharField(
        max_length=100,
        verbose_name="Nom de la compétence"
    )

    pourcentage = models.PositiveIntegerField(
        verbose_name="Niveau (%)",
        help_text="Entre 0 et 100"
    )

    ordre = models.PositiveIntegerField(
        default=0,
        verbose_name="Ordre d'affichage"
    )

    class Meta:
        verbose_name = "Compétence"
        verbose_name_plural = "Compétences"
        ordering = ["ordre"]

    def __str__(self):
        return f"{self.nom} — {self.pourcentage}%"


# ─────────────────────────────────────────────
# 3. STATISTIQUES
# ─────────────────────────────────────────────
class Statistique(models.Model):
    """
    Chiffres clés affichés dans la section stats.
    Ex: 15+ Projets réalisés
    """

    icone = models.CharField(
        max_length=100,
        verbose_name="Classe icône Font Awesome",
        help_text="Ex: fa-solid fa-diagram-project"
    )

    valeur = models.CharField(
        max_length=20,
        verbose_name="Valeur",
        help_text="Ex: 15+, 100%, 24/7"
    )

    label = models.CharField(
        max_length=100,
        verbose_name="Label",
        help_text="Ex: Projets réalisés"
    )

    ordre = models.PositiveIntegerField(
        default=0,
        verbose_name="Ordre d'affichage"
    )

    class Meta:
        verbose_name = "Statistique"
        verbose_name_plural = "Statistiques"
        ordering = ["ordre"]

    def __str__(self):
        return f"{self.valeur} — {self.label}"


# ─────────────────────────────────────────────
# 4. PROJETS
# ─────────────────────────────────────────────
class Projet(models.Model):
    """
    Projet réalisé avec image, description et technologies.
    """

    titre = models.CharField(
        max_length=100,
        verbose_name="Titre du projet"
    )

    description = models.TextField(
        verbose_name="Description"
    )

    image = models.ImageField(
        upload_to="projets/",
        verbose_name="Image du projet",
        blank=True,
        null=True
    )

    technologies = models.CharField(
        max_length=300,
        verbose_name="Technologies",
        help_text="Séparer par des virgules. Ex: Django, Python, PostgreSQL"
    )

    lien = models.URLField(
        verbose_name="Lien du projet",
        blank=True
    )

    ordre = models.PositiveIntegerField(
        default=0,
        verbose_name="Ordre d'affichage"
    )

    actif = models.BooleanField(
        default=True,
        verbose_name="Afficher ce projet"
    )

    date_creation = models.DateField(
        auto_now_add=True,
        verbose_name="Date d'ajout"
    )

    class Meta:
        verbose_name = "Projet"
        verbose_name_plural = "Projets"
        ordering = ["ordre"]

    def __str__(self):
        return self.titre

    def get_technologies_list(self):
        """Retourner les technologies sous forme de liste."""
        return [
            tech.strip()
            for tech in self.technologies.split(",")
        ]


# ─────────────────────────────────────────────
# 5. SERVICES
# ─────────────────────────────────────────────
class Service(models.Model):
    """
    Services proposés.
    """

    icone = models.CharField(
        max_length=100,
        verbose_name="Classe icône Font Awesome",
        help_text="Ex: fa-solid fa-globe"
    )

    titre = models.CharField(
        max_length=100,
        verbose_name="Titre du service"
    )

    description = models.TextField(
        verbose_name="Description"
    )

    ordre = models.PositiveIntegerField(
        default=0,
        verbose_name="Ordre d'affichage"
    )

    class Meta:
        verbose_name = "Service"
        verbose_name_plural = "Services"
        ordering = ["ordre"]

    def __str__(self):
        return self.titre


# ─────────────────────────────────────────────
# 6. EXPÉRIENCE PROFESSIONNELLE
# ─────────────────────────────────────────────
class Experience(models.Model):
    """
    Expérience professionnelle.
    """

    poste = models.CharField(
        max_length=150,
        verbose_name="Poste"
    )

    entreprise = models.CharField(
        max_length=150,
        verbose_name="Entreprise / Organisation"
    )

    description = models.TextField(
        verbose_name="Description"
    )

    date_debut = models.CharField(
        max_length=20,
        verbose_name="Date de début",
        help_text="Ex: 08/2025"
    )

    date_fin = models.CharField(
        max_length=20,
        verbose_name="Date de fin",
        help_text="Ex: 01/2026 ou Présent",
        blank=True,
        default="Présent"
    )

    ordre = models.PositiveIntegerField(
        default=0,
        verbose_name="Ordre d'affichage"
    )

    class Meta:
        verbose_name = "Expérience"
        verbose_name_plural = "Expériences"
        ordering = ["ordre"]

    def __str__(self):
        return f"{self.poste} — {self.entreprise}"


# ─────────────────────────────────────────────
# 7. FORMATION
# ─────────────────────────────────────────────
class Formation(models.Model):
    """
    Formation académique.
    """

    diplome = models.CharField(
        max_length=150,
        verbose_name="Diplôme / Formation"
    )

    etablissement = models.CharField(
        max_length=150,
        verbose_name="Établissement"
    )

    description = models.TextField(
        verbose_name="Description",
        blank=True
    )

    date_debut = models.CharField(
        max_length=20,
        verbose_name="Date de début",
        help_text="Ex: 2023"
    )

    date_fin = models.CharField(
        max_length=20,
        verbose_name="Date de fin",
        help_text="Ex: 2026 ou Présent",
        blank=True,
        default="Présent"
    )

    ordre = models.PositiveIntegerField(
        default=0,
        verbose_name="Ordre d'affichage"
    )

    class Meta:
        verbose_name = "Formation"
        verbose_name_plural = "Formations"
        ordering = ["ordre"]

    def __str__(self):
        return f"{self.diplome} — {self.etablissement}"


# ─────────────────────────────────────────────
# 8. MESSAGES DE CONTACT
# ─────────────────────────────────────────────
class MessageContact(models.Model):
    """
    Messages reçus via le formulaire de contact.
    """

    nom = models.CharField(
        max_length=100,
        verbose_name="Nom complet"
    )

    email = models.EmailField(
        verbose_name="Email"
    )

    sujet = models.CharField(
        max_length=200,
        verbose_name="Sujet"
    )

    message = models.TextField(
        verbose_name="Message"
    )

    date_envoi = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date d'envoi"
    )

    lu = models.BooleanField(
        default=False,
        verbose_name="Message lu"
    )

    class Meta:
        verbose_name = "Message de contact"
        verbose_name_plural = "Messages de contact"
        ordering = ["-date_envoi"]

    def __str__(self):
        return f"{self.nom} — {self.sujet}"