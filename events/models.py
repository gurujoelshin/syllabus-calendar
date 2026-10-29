"""
Database models for the calendar.

A "model" is a Python class that Django turns into a database table.
Each attribute below becomes a column, and each Event object you save
becomes one row.
"""

from datetime import timedelta

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone


class Event(models.Model):
    # Categories help color-code the calendar. They will also be useful
    # later, when the syllabus tool sorts what it finds into exams,
    # assignments, and so on.
    CATEGORY_CHOICES = [
        ("class", "Class"),
        ("assignment", "Assignment"),
        ("exam", "Exam"),
        ("reading", "Reading"),
        ("other", "Other"),
    ]

    # Records whether a person typed the event in or the syllabus
    # tool created it (used in phase 2).
    SOURCE_CHOICES = [
        ("manual", "Added manually"),
        ("syllabus", "Imported from syllabus"),
    ]

    # Every event belongs to one user. If that user is deleted, their
    # events are deleted too (CASCADE).
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="events",
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start = models.DateTimeField()
    end = models.DateTimeField(null=True, blank=True)
    all_day = models.BooleanField(default=False)
    category = models.CharField(
        max_length=20, choices=CATEGORY_CHOICES, default="other"
    )
    source = models.CharField(
        max_length=20, choices=SOURCE_CHOICES, default="manual"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["start"]  # earliest events first

    def __str__(self):
        """How an event is shown in the admin site and in the shell."""
        return f"{self.title} ({self.start:%Y-%m-%d})"

    def get_absolute_url(self):
        """The page for editing this event."""
        return reverse("event_edit", args=[self.pk])

    def local_start(self):
        """Start time converted to the time zone in settings.py."""
        return timezone.localtime(self.start)

    def local_end(self):
        """End time in local time, or None if there is no end time."""
        if self.end is None:
            return None
        return timezone.localtime(self.end)

    def days_covered(self):
        """Return a list of every date this event touches.

        A one-day event returns one date. An event from Monday to
        Wednesday returns three dates, so it shows up on each day of
        the calendar.
        """
        first_day = self.local_start().date()
        last_day = first_day
        if self.end is not None:
            last_day = self.local_end().date()

        days = []
        current = first_day
        while current <= last_day:
            days.append(current)
            current = current + timedelta(days=1)
        return days
