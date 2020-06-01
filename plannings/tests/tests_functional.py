from datetime import timedelta, date, time

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import tag
from django.urls import reverse

from selenium.webdriver.firefox.webdriver import WebDriver

from accounts.models import User
from accounts.tests.utils import log_user_in
from plannings.models import Planning, Event


class TestFunctionalPlanningCreation(StaticLiveServerTestCase):
    fixtures = ['users']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # FIXME bug sur la fixture
        cls.selenium = WebDriver()
        cls.selenium.implicitly_wait(15)


    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def setUp(self):
        self.user = log_user_in(self.selenium, self.live_server_url)

    # Todo réessayer cette facon de login
    # def setUp(self):
    #     session_cookie = create_session_cookie(self.user)
    #     self.selenium.get(self.live_server_url + '/404doesntexist/')
    #     self.selenium.add_cookie(session_cookie)
    #     self.selenium.refresh()

    @tag('selenium')
    def test_create_minimal_planning(self):
        self.assertFalse(self.user.planning_created.count())
        path = self.live_server_url + reverse('plannings:create')
        self.selenium.get(path)
        field = self.selenium.find_element_by_xpath(
            "//form[@id='planning_form']//input[@name='name']")
        field.send_keys('Test')
        button = self.selenium.find_element_by_xpath(
            "//input[@type='submit'][@form='planning_form']")
        button.click()
        self.assertIn('created', self.selenium.current_url)
        self.assertTrue(self.user.planning_created.count())
        # TODO: verifier le planning avec l'ekey si elle est
        #  transmise en argument dans le lien

    @tag('selenium')
    def test_create_maximal_planning(self):
        self.assertFalse(self.user.planning_created.count())
        driver = self.selenium
        elms = {}
        name_list = ['id_name', 'id_protected', 'guest_email', 'guest_submit',
                     'event_dropdown', 'id_date', 'id_time', 'id_description',
                     'id_address', 'event_submit', 'planning_submit']
        path = self.live_server_url + reverse('plannings:create')
        self.selenium.get(path)
        for name in name_list:
            elms[name] = driver.find_element_by_id(name)

        elms['id_name'].send_keys('Test')
        elms['id_protected'].click()
        elms['guest_email'].send_keys('guest@test.com')
        elms['guest_submit'].click()
        elms['event_dropdown'].click()
        elms['id_date'].send_keys('2020-01-01')
        elms['id_time'].send_keys('12:12')
        elms['id_description'].send_keys('This is a description')
        elms['id_address'].send_keys("2 boulevard something, 75003 Paris")
        elms['event_submit'].click()
        elms['planning_submit'].click()

        self.assertIn('created', self.selenium.current_url)
        self.assertTrue(self.user.planning_created.count())
        # TODO: verifier le planning avec l'ekey si elle est
        #  transmise en argument dans le lien


class TestFunctionalPlanningEdition(StaticLiveServerTestCase):
    fixtures = ['plannings', 'users']

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
        self.client.force_login(self.user)  # TODO: Créer une fonction login dans utils
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
        for elem in ['date', 'time']:
            send_attrs[elem] = send_attrs[elem].isoformat()
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
        # TODO: tester contenu de la carte

        # Delete the second event
        self.driver.find_element_by_id(
            event2_prefix + 'event_dropdown').click()
        self.driver.find_element_by_id(event2_prefix + 'DELETE').click()
        self.driver.find_element_by_id(event2_prefix + 'validate').click()
        # TODO: tester contenu de la carte

        # Send the form
        self.driver.find_element_by_id('planning_submit').click()

        # Test the first event modification, and the second event deletion
        event1.refresh_from_db()
        for key, value in new_attrs.items():
            self.assertEqual(value, getattr(event1, key))
        self.assertEqual(old_count-1, self.planning.event_set.count())

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
        # TODO: tester contenu de la carte
        # TODO: tester reset add form

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
        add_input = self.driver.find_element_by_id('guest_email')
        add_submit = self.driver.find_element_by_id('guest_submit')
        for email in [email_to_add, email_to_add_then_delete]:
            add_input.send_keys(email)
            add_submit.click()
        # Delete some emails
        self.driver.find_element_by_id("DeleteGuestDropdown").click()
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
