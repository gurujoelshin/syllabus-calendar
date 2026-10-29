"""
Try the syllabus reader from the terminal, before the web pages exist.

Usage (from the project folder):
    python manage.py try_syllabus path\\to\\syllabus.pdf 2026-08-17

The date is the first day of classes. Nothing is added to the calendar;
this only prints what the AI found.
"""

from datetime import date
from pathlib import Path

from django.core.files import File
from django.core.management.base import BaseCommand, CommandError

from syllabus.ai import AIError, find_events
from syllabus.extract import ExtractionError, extract_text


class Command(BaseCommand):
    help = "Read a syllabus file and print the events the AI finds."

    def add_arguments(self, parser):
        parser.add_argument("file", help="Path to a .pdf or .docx syllabus")
        parser.add_argument("semester_start", help="First day of classes, as YYYY-MM-DD")
        parser.add_argument(
            "--show-text", action="store_true",
            help="Also print the text that was read from the file",
        )

    def handle(self, *args, **options):
        path = Path(options["file"])
        if not path.exists():
            raise CommandError(f"File not found: {path}")

        try:
            semester_start = date.fromisoformat(options["semester_start"])
        except ValueError:
            raise CommandError("The semester start must look like 2026-08-17.")

        try:
            with path.open("rb") as handle:
                text = extract_text(File(handle, name=path.name))
        except ExtractionError as error:
            raise CommandError(str(error))

        if options["show_text"]:
            self.stdout.write(text)
            self.stdout.write("-" * 60)

        self.stdout.write(f"Read {len(text):,} characters. Asking Gemini...")

        try:
            events = find_events(text, semester_start)
        except AIError as error:
            raise CommandError(str(error))

        self.stdout.write(self.style.SUCCESS(f"Found {len(events)} event(s):"))
        for event in events:
            when = event["date"]
            if event["start_time"]:
                when += " " + event["start_time"]
            self.stdout.write(f"  {when:<17} [{event['category']:<10}] {event['title']}")
