# Syllabus calendar

This is the empty starting point for learning Django by building a syllabus
calendar yourself. Nothing in the project knows about calendars yet: there are
no custom models, views, templates, forms, or admin registrations.

## Learning goals

At this stage, learn how to:

- create and activate a Python virtual environment;
- install Django from `requirements.txt`;
- understand the difference between a Django **project** and an **app**;
- read the settings, URL configuration, and `manage.py` entry point;
- run Django's built-in checks and development server.

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

## What the starting files do

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

## Suggested next learning steps

Add one small piece at a time and run `python manage.py check` after each
change:

1. Create a `calendar_app` with `python manage.py startapp calendar_app`.
2. Add one simple model and learn how `makemigrations` and `migrate` work.
3. Register that model in the admin so you can enter one record manually.
4. Write one view and URL, then return a plain response.
5. Replace the response with a template that lists your records.
6. Add PDF upload and parsing only after the manual data path is clear.
7. Add event editing, task generation, daily to-do lists, countdowns,
   reminders, and customization as separate milestones.

The goal is to understand each layer before adding the next one.
