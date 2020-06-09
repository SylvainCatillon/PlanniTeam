import os

from django.contrib.auth import get_user_model
from django.core.mail import send_mass_mail
from django.conf import settings

from plannings.models import GuestEmail

from .messages import guests_notifications_texts, events_changes_texts


class Notifier:

    def __init__(self, planning):
        self.UserModel = get_user_model()
        self.domain = os.environ.get('DOMAIN', "")
        self.planning = planning
        self.planning_name = self.planning.name
        self.planning_url = self.domain + self.planning.get_absolute_url()

    def notify_events_changes(self, event_formset):
        """Notify the participants of a planning with the changements
        on a given events formset"""
        texts = events_changes_texts
        added = event_formset.new_objects
        modified = [e[0] for e in event_formset.changed_objects]
        deleted = event_formset.deleted_objects
        if added or modified or deleted:
            participants = self.UserModel.objects.filter(
                event__planning=self.planning).distinct()
            data = []
            subject = texts['subject'].format(planning_name=self.planning_name)
            message = texts['base_message']
            for row in [(added, texts["added"]), (modified, texts["modified"]),
                        (deleted, texts["deleted"])]:
                events = row[0]
                if events:
                    dates = [event.date.strftime("%d/%m/%Y")
                             for event in events]
                    events_str = ", ".join(dates)
                    message += texts['event_row'].format(type=row[1],
                                                         events=events_str)

            for user in participants:
                data.append((
                    subject,
                    message.format(user_name=user.first_name,
                                   planning_name=self.planning_name,
                                   planning_url=self.planning_url),
                    settings.EMAIL_HOST,
                    [user.email],
                ))
            send_mass_mail(data, fail_silently=False)

    def notify_guests(self, pk_set):
        """Notify the guests of a planning"""
        texts = guests_notifications_texts
        creator_name = self.planning.creator.first_name
        subject = texts['subject']
        data = []
        emails = [guest.email for guest in
                  GuestEmail.objects.filter(pk__in=pk_set)]
        for email in emails:
            try:
                user = self.UserModel.objects.get(email=email)
                message = texts['user_message'].format(
                    user_name=user.first_name,
                    creator_name=creator_name,
                    planning_name=self.planning_name,
                    planning_url=self.planning_url
                )
            except self.UserModel.DoesNotExist:
                message = texts['new_user_message'].format(
                    creator_name=creator_name,
                    planning_name=self.planning_name,
                    domain=self.domain,
                    planning_url=self.planning_url
                )
            data.append((
                subject,
                message,
                settings.EMAIL_HOST,
                [email],
            ))
        send_mass_mail(data, fail_silently=False)
