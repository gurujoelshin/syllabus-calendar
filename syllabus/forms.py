"""
Forms for the syllabus tool.

SyllabusUploadForm - the file picker and "first day of classes" date.
ImportEventForm    - one row of the review table (one found event).
ImportEventFormSet - all the rows together, so they can be submitted
                     and checked as a single form.

These are plain Forms (not ModelForms) because their data doesn't go
straight into the database: the upload is read and thrown away, and the
review rows are checked first, then turned into Events by the view.
"""

from pathlib import Path

from django import forms

from events.models import Event

from .extract import ALLOWED_EXTENSIONS

# Syllabi are small. 10 MB leaves lots of room while stopping someone
# from uploading, say, a whole textbook.
MAX_UPLOAD_MB = 10


class SyllabusUploadForm(forms.Form):
    syllabus_file = forms.FileField(
        label="Syllabus file",
        help_text="A .pdf or .docx file, up to 10 MB.",
        # accept= makes the browser's file picker show only these types.
        widget=forms.ClearableFileInput(attrs={"accept": ".pdf,.docx"}),
    )
    semester_start = forms.DateField(
        label="First day of classes",
        help_text="Used to work out the year when the syllabus leaves it out.",
        widget=forms.DateInput(attrs={"type": "date"}),
    )

    def clean_syllabus_file(self):
        """Check the file's type and size before we try to read it.

        Django calls any method named clean_<fieldname> automatically
        when the form is validated.
        """
        uploaded = self.cleaned_data["syllabus_file"]

        extension = Path(uploaded.name).suffix.lower()
        if extension not in ALLOWED_EXTENSIONS:
            raise forms.ValidationError("Please choose a .pdf or .docx file.")

        if uploaded.size > MAX_UPLOAD_MB * 1024 * 1024:
            raise forms.ValidationError(f"That file is larger than {MAX_UPLOAD_MB} MB.")

        return uploaded


class ImportEventForm(forms.Form):
    """One row on the review page: a single event the AI found.

    Every field starts filled in with the AI's answer, and the user can
    change any of them before importing.
    """

    include = forms.BooleanField(required=False, initial=True, label="Add")
    # title and date are "required=False" here on purpose: an unticked
    # row shouldn't block the import just because it's blank. clean()
    # below requires them only for ticked rows.
    title = forms.CharField(max_length=200, required=False)
    date = forms.DateField(
        required=False, widget=forms.DateInput(attrs={"type": "date"})
    )
    start_time = forms.TimeField(
        required=False, widget=forms.TimeInput(attrs={"type": "time"}, format="%H:%M")
    )
    end_time = forms.TimeField(
        required=False, widget=forms.TimeInput(attrs={"type": "time"}, format="%H:%M")
    )
    # Reuse the calendar's own category list so the two always match.
    category = forms.ChoiceField(choices=Event.CATEGORY_CHOICES)
    # Kept but not shown as a box: it becomes the event's description.
    details = forms.CharField(required=False, widget=forms.HiddenInput)

    def clean(self):
        cleaned_data = super().clean()

        if not cleaned_data.get("include"):
            return cleaned_data  # unticked rows are skipped, so don't check them

        if not cleaned_data.get("title", "").strip():
            self.add_error("title", "Give this event a name, or untick it.")
        if not cleaned_data.get("date") and "date" not in self.errors:
            self.add_error("date", "Pick a date, or untick this event.")

        start = cleaned_data.get("start_time")
        end = cleaned_data.get("end_time")
        if end and not start:
            self.add_error("start_time", "Add a start time to go with the end time.")
        elif start and end and end < start:
            self.add_error("end_time", "The end time can't be before the start time.")

        return cleaned_data


# formset_factory makes a "FormSet" class: a group of ImportEventForms
# that are shown, submitted, and validated together. extra=0 means no
# blank rows are added beyond the events we give it.
ImportEventFormSet = forms.formset_factory(ImportEventForm, extra=0)
