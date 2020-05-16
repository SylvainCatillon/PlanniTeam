from django.db import models
from encrypted_id.models import EncryptedIDModel

from accounts.models import User


class GuestMail(models.Model):
    mail = models.EmailField()


class Planning(EncryptedIDModel):
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    protected = models.BooleanField(default=False)
    guest_mails = models.ManyToManyField(GuestMail)


class Event(models.Model):
    planning = models.ForeignKey(Planning, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField(blank=True, null=True)
    description = models.TextField(blank=True)
    address = models.CharField(max_length=300, blank=True)
#     participations = models.ManyToManyField(User, through='Participation')

