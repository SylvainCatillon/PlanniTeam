from datetime import timedelta, date, time

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import tag
from django.urls import reverse

from selenium.webdriver.firefox.webdriver import WebDriver

from accounts.models import User
from plannings.models import Planning, Event


class TestFunctionalPlanningCreation(StaticLiveServerTestCase):
    fixtures = ['users']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.driver = WebDriver()
        cls.driver.implicitly_wait(15)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super().tearDownClass()

    def setUp(self):
        self.user = User.objects.get(first_name='Creator')
        self.path = self.live_server_url + reverse('plannings:create')

        # Set the cookies to fake a user login
        self.client.force_login(
            self.user)
        cookie = self.client.cookies['sessionid']
        # 404 page are the quickest to load
        self.driver.get(
            self.live_server_url + '/404doesntexist/')
        self.driver.add_cookie(
            {'name': 'sessionid', 'value': cookie.value, 'secure': False,
             'path': '/'})
        self.driver.refresh()

    @tag('selenium')
    def test_create_minimal_planning(self):
        self.assertFalse(self.user.planning_created.count())
        self.driver.get(self.path)
        field = self.driver.find_element_by_xpath(
            "//form[@id='planning_form']//input[@name='name']")
        field.send_keys('Test')
        self.driver.find_element_by_id('planning_submit').click()

        self.assertIn('created', self.driver.current_url)
        self.assertTrue(self.user.planning_created.count())

    @tag('selenium')
    def test_create_maximal_planning(self):
        self.assertFalse(self.user.planning_created.count())
        planning_name = 'Test'
        guest_email = 'guest@test.com'
        event_data = {'date': date(2020, 1, 1),
                      'time': time(20, 30),
                      'description': 'This is a description',
                      'address': '2 boulevard something, 75003 Paris'}
        event_fields = dict(event_data)
        event_fields['date'] = event_fields['date'].strftime('%Y-%m-%d')
        event_fields['time'] = event_fields['time'].strftime('%H:%M')
        prefix = 'id_event_set-__prefix__-'
        name_list = [
            'id_name', 'id_protected', 'add_guest_input',
            'add_guest_submit', prefix + 'event_dropdown', prefix + 'validate'
        ]
        self.driver.get(self.path)

        elms = [self.driver.find_element_by_id(name) for name in name_list]

        elms[0].send_keys(planning_name)
        elms[1].click()
        elms[2].send_keys(guest_email)
        elms[3].click()
        elms[4].click()
        for field, data in event_fields.items():
            elm = self.driver.find_element_by_id(prefix + field)
            elm.send_keys(data)
        elms[5].click()

        self.driver.find_element_by_id('planning_submit').click()

        # Test if the user is redirected and a planning is created
        self.assertIn('created', self.driver.current_url)
        self.assertTrue(self.user.planning_created.count())

        # Test if the planning has the correct data
        planning = Planning.objects.get(name=planning_name)
        self.assertIn(guest_email, planning.get_guest_emails)
        event = planning.event_set.first()
        for key, value in event_data.items():
            self.assertEqual(value, getattr(event, key))


