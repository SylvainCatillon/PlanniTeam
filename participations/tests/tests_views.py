from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from plannings.models import Planning, Event


class DisplayViewTestCase(TestCase):
    fixtures = ['users', 'plannings', 'participations']

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
        self.assertEqual(response.status_code, 200)
        events = Event.objects.filter(planning=self.planning)
        other_participants = []
        for user in User.objects.filter(event__in=events)\
                                .order_by('first_name'):
            if user != self.user and user not in other_participants:
                other_participants.append(user)
        self.assertIn('other_participants', response.context.keys())
        self.assertEqual(other_participants,
                         response.context['other_participants'])

    def test_events_in_context(self):
        response = self.client.get(reverse('participations:view', kwargs={
            'planning_ekey': self.key}))
        self.assertEqual(response.status_code, 200)
        self.assertIn('events', response.context)
        context_events = response.context['events']
        for event in Event.objects.filter(planning=self.planning):
            self.assertIn(event, context_events.keys())
            for participation in event.participation_set.exclude(
                    participant=self.user):
                self.assertIn(participation, context_events[event])
