from django.test import TestCase
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from accounts.models import User
from plannings.models import Planning


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
        self.assertEqual(response.context['form'].initial['creator'],
                         self.user.pk)

    def test_create_minimal_planning(self):
        name = 'Test'
        response = self.client.post(reverse('plannings:create'),
                                    {'name': name, 'creator': self.user.pk})
        planning = Planning.objects.get(name=name)
        self.assertIn(planning, self.user.planning_created.all())
        self.assertRedirects(response, reverse('plannings:created', kwargs={
            'planning_ekey': planning.ekey}))

    def test_create_planning_with_guests(self):
        guest_mails = ["participant@test.com",
                       "participant2@test.com",
                       "participant3@test.com"]
        params = {'name': 'Test', 'protected': True, 'guest_mail': guest_mails,
                  'creator': self.user.pk}
        response = self.client.post(reverse('plannings:create'), params)
        planning = Planning.objects.get(name=params['name'])
        self.assertRedirects(response, reverse('plannings:created', kwargs={
            'planning_ekey': planning.ekey}))
        self.assertEqual(params.pop('guest_mail'),
                         [e.mail for e in planning.guest_mails.all()])
        self.assertEqual(params.pop('creator'), planning.creator.pk)
        for key, value in params.items():
            self.assertEqual(getattr(planning, key), value)

    def test_create_not_logged_user(self):
        name = 'Test'
        response = self.client.post(reverse('plannings:create'),
                                    {'name': name, 'creator': 0})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'creator', _(
            'Select a valid choice. That choice is not one of the available '
            'choices.')) 
