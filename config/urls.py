"""
Project URL config file
"""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("syllabus/", include("syllabus.urls")),
    path("", include("events.urls")),
]
