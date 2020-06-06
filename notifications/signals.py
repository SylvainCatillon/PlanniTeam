import os

from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.core.mail import send_mass_mail
from django.conf import settings
from django.contrib.auth import get_user_model

from plannings.models import Planning, GuestEmail


@receiver(m2m_changed, sender=Planning.guest_emails.through)
def notify_guest(sender, **kwargs):
    if kwargs.get('action') == 'post_add':
        User = get_user_model()
        domain = os.environ.get('DOMAIN', "")
        planning = kwargs.get('instance')
        creator = planning.creator.first_name
        subject = "Nouvelle invitation sur PlanniTeam"
        data = []
        emails = [guest.email for guest in GuestEmail.objects.filter(pk__in=kwargs.get('pk_set'))]
        for email in emails:
            try:
                user = User.objects.get(email=email)
                message = f"Bonjour {user.first_name}. {creator} vous a invité" \
                          f" au planning {planning.name}.\nPour y participer" \
                          f", connectez vous avec votre compte et rejoignez" \
                          f" {domain+planning.get_absolute_url()}"
            except User.DoesNotExist:
                message = f"Bonjour. {creator} vous a invité au planning" \
                          f" {planning.name}.\nPour y participer, créez un" \
                          f" compte sur {domain} avec cette adresse email " \
                          f"et rejoignez {domain+planning.get_absolute_url()}"
            data.append((
                subject,
                message.format(planning.name, email),
                settings.EMAIL_HOST,
                [email],
            ))
        send_mass_mail(data, fail_silently=False)
