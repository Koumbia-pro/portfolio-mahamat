"""
URLs — Application Portfolio
"""

from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("contact/", views.contact, name="contact"),
    path("cv/", views.telecharger_cv, name="telecharger_cv"),
    path("robots.txt", views.robots_txt, name="robots"),
    path("sitemap.xml", views.sitemap_xml, name="sitemap"),
    path("favicon.ico", views.favicon, name="favicon"),
]
