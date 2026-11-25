"""
URLs principales — Portfolio Mahamat Hassan Oumar
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve

urlpatterns = [
    # Administration Django (chemin configurable avec ADMIN_URL)
    path(settings.ADMIN_URL, admin.site.urls),

    # Tableau de bord personnel
    path("dashboard/", include("portfolio.dashboard_urls")),

    # Application portfolio
    path("", include("portfolio.urls")),
]

if settings.DEBUG:
    # En développement, Django sert les fichiers envoyés (photo, CV, images).
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    # En production, ils sont servis depuis MEDIA_ROOT. Sur Railway, il faut
    # un volume monté sur ce dossier pour qu'ils survivent aux redéploiements.
    urlpatterns += [
        re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
    ]
