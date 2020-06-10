from django.contrib import admin

from participations.models import Participation


class ParticipationAdmin(admin.ModelAdmin):
    list_display = ('participant', 'event', 'answer')


admin.site.register(Participation, ParticipationAdmin)
