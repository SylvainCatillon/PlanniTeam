import datetime

from django.test import TestCase
from django.core import mail
from django.contrib.auth import get_user_model

from notifications.notifier import Notifier
from plannings.forms import EventInlineFormSet
from plannings.utils import add_guests, update_guests
from plannings.models import Planning, Event


class NotificationsTestCase(TestCase):
    fixtures = ['users', 'plannings', 'participations']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.creator = get_user_model().objects.get(first_name='Creator')
        cls.participant = get_user_model().objects.get(
            first_name='Participant')

    def setUp(self):
        self.client.force_login(self.creator)

    def test_notify_guest_planning_creation(self):
        guest_emails = [self.participant.email,
                        "participant2@test.com",
                        "participant3@test.com"]
        params = dict(name='TestNotif', creator=self.creator, protected=True)
        planning = Planning.objects.create(**params)
        add_guests(planning, guest_emails)

        self.assertEqual(len(guest_emails), len(mail.outbox))
        for email in mail.outbox:
            self.assertEqual(1, len(email.to))
            receiver = email.to[0]
            self.assertIn(receiver, guest_emails)
            # Assert that the name of the participant is in the message
            if receiver == self.participant.email:
                self.assertIn(self.participant.first_name, email.body)
            guest_emails.remove(receiver)
        # Assert that all the guests' emails have been found
        self.assertEqual(len(guest_emails), 0)

    def test_notify_guest_planning_edition(self):
        planning = Planning.objects.first()
        guest_emails = planning.get_guest_emails
        # Assert that there are pre-existing guests
        self.assertTrue(len(guest_emails))
        new_guest = 'newguest@test.com'
        guest_emails.append(new_guest)
        update_guests(planning, guest_emails)

        # Assert that only the new guest got an email
        self.assertEqual(1, len(mail.outbox))
        self.assertEqual(mail.outbox[0].to[0], new_guest)

    def test_notify_event_changes(self):
        planning = Planning.objects.first()
        participants = [user.email for user in get_user_model().objects.filter(
            event__planning__pk=planning.pk).distinct()]
        # Assert that there are participants
        self.assertTrue(len(participants))
        events = [Event(planning=planning, date=datetime.date(2020, 1, i)) for
                  i in range(1, 4)]
        formset = EventInlineFormSet()
        formset.new_objects = [events[0], events[1]]
        formset.changed_objects = []
        formset.deleted_objects = [events[2]]
        notifier = Notifier(planning)
        notifier.notify_events_changes(formset)

        # Assert that all the participants got an email
        self.assertEqual(len(participants), len(mail.outbox))
        for email in mail.outbox:
            self.assertEqual(1, len(email.to))
            self.assertIn(email.to[0], participants)
            participants.remove(email.to[0])
        self.assertEqual(len(participants), 0)
