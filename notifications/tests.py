from django.test import TestCase
from django.core import mail
from django.contrib.auth import get_user_model
from django.urls import reverse

from plannings.utils import add_guests, update_guests
from plannings.models import Planning


class NotificationsTestCase(TestCase):
    fixtures = ['users', 'plannings']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.creator = get_user_model().objects.get(first_name='Creator')
        cls.participant = get_user_model().objects.get(first_name='Participant')

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
        for Email in mail.outbox:
            email = Email.to[0]
            self.assertIn(email, guest_emails)
            if email == self.participant.email:
                self.assertIn(self.participant.first_name, Email.body)
            guest_emails.remove(email)
        # Assert that all the guests' emails have been found
        self.assertEqual(len(guest_emails), 0)

    def test_notify_guest_planning_edition(self):
        planning = Planning.objects.first()
        guest_emails = planning.get_guest_emails
        old_guest = guest_emails[0]
        new_guest = 'newguest@test.com'
        guest_emails.append(new_guest)
        update_guests(planning, guest_emails)

        # Assert that the new guest got an email, but not the old guest
        self.assertEqual(len(guest_emails)-1, len(mail.outbox))
        for email in mail.outbox:
            self.assertIn(email.to[0], guest_emails)
            guest_emails.remove(email.to[0])
        self.assertEqual(guest_emails, [old_guest])


