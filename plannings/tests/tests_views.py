import json

from django.test import TestCase
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from accounts.models import User
from plannings.models import Planning
from plannings.forms import EventInlineFormSet


class PlanningCreationViewTest(TestCase):
    fixtures = ['users']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.get(first_name='Creator')
        cls.prefix = EventInlineFormSet.get_default_prefix()
        cls.events_data = [
            {'date': '2020-12-05', 'time': '',
             'description': '', 'address': ''},
            {'date': '2020-12-06', 'time': '18:05:00',
             'description': '', 'address': ''},
            {'date': '2020-12-07', 'time': '18:30:00',
             'description': 'A pretty long description with specials '
                            'char as = and & and # or è, é, %, ?!, *,'
                            '$,},@,+256...',
             'address': ''},
            {'date': '2020-12-08', 'time': '20:00:00',
             'description': 'This is description',
             'address': '2 boulevard something'}
        ]
        cls.event_setform_data = {
            cls.prefix+'-TOTAL_FORMS': 0,
            cls.prefix+'-INITIAL_FORMS': '0',
            cls.prefix+'-MAX_NUM_FORMS': '',
        }

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
        params = dict(self.event_setform_data,
                      name='Test', creator=self.user.pk)
        response = self.client.post(reverse('plannings:create'), params)
        planning = Planning.objects.get(name=params['name'])
        self.assertIn(planning, self.user.planning_created.all())
        self.assertFalse(planning.protected)
        self.assertRedirects(response, reverse('plannings:created', kwargs={
            'planning_ekey': planning.ekey}))

    def test_create_protected_planning_without_guests(self):
        params = dict(self.event_setform_data,
                      name='Test', creator=self.user.pk,
                      protected=True)
        response = self.client.post(reverse('plannings:create'), params)
        planning = Planning.objects.get(name=params['name'])
        self.assertIn(planning, self.user.planning_created.all())
        self.assertTrue(planning.protected)
        self.assertQuerysetEqual(planning.guest_emails.all(), [])
        self.assertRedirects(response, reverse('plannings:created', kwargs={
            'planning_ekey': planning.ekey}))

    def test_create_planning_with_guests(self):
        guest_emails = ["participant@test.com",
                        "participant2@test.com",
                        "participant3@test.com"]
        params = dict(self.event_setform_data,
                      name='Test', creator=self.user.pk,
                      protected=True, guest_email=guest_emails)
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

    def test_get_check_event_throw_405(self):
        response = self.client.get(reverse('plannings:check_event'))
        self.assertEqual(response.status_code, 405)

    def test_event_check_invalid_data(self):
        event_args = {'date': '2020,12,07', 'time': '18-30-00',
                      'description': 'A pretty long description with specials '
                                     'char as = and & and # or è, é, %, ?!, *,'
                                     '$,},@,+256...',
                      'address': '10 boulevard something, 75010 Paris'}
        response = self.client.post(reverse('plannings:check_event'),
                                    event_args)
        self.assertEqual(response.status_code, 422)
        errors = json.loads(response.content)
        self.assertEqual(errors['date'], [
            {'message': _('Enter a valid date.'), 'code': 'invalid'}])
        self.assertEqual(errors['time'], [
            {'message': _('Enter a valid time.'), 'code': 'invalid'}])

    def test_event_check_empty_data(self):
        response = self.client.post(reverse('plannings:check_event'), {})
        self.assertEqual(response.status_code, 422)
        errors = json.loads(response.content)
        self.assertEqual(errors['date'], [
            {'message': _('This field is required.'), 'code': 'required'}])

    def test_event_check_valid_data(self):
        event_args = {'date': '2020-12-07', 'time': '18:30:00',
                      'description': 'A pretty long description with specials '
                                     'char as = and & and # or è, é, %, ?!, *,'
                                     '$,},@,+256...',
                      'address': '10 boulevard something, 75010 Paris'}
        response = self.client.post(reverse('plannings:check_event'),
                                    event_args)
        self.assertEqual(response.status_code, 200)

    def test_create_with_event(self):
        for i, event in enumerate(self.events_data):
            self.event_setform_data[self.prefix+'-TOTAL_FORMS'] += 1
            for key, value in event.items():
                self.event_setform_data[f"{self.prefix}-{i}-{key}"] = value
        params = dict(self.event_setform_data,
                      name='Test', creator=self.user.pk)
        response = self.client.post(reverse('plannings:create'), params)
        planning = Planning.objects.get(name=params['name'])

        # The user is redirected to a success page
        self.assertRedirects(response, reverse('plannings:created', kwargs={
            'planning_ekey': planning.ekey}))

        # The planning has all the wanted attributes
        self.assertEqual(params.get('creator'), planning.creator.pk)
        for event in self.events_data:
            created_event = planning.event_set.get(date=event['date'])
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
        for i, event in enumerate(self.events_data):
            self.event_setform_data[self.prefix+'-TOTAL_FORMS'] += 1
            for key, value in event.items():
                self.event_setform_data[f"{self.prefix}-{i}-{key}"] = value
        guest_emails = ["participant@test.com",
                        "participant2@test.com",
                        "participant3@test.com"]
        params = dict(self.event_setform_data,
                      name='Test', creator=self.user.pk,
                      protected=True, guest_email=guest_emails)
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
        for event in self.events_data:
            created_event = planning.event_set.get(date=event['date'])
            for key, value in event.items():
                if value and key != 'date':
                    if key == 'time':
                        # Convert to string the datetime object in Event.time
                        self.assertEqual(str(created_event.time),
                                         value)
                    else:
                        self.assertEqual(getattr(created_event, key),
                                         value)
