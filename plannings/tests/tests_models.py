from django.test import TestCase

from accounts.models import User
from plannings.models import Planning


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
