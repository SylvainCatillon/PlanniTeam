from django.db import models
from django.urls import reverse
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
    name = models.CharField('nom', max_length=200)
    protected = models.BooleanField('protégé', default=False)
    guest_emails = models.ManyToManyField(GuestEmail)

    def __str__(self):
        return f"Planning {self.name} by {self.creator.email}"

    @property
    def get_guest_emails(self):
        return [guest.email for guest in self.guest_emails.all()]

    def user_has_access(self, user):
        return (not self.protected) or (user == self.creator) or \
               (user.email in self.get_guest_emails)

    def get_absolute_url(self):
        return reverse(
            'participations:view', args=(str(self.ekey),))


class Event(models.Model):
    planning = models.ForeignKey(Planning, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField('horaire', blank=True, null=True)
    description = models.TextField(blank=True)
    address = models.CharField('adresse', max_length=300, blank=True)
    participants = models.ManyToManyField(
        User, through='participations.Participation')

    class Meta:
        ordering = ['date']
