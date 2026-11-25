"""
Django settings — Portfolio Mahamat Hassan Oumar

Toute la configuration sensible vient des variables d'environnement
(fichier .env en local, variables Railway en production).
Voir .env.example pour la liste complète.
"""

import os
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse

from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Charger le .env à la racine du projet (quel que soit le dossier courant)
load_dotenv(BASE_DIR / ".env")


def env_bool(nom, defaut=False):
    valeur = os.getenv(nom)
    if valeur is None:
        return defaut
    return valeur.strip().lower() in {"1", "true", "yes", "on", "oui"}


def env_list(nom, defaut=""):
    return [v.strip() for v in os.getenv(nom, defaut).split(",") if v.strip()]


# ─────────────────────────────────────────────
# ENVIRONNEMENT
# ─────────────────────────────────────────────
DJANGO_ENV = os.getenv("DJANGO_ENV", "development")
IS_PRODUCTION = DJANGO_ENV == "production"
TESTING = len(sys.argv) > 1 and sys.argv[1] == "test"

# ─────────────────────────────────────────────
# SÉCURITÉ
# ─────────────────────────────────────────────
SECRET_KEY = os.getenv("SECRET_KEY", "")
if not SECRET_KEY:
    if IS_PRODUCTION:
        raise ImproperlyConfigured("SECRET_KEY doit être définie en production.")
    # Clé de secours réservée au développement local
    SECRET_KEY = "dev-only-insecure-key-ne-pas-utiliser-en-production"

# DEBUG est toujours désactivé en production, même si la variable est oubliée.
DEBUG = env_bool("DEBUG") and not IS_PRODUCTION

ALLOWED_HOSTS = env_list("ALLOWED_HOSTS", "localhost,127.0.0.1")

# Domaine public fourni automatiquement par Railway
RAILWAY_DOMAIN = os.getenv("RAILWAY_PUBLIC_DOMAIN", "").strip()
if RAILWAY_DOMAIN and RAILWAY_DOMAIN not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(RAILWAY_DOMAIN)

# Chemin de l'administration Django (le changer complique les attaques automatisées)
ADMIN_URL = os.getenv("ADMIN_URL", "admin/").strip("/") + "/"

# ─────────────────────────────────────────────
# APPLICATIONS
# ─────────────────────────────────────────────
INSTALLED_APPS = [
    "portfolio.apps.PortfolioAdminConfig",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "portfolio",
]

# ─────────────────────────────────────────────
# MIDDLEWARE
# ─────────────────────────────────────────────
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "portfolio.middleware.SecurityHeadersMiddleware",
]

ROOT_URLCONF = "config.urls"

# ─────────────────────────────────────────────
# TEMPLATES
# ─────────────────────────────────────────────
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# ─────────────────────────────────────────────
# BASE DE DONNÉES
# ─────────────────────────────────────────────
# Ordre de priorité :
#   1. DB_ENGINE=sqlite        → SQLite (tests en local sans PostgreSQL)
#   2. DATABASE_URL            → fournie automatiquement par Railway
#   3. DB_NAME / DB_USER / …   → configuration PostgreSQL manuelle
DATABASE_URL = os.getenv("DATABASE_URL", "").strip()

if os.getenv("DB_ENGINE", "postgresql") == "sqlite":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": os.getenv("SQLITE_PATH", BASE_DIR / "db.sqlite3"),
            # Attendre jusqu'à 20 s si un autre processus écrit en même temps
            "OPTIONS": {"timeout": 20},
        }
    }
elif DATABASE_URL:
    url = urlparse(DATABASE_URL)
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": unquote(url.path.lstrip("/")),
            "USER": unquote(url.username or ""),
            "PASSWORD": unquote(url.password or ""),
            "HOST": url.hostname or "",
            "PORT": str(url.port or 5432),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("DB_NAME"),
            "USER": os.getenv("DB_USER"),
            "PASSWORD": os.getenv("DB_PASSWORD"),
            "HOST": os.getenv("DB_HOST", "localhost"),
            "PORT": os.getenv("DB_PORT", "5432"),
        }
    }

if DATABASES["default"]["ENGINE"].endswith("postgresql"):
    DATABASES["default"]["OPTIONS"] = {"connect_timeout": 10}
    # Réutiliser les connexions plutôt que d'en ouvrir une par requête
    DATABASES["default"]["CONN_MAX_AGE"] = 60
    DATABASES["default"]["CONN_HEALTH_CHECKS"] = True

# ─────────────────────────────────────────────
# CACHE (limitation des tentatives de connexion et des messages)
# ─────────────────────────────────────────────
# En production, cache sur disque : partagé entre tous les processus du serveur
# (Passenger chez o2switch, Gunicorn ailleurs), donc les limites restent fiables.
if IS_PRODUCTION and not TESTING:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
            "LOCATION": os.getenv("CACHE_DIR", str(BASE_DIR / "var" / "cache")),
        }
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "portfolio",
        }
    }

# ─────────────────────────────────────────────
# MOT DE PASSE
# ─────────────────────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
     "OPTIONS": {"min_length": 10}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]
