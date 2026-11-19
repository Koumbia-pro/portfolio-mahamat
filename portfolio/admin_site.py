"""
Site d'administration Django (secours).
Le vrai tableau de bord du portfolio est sur /dashboard/.
"""

from django.contrib import admin


class PortfolioAdminSite(admin.AdminSite):
    site_header = "Portfolio — Mahamat Hassan Oumar"
    site_title = "Admin Portfolio"
    index_title = "Administration avancée"
    site_url = None  # le lien « Voir le site » est ajouté dans base_site.html
