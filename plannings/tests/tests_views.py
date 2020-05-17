from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from plannings.models import Planning


class TestPlanningCreation(TestCase):
    fixtures = ['users']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.get(first_name='Creator')

    def setUp(self):
        self.client.force_login(self.user)

    def test_get_creation_page(self):
        response = self.client.get(reverse('plannings:create'))
        self.assertEqual(response.status_code, 200)

    def test_create_minimal_planning(self):
        name = 'Test'
        response = self.client.post(reverse('plannings:create'),
                                    {'name': name})
        self.assertEqual(response.status_code, 302)
        planning = Planning.objects.get(name=name)
        self.assertIn(planning, self.user.planning_created.all())

    def test_create_planning_with_guests(self):
        guest_mails = ["participant@test.com",
                      "participant2@test.com",
                      "participant3@test.com"]
        params = dict(
            name='Test',
            protected=True,
            guest_mails=guest_mails
        )
        response = self.client.post(reverse('plannings:create'),
                                    params)
        self.assertEqual(response.status_code, 302)
        planning = Planning.objects.all()[0]
        self.assertEqual(params.pop('guest_mails'),
                         [e.mail for e in planning.guest_mails.all()])
        for key, value in params.items():
            self.assertEqual(getattr(planning, key), value)
