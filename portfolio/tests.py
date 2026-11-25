"""
Tests du portfolio : pages publiques, formulaire de contact, sécurité,
tableau de bord et traitement des images.

Lancer : python manage.py test
"""

import shutil
import tempfile
from io import BytesIO

from django.contrib.auth.models import User
from django.core import mail
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

from .models import Competence, CategorieCompetence, MessageContact, Profil, Projet, VisiteJour

MEDIA_TEMP = tempfile.mkdtemp()


def image_png(largeur=3000, hauteur=2000, mode="RGB"):
    tampon = BytesIO()
    Image.new(mode, (largeur, hauteur), "purple").save(tampon, "PNG")
    return SimpleUploadedFile("photo.png", tampon.getvalue(), content_type="image/png")


def creer_profil(**kwargs):
    donnees = {
        "nom": "Mahamat Hassan Oumar", "titre": "Data Science", "description_courte": "Bonjour",
        "localisation": "Ouagadougou, Burkina Faso", "email": "contact@example.com", "langues": "Français",
    }
    donnees.update(kwargs)
    return Profil.objects.create(**donnees)


class BaseTest(TestCase):
    def setUp(self):
        cache.clear()


# ─────────────────────────────────────────────
# Pages publiques
# ─────────────────────────────────────────────
class PagePubliqueTests(BaseTest):
    def test_accueil_sans_contenu(self):
        r = self.client.get("/")
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Mahamat Hassan Oumar")

    def test_accueil_avec_profil(self):
        creer_profil(github="https://github.com/exemple")
        r = self.client.get("/")
        self.assertContains(r, 'rel="canonical"')
        self.assertContains(r, "application/ld+json")
        self.assertContains(r, "contact@<wbr>example.com")
        self.assertContains(r, 'rel="noopener noreferrer"')

    def test_head_autorise(self):
        """Les robots et outils de surveillance utilisent HEAD."""
        self.assertEqual(self.client.head("/").status_code, 200)

    def test_json_ld_ne_peut_pas_fermer_le_script(self):
        creer_profil(titre="</script><script>alert(1)</script>")
        r = self.client.get("/")
        self.assertNotContains(r, "</script><script>alert(1)")

    def test_robots_sitemap_favicon(self):
        r = self.client.get("/robots.txt")
        self.assertContains(r, "Disallow: /dashboard/")
        self.assertContains(r, "Sitemap:")
        self.assertContains(self.client.get("/sitemap.xml"), "<urlset")
        self.assertEqual(self.client.get("/favicon.ico").status_code, 301)

    @override_settings(DEBUG=False)
    def test_page_404_personnalisee(self):
        r = self.client.get("/page-qui-nexiste-pas/")
        self.assertEqual(r.status_code, 404)
        self.assertContains(r, "Cette page n'existe pas", status_code=404)

    def test_entetes_de_securite(self):
        r = self.client.get("/")
        self.assertIn("default-src 'self'", r["Content-Security-Policy"])
        self.assertIn("frame-ancestors 'none'", r["Content-Security-Policy"])
        self.assertIn("camera=()", r["Permissions-Policy"])
        self.assertEqual(r["X-Frame-Options"], "DENY")
        self.assertEqual(r["X-Content-Type-Options"], "nosniff")

    def test_visite_comptee_une_fois_par_jour(self):
        self.client.get("/", HTTP_USER_AGENT="Mozilla/5.0 (iPhone)")
        self.client.get("/", HTTP_USER_AGENT="Mozilla/5.0 (iPhone)")
        jour = VisiteJour.objects.get()
        self.assertEqual(jour.vues, 1)
        self.assertEqual(jour.vues_mobile, 1)

    def test_robots_non_comptes(self):
        self.client.get("/", HTTP_USER_AGENT="Googlebot/2.1")
        self.assertFalse(VisiteJour.objects.exists())

    def test_pas_de_session_creee_pour_un_visiteur(self):
        r = self.client.get("/", HTTP_USER_AGENT="Mozilla/5.0")
        self.assertNotIn("sessionid", r.cookies)

    def test_technologies_sans_entree_vide(self):
        projet = Projet(titre="X", description="Y", technologies="Python, , Django,")
        self.assertEqual(projet.get_technologies_list(), ["Python", "Django"])

    def test_telechargement_cv(self):
        r = self.client.get(reverse("telecharger_cv"))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r["Content-Type"], "application/pdf")
        self.assertIn("attachment", r["Content-Disposition"])


