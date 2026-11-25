from django.apps import AppConfig
from django.contrib.admin import apps as admin_apps


class PortfolioConfig(AppConfig):
    default = True
    name = "portfolio"
    verbose_name = "Mon portfolio"


class PortfolioAdminConfig(admin_apps.AdminConfig):
    """Remplace l'admin Django par l'admin avec tableau de bord."""
    default = False
    default_site = "portfolio.admin_site.PortfolioAdminSite"
