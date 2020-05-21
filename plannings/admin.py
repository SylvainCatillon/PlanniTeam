from django.contrib import admin

from .models import Planning, Event, GuestEmail


class EventInline(admin.TabularInline):
    model = Event
    extra = 1


class PlanningAdmin(admin.ModelAdmin):
    list_display = ('name', 'creator',
                    'last_modification_date', 'creation_date')
    inlines = [EventInline]


admin.site.register(Planning, PlanningAdmin)
admin.site.register(GuestEmail)
