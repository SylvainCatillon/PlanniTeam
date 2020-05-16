from django.test import TestCase
from datetime import date, time

from accounts.models import User
from plannings.models import Planning, Event


class PlanningTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(
            email='creator@test.com',
            password='test_password')

    def test_unprotected_planning_creation(self):
        planning = Planning.objects.create(creator=self.user, name='Test')
        self.assertIsInstance(planning, Planning)
        self.assertFalse(planning.protected)

    def test_protected_planning_creation(self):
        planning = Planning.objects.create(creator=self.user, name='Test',
                                           protected=True)
        guest_mail = 'guest@test.com'
        planning.guest_mails.create(mail=guest_mail)
        self.assertIsInstance(planning, Planning)
        self.assertTrue(planning.protected)
        self.assertEqual(planning.guest_mails.all()[0].mail, guest_mail)


class EventTestCase(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        user = User.objects.create_user(
            email='creator@test.com',
            password='test_password')
        cls.planning = Planning.objects.create(creator=user, name='Test')

    def test_less_info_event_creation(self):
        event_date = date(2020, 12, 8)
        event = Event.objects.create(planning=self.planning,
                                     date=event_date)
        self.assertIsInstance(event, Event)
        self.assertEqual(event_date, event.date)

    def test_more_info_event_creation(self):
        event_date = date(2020, 12, 8)
        event_time = time(18, 30)
        description = "Ceci est la description de l'événement"
        address = "15 rue Michel Drucker, 75003 Paris"
        event = Event.objects.create(planning=self.planning,
                                     date=event_date,
                                     time=event_time,
                                     description=description,
                                     address=address)
        self.assertIsInstance(event, Event)
        self.assertEqual(event.description, description)
        self.assertEqual(event.address, address)
        self.assertEqual(event_date, event.date)
        self.assertEqual(event_time, event.time)
