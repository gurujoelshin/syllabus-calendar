"""
URLs for the calendar.

<int:year> captures a whole number from the address and passes it to
the view as an argument, e.g. /2026/10/ calls calendar_view(year=2026, month=10).
The name= values let templates and views refer to a page by name
instead of typing out its address.
"""

from django.urls import path

from . import views

urlpatterns = [
    path("", views.calendar_view, name="calendar"),
    path("<int:year>/<int:month>/", views.calendar_view, name="calendar_month"),
    path("events/add/", views.event_add, name="event_add"),
    path("events/<int:pk>/edit/", views.event_edit, name="event_edit"),
    path("events/<int:pk>/delete/", views.event_delete, name="event_delete"),
]
