from django.test import TestCase

from accounts.models import User


class UserTestCase(TestCase):
    """"TestCase for the Model User"""

    def test_user_creation(self):
        """Tests that a user can be created"""
        user = User.objects.create_user(email='test@test.com',
                                        first_name='test',
                                        password='test_password')
        self.assertIsInstance(user, User)

    def test_user_without_email(self):
        """Tests that a user can't be created without email"""
        with self.assertRaisesMessage(
                ValueError,
                'The given email must be set'):
            User.objects.create_user(
                email="", first_name='test', password='test_password')

    def test_superuser_creation(self):
        """Tests that a superuser can be created"""
        superuser = User.objects.create_superuser(email='test@test.com',
                                                  first_name='test',
                                                  password='test_password')
        self.assertIsInstance(superuser, User)
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)

    def test_failed_superuser_creation(self):
        """Tests that a superuser can't be created with
        is_staff=False or is_superuser=False"""
        with self.assertRaises(ValueError):
            User.objects.create_superuser(email='test@test.com',
                                          first_name='test',
                                          password='test_password',
                                          is_staff=False)
        with self.assertRaises(ValueError):
            User.objects.create_superuser(email='test2@test.com',
                                          first_name='test2',
                                          password='test_password',
                                          is_superuser=False)
