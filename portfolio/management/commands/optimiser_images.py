"""
Optimise les images déjà envoyées (photo de profil, images des projets) :
redressement, redimensionnement, suppression des métadonnées EXIF.

Utilisation :
    python manage.py optimiser_images            # affiche ce qui serait fait
    python manage.py optimiser_images --appliquer
"""

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management.base import BaseCommand

from portfolio.images import TAILLE_PHOTO, TAILLE_PROJET
from portfolio.models import Profil, Projet


class Command(BaseCommand):
    help = "Redimensionne et allège les images déjà enregistrées."

    def add_arguments(self, parser):
        parser.add_argument("--appliquer", action="store_true", help="Enregistrer les changements.")

    def handle(self, *args, appliquer=False, **options):
        cibles = [(p, "photo", TAILLE_PHOTO) for p in Profil.objects.exclude(photo="")]
        cibles += [(p, "image", TAILLE_PROJET) for p in Projet.objects.exclude(image="")]
        if not cibles:
            self.stdout.write("Aucune image à traiter.")
            return

        for objet, champ, taille in cibles:
            fichier = getattr(objet, champ)
            try:
                avant = fichier.size
                fichier.open("rb")
                contenu = fichier.read()
                fichier.close()
            except FileNotFoundError:
                self.stdout.write(self.style.WARNING(f"Introuvable : {fichier.name}"))
                continue

            if not appliquer:
                self.stdout.write(f"{fichier.name} — {avant / 1024:.0f} Ko (max {taille} px)")
                continue

            ancien = fichier.name
            nom = ancien.rsplit("/", 1)[-1]
            setattr(objet, champ, SimpleUploadedFile(nom, contenu))
            objet.save()  # save() du modèle appelle optimiser_image
            nouveau = getattr(objet, champ)
            if nouveau.name != ancien:
                fichier.storage.delete(ancien)
            self.stdout.write(self.style.SUCCESS(
                f"{ancien} → {nouveau.name} : {avant / 1024:.0f} Ko → {nouveau.size / 1024:.0f} Ko"
            ))

        if not appliquer:
            self.stdout.write("Relancer avec --appliquer pour optimiser ces images.")