# ─────────────────────────────────────────────
# Formulaire de contact
# ─────────────────────────────────────────────
@override_settings(CONTACT_EMAIL="moi@example.com",
                   EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class ContactTests(BaseTest):
    url = "/contact/"
    valide = {"name": "Awa", "email": "awa@example.com", "subject": "Stage", "message": "Bonjour, je vous écris pour un stage."}

    def test_message_valide(self):
        r = self.client.post(self.url, self.valide)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["status"], "success")
        self.assertEqual(MessageContact.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].reply_to, ["awa@example.com"])

    def test_get_refuse(self):
        self.assertEqual(self.client.get(self.url).status_code, 405)

    def test_champs_obligatoires(self):
        r = self.client.post(self.url, {"name": "", "email": "", "message": ""})
        self.assertEqual(r.status_code, 400)
        self.assertFalse(MessageContact.objects.exists())

    def test_email_invalide(self):
        r = self.client.post(self.url, {**self.valide, "email": "pas-un-email"})
        self.assertEqual(r.status_code, 400)

    def test_injection_entete_email(self):
        """Un retour à la ligne dans le nom ne doit pas casser l'email."""
        r = self.client.post(self.url, {**self.valide, "name": "Awa\nBcc: pirate@example.com"})
        self.assertEqual(r.status_code, 200)
        self.assertNotIn("\n", mail.outbox[0].subject)

    def test_piege_a_robots(self):
        r = self.client.post(self.url, {**self.valide, "website": "http://spam.example"})
        self.assertEqual(r.json()["status"], "success")
        self.assertFalse(MessageContact.objects.exists())
        self.assertEqual(len(mail.outbox), 0)

    def test_limite_de_messages(self):
        for _ in range(5):
            self.assertEqual(self.client.post(self.url, self.valide).status_code, 200)
        self.assertEqual(self.client.post(self.url, self.valide).status_code, 429)
        self.assertEqual(MessageContact.objects.count(), 5)

    @override_settings(EMAIL_BACKEND="portfolio.tests.BackendEnPanne")
    def test_panne_smtp_le_message_reste_enregistre(self):
        r = self.client.post(self.url, self.valide)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(MessageContact.objects.count(), 1)

    @override_settings(USE_X_FORWARDED_FOR=False)
    def test_x_forwarded_for_ignore_sans_proxy(self):
        """Sans proxy de confiance, changer X-Forwarded-For ne contourne pas la limite."""
        for i in range(5):
            self.client.post(self.url, self.valide, HTTP_X_FORWARDED_FOR=f"10.0.0.{i}")
        r = self.client.post(self.url, self.valide, HTTP_X_FORWARDED_FOR="10.0.0.99")
        self.assertEqual(r.status_code, 429)

    def test_csrf_obligatoire(self):
        from django.test import Client
        client = Client(enforce_csrf_checks=True)
        self.assertEqual(client.post(self.url, self.valide).status_code, 403)


class BackendEnPanne:
    def __init__(self, *args, **kwargs):
        pass

    def send_messages(self, messages):
        raise ConnectionError("SMTP indisponible")


