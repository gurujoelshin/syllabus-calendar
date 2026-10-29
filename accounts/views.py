"""
Views for user accounts
"""

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect, render


def signup(request):
    """
    Sign-up form for a user to create an account
    request: request object created by Django when browser is pinged for "/signup/" page
    """
    # Someone who is already logged in doesn't need to sign up.
    if request.user.is_authenticated:
        return redirect("calendar")

    if request.method == "POST":
        # The form was submitted: fill it with what the user typed.
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()        # creates the user in the database
            login(request, user)      # logs them in right away
            messages.success(request, f"Welcome, {user.username}!")
            return redirect("calendar")
    else:
        # First visit to the page: show an empty form.
        form = UserCreationForm()

    return render(request, "accounts/signup.html", {"form": form})
