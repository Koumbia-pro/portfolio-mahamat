"""
Point d'entrée pour l'hébergement o2switch (cPanel « Setup Python App » / Passenger).

Dans cPanel :
    Application startup file : passenger_wsgi.py
    Application Entry point  : application
"""

import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

from django.core.wsgi import get_wsgi_application  # noqa: E402

application = get_wsgi_application()
