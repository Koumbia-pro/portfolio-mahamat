"""
En-têtes de sécurité supplémentaires.

La Content-Security-Policy limite ce que le navigateur accepte de charger :
même si un texte malveillant arrivait dans une page, aucun script externe
ou en ligne ne pourrait s'exécuter.
"""

from django.conf import settings

CSP = "; ".join([
    "default-src 'self'",
    "script-src 'self'",
    # Les styles en ligne servent aux variables CSS d'animation (style="--d:2")
    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdnjs.cloudflare.com",
    "font-src 'self' data: https://fonts.gstatic.com https://cdnjs.cloudflare.com",
    "img-src 'self' data: blob:",
    "connect-src 'self'",
    "object-src 'none'",
    "base-uri 'self'",
    "form-action 'self'",
    "frame-ancestors 'none'",
])

PERMISSIONS_POLICY = "camera=(), microphone=(), geolocation=(), payment=(), usb=(), interest-cohort=()"


class SecurityHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.admin_prefix = "/" + settings.ADMIN_URL

    def __call__(self, request):
        response = self.get_response(request)
        response.setdefault("Permissions-Policy", PERMISSIONS_POLICY)
        # L'admin Django gère ses propres scripts : on ne lui impose pas la CSP.
        if not request.path.startswith(self.admin_prefix):
            response.setdefault("Content-Security-Policy", CSP)
        return response
