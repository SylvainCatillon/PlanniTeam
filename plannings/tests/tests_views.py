from urllib.parse import quote, urlencode

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

    def test_user_in_initial_form_data(self):
        response = self.client.get(reverse('plannings:create'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['planning_form'].initial['creator'],
                         self.user.pk)

    def test_create_fake_user(self):
        name = 'Test'
        response = self.client.post(reverse('plannings:create'),
                                    {'name': name, 'creator': 0})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'planning_form', 'creator', _(
            'Select a valid choice. That choice is not one of the available '
            'choices.'))

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

        # The user is redirected to a success page
        self.assertRedirects(response, reverse('plannings:created', kwargs={
            'planning_ekey': planning.ekey}))

        # The planning has all the wanted attributes
        self.assertTrue(planning.protected)
        self.assertEqual(params['guest_email'],
                         [e.email for e in planning.guest_emails.all()])
        self.assertEqual(params['creator'], planning.creator.pk)

    def test_create_with_event(self):
        event_dict = [
            {'date': '2020-12-05', 'time': '', 'description': '', 'address': ''},
            {'date': '2020-12-06', 'time': '18:05:00', 'description': '',
             'address': ''},
            {'date': '2020-12-07', 'time': '18:30:00',
             'description': 'A pretty long description with specials '
                                  'char as = and & and # or è, é, %, ?!, *,'
                                  '$,},@,+256...',
             'address': ''},
            {'date': '2020-12-08', 'time': '20:00:00',
             'description': 'This%20is%20description',
             'address': '2%20boulevard%20something'}
        ]
        # use urllib.encode to escape char
        event_list = [urlencode(d, quote_via=quote) for d in event_dict]
        params = {'name': 'Test', 'event': event_list, 'creator': self.user.pk}
        response = self.client.post(reverse('plannings:create'), params)
        planning = Planning.objects.get(name=params['name'])

        # The user is redirected to a success page
        self.assertRedirects(response, reverse('plannings:created', kwargs={
            'planning_ekey': planning.ekey}))

        # The planning has all the wanted attributes
        self.assertEqual(params.get('creator'), planning.creator.pk)
        created_events = Event.objects.filter(planning=planning)
        for event in event_dict:
            created_event = created_events.get(date=event['date'])
            for key, value in event.items():
                if value and key != 'date':
                    if key == 'time':
                        # Convert to string the datetime object in Event.time
                        self.assertEqual(str(created_event.time),
                                         value)
                    else:
                        self.assertEqual(getattr(created_event, key),
                                         value)

    def test_create_with_event_and_guests(self):
        event_dict = [
            {'date': '2020-12-05', 'time': '', 'description': '',
             'address': ''},
            {'date': '2020-12-06', 'time': '18:05:00', 'description': '',
             'address': ''},
            {'date': '2020-12-07', 'time': '18:30:00',
             'description': 'A pretty long description with specials '
                            'char as = and & and # or è, é, %, ?!, *,'
                            '$,},@,+256...',
             'address': ''},
            {'date': '2020-12-08', 'time': '20:00:00',
             'description': 'This%20is%20description',
             'address': '2%20boulevard%20something'}
        ]
        # use urllib.encode to escape char
        event_list = [urlencode(d, quote_via=quote) for d in event_dict]
        guest_emails = ["participant@test.com",
                        "participant2@test.com",
                        "participant3@test.com"]
        params = {'name': 'Test', 'event': event_list, 'creator': self.user.pk,
                  'protected': True, 'guest_email': guest_emails}
        response = self.client.post(reverse('plannings:create'), params)
        planning = Planning.objects.get(name=params['name'])

        # The user is redirected to a success page
        self.assertRedirects(response, reverse('plannings:created', kwargs={
            'planning_ekey': planning.ekey}))

        # The planning has all the wanted attributes
        self.assertEqual(params.get('creator'), planning.creator.pk)
        self.assertTrue(planning.protected)
        self.assertEqual(params['guest_email'],
                         [e.email for e in planning.guest_emails.all()])
        created_events = Event.objects.filter(planning=planning)
        for event in event_dict:
            created_event = created_events.get(date=event['date'])
            for key, value in event.items():
                if value and key != 'date':
                    if key == 'time':
                        self.assertEqual(str(created_event.time), value)
                    else:
                        self.assertEqual(getattr(created_event, key), value)