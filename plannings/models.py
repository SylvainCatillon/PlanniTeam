from django.db import models
from encrypted_id.models import EncryptedIDModel

from accounts.models import User


class GuestEmail(models.Model):
    email = models.EmailField()

    def __str__(self):
        return self.email


class Planning(EncryptedIDModel):
    creator = models.ForeignKey(User, on_delete=models.CASCADE,
                                related_name='planning_created')
    creation_date = models.DateTimeField(auto_now_add=True)
    # TODO: lier à la création/modification d'event.
    #  Via une fonction qui récupère le champ last_modified de Event?
    last_modification_date = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=200)
    protected = models.BooleanField(default=False)
    guest_emails = models.ManyToManyField(GuestEmail)

    def __str__(self):
        return f"Planning {self.name} by {self.creator.email}"


class Event(models.Model):
    planning = models.ForeignKey(Planning, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField(blank=True, null=True)
    description = models.TextField(blank=True)
    address = models.CharField(max_length=300, blank=True)
    participations = models.ManyToManyField(
        User, through='participations.Participation')

    class Meta:
        ordering = ['date']
