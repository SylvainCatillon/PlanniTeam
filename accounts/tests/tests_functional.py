from django.contrib.auth import get_user_model
from django.test import LiveServerTestCase
from django.urls import reverse
from django.conf import settings

from selenium.webdriver.firefox.webdriver import WebDriver


class TestFunctionalAccounts(LiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.driver = WebDriver()
        cls.driver.implicitly_wait(15)
        cls.user_info = {
            "email": "user@test.com",
            "password": "test_user_password",
            "first_name": "Test"}

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super().tearDownClass()

    def test_create_account(self):
        self.driver.get(self.live_server_url + reverse("accounts:create"))
        username = self.driver.find_element_by_name("email")
        username.send_keys(self.user_info["email"])
        username = self.driver.find_element_by_name("first_name")
        username.send_keys(self.user_info["first_name"])
        password1 = self.driver.find_element_by_name("password1")
        password1.send_keys(self.user_info["password"])
        password2 = self.driver.find_element_by_name("password2")
        password2.send_keys(self.user_info["password"])
        self.driver.find_element_by_xpath(
            "//input[@type='submit']").click()

        redirect_url = self.live_server_url + settings.LOGIN_REDIRECT_URL
        self.assertURLEqual(redirect_url, self.driver.current_url)
        body = self.driver.find_element_by_tag_name('body')
        self.assertIn(self.user_info['first_name'], body.text)

    def tests_login(self):
        user = get_user_model().objects.create_user(**self.user_info)

        self.driver.get(self.live_server_url+reverse("accounts:login"))
        username = self.driver.find_element_by_name("username")
        username.send_keys(self.user_info["email"])
        password = self.driver.find_element_by_name("password")
        password.send_keys(self.user_info["password"])
        self.driver.find_element_by_xpath(
            "//input[@type='submit']").click()

        redirect_url = self.live_server_url + settings.LOGIN_REDIRECT_URL
        self.assertURLEqual(redirect_url, self.driver.current_url)
        body = self.driver.find_element_by_tag_name('body')
        self.assertIn(self.user_info['first_name'], body.text)

