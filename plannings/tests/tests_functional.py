from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import tag
from django.urls import reverse

from selenium.webdriver.firefox.webdriver import WebDriver

from accounts.models import User
from plannings.models import Planning


class TestFunctionalPlanningCreation(StaticLiveServerTestCase):
    fixtures = ['users']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # FIXME bug sur la fixture
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
            self.user)  # TODO: Créer une fonction login dans utils
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
        submit = self.driver.find_element_by_xpath(
            "//form[@id='planning_form']//input[@type='submit']")
        submit.click()
        self.assertIn('created', self.driver.current_url)
        self.assertTrue(self.user.planning_created.count())
        # TODO: verifier le planning avec l'ekey si elle est
        #  transmise en argument dans le lien

    @tag('selenium')
    def test_create_maximal_planning(self):
        self.assertFalse(self.user.planning_created.count())
        planning_name = 'Test'
        guest_email = 'guest@test.com'
        event_data = {'date': '2020-01-01',
                      'time': '12:12:00',
                      'description': 'This is a description',
                      'address': '2 boulevard something, 75003 Paris'}
        prefix = 'id_event_set-__prefix__-'
        name_list = ['id_name', 'id_protected', 'add_guest_input',
                     'add_guest_submit']
        for name in ['event_dropdown', 'date', 'time', 'description',
                     'address', 'validate']:
            name_list.append(prefix+name)
        self.driver.get(self.path)

        elms = [self.driver.find_element_by_id(name) for name in name_list]

        elms[0].send_keys(planning_name)
        elms[1].click()
        elms[2].send_keys(guest_email)
        elms[3].click()
        elms[4].click()
        elms[5].send_keys(event_data['date'])
        elms[6].send_keys(event_data['time'])
        elms[7].send_keys(event_data['description'])
        elms[8].send_keys(event_data['address']) # Todo: factoriser
        elms[9].click()

        submit = self.driver.find_element_by_xpath(
            "//form[@id='planning_form']//input[@type='submit']")
        submit.click()

        # Test if the user is redirected and a planning is created
        self.assertIn('created', self.driver.current_url)
        self.assertTrue(self.user.planning_created.count())

        # Test if the planning has the correct data
        planning = Planning.objects.get(name=planning_name)
        self.assertIn(guest_email, planning.get_guest_emails)
        event = planning.event_set.first()
        for key, value in event_data.items():
            self.assertEqual(value, str(getattr(event, key)))
