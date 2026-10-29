# Syllabus Calendar

A calendar web app built with Django. Create, Edit, and View Events on the web application.
This calendar specifically has an AI tool to pull events from a syllabus PDF or DOCX file (classes, tests, etc.),
let the user edit the events on a separate review page, and then post it on their own calendar.

---

## Python Requirement

You need **Python 3.10 or newer** to run this web application.

## Running the program

Open a terminal in the project folder (the one with `manage.py`) or change directory in a new PowerShell/Command Prompt Window.

**1. Create a virtual environment** (a private folder of packages for this project)

```
python -m venv venv
```

**2. Turn on virtual environment**

- Windows: `venv\Scripts\activate`
- macOS / Linux: `source venv/bin/activate`

`(venv)` should show up in front of the terminal line.

**3. Install the packages**

```
pip install -r requirements.txt
```

**4. Add a Gemini API key** (needed for the syllabus feature to work)

1. Get a free key from **Google AI Studio**: sign in with a Google account
   and choose "Get API key". Copy the key that is made.
2. In the project folder, make a copy of `.env.example` and name the copy `.env`.
3. Open `.env` and paste your key after `GEMINI_API_KEY=`, with no spaces or quotes:
   ```
   GEMINI_API_KEY=your-key-here
   ```
This step is here to ensure any information submitted by users running this on their local machines are pinned
to their specific API key. Please contact joel.shin@westpoint.edu if assistance is needed.

**5. Create the database**

```
python manage.py migrate
```

**6. Create an admin user** (follow the prompts)

```
python manage.py createsuperuser
```

**7. Start the server**

```
python manage.py runserver
```

Open **http://127.0.0.1:8000/** in your browser. Press `Ctrl+C` in the
terminal to stop the server.

For every time running the server after completing these steps, you will only need steps 2 (activate) and 7 (runserver).

---

## Instructions for the instructor

1. If you have not already, unzip the project and follow steps 1–7 above. For step 4, use your own
   free Gemini key. No key is included with the project, on purpose.
2. Run the automated tests (no key or internet needed; they use a fake AI):
   ```
   python manage.py test
   ```
   Expected result: `Ran 44 tests ... OK`
3. To try the syllabus import: log in, click **Import syllabus**, upload any
   course syllabus (.pdf or .docx), and enter the first day of classes for that course.

---

## Using the app

| Page | Address | What it does |
|---|---|---|
| Calendar | `/` | This month's events. Arrows change month. |
| Add event | `/events/add/` | Or click any date number on the calendar. |
| Edit / delete | click an event | Opens the edit form with a Delete button. |
| Import syllabus | `/syllabus/` | Upload a syllabus and let the AI find events. |
| Sign up | `/accounts/signup/` | Create a regular account. |
| Admin | `/admin/` | Admin users only: manage all users and events. |

Each user only sees their own events.

To change the time zone events are shown in, edit `TIME_ZONE` in
`config/settings.py`.

### Importing a syllabus

1. Click **Import syllabus** and choose a `.pdf` or `.docx` file (up to 10 MB).
2. Enter the **first day of classes** for the course. This gives an anchoring point for 
   parsing the course schedule.
3. Click **Read syllabus**. The AI should run and create the events.
4. On the review page, check each event against the actual syllabus. You can
   change date, time, name, or category. You can untick events not intended to be added.
5. Click **Add ticked events to calendar**.


### Changing the AI model

The default model is `gemini-3.5-flash-lite`. To use a different Gemini
model, add a line like this to `.env` and restart the server:

```
SYLLABUS_AI_MODEL=gemini-3.8-flash
```


---

## Project File Organization

```
manage.py              Command-line tool: runserver, migrate, test, etc.
make_submission.py     Makes a clean zip without your key or database
requirements.txt       Packages to install
.env.example           Template for your .env file (no real key in it)

config/                Project-wide setup
  settings.py          Installed apps, database, login, time zone, AI model
  urls.py              Top-level addresses: /admin/, /accounts/, /syllabus/, calendar

accounts/              User accounts
  urls.py              Sign-up page and Django's built-in login/logout
  views.py             The sign-up view

events/                The calendar
  models.py            The Event table (title, start, end, category, source, ...)
  forms.py             The add/edit form, with an end-after-start check
  views.py             Month view, add, edit, delete
  urls.py              Addresses for those views
  admin.py             How events appear on the admin site
  tests.py             Automated tests for the calendar
  migrations/          Instructions Django uses to build the database table

syllabus/              The syllabus import tool
  extract.py           Reads the text out of a .pdf or .docx file
  ai.py                Sends that text to Gemini and checks its answer
                       (the only file that talks to the AI)
  forms.py             The upload form and the review checklist
  views.py             The upload page and the review/import page
  urls.py              Addresses for those pages
  tests.py             Automated tests, using a fake AI (intended outcome)
  management/commands/
    try_syllabus.py    The try_syllabus terminal command

templates/             HTML pages
  base.html            Shared layout: top bar, messages
  registration/        Login page
  accounts/            Sign-up page
  events/              Calendar, event form, delete confirmation
  syllabus/            Upload page and review page
  partials/            Reusable form layout

static/css/style.css   All the styling
```

