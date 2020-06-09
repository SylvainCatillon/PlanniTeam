from django.db import models
from django.urls import reverse
from encrypted_id.models import EncryptedIDModel

from accounts.models import User


class GuestEmail(models.Model):
    """GuestEmail Model. Define the emails that a planning creator will provide
    for a list of guests."""

    email = models.EmailField()

    def __str__(self):
        return self.email

    class Meta:
        ordering = ['email']


class Planning(EncryptedIDModel):
    """Planning Model.
    creator: Foreign key to the user who created the planning.
    creation_date: DateTime field saving the date of creation of the planning
    last_modification_date: DateTime field saving the date of
    the last modification of the planning.
    name: Name of the planning.
    protected: Define the access rule of the planning.
    If the planning is protected, only the guests can access.
    guest_emails: Emails of the planning's guests. Many to Many field.
    """

    creator = models.ForeignKey(User, on_delete=models.CASCADE,
                                related_name='planning_created')
    creation_date = models.DateTimeField(auto_now_add=True)
    last_modification_date = models.DateTimeField(auto_now=True)
    name = models.CharField('nom', max_length=200)
    protected = models.BooleanField('protégé', default=False)
    guest_emails = models.ManyToManyField(GuestEmail)

    def __str__(self):
        return f"Planning {self.name} by {self.creator.email}"

    @property
    def get_guest_emails(self):
        """Returns the emails of the planning's guests"""
        return [guest.email for guest in self.guest_emails.all()]

    def user_has_access(self, user):
        """Takes a user as arg, and return True if this userhas access.
        A user has access to a planning if:
        -The planning isn't protected.
        -The user is the creator of the planning.
        -The user's email is in the guests' emails list."""
        return (not self.protected) or (user == self.creator) or \
               (user.email in self.get_guest_emails)

    def get_absolute_url(self):
        return reverse(
            'participations:view', args=(str(self.ekey),))


class Event(models.Model):
    """Event Model."""
    planning = models.ForeignKey(Planning, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField('horaire', blank=True, null=True)
    description = models.TextField(blank=True)
    address = models.CharField('adresse', max_length=300, blank=True)
    participants = models.ManyToManyField(
        User, through='participations.Participation')

    class Meta:
        ordering = ['date']
