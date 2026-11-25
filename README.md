# Portfolio — Mahamat Hassan Oumar

Portfolio professionnel (Data Science & Machine Learning) développé avec Django,
avec un **tableau de bord personnel** pour modifier tout le contenu sans toucher au code.

## Technologies

- **Backend** : Python 3.12 / Django 5.2
- **Base de données** : PostgreSQL (SQLite possible en local)
- **Frontend** : HTML / CSS / JavaScript (sans framework)
- **Production** : Gunicorn + WhiteNoise, déploiement sur Railway

## Fonctionnalités

- Site une page animé : accueil, à propos, compétences, projets filtrables, services, parcours, contact
- Thème clair / sombre, responsive mobile → grand écran, respect de « réduire les animations »
- Tableau de bord `/dashboard/` : profil, projets, compétences, expériences, formations, services,
  technologies, chiffres clés, messages reçus, statistiques de visites (sans données personnelles)
- Images envoyées redimensionnées et allégées automatiquement (métadonnées GPS supprimées)
- SEO : balises Open Graph / Twitter, données structurées schema.org, `robots.txt`, `sitemap.xml`

## Installation locale

```bash
git clone https://github.com/Koumbia-pro/portfolio-mahamat.git
cd portfolio-mahamat
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env              # puis adapter les valeurs (DB_ENGINE=sqlite pour aller vite)
python manage.py migrate
python manage.py createsuperuser  # coche « staff » automatiquement
python manage.py seed_portfolio   # contenu de départ (facultatif)
python manage.py runserver
```

- Site : http://127.0.0.1:8000/
- Tableau de bord : http://127.0.0.1:8000/dashboard/
- Admin Django (avancé) : http://127.0.0.1:8000/admin/ (ou la valeur de `ADMIN_URL`)

## Commandes utiles

| Commande | Rôle |
| --- | --- |
| `python manage.py test` | Lance les tests automatiques |
| `python manage.py seed_portfolio [--reset]` | Remplit la base avec le contenu du CV |
| `python manage.py optimiser_images [--appliquer]` | Allège les images déjà envoyées |
| `python manage.py check --deploy` | Vérifie la configuration de production |

## Déploiement sur Railway

1. Créer un service depuis le dépôt GitHub et ajouter une base **PostgreSQL**
   (Railway fournit `DATABASE_URL` automatiquement).
2. Ajouter un **volume** monté sur `/app/media` et la variable `MEDIA_ROOT=/app/media`,
   sinon la photo, le CV et les images envoyés disparaissent à chaque redéploiement.
3. Définir les variables :

   | Variable | Exemple |
   | --- | --- |
   | `DJANGO_ENV` | `production` |
   | `SECRET_KEY` | longue chaîne aléatoire |
   | `ALLOWED_HOSTS` | `mon-domaine.com` (le domaine Railway est ajouté automatiquement) |
   | `CSRF_TRUSTED_ORIGINS` | `https://mon-domaine.com` |
   | `ADMIN_URL` | `gestion-xxxx/` (chemin difficile à deviner) |
   | `EMAIL_HOST_USER` / `EMAIL_HOST_PASSWORD` | compte Gmail + mot de passe d'application |

4. Le `Procfile` exécute `collectstatic`, `migrate` puis lance Gunicorn.

## Sécurité

- Secrets uniquement dans les variables d'environnement (`.env` n'est jamais versionné)
- En production : HTTPS forcé, HSTS, cookies sécurisés, `DEBUG` toujours désactivé
- En-têtes : Content-Security-Policy, Permissions-Policy, X-Frame-Options, nosniff, Referrer-Policy
- Connexion limitée (blocage 15 min après plusieurs échecs), une seule page de connexion pour le dashboard et l'admin
- Formulaire de contact : CSRF, champ piège anti-robots, 5 messages / heure / IP, protection contre l'injection d'en-têtes email
- Fichiers envoyés : taille limitée, CV vérifié comme vrai PDF, images ré-encodées

## Structure

```
portfolio-mahamat/
├── config/              → Configuration Django (settings, urls)
├── portfolio/           → Application : modèles, vues, dashboard, sécurité, images, tests
├── templates/           → Pages (portfolio, dashboard, admin, 404/500)
├── static/              → CSS / JS / images / CV par défaut
├── Procfile             → Commande de démarrage en production
└── requirements.txt     → Dépendances
```

## Licence

© Mahamat Hassan Oumar. Tous droits réservés.
