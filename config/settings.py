"""
Django settings file: Apps installed, templates and static file locations, 
database to use, login behavior (URL)
"""

import os
from pathlib import Path

# BASE_DIR - Django finds absolute physical path to build off from when running web app/assets
BASE_DIR = Path(__file__).resolve().parent.parent

# Load secret settings (like the AI API key) from a .env file, if it exists.
from dotenv import load_dotenv
load_dotenv(BASE_DIR / ".env")


# Security for login sessions

SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "django-insecure-local-dev-key-change-me-if-you-ever-deploy-this",
)

# DEBUG = True shows detailed error pages, which helps while learning.
DEBUG = True

# Local Hosting
ALLOWED_HOSTS = ["127.0.0.1", "localhost"]


# Apps

INSTALLED_APPS = [
    # Built-in Django apps
    "django.contrib.admin",         # the /admin/ site
    "django.contrib.auth",          # users, passwords, login
    "django.contrib.contenttypes",
    "django.contrib.sessions",      # remembers who is logged in
    "django.contrib.messages",      # "Event saved!" style notices
    "django.contrib.staticfiles",   # CSS files
    # Our apps
    "accounts",                     # sign up / log in / log out
    "events",                       # the calendar and its events
    "syllabus",                     # the syllabus upload + AI tool
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
] # security measures for web requests to run through

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # Project-wide templates (base.html, login page) live in /templates
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# Database via SQLite

# Where SQLite stores database: primarily "db.sqlite3"
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# Password

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# Login/Logout

LOGIN_URL = "login"                 # where to send people who aren't logged in
LOGIN_REDIRECT_URL = "calendar"     # where to go after logging in
LOGOUT_REDIRECT_URL = "login"       # where to go after logging out

# Default Time zone, lang, internationalization

# Time zone, Language

LANGUAGE_CODE = "en-us"

# Default time Zone for Events: NY

TIME_ZONE = "America/New_York"

USE_I18N = True
USE_TZ = True                       # Adapt to different time zones


# Location of static Files (CSS)

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]


# --- Syllabus AI tool ---------------------------------------------------

# The API key is read from GEMINI_API_KEY in your .env file.
# This setting chooses which Gemini model reads the syllabus.
SYLLABUS_AI_MODEL = os.environ.get("SYLLABUS_AI_MODEL", "gemini-3.5-flash-lite")
