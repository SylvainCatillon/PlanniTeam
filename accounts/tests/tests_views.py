from django.contrib.auth import authenticate
from django.test import TestCase
from django.urls import reverse

from accounts.models import User


class NewUserTestCase(TestCase):
    """TestCase for the tests regarding a new user"""

    def test_user_creation(self):
        """Tests if a user can be created through the view 'create'"""
        user_info = {
            'email': 'test@test.com',
            'first_name': 'test',
            'password1': 'test_password',
            'password2': 'test_password',
        }
        self.assertIsNone(authenticate(
            email=user_info["email"],
            password=user_info["password1"]))
        response = self.client.post(reverse("accounts:create"), user_info)
        self.assertIsNotNone(authenticate(
            email=user_info["email"],
            password=user_info["password1"]))
        self.assertRedirects(
            response, "/accounts/profile/",
            msg_prefix="User not redirected to profile")


class UnLoggedUserTestCase(TestCase):
    """TestCase for the tests regarding an un logged user"""

    @classmethod
    def setUpClass(cls):
        """Create a user at the set up of the class"""
        super().setUpClass()
        cls.user_info = {
            'email': 'test@test.com',
            'first_name': 'test',
            'password': 'test_password',
        }
        cls.user = User.objects.create_user(**cls.user_info)

    def test_user_login(self):
        """Tests if a user can log in though the view 'login'.
        -Make a GET request to the view
        -Assert that the user isn't logged
        -Make a POST request with a valid username/password combinaison
        -Assert that the user is now logged
        -Assert that the user is redirected to the 'profil' page"""
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        response = self.client.post(reverse('accounts:login'), {
            'username': self.user_info['email'],
            'password': self.user_info['password'],
        })
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        self.assertRedirects(
            response, "/accounts/profile/",
            msg_prefix="User not redirected to profile")

    def test_profile_access(self):
        """Tests that an un logged who try to access the 'profile' page is
        redirected to the 'login' page"""
        response = self.client.get(reverse("accounts:profile"))
        self.assertRedirects(
            response, '/accounts/login/?next=/accounts/profile/',
            msg_prefix='User not redirected to login')


class LoggedUserTestCase(TestCase):
    """TestCase for the tests regarding a logged user"""

    @classmethod
    def setUpClass(cls):
        """Create a user at the set up of the class"""
        super().setUpClass()
        cls.user_info = {
            'email': 'test@test.com',
            'first_name': 'test',
            'password': 'test_password',
        }
        cls.user = User.objects.create_user(**cls.user_info)

    def setUp(self):
        """Login the user at the set up of each test"""
        self.client.login(email=self.user_info['email'],
                          password=self.user_info['password'])

    def test_logout(self):
        """Tests that a user can logout"""
        self.assertIn('_auth_user_id', self.client.session.keys(),
                      msg="User isn't logged before logout request")
        self.client.get(reverse('accounts:logout'))
        self.assertNotIn('_auth_user_id', self.client.session.keys(),
                         msg="User is still logged after logout request")

    def test_profile(self):
        """Tests that a logged user can access the profile page and see:
        -their email
        -their first_name"""
        response = self.client.get(reverse("accounts:profile"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user.email)
        self.assertContains(response, self.user.first_name)
