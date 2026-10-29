"""
Views for the syllabus tool.

  upload_syllabus - the page with the file picker. It reads the file,
                    asks the AI for events, and saves the results in
                    the user's session.
  review_events   - shows what the AI found as an editable checklist,
                    and adds the ticked events to the calendar.

What's a session? Django gives each logged-in browser a small private
storage space on the server. We keep the AI's results there between
the upload page and the review page, so nothing is added to the
calendar until the user has looked at it.
"""

from datetime import date, datetime, time

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import redirect, render
from django.utils import timezone

from events.models import Event

from .ai import AIError, find_events
from .extract import ExtractionError, extract_text
from .forms import ImportEventFormSet, SyllabusUploadForm

# The name of the "drawer" in the session where results are stored.
SESSION_KEY = "syllabus_import"


@login_required
def upload_syllabus(request):
    """Show the upload form, then read the file and ask the AI."""
    if request.method == "POST":
        # Uploaded files arrive in request.FILES, not request.POST.
        form = SyllabusUploadForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded = form.cleaned_data["syllabus_file"]
            semester_start = form.cleaned_data["semester_start"]

            try:
                text = extract_text(uploaded)
                events = find_events(text, semester_start)
            except (ExtractionError, AIError) as error:
                # Both error types carry a message written for the user,
                # so we show it on the form instead of crashing.
                form.add_error(None, str(error))
            else:
                # Runs only if the try block raised no error.
                request.session[SESSION_KEY] = {
                    "filename": uploaded.name,
                    "semester_start": semester_start.isoformat(),
                    "events": events,
                }
                return redirect("syllabus_review")
    else:
        form = SyllabusUploadForm()

    return render(request, "syllabus/upload.html", {"form": form})


@login_required
def review_events(request):
    """Show the AI's events as an editable checklist and import the ticked ones."""
    results = request.session.get(SESSION_KEY)
    if results is None:
        messages.info(request, "Upload a syllabus first.")
        return redirect("syllabus_upload")

    if request.method == "POST":
        # "prefix" keeps each row's field names apart in the submitted
        # data: events-0-title, events-1-title, and so on.
        formset = ImportEventFormSet(request.POST, prefix="events")
        if formset.is_valid():
            chosen = [row for row in formset.cleaned_data if row.get("include")]
            if not chosen:
                messages.error(request, "Tick at least one event to add, or upload a different file.")
            else:
                added, skipped, first_date = import_events(request.user, chosen)

                del request.session[SESSION_KEY]  # this upload is finished
                report_import(request, results["filename"], added, skipped)
                return redirect("calendar_month", year=first_date.year, month=first_date.month)
    else:
        # First visit: fill each row with one of the AI's events. The
        # session stores dates and times as text, so convert them back.
        initial_rows = []
        for event in results["events"]:
            initial_rows.append({
                "include": True,
                "title": event["title"],
                "date": date.fromisoformat(event["date"]),
                "start_time": text_to_time(event["start_time"]),
                "end_time": text_to_time(event["end_time"]),
                "category": event["category"],
                "details": event["details"],
            })
        formset = ImportEventFormSet(initial=initial_rows, prefix="events")

    return render(request, "syllabus/review.html", {
        "filename": results["filename"],
        "formset": formset,
    })


# --- Helper functions ------------------------------------------------------

def import_events(user, rows):
    """Create an Event for each chosen row. Returns (added, skipped, first_date).

    Rows that exactly match an event already on the user's calendar
    (same title and start) are skipped, so importing the same syllabus
    twice doesn't create doubles.
    """
    added = 0
    skipped = 0

    # transaction.atomic() means "all or nothing": if anything fails
    # partway through, none of the events are saved.
    with transaction.atomic():
        for row in rows:
            start, end, all_day = row_to_datetimes(row)

            already_there = Event.objects.filter(
                owner=user, title=row["title"].strip(), start=start
            ).exists()
            if already_there:
                skipped += 1
                continue

            Event.objects.create(
                owner=user,
                title=row["title"].strip(),
                description=row["details"],
                start=start,
                end=end,
                all_day=all_day,
                category=row["category"],
                source="syllabus",
            )
            added += 1

    first_date = min(row["date"] for row in rows)
    return added, skipped, first_date


def row_to_datetimes(row):
    """Turn a row's date and times into (start, end, all_day).

    A row with no start time becomes an all-day event starting at
    midnight. make_aware() attaches the time zone from settings.py.
    """
    start_time = row["start_time"]
    end_time = row["end_time"]

    if start_time is None:
        start = timezone.make_aware(datetime.combine(row["date"], time(0, 0)))
        return start, None, True

    start = timezone.make_aware(datetime.combine(row["date"], start_time))
    end = None
    if end_time is not None:
        end = timezone.make_aware(datetime.combine(row["date"], end_time))
    return start, end, False


def report_import(request, filename, added, skipped):
    """Show a short message on the calendar about what was imported."""
    text = f"Added {added} event{'s' if added != 1 else ''} from {filename}."
    if skipped:
        text += f" Skipped {skipped} already on your calendar."
    messages.success(request, text)


def text_to_time(text):
    """Turn "13:00" into a time object, or None into None."""
    if text is None:
        return None
    return time.fromisoformat(text)
