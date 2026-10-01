"""Command-line helper for working with this Django project."""

import os
import sys


def main():
    """Run Django's command-line tools."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "syllabus_calendar.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