if TESTING:
    # Hachage rapide uniquement pendant les tests (jamais en production)
    PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

# ─────────────────────────────────────────────
# LANGUE ET TIMEZONE
# ─────────────────────────────────────────────
LANGUAGE_CODE = "fr-fr"
TIME_ZONE = "Africa/Ouagadougou"
USE_I18N = True
USE_TZ = True

# ─────────────────────────────────────────────
# FICHIERS STATIQUES
# ─────────────────────────────────────────────
STATIC_URL = "/static/"
STATIC_ROOT = Path(os.getenv("STATIC_ROOT", BASE_DIR / "staticfiles"))
STATICFILES_DIRS = [BASE_DIR / "static"]
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        # Les tests n'ont pas besoin de collectstatic
        "BACKEND": (
            "django.contrib.staticfiles.storage.StaticFilesStorage"
            if TESTING
            else "whitenoise.storage.CompressedManifestStaticFilesStorage"
        ),
    },
}

# ─────────────────────────────────────────────
# FICHIERS MEDIA (photo, CV, images des projets)
# ─────────────────────────────────────────────
MEDIA_URL = "/media/"
MEDIA_ROOT = Path(os.getenv("MEDIA_ROOT", BASE_DIR / "media"))

# Taille maximale d'un fichier envoyé depuis le dashboard
MAX_UPLOAD_MB = int(os.getenv("MAX_UPLOAD_MB", 10))
FILE_UPLOAD_PERMISSIONS = 0o644

# ─────────────────────────────────────────────
# EMAIL
# ─────────────────────────────────────────────
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = env_bool("EMAIL_USE_TLS", True)
EMAIL_TIMEOUT = 10  # ne jamais bloquer le formulaire si le serveur SMTP est lent
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", EMAIL_HOST_USER or "webmaster@localhost")
SERVER_EMAIL = DEFAULT_FROM_EMAIL
# Adresse qui reçoit les messages du formulaire de contact
CONTACT_EMAIL = os.getenv("CONTACT_EMAIL", EMAIL_HOST_USER)

if EMAIL_HOST_USER and EMAIL_HOST_PASSWORD:
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
else:
    # Sans identifiants SMTP, les emails s'affichent dans la console
    # (les messages restent enregistrés dans le dashboard).
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# ─────────────────────────────────────────────
# PROTECTION CSRF
# ─────────────────────────────────────────────
CSRF_TRUSTED_ORIGINS = env_list("CSRF_TRUSTED_ORIGINS")
if RAILWAY_DOMAIN:
    CSRF_TRUSTED_ORIGINS.append(f"https://{RAILWAY_DOMAIN}")
if not IS_PRODUCTION:
    CSRF_TRUSTED_ORIGINS += ["http://localhost:8000", "http://127.0.0.1:8000"]

# ─────────────────────────────────────────────
# SESSIONS ET COOKIES
# ─────────────────────────────────────────────
SESSION_COOKIE_AGE = 3600 * 8  # une journée de travail sur le dashboard
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_HTTPONLY = True  # le jeton est lu dans le formulaire, pas dans le cookie
CSRF_COOKIE_SAMESITE = "Lax"

# ─────────────────────────────────────────────
# EN-TÊTES DE SÉCURITÉ (toujours actifs)
# ─────────────────────────────────────────────
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
SECURE_CROSS_ORIGIN_OPENER_POLICY = "same-origin"
X_FRAME_OPTIONS = "DENY"

# ─────────────────────────────────────────────
# SÉCURITÉ EN PRODUCTION
# ─────────────────────────────────────────────
# Adresse IP du visiteur : ne lire X-Forwarded-For que derrière un proxy de confiance
# (Railway : True). Sur o2switch, Apache transmet directement la vraie adresse.
USE_X_FORWARDED_FOR = env_bool("USE_X_FORWARDED_FOR", False)

if IS_PRODUCTION:
    # Si un proxy termine le HTTPS devant Django (Railway…), il l'indique dans
    # X-Forwarded-Proto. Sans en-tête, Django utilise le schéma réel de la requête.
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = env_bool("SECURE_SSL_REDIRECT", True)
    SECURE_HSTS_SECONDS = int(os.getenv("SECURE_HSTS_SECONDS", 31536000))
    SECURE_HSTS_INCLUDE_SUBDOMAINS = env_bool("SECURE_HSTS_INCLUDE_SUBDOMAINS", False)
    SECURE_HSTS_PRELOAD = env_bool("SECURE_HSTS_PRELOAD", False)
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

# ─────────────────────────────────────────────
# LOGS
# ─────────────────────────────────────────────
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "portfolio": {
            "handlers": ["console"],
            "level": "INFO" if IS_PRODUCTION else "DEBUG",
            "propagate": False,
        },
    },
}

# ─────────────────────────────────────────────
# DIVERS
# ─────────────────────────────────────────────
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Connexion au tableau de bord
LOGIN_URL = "dashboard:connexion"
LOGIN_REDIRECT_URL = "dashboard:accueil"
