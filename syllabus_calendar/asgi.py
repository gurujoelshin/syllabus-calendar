"""ASGI entry point for deployment servers."""

import os

from django.core.asgi import get_asgi_application


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "syllabus_calendar.settings")

application = get_asgi_application()
