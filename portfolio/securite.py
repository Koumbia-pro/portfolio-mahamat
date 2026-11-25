"""
Outils de sécurité : adresse IP du visiteur et limitation des tentatives.
"""

from django.conf import settings
from django.core.cache import cache


def adresse_ip(request):
    """
    Adresse IP du visiteur.

    Derrière un proxy de confiance (USE_X_FORWARDED_FOR=True, ex. Railway),
    la vraie adresse est ajoutée à la FIN de X-Forwarded-For : on prend la
    dernière valeur (les premières peuvent être inventées par le visiteur).
    Sinon (o2switch), on ignore cet en-tête, que n'importe qui peut falsifier.
    """
    if settings.USE_X_FORWARDED_FOR:
        transmis = request.META.get("HTTP_X_FORWARDED_FOR", "")
        if transmis:
            return transmis.split(",")[-1].strip()
    return request.META.get("REMOTE_ADDR", "")


class Limiteur:
    """
    Compte des événements par clé sur une fenêtre de temps.
    Ex. : 5 messages par heure et par adresse IP.
    """

    def __init__(self, nom, maximum, fenetre_secondes):
        self.nom = nom
        self.maximum = maximum
        self.fenetre = fenetre_secondes

    def _cle(self, cle):
        return f"limite:{self.nom}:{cle}"

    def depasse(self, cle):
        return cache.get(self._cle(cle), 0) >= self.maximum

    def enregistrer(self, cle):
        k = self._cle(cle)
        if not cache.add(k, 1, self.fenetre):
            try:
                cache.incr(k)
            except ValueError:  # la clé vient d'expirer
                cache.set(k, 1, self.fenetre)

    def reinitialiser(self, cle):
        cache.delete(self._cle(cle))


# 5 messages de contact par heure et par IP
limite_contact = Limiteur("contact", 5, 3600)
# 8 échecs de connexion par IP, 15 par identifiant, sur 15 minutes
limite_connexion_ip = Limiteur("login-ip", 8, 900)
limite_connexion_user = Limiteur("login-user", 15, 900)
