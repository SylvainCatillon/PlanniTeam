from datetime import date, time

from django.test import TestCase

from accounts.models import User
from plannings.models import Planning, Event


class PlanningTestCase(TestCase):
    fixtures = ['users']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.get(first_name='Creator')

    def test_unprotected_planning_creation(self):
        planning = Planning.objects.create(creator=self.user, name='Test')
        self.assertIsInstance(planning, Planning)
        self.assertFalse(planning.protected)

    def test_protected_planning_creation(self):
        planning = Planning.objects.create(creator=self.user, name='Test',
                                           protected=True)
        guest_email = 'guest@test.com'
        planning.guest_emails.create(email=guest_email)
        self.assertIsInstance(planning, Planning)
        self.assertTrue(planning.protected)
        self.assertEqual(planning.guest_emails.all()[0].email, guest_email)


class EventTestCase(TestCase):
    fixtures = ['users']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        user = User.objects.get(first_name='Creator')
        cls.planning = Planning.objects.create(creator=user, name='Test')

    def test_less_info_event_creation(self):
        event_params = dict(
            planning=self.planning,
            date=date(2020, 12, 8))
        event = Event.objects.create(**event_params)
        self.assertIsInstance(event, Event)
        for key, value in event_params.items():
            self.assertEqual(getattr(event, key), value)

    def test_more_info_event_creation(self):
        event_params = dict(
            planning=self.planning,
            date=date(2020, 12, 8),
            time=time(18, 30),
            description="Ceci est la description de l'événement",
            address="15 rue Michel Drucker, 75003 Paris")
        event = Event.objects.create(**event_params)
        self.assertIsInstance(event, Event)
        for key, value in event_params.items():
            self.assertEqual(getattr(event, key), value)
