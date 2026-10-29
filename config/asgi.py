"""
ASGI config file

"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings") # orient Django to proper configuration settings for project

application = get_asgi_application() # ASGI callable variable is exposed as "application"
