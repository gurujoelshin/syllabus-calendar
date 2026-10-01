# Syllabus calendar
A calendar app that takes a syllabus for a class and automatically makes events that upload to the calendar. The calendar holds features such as the ability to make tasks for an event (which can appear as separate events and appear on a separate to-do list).

## Setup

From this folder, create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Run the built-in project checks:

```powershell
python manage.py check
```

Start the development server:

```powershell
python manage.py runserver
```

The project has only Django's default admin URL at
<http://127.0.0.1:8000/admin/>. There is no custom calendar page yet.

## Starting files

- `manage.py` is the command-line entry point for Django commands.
- `syllabus_calendar/settings.py` contains project configuration, including the
  installed built-in Django apps and SQLite database setting.
- `syllabus_calendar/urls.py` contains the project's URL table. It currently
  exposes only Django's default admin route.
- `syllabus_calendar/asgi.py` and `syllabus_calendar/wsgi.py` are entry points
  used by different kinds of web servers later.
- `requirements.txt` records the Django dependency.
- `.gitignore` keeps local Python caches, virtual environments, and databases
  out of version control.

