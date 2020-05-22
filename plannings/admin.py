from django.contrib import admin

from .models import Planning, Event, GuestEmail
from participations.models import Participation


class ParticipationInline(admin.TabularInline):
    model = Participation
    extra = 7


class EventAdmin(admin.ModelAdmin):
    list_display = ('planning', 'date', 'time', 'description', 'address')
    inlines = [ParticipationInline]


class EventInline(admin.TabularInline):
    model = Event
    extra = 1


class PlanningAdmin(admin.ModelAdmin):
    list_display = ('name', 'creator',
                    'last_modification_date', 'creation_date')
    inlines = [EventInline]


admin.site.register(Planning, PlanningAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(GuestEmail)
