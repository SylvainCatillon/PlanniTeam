from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from plannings.models import Planning, Event


class DisplayViewTestCase(TestCase):
    fixtures = ['users', 'plannings']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.planning = Planning.objects.get(name='Test')
        cls.user = User.objects.get(first_name='Participant')
        cls.key = cls.planning.ekey

    def setUp(self):
        self.client.force_login(self.user)

    def test_redirect_if_not_logged(self):
        self.client.logout()
        response = self.client.get(reverse('participations:view', kwargs={
            'planning_ekey': self.key}))
        self.assertRedirects(
            response,
            f'/accounts/login/?next=/participations/view/{self.key}/')

    def test_get_page_by_url(self):
        response = self.client.get(
            f'/participations/view/{self.key}/')
        self.assertEqual(response.status_code, 200)

    def test_get_page_by_name(self):
        response = self.client.get(reverse('participations:view', kwargs={
            'planning_ekey': self.key}))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('participations:view', kwargs={
            'planning_ekey': self.key}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,
                                'participations/view_planning.html')

    # TODO: test_stranger_cant_access

    def test_participants_in_context(self):
        response = self.client.get(reverse('participations:view', kwargs={
            'planning_ekey': self.key}))
        events = Event.objects.filter(planning=self.planning)
        participants_list = []
        for user in User.objects.filter(event__in=events):
            if user not in participants_list:
                participants_list.append(user)
        self.assertIn(participants_list, response.context)  # FIXME

