from django.shortcuts import render

# Create your views here.

from .models import CalendarEvent

def calendar_home(request):
    events = CalendarEvent.objects.order_by('date')

    return render (
        request,
        "calendar_app/calendar_home.html",
        {"events": events},
    )