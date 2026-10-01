"""WSGI entry point for deployment servers."""

import os

from django.core.wsgi import get_wsgi_application


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "syllabus_calendar.settings")

application = get_wsgi_application()
