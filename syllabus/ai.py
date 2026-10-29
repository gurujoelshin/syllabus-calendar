"""
Ask the Gemini AI to find dated events in a syllabus.

This is the ONLY file that talks to the AI. The rest of the app just
calls find_events(). To switch to a different AI provider later, you
would rewrite this file and leave everything else alone.
"""

import os
from datetime import date, time
from typing import Literal, Optional

from django.conf import settings
from google import genai
from google.genai import errors
from pydantic import BaseModel, Field, ValidationError

# Very long files are cut off at this many characters, to stay well
# inside the free tier's limits. A typical syllabus is far shorter.
MAX_CHARACTERS = 60_000


# --- The shape of the answer we want -------------------------------------
#
# These Pydantic classes describe the exact JSON we want back. We send
# this description to Gemini, and Gemini is required to answer in this
# shape. The Field descriptions are instructions the AI reads too.

class FoundEvent(BaseModel):
    title: str = Field(description="Short name, e.g. 'Midterm Exam' or 'Homework 3 due'.")
    date: str = Field(description="The date in YYYY-MM-DD format.")
    start_time: Optional[str] = Field(
        description="Start or due time in 24-hour HH:MM format, or null if no time is given."
    )
    end_time: Optional[str] = Field(
        description="End time in 24-hour HH:MM format, or null if no end time is given."
    )
    category: Literal["class", "assignment", "exam", "reading", "other"]
    details: str = Field(
        description="One short sentence of useful detail from the syllabus, or an empty string."
    )


class FoundEvents(BaseModel):
    events: list[FoundEvent]


class AIError(Exception):
    """Raised when the AI step fails. The message can be shown to the user."""


# --- The main function -----------------------------------------------------

def find_events(syllabus_text, semester_start):
    """Send the syllabus text to Gemini and return a list of event dictionaries.

    syllabus_text  - the text from extract.extract_text()
    semester_start - a date object: the first day of classes

    Each event in the returned list looks like:
      {"title": "Midterm Exam", "date": "2026-10-14", "start_time": "13:00",
       "end_time": None, "category": "exam", "details": "Covers chapters 1-6."}
    Dates and times are plain strings so the list can be stored in the
    user's session between the upload page and the review page.
    """
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise AIError(
            "No Gemini API key was found. Add GEMINI_API_KEY to the .env file "
            "in the project folder, then restart the server."
        )

    # Everything that could fail because of OUR code happens here, before
    # the try block below, so a typo shows a real error instead of being
    # mistaken for a network problem.
    model = settings.SYLLABUS_AI_MODEL
    prompt = build_prompt(syllabus_text, semester_start)
    client = genai.Client(api_key=api_key)

    try:
        response = client.models.generate_content(
            model=model,
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_json_schema": FoundEvents.model_json_schema(),
                "temperature": 0,  # 0 = most consistent answers
            },
        )
    except errors.APIError as error:
        raise AIError(friendly_api_message(error))
    except Exception:
        # Anything else is almost always a network problem.
        raise AIError("Couldn't reach Gemini. Check your internet connection and try again.")

    try:
        result = FoundEvents.model_validate_json(response.text or "")
    except ValidationError:
        raise AIError("Gemini's answer wasn't in the expected format. Please try again.")

    return clean_events(result.events)


# --- Helper functions ------------------------------------------------------

def build_prompt(syllabus_text, semester_start):
    """Write the instructions we send to Gemini, followed by the syllabus."""
    if len(syllabus_text) > MAX_CHARACTERS:
        syllabus_text = syllabus_text[:MAX_CHARACTERS]

    return f"""You are reading a college course syllabus. List every item that
happens on a specific date: exams, quizzes, assignment and project due dates,
readings due, presentations, labs, holidays, and breaks.

Rules:
- The semester starts on {semester_start:%A, %B %d, %Y}. When a date has no
  year, use the year that places it within about five months after that start.
- Only include items whose date is stated or can be worked out exactly.
  If an item only says something like "Week 5" and the syllabus gives no way
  to find the exact date, leave it out.
- Do not list regular weekly class meetings (like "Lectures MWF 10:00").
  Do list one-time sessions, such as an exam review on a specific date.
- A due date with no time: start_time is null. Use 24-hour time.
- Use category "exam" for exams and quizzes, "assignment" for anything
  submitted, "reading" for readings, "class" for special class sessions,
  and "other" for holidays, breaks, and anything else.
- Do not invent anything that is not in the syllabus.

SYLLABUS:
{syllabus_text}
"""


def clean_events(found_events):
    """Turn the AI's events into dictionaries, dropping any with bad dates.

    Even with a required format, an AI can produce a date like
    "2026-02-30". Checking each one here keeps bad data off the calendar.
    """
    cleaned = []
    for event in found_events:
        try:
            date.fromisoformat(event.date)
        except ValueError:
            continue  # skip events whose date isn't a real date

        title = event.title.strip()
        if not title:
            continue

        cleaned.append({
            "title": title[:200],  # the Event model allows 200 characters
            "date": event.date,
            "start_time": valid_time_or_none(event.start_time),
            "end_time": valid_time_or_none(event.end_time),
            "category": event.category.lower(),
            "details": event.details.strip(),
        })

    cleaned.sort(key=lambda item: (item["date"], item["start_time"] or ""))
    return cleaned


def valid_time_or_none(text):
    """Return text if it's a real HH:MM time, otherwise None."""
    if not text:
        return None
    try:
        return time.fromisoformat(text).strftime("%H:%M")
    except ValueError:
        return None


def friendly_api_message(error):
    """Explain an error from Gemini in plain words."""
    if error.code == 429:
        return ("The free Gemini limit has been reached for now. "
                "Wait a minute (or until tomorrow) and try again.")
    if error.code in (400, 401, 403):
        return ("Gemini rejected the request. Check that GEMINI_API_KEY in your "
                ".env file is correct, and that SYLLABUS_AI_MODEL is a valid model name.")
    if error.code == 404:
        return "Gemini couldn't find that model. Check SYLLABUS_AI_MODEL in your .env file."
    return f"Gemini had a problem (error {error.code}). Please try again in a moment."