class TestFunctionalPlanningEdition(StaticLiveServerTestCase):
    fixtures = ['users', 'plannings']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.driver = WebDriver()
        cls.driver.implicitly_wait(15)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super().tearDownClass()

    def setUp(self):
        self.planning = Planning.objects.first()
        self.user = User.objects.get(first_name='Creator')
        self.path = self.live_server_url + reverse('plannings:edit', kwargs={
            'planning_ekey': self.planning.ekey})

        # Set the cookies to fake a user login
        self.client.force_login(self.user)
        cookie = self.client.cookies['sessionid']
        # 404 page are the quickest to load
        self.driver.get(
            self.live_server_url + '/404doesntexist/')
        self.driver.add_cookie(
            {'name': 'sessionid', 'value': cookie.value, 'secure': False,
             'path': '/'})
        self.driver.refresh()

    def add_event(self, attrs):
        """
        Add a new event on the edit page. Take a dict of attrs as argument.
        """
        new_event_prefix = "id_event_set-__prefix__-"
        new_event_dropdown = self.driver.find_element_by_id(
            new_event_prefix + 'event_dropdown')
        new_event_validate = self.driver.find_element_by_id(
            new_event_prefix + 'validate')

        new_event_dropdown.click()
        for key, value in attrs.items():
            elem = self.driver.find_element_by_id(new_event_prefix + key)
            elem.send_keys(value)
        new_event_validate.click()

    @tag('selenium')
    def test_modify_events(self):
        # Set the elements of test
        old_count = self.planning.event_set.count()
        event1 = self.planning.event_set.first()
        new_attrs = {
            'date': event1.date+timedelta(1),
            'time': event1.time.replace(minute=event1.time.minute+1),
            'description': event1.description+'TEST',
            'address': event1.address+'TEST'
        }
        send_attrs = dict(new_attrs)
        send_attrs['date'] = send_attrs['date'].strftime('%Y-%m-%d')
        send_attrs['time'] = send_attrs['time'].strftime('%H:%M')
        event1_prefix = "id_event_set-0-"
        event2_prefix = "id_event_set-1-"

        for key, value in new_attrs.items():
            self.assertNotEqual(value, getattr(event1, key))

        self.driver.get(self.path)

        # Modify the first event
        self.driver.find_element_by_id(
            event1_prefix + 'event_dropdown').click()
        for key, value in send_attrs.items():
            elem = self.driver.find_element_by_id(event1_prefix + key)
            elem.clear()
            elem.send_keys(value)
        self.driver.find_element_by_id(event1_prefix + 'validate').click()

        # Delete the second event
        self.driver.find_element_by_id(
            event2_prefix + 'event_dropdown').click()
        self.driver.find_element_by_id(event2_prefix + 'DELETE').click()
        self.driver.find_element_by_id(event2_prefix + 'validate').click()

        # Send the form
        self.driver.find_element_by_id('planning_submit').click()

        # Test the first event modification, and the second event deletion
        event1.refresh_from_db()
        for key, value in new_attrs.items():
            self.assertEqual(value, getattr(event1, key))
        self.assertEqual(old_count-1, self.planning.event_set.count())

    @tag('selenium')
    def test_unvalidated_modifications_are_not_saved(self):
        # Set the elements of test
        event = self.planning.event_set.first()
        new_attrs = {
            'date': event.date + timedelta(1),
            'time': event.time.replace(minute=event.time.minute + 1),
            'description': event.description + 'TEST',
            'address': event.address + 'TEST'
        }
        send_attrs = dict(new_attrs)
        send_attrs['date'] = send_attrs['date'].strftime('%Y-%m-%d')
        send_attrs['time'] = send_attrs['time'].strftime('%H:%M')
        event_prefix = "id_event_set-0-"

        self.driver.get(self.path)

        # Modify the first event but don't click on 'validate'
        self.driver.find_element_by_id(
            event_prefix + 'event_dropdown').click()
        for key, value in send_attrs.items():
            elem = self.driver.find_element_by_id(event_prefix + key)
            elem.clear()
            elem.send_keys(value)

        # Send the form
        self.driver.find_element_by_id('planning_submit').click()

        # Test the event data haven't changed
        event.refresh_from_db()
        for key, value in new_attrs.items():
            self.assertNotEqual(value, getattr(event, key))

    @tag('selenium')
    def test_add_events(self):
        old_count = self.planning.event_set.count()
        event1_attrs = {
            'date': '2020-02-02',
            'time': '05:05',
            'description': 'test description',
            'address': 'test address'
        }
        event2_date = '2020-03-03'
        event3_date = '2020-04-04'
        event3_modified_description = 'Modified descripiton'

        self.driver.get(self.path)

        # Add event1
        self.add_event(event1_attrs)

        # Add event2 then modify it
        self.add_event({'date': event2_date})

        total_forms = self.driver.find_element_by_id(
            "id_event_set-TOTAL_FORMS").get_attribute('value')
        created_event_prefix = "id_event_set-" + str(int(total_forms)-1) + "-"
        self.driver.find_element_by_id(
            created_event_prefix + 'event_dropdown').click()
        self.driver.find_element_by_id(
            created_event_prefix + 'DELETE').click()
        self.driver.find_element_by_id(
            created_event_prefix + 'validate').click()

        # Add event3 then delete it
        self.add_event({'date': event3_date})

        total_forms = self.driver.find_element_by_id(
            "id_event_set-TOTAL_FORMS").get_attribute('value')
        created_event_prefix = "id_event_set-" + str(int(total_forms)-1) + "-"
        self.driver.find_element_by_id(
            created_event_prefix + 'event_dropdown').click()
        self.driver.find_element_by_id(
            created_event_prefix + 'description').send_keys(
                event3_modified_description)
        self.driver.find_element_by_id(
            created_event_prefix + 'validate').click()

        # Send the form
        self.driver.find_element_by_id('planning_submit').click()

        self.assertEqual(old_count + 2, self.planning.event_set.count())

        # Test event1 is created
        event1 = self.planning.event_set.get(date=event1_attrs['date'])
        self.assertEqual(event1_attrs['description'], event1.description)
        self.assertEqual(event1_attrs['address'], event1.address)

        # Test event2 isn't created
        with self.assertRaises(Event.DoesNotExist):
            self.planning.event_set.get(date=event2_date)

        # Test event3 is created with the modified description
        event3 = self.planning.event_set.get(date=event3_date)
        self.assertEqual(event3_modified_description, event3.description)

    @tag('selenium')
    def test_modify_guests(self):
        # Set the test data
        old_guests = self.planning.get_guest_emails
        email_to_delete = old_guests[0]
        email_to_add = 'newparticipant@test.com'
        email_to_add_then_delete = 'fail@test.com'

        self.driver.get(self.path)

        # Add some emails
        add_input = self.driver.find_element_by_id('add_guest_input')
        add_submit = self.driver.find_element_by_id('add_guest_submit')
        for email in [email_to_add, email_to_add_then_delete]:
            add_input.send_keys(email)
            add_submit.click()
        # Delete some emails
        self.driver.find_element_by_id("delete_guest_dropdown").click()
        for email in [email_to_delete, email_to_add_then_delete]:
            self.driver.find_element_by_xpath(
                "//option[@value='" + email + "']").click()
        self.driver.find_element_by_id("delete_guest_submit").click()
        # Send the form
        self.driver.find_element_by_id("planning_submit").click()

        # Test the result
        new_guests = self.planning.get_guest_emails
        self.assertNotIn(email_to_delete, new_guests)
        self.assertNotIn(email_to_add_then_delete, new_guests)
        self.assertIn(email_to_add, new_guests)
