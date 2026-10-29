"""
Form adding/editing file
Uses event model from models.py
"""

from django import forms

from .models import Event

# Date/Time picker formatting
DATETIME_INPUT_FORMAT = "%Y-%m-%dT%H:%M"


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        '''
        "owner" and "source" are left out on purpose: the view fills
        those in, so users can't create events for someone else.
        '''
        fields = ["title", "start", "end", "all_day", "category", "description"]
        widgets = {
            "start": forms.DateTimeInput(
                attrs={"type": "datetime-local"}, format=DATETIME_INPUT_FORMAT
            ),
            "end": forms.DateTimeInput(
                attrs={"type": "datetime-local"}, format=DATETIME_INPUT_FORMAT
            ),
            "description": forms.Textarea(attrs={"rows": 4}),
        }
        labels = {
            "start": "Starts",
            "end": "Ends (optional)",
            "all_day": "All-day event",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        '''
        Tell Django how to read the date-and-time values the browser sends
        '''
        self.fields["start"].input_formats = [DATETIME_INPUT_FORMAT]
        self.fields["end"].input_formats = [DATETIME_INPUT_FORMAT]

    def clean(self):
        """Extra check that runs after each field has been validated."""
        cleaned_data = super().clean()
        start = cleaned_data.get("start")
        end = cleaned_data.get("end")

        if start and end and end < start:
            self.add_error("end", "The end time can't be before the start time.")

        return cleaned_data
