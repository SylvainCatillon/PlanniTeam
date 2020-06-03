from django.test import TestCase

from accounts.models import User
from plannings.models import Planning, GuestEmail
from plannings.utils import update_guests, add_guests


class PlanningsUtilsTestCase(TestCase):
    fixtures = ['users', 'plannings']

    def test_update_guests(self):
        planning = Planning.objects.first()
        guests = planning.get_guest_emails
        guest_to_delete = guests.pop(0)
        guest_to_add = 'newguest@test.com'
        guests.append(guest_to_add)

        self.assertIn(guest_to_delete, planning.get_guest_emails)
        self.assertNotIn(guest_to_add, planning.get_guest_emails)

        update_guests(planning, guests)
        updated_guests = planning.get_guest_emails
        self.assertNotIn(guest_to_delete, updated_guests)
        self.assertIn(guest_to_add, updated_guests)

    def test_add_guests(self):
        creator = User.objects.get(first_name='Creator')
        planning = Planning.objects.create(
            name="TestAddGuests", creator=creator, protected=True)
        self.assertFalse(len(planning.get_guest_emails))
        guests = ["guest1@test.com", "guest2@test.com"]
        guests.append(GuestEmail.objects.first().email)

        add_guests(planning, guests)
        planning_guests = planning.get_guest_emails
        for guest in guests:
            self.assertIn(guest, planning_guests)
