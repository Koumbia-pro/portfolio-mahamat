"""
Traitement des fichiers envoyés depuis le dashboard ou l'admin.

- Les images sont redressées (photos de téléphone), redimensionnées et
  ré-encodées : une photo de 5 Mo devient ~150 Ko, le site charge plus vite.
- Les métadonnées EXIF (position GPS, modèle du téléphone…) sont supprimées.
"""

from io import BytesIO
from pathlib import Path

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from PIL import Image, ImageOps

TAILLE_PHOTO = 900       # px, plus grand côté
TAILLE_PROJET = 1600     # px, plus grand côté


def _deja_enregistre(fichier):
    """Un fichier déjà stocké a été validé lors de son envoi : on ne le relit pas."""
    return getattr(fichier, "_committed", False)


def valider_taille_fichier(fichier):
    if _deja_enregistre(fichier):
        return
    maximum = settings.MAX_UPLOAD_MB * 1024 * 1024
    if fichier.size and fichier.size > maximum:
        raise ValidationError(
            f"Fichier trop lourd ({fichier.size / 1024 / 1024:.1f} Mo). "
            f"Maximum : {settings.MAX_UPLOAD_MB} Mo."
        )


def valider_pdf(fichier):
    """Vérifier que le fichier est vraiment un PDF (pas seulement son extension)."""
    if _deja_enregistre(fichier):
        return
    position = fichier.tell() if hasattr(fichier, "tell") else 0
    try:
        fichier.seek(0)
        debut = fichier.read(5)
    finally:
        fichier.seek(position)
    if debut != b"%PDF-":
        raise ValidationError("Ce fichier n'est pas un PDF valide.")


def optimiser_image(champ, taille_max):
    """
    Remplacer le fichier d'un ImageField non encore enregistré par une
    version optimisée. Ne fait rien si l'image ne peut pas être lue.
    """
    if not champ or getattr(champ, "_committed", True):
        return
    try:
        champ.open()
        champ.seek(0)
        image = Image.open(champ)
        image = ImageOps.exif_transpose(image)
        image.thumbnail((taille_max, taille_max), Image.Resampling.LANCZOS)
    except Exception:  # image illisible : on garde le fichier d'origine
        return

    transparente = image.mode in ("RGBA", "LA") or (
        image.mode == "P" and "transparency" in image.info
    )
    tampon = BytesIO()
    if transparente:
        image.convert("RGBA").save(tampon, "WEBP", quality=85, method=6)
        extension = "webp"
    else:
        image.convert("RGB").save(tampon, "JPEG", quality=85, optimize=True, progressive=True)
        extension = "jpg"

    nom = f"{Path(champ.name).stem[:80]}.{extension}"
    champ.save(nom, ContentFile(tampon.getvalue()), save=False)
