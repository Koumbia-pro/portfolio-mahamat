"""
Remplit la base avec le contenu du CV de Mahamat Hassan Oumar.

Utilisation :
    python manage.py seed_portfolio           # ne fait rien si un profil existe déjà
    python manage.py seed_portfolio --reset   # efface le contenu et le recrée

Tout reste modifiable ensuite depuis l'administration Django.
"""

from django.core.management.base import BaseCommand
from django.db import transaction

from portfolio.models import (
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

# (nom, icône Font Awesome, tourne autour de la photo)
TECHNOLOGIES = [
    ("Python", "fa-brands fa-python", True),
    ("Machine Learning", "fa-solid fa-brain", True),
    ("Deep Learning", "fa-solid fa-network-wired", False),
    ("Pandas", "fa-solid fa-table", False),
    ("Plotly", "fa-solid fa-chart-line", True),
    ("Streamlit", "fa-solid fa-gauge-high", False),
    ("Spark", "fa-solid fa-bolt", False),
    ("Hadoop", "fa-solid fa-server", False),
    ("Docker", "fa-brands fa-docker", True),
    ("Django", "fa-solid fa-leaf", False),
    ("PostgreSQL", "fa-solid fa-database", True),
    ("Git", "fa-brands fa-git-alt", False),
]


PROFIL = {
    "nom": "Mahamat Hassan Oumar",
    "titre": "Data Science & Machine Learning",
    "description_courte": (
        "Étudiant en Master 1 Intelligence Artificielle, je transforme des données "
        "brutes en modèles prédictifs, en tableaux de bord et en applications web utiles."
    ),
    "description_longue": (
        "Je suis étudiant en Master 1 Intelligence Artificielle à l'Université Aube Nouvelle "
        "de Ouagadougou. J'aime construire des solutions data de bout en bout : collecter et "
        "nettoyer les données, choisir et évaluer les bons modèles, puis rendre les résultats "
        "accessibles grâce à des tableaux de bord interactifs et des applications web.\n\n"
        "Au sein de l'équipe SahelPredict, je suis responsable de la modélisation d'un système "
        "de prévision des prix des céréales au Burkina Faso. Mon objectif : mettre l'IA au "
        "service de projets concrets, en particulier ceux qui ont un impact en Afrique de l'Ouest."
    ),
    "localisation": "Ouagadougou, Burkina Faso",
    "email": "mdoukoumbia@gmail.com",
    "telephone": "+226 05 50 57 00",
    "langues": "Français, Anglais",
    "disponible": True,
    "github": "https://github.com/Koumbia-pro",
}

COMPETENCES = [
    ("Machine Learning & IA", [
        ("Apprentissage supervisé (scikit-learn)", 80),
        ("Deep Learning (TensorFlow / PyTorch)", 65),
        ("Séries temporelles (SARIMA, LSTM)", 70),
        ("NLP & Text mining", 65),
    ]),
    ("Data Science & Visualisation", [
        ("Python · Pandas · NumPy", 85),
        ("Plotly · Seaborn · Matplotlib", 80),
        ("Streamlit & tableaux de bord", 80),
        ("Power BI", 60),
    ]),
    ("Big Data & Cloud", [
        ("Hadoop · HDFS · MapReduce", 65),
        ("Spark · Hive · Kafka", 60),
        ("Docker & Linux", 70),
    ]),
    ("Web & Bases de données", [
        ("Django", 75),
        ("PostgreSQL · SQL", 75),
        ("HTML · CSS · JavaScript", 70),
        ("Entrepôts de données", 65),
    ]),
]

STATISTIQUES = [
    ("fa-solid fa-diagram-project", "4+", "Projets réalisés"),
    ("fa-solid fa-microchip", "20+", "Technologies utilisées"),
    ("fa-solid fa-graduation-cap", "11", "Modules IA & Data"),
    ("fa-solid fa-language", "2", "Langues de travail"),
]

PROJETS = [
    {
        "titre": "SahelPredict — Prévision des prix des céréales",
        "description": (
            "Projet intégrateur du Master IA (équipe de 3), où je suis responsable de la "
            "modélisation. Prévision des prix des céréales sur les marchés du Burkina Faso à "
            "partir des données ouvertes du Programme alimentaire mondial (1992–2024), en "
            "comparant un modèle naïf saisonnier, SARIMA, le gradient boosting et un LSTM."
        ),
        "technologies": "Python, SARIMA, Gradient Boosting, LSTM, PostgreSQL",
        "categorie": "Machine Learning",
    },
    {
        "titre": "Plateforme d'analyse d'audience web",
        "description": (
            "Dashboard Streamlit interactif construit sur 5 000 logs HTTP : indicateurs clés, "
            "filtres, heatmap des heures de pointe, suivi des erreurs et des temps de réponse, "
            "export CSV. Pipeline de nettoyage commun au notebook et à l'application."
        ),
        "technologies": "Pandas, Plotly, Seaborn, Streamlit, Jupyter",
        "categorie": "Data",
    },
    {
        "titre": "Portfolio professionnel",
        "description": (
            "Ce site : une application Django entièrement administrable, avec formulaire de "
            "contact (validation, enregistrement et notification par e-mail) et une "
            "configuration de production sécurisée (HTTPS, HSTS, CSRF, secrets en variables "
            "d'environnement)."
        ),
        "technologies": "Django, PostgreSQL, JavaScript, Canvas",
        "categorie": "Web",
    },
    {
        "titre": "Cloud computing au service de l'IA",
        "description": (
            "Rapport de recherche et soutenance en groupe de 4 : architectures cloud pour le "
            "machine learning, infrastructures accélérées, MLOps, coûts, sécurité et "
            "souveraineté, avec une analyse appliquée au contexte du Burkina Faso."
        ),
        "technologies": "Cloud, MLOps, Recherche, Soutenance",
        "categorie": "Recherche",
    },
]

SERVICES = [
    ("fa-solid fa-brain", "Modèles de Machine Learning",
     "Conception, entraînement et évaluation de modèles prédictifs adaptés à votre problème, "
     "avec un protocole de validation rigoureux."),
    ("fa-solid fa-chart-line", "Analyse & visualisation de données",
     "Nettoyage de vos données et tableaux de bord interactifs pour suivre vos indicateurs "
     "et prendre de meilleures décisions."),
    ("fa-solid fa-code", "Applications web Django",
     "Sites et applications web sécurisés, avec base de données et interface "
     "d'administration simple à utiliser."),
    ("fa-solid fa-database", "Pipelines de données",
     "Collecte, transformation et stockage de données à grande échelle avec les outils "
     "Big Data (Hadoop, Spark, Kafka)."),
]

EXPERIENCES = [
    ("Responsable modélisation", "Équipe SahelPredict — Projet intégrateur M1 IA",
     "Choix et entraînement des modèles, protocole d'évaluation, journal des expériences et "
     "analyse des erreurs pour la prévision des prix des céréales.",
     "2026", "Présent"),
    ("Chercheur (travail de groupe)", "Module Cloud Computing — Université Aube Nouvelle",
     "Rapport de recherche sur le cloud au service de l'IA et du ML, présenté en soutenance.",
     "2026", "2026"),
]

FORMATIONS = [
    ("Master 1 Intelligence Artificielle", "Université Aube Nouvelle — Ouagadougou",
     "Apprentissage supervisé et non supervisé, Big Data, Text mining, Cloud computing, "
     "entrepôts de données, optimisation, traitement d'images, web sémantique.",
     "2025", "Présent"),
]


class Command(BaseCommand):
    help = "Remplit le portfolio avec le contenu du CV de Mahamat Hassan Oumar."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Efface le contenu existant (hors messages de contact) avant de le recréer.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if Profil.objects.exists() and not options["reset"]:
            self.stdout.write(self.style.WARNING(
                "Un profil existe déjà : rien n'a été modifié. "
                "Utilise --reset pour tout remplacer."
            ))
            return

        for model in (Competence, CategorieCompetence, Statistique, Projet, Technologie,
                      Service, Experience, Formation, Profil):
            model.objects.all().delete()

        Profil.objects.create(**PROFIL)

        for i, (nom, competences) in enumerate(COMPETENCES):
            categorie = CategorieCompetence.objects.create(nom=nom, ordre=i)
            for j, (comp, niveau) in enumerate(competences):
                Competence.objects.create(
                    categorie=categorie, nom=comp, pourcentage=niveau, ordre=j
                )

        for i, (icone, valeur, label) in enumerate(STATISTIQUES):
            Statistique.objects.create(icone=icone, valeur=valeur, label=label, ordre=i)

        for i, (nom, icone, orbite) in enumerate(TECHNOLOGIES):
            Technologie.objects.create(nom=nom, icone=icone, afficher_orbite=orbite, ordre=i)

        for i, projet in enumerate(PROJETS):
            Projet.objects.create(ordre=i, **projet)

        for i, (icone, titre, description) in enumerate(SERVICES):
            Service.objects.create(icone=icone, titre=titre, description=description, ordre=i)

        for i, (poste, entreprise, description, debut, fin) in enumerate(EXPERIENCES):
            Experience.objects.create(
                poste=poste, entreprise=entreprise, description=description,
                date_debut=debut, date_fin=fin, ordre=i,
            )

        for i, (diplome, etablissement, description, debut, fin) in enumerate(FORMATIONS):
            Formation.objects.create(
                diplome=diplome, etablissement=etablissement, description=description,
                date_debut=debut, date_fin=fin, ordre=i,
            )

        self.stdout.write(self.style.SUCCESS("Portfolio rempli avec succès ✅"))
