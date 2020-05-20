from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import tag
from django.urls import reverse

from selenium.webdriver.firefox.webdriver import WebDriver

from accounts.models import User
from accounts.tests.utils import log_user_in
from plannings.models import Planning


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
