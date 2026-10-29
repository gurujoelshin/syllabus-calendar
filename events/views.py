"""
Views for the calendar.

Each function handles one page:
  calendar_view  - the month grid
  event_add      - the "add event" form
  event_edit     - the "edit event" form
  event_delete   - the "are you sure?" page for deleting

@login_required at the top of each one sends visitors who aren't
logged in to the login page first.
"""

import calendar
from datetime import date, datetime, time, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import EventForm
from .models import Event


@login_required
def calendar_view(request, year=None, month=None):
    """Show one month as a grid of weeks, with each day's events."""
    today = timezone.localdate()

    # With no year/month in the URL, show the current month.
    if year is None or month is None:
        year = today.year
        month = today.month

    # Guard against addresses like /2026/13/ that aren't real months.
    if not (1 <= month <= 12 and 1 <= year <= 9999):
        raise Http404("That month doesn't exist.")

    # monthdatescalendar() returns a list of weeks; each week is a list
    # of 7 dates. Weeks include a few days from the months before and
    # after so that every row is full. firstweekday=6 starts on Sunday.
    month_calendar = calendar.Calendar(firstweekday=6)
    weeks_of_dates = month_calendar.monthdatescalendar(year, month)
    first_shown = weeks_of_dates[0][0]
    last_shown = weeks_of_dates[-1][-1]

    events_by_day = get_events_by_day(request.user, first_shown, last_shown)

    # Build a list of weeks, where each day is a small dictionary the
    # template can display.
    weeks = []
    for week in weeks_of_dates:
        days = []
        for day in week:
            days.append({
                "date": day,
                "in_month": day.month == month,
                "is_today": day == today,
                "events": events_by_day.get(day, []),
            })
        weeks.append(days)

    # Work out the previous and next month for the arrow buttons.
    if month == 1:
        prev_year, prev_month = year - 1, 12
    else:
        prev_year, prev_month = year, month - 1
    if month == 12:
        next_year, next_month = year + 1, 1
    else:
        next_year, next_month = year, month + 1

    # The next few events, for the list beside the calendar.
    upcoming = Event.objects.filter(
        owner=request.user, start__gte=timezone.now()
    )[:5]

    context = {
        "weeks": weeks,
        "month_name": calendar.month_name[month],
        "year": year,
        "month": month,
        "weekday_names": ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"],
        "prev_year": prev_year,
        "prev_month": prev_month,
        "next_year": next_year,
        "next_month": next_month,
        "upcoming": upcoming,
        "today": today,
    }
    return render(request, "events/calendar.html", context)


def get_events_by_day(user, first_day, last_day):
    """Return a dictionary of {date: [events on that date]}.

    Only events that touch the dates between first_day and last_day
    are loaded from the database.
    """
    range_start = timezone.make_aware(datetime.combine(first_day, time.min))
    range_end = timezone.make_aware(datetime.combine(last_day + timedelta(days=1), time.min))

    # An event is visible if it starts before the range ends AND either
    # it ends after the range starts, or it has no end and starts inside
    # the range. Q objects let us combine conditions with | (OR).
    events = Event.objects.filter(owner=user, start__lt=range_end).filter(
        Q(end__gte=range_start) | Q(end__isnull=True, start__gte=range_start)
    )

    events_by_day = {}
    for event in events:
        for day in event.days_covered():
            if first_day <= day <= last_day:
                events_by_day.setdefault(day, []).append(event)
    return events_by_day


@login_required
def event_add(request):
    """Show an empty event form and save a new event when it's submitted."""
    if request.method == "POST":
        form = EventForm(request.POST)
        if form.is_valid():
            # commit=False builds the event without saving it yet, so we
            # can attach the logged-in user as its owner first.
            event = form.save(commit=False)
            event.owner = request.user
            event.source = "manual"
            event.save()
            messages.success(request, f'Added "{event.title}".')
            return redirect_to_event_month(event)
    else:
        # Clicking a day on the calendar links here with ?date=YYYY-MM-DD,
        # so we pre-fill the start time with 9:00 AM on that day.
        initial = {}
        chosen_date = parse_date(request.GET.get("date"))
        if chosen_date is not None:
            initial["start"] = datetime.combine(chosen_date, time(9, 0))
        form = EventForm(initial=initial)

    return render(request, "events/event_form.html", {"form": form, "is_new": True})


@login_required
def event_edit(request, pk):
    """Show the form filled in with an existing event, and save changes."""
    # owner=request.user makes sure people can only edit their own events.
    event = get_object_or_404(Event, pk=pk, owner=request.user)

    if request.method == "POST":
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, f'Saved "{event.title}".')
            return redirect_to_event_month(event)
    else:
        form = EventForm(instance=event)

    return render(
        request,
        "events/event_form.html",
        {"form": form, "event": event, "is_new": False},
    )


@login_required
def event_delete(request, pk):
    """Ask for confirmation, then delete the event."""
    event = get_object_or_404(Event, pk=pk, owner=request.user)

    if request.method == "POST":
        title = event.title
        event.delete()
        messages.success(request, f'Deleted "{title}".')
        return redirect_to_event_month(event)

    return render(request, "events/event_confirm_delete.html", {"event": event})


# --- Small helper functions ------------------------------------------

def redirect_to_event_month(event):
    """Go back to the calendar month that contains the event."""
    start = event.local_start()
    return redirect("calendar_month", year=start.year, month=start.month)


def parse_date(text):
    """Turn 'YYYY-MM-DD' into a date, or return None if it isn't valid."""
    if not text:
        return None
    try:
        return date.fromisoformat(text)
    except ValueError:
        return None
