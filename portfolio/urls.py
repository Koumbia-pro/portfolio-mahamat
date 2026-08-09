"""
URLs — Application Portfolio
"""

from django.urls import path
from . import views

urlpatterns = [

    # Page principale
    path(
        "",
        views.index,
        name="index",
    ),

    # Formulaire contact
    path(
        "contact/",
        views.contact,
        name="contact",
    ),

    # Télécharger CV
    path(
        "cv/",
        views.telecharger_cv,
        name="telecharger_cv",
    ),

]