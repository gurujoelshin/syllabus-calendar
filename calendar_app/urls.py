from django.urls import path

from . import views

urlpatterns = [
    path("", views.calendar_home, name="calendar_home"),
    ]
