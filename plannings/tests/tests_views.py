from urllib.parse import quote, unquote

from django.test import TestCase
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from accounts.models import User
from plannings.models import Planning, Event


class PlanningCreationViewTest(TestCase):
    fixtures = ['users']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.get(first_name='Creator')

    def setUp(self):
        self.client.force_login(self.user)

    def test_redirect_if_not_logged(self):
        self.client.logout()
        response = self.client.get(reverse('plannings:create'))
        self.assertRedirects(
            response, '/accounts/login/?next=/plannings/create/')

    def test_get_creation_page_by_url(self):
        response = self.client.get('/plannings/create/')
        self.assertEqual(response.status_code, 200)

    def test_get_creation_page_by_name(self):
        response = self.client.get(reverse('plannings:create'))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('plannings:create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'plannings/create_planning.html')

    def test_form_user_in_initial_data(self):
        response = self.client.get(reverse('plannings:create'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['planning_form'].initial['creator'],
                         self.user.pk)

    def test_create_minimal_planning(self):
        name = 'Test'
        response = self.client.post(reverse('plannings:create'),
                                    {'name': name, 'creator': self.user.pk})
        planning = Planning.objects.get(name=name)
        self.assertIn(planning, self.user.planning_created.all())
        self.assertFalse(planning.protected)
        self.assertRedirects(response, reverse('plannings:created', kwargs={
            'planning_ekey': planning.ekey}))

    def test_create_protected_planning_without_guests(self):
        name = 'Test'
        response = self.client.post(
            reverse('plannings:create'),
            {'name': name, 'creator': self.user.pk, 'protected': True})
        planning = Planning.objects.get(name=name)
        self.assertIn(planning, self.user.planning_created.all())
        self.assertTrue(planning.protected)
        self.assertQuerysetEqual(planning.guest_emails.all(), [])
        self.assertRedirects(response, reverse('plannings:created', kwargs={
            'planning_ekey': planning.ekey}))

    def test_create_planning_with_guests(self):
        guest_emails = ["participant@test.com",
                        "participant2@test.com",
                        "participant3@test.com"]
        params = {'name': 'Test', 'protected': True,
                  'guest_email': guest_emails, 'creator': self.user.pk}
        response = self.client.post(reverse('plannings:create'), params)
        planning = Planning.objects.get(name=params['name'])
        self.assertRedirects(response, reverse('plannings:created', kwargs={
            'planning_ekey': planning.ekey}))
        self.assertEqual(params.pop('guest_email'),
                         [e.email for e in planning.guest_emails.all()])
        self.assertEqual(params.pop('creator'), planning.creator.pk)
        for key, value in params.items():
            self.assertEqual(getattr(planning, key), value)

    def test_create_not_logged_user(self):
        name = 'Test'
        response = self.client.post(reverse('plannings:create'),
                                    {'name': name, 'creator': 0})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'planning_form', 'creator', _(
            'Select a valid choice. That choice is not one of the available '
            'choices.'))

    def test_create_with_event(self):
        event_dict = [
            {'date': '2020-12-05', 'time': '', 'description': '', 'address': ''},
            {'date': '2020-12-06', 'time': quote('18:05:00'), 'description': '',
             'address': ''},
            {'date': '2020-12-07', 'time': quote('18:30:00'),
             'description': 'bdmazbdoazh%3Dzakjdgazdg%26bgosgfpo%3Dazkjdgapzidgamzdg%C3%A2o',
             'address': ''},
            {'date': '2020-12-08', 'time': quote('20:00:00'), 'description': quote('This%20is%20description'),
             'address': quote('2%20boulevard%20something')}
        ]
        event_list = ["&".join("=".join(itms) for itms in d.items()) for d in event_dict]
        params = {'name': 'Test', 'event': event_list, 'creator': self.user.pk}
        response = self.client.post(reverse('plannings:create'), params)
        planning = Planning.objects.get(name=params['name'])
        self.assertRedirects(response, reverse('plannings:created', kwargs={
            'planning_ekey': planning.ekey}))
        self.assertEqual(params.get('creator'), planning.creator.pk)
        self.assertEqual(params.get('name'), planning.name)
        created_events = Event.objects.filter(planning=planning)
        for event in event_dict:
            created_event = created_events.get(date=event['date'])
            for key, value in event.items():
                if value and key != 'date':
                    if key == 'time':
                        self.assertEqual(str(created_event.time), unquote(value))
                    else:
                        self.assertEqual(getattr(created_event, key), unquote(value))