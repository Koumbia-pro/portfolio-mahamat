"""
URLs du tableau de bord personnel — /dashboard/
"""

from django.urls import path

from . import dashboard_views as v

app_name = "dashboard"

urlpatterns = [
    path("", v.accueil, name="accueil"),
    path("connexion/", v.ConnexionView.as_view(), name="connexion"),
    path("deconnexion/", v.DeconnexionView.as_view(), name="deconnexion"),
    path("profil/", v.profil, name="profil"),

    path("messages/", v.messages_liste, name="messages"),
    path("messages/<int:pk>/", v.message_detail, name="message"),
    path("messages/<int:pk>/action/", v.message_action, name="message_action"),

    path("<slug:section>/", v.liste, name="liste"),
    path("<slug:section>/nouveau/", v.creer, name="creer"),
    path("<slug:section>/<int:pk>/", v.modifier, name="modifier"),
    path("<slug:section>/<int:pk>/supprimer/", v.supprimer, name="supprimer"),
    path("<slug:section>/<int:pk>/basculer/", v.basculer, name="basculer"),
]
