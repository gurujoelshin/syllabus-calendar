"""
Automated tests for calendar app

Use python manage.py test with venv

"""

from datetime import datetime

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Event


def local_datetime(year, month, day, hour=9, minute=0):
    """Make a time-zone-aware datetime in the project's time zone."""
    return timezone.make_aware(datetime(year, month, day, hour, minute))


class CalendarTests(TestCase):
    def setUp(self):
        """Runs before every test: create two users and log in as one."""
        self.user = User.objects.create_user("alice", password="test-pass-123")
        self.other_user = User.objects.create_user("bob", password="test-pass-123")
        self.client.login(username="alice", password="test-pass-123")

    def test_calendar_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse("calendar"))
        self.assertRedirects(response, reverse("login") + "?next=/")

    def test_calendar_shows_own_events_only(self):
        Event.objects.create(owner=self.user, title="My exam", start=local_datetime(2026, 10, 15))
        Event.objects.create(owner=self.other_user, title="Bob's party", start=local_datetime(2026, 10, 15))

        response = self.client.get(reverse("calendar_month", args=[2026, 10]))

        self.assertContains(response, "My exam")
        self.assertNotContains(response, "Bob's party")

    def test_invalid_month_is_404(self):
        response = self.client.get("/2026/13/")
        self.assertEqual(response.status_code, 404)

    def test_add_event(self):
        response = self.client.post(reverse("event_add"), {
            "title": "Homework 1",
            "start": "2026-10-20T23:59",
            "category": "assignment",
            "description": "",
        })
        self.assertRedirects(response, reverse("calendar_month", args=[2026, 10]))

        event = Event.objects.get(title="Homework 1")
        self.assertEqual(event.owner, self.user)
        self.assertEqual(event.local_start().hour, 23)

    def test_end_before_start_is_rejected(self):
        response = self.client.post(reverse("event_add"), {
            "title": "Backwards",
            "start": "2026-10-20T10:00",
            "end": "2026-10-20T09:00",
            "category": "other",
        })
        self.assertEqual(response.status_code, 200)  # form shown again
        self.assertContains(response, "can&#x27;t be before")
        self.assertFalse(Event.objects.filter(title="Backwards").exists())

    def test_edit_event(self):
        event = Event.objects.create(owner=self.user, title="Old title", start=local_datetime(2026, 10, 5))
        self.client.post(reverse("event_edit", args=[event.pk]), {
            "title": "New title",
            "start": "2026-10-05T09:00",
            "category": "exam",
        })
        event.refresh_from_db()
        self.assertEqual(event.title, "New title")
        self.assertEqual(event.category, "exam")

    def test_delete_event(self):
        event = Event.objects.create(owner=self.user, title="Delete me", start=local_datetime(2026, 10, 5))
        self.client.post(reverse("event_delete", args=[event.pk]))
        self.assertFalse(Event.objects.filter(pk=event.pk).exists())

    def test_cannot_edit_someone_elses_event(self):
        event = Event.objects.create(owner=self.other_user, title="Bob's", start=local_datetime(2026, 10, 5))
        response = self.client.get(reverse("event_edit", args=[event.pk]))
        self.assertEqual(response.status_code, 404)

    def test_multi_day_event_covers_each_day(self):
        event = Event.objects.create(
            owner=self.user,
            title="Conference",
            start=local_datetime(2026, 10, 7),
            end=local_datetime(2026, 10, 9, 17),
        )
        self.assertEqual(len(event.days_covered()), 3)


class SignupTests(TestCase):
    def test_signup_creates_user_and_logs_in(self):
        response = self.client.post(reverse("signup"), {
            "username": "newstudent",
            "password1": "a-long-Unusual-pass-42",
            "password2": "a-long-Unusual-pass-42",
        })
        self.assertRedirects(response, reverse("calendar"))
        self.assertTrue(User.objects.filter(username="newstudent").exists())