# ─────────────────────────────────────────────
# Tableau de bord
# ─────────────────────────────────────────────
class DashboardTests(BaseTest):
    def setUp(self):
        super().setUp()
        self.admin = User.objects.create_user("admin", password="motdepasse-solide-123", is_staff=True)
        self.visiteur = User.objects.create_user("visiteur", password="motdepasse-solide-123")

    def test_acces_refuse_sans_connexion(self):
        r = self.client.get("/dashboard/")
        self.assertRedirects(r, "/dashboard/connexion/?next=/dashboard/")

    def test_compte_non_staff_refuse(self):
        r = self.client.post("/dashboard/connexion/", {"username": "visiteur", "password": "motdepasse-solide-123"})
        self.assertContains(r, "pas accès au tableau de bord")

    def test_connexion_staff(self):
        r = self.client.post("/dashboard/connexion/", {"username": "admin", "password": "motdepasse-solide-123"})
        self.assertRedirects(r, "/dashboard/")

    def test_blocage_apres_trop_d_echecs(self):
        for _ in range(8):
            self.client.post("/dashboard/connexion/", {"username": "admin", "password": "faux"})
        r = self.client.post("/dashboard/connexion/", {"username": "admin", "password": "motdepasse-solide-123"})
        self.assertEqual(r.status_code, 429)
        self.assertContains(r, "Trop de tentatives", status_code=429)

    def test_redirection_externe_interdite(self):
        r = self.client.post("/dashboard/connexion/?next=https://pirate.example",
                             {"username": "admin", "password": "motdepasse-solide-123",
                              "next": "https://pirate.example"})
        self.assertRedirects(r, "/dashboard/")

    def test_admin_utilise_la_connexion_du_dashboard(self):
        r = self.client.get("/admin/login/")
        self.assertEqual(r.status_code, 302)
        self.assertIn("/dashboard/connexion/", r["Location"])

    def test_pages_du_dashboard(self):
        self.client.force_login(self.admin)
        creer_profil()
        for url in ["/dashboard/", "/dashboard/profil/", "/dashboard/messages/",
                    "/dashboard/projets/", "/dashboard/competences/", "/dashboard/projets/nouveau/"]:
            self.assertEqual(self.client.get(url).status_code, 200, url)
        self.assertEqual(self.client.get("/dashboard/inconnue/").status_code, 404)

    def test_suppression_en_post_uniquement(self):
        self.client.force_login(self.admin)
        projet = Projet.objects.create(titre="P", description="D", technologies="Python")
        self.assertEqual(self.client.get(f"/dashboard/projets/{projet.pk}/supprimer/").status_code, 405)
        self.client.post(f"/dashboard/projets/{projet.pk}/supprimer/")
        self.assertFalse(Projet.objects.exists())

    def test_niveau_de_competence_plafonne(self):
        self.client.force_login(self.admin)
        cat = CategorieCompetence.objects.create(nom="ML")
        self.client.post("/dashboard/competences/nouveau/",
                         {"categorie": cat.pk, "nom": "Python", "pourcentage": 150, "ordre": 0})
        self.assertFalse(Competence.objects.exists())


# ─────────────────────────────────────────────
# Images et fichiers envoyés
# ─────────────────────────────────────────────
@override_settings(MEDIA_ROOT=MEDIA_TEMP)
class FichiersTests(BaseTest):
    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(MEDIA_TEMP, ignore_errors=True)
        super().tearDownClass()

    def test_photo_redimensionnee_et_convertie(self):
        profil = creer_profil(photo=image_png(3000, 2000))
        with Image.open(profil.photo.path) as im:
            self.assertLessEqual(max(im.size), 900)
            self.assertEqual(im.format, "JPEG")

    def test_image_transparente_garde_la_transparence(self):
        projet = Projet.objects.create(titre="P", description="D", technologies="Python",
                                       image=image_png(2400, 1200, mode="RGBA"))
        with Image.open(projet.image.path) as im:
            self.assertEqual(im.format, "WEBP")
            self.assertLessEqual(max(im.size), 1600)

    def test_cv_doit_etre_un_vrai_pdf(self):
        admin = User.objects.create_user("admin", password="x", is_staff=True)
        self.client.force_login(admin)
        creer_profil()
        faux = SimpleUploadedFile("cv.pdf", b"<html><script>alert(1)</script></html>", content_type="application/pdf")
        r = self.client.post("/dashboard/profil/", {
            "nom": "M", "titre": "T", "description_courte": "D", "localisation": "L",
            "email": "a@example.com", "langues": "FR", "cv": faux,
        })
        self.assertContains(r, "pas un PDF valide")
        self.assertFalse(Profil.objects.get().cv)
