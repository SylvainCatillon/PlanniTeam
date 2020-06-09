from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from plannings.models import Planning
from .Notifier import Notifier


@receiver(m2m_changed, sender=Planning.guest_emails.through)
def notify_guest(sender, **kwargs):
    if kwargs.get('action') == 'post_add':
        notification = Notifier(kwargs.get('instance'))
        notification.notify_guests(kwargs.get('pk_set'))

