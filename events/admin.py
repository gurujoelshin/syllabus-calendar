"""
Admin features for admin users

Admin users can view, search, filter, and edit user events from Django admin interface
"""

from django.contrib import admin

from .models import Event


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "owner", "category", "start", "end", "all_day", "source")
    list_filter = ("category", "source", "all_day", "owner")
    search_fields = ("title", "description")
    date_hierarchy = "start"
