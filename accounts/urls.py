"""
URLs for users using Django prebuilt URL authentication module + signup page
"""

from django.urls import include, path # pull Django urls from prebuilt module

from . import views # import views.py

urlpatterns = [
    path("signup/", views.signup, name="signup"), # map signup page
    path("", include("django.contrib.auth.urls")), # map authentication urls
]
