"""URLs for the syllabus tool (everything under /syllabus/)."""

from django.urls import path

from . import views

urlpatterns = [
    path("", views.upload_syllabus, name="syllabus_upload"),
    path("review/", views.review_events, name="syllabus_review"),
]
