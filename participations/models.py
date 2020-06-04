from django.db import models
from django.utils.translation import gettext_lazy as _

from accounts.models import User
from plannings.models import Event


class Participation(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    participant = models.ForeignKey(User, on_delete=models.CASCADE)
    answer_choices = [
        ('YES', _('Yes')),
        ('NO', _('No')),
        ('MAYBE', 'Peut-être')  # TODO: gérer traduction
    ]
    answer = models.CharField(max_length=5, choices=answer_choices)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['event', 'participant'],
                                    name='unique_participant_event'),
            # TODO: CheckConstraint vérifiant que l'email de l'user est dans
            #  la guest_mail du planning de l'event
        ]
        ordering = ['participant__first_name']

    def __str__(self):
        participant = self.participant.first_name
        event = self.event.pk
        return f"Participant: {participant}, Event: {event}"
