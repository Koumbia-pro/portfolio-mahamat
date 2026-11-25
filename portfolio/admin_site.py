"""
Site d'administration Django (secours).
Le vrai tableau de bord du portfolio est sur /dashboard/.
"""

from urllib.parse import urlencode

from django.contrib import admin
from django.shortcuts import redirect
from django.urls import reverse


class PortfolioAdminSite(admin.AdminSite):
    site_header = "Portfolio — Mahamat Hassan Oumar"
    site_title = "Admin Portfolio"
    index_title = "Administration avancée"
    site_url = None  # le lien « Voir le site » est ajouté dans base_site.html

    def login(self, request, extra_context=None):
        """
        Une seule page de connexion pour tout le site : celle du dashboard,
        qui limite les tentatives de mot de passe.
        """
        suite = request.GET.get("next") or reverse("admin:index", current_app=self.name)
        return redirect(f"{reverse('dashboard:connexion')}?{urlencode({'next': suite})}")
