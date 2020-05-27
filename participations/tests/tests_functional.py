from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import tag
from django.urls import reverse

from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from accounts.models import User
from participations.models import Participation
from plannings.models import Planning, Event


class TestFunctionalPlanningParticipation(StaticLiveServerTestCase):
    fixtures = ['plannings', 'users', 'participations']

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
        self.user = User.objects.get(first_name='Participant')

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

    @tag('selenium')
    def test_participate(self):
        path = self.live_server_url + reverse('participations:view', kwargs={
            'planning_ekey': self.planning.ekey})
        self.driver.get(path)

        # Prepare the data to be tested: one event with an existing
        # participation, and one without
        event1 = Event.objects.get(pk=1)
        event2 = Event.objects.get(pk=2)
        existing_participation = Participation.objects.get(
            participant=self.user, event=event1)
        with self.assertRaises(Participation.DoesNotExist):
            Participation.objects.get(participant=self.user, event=event2)
        old_answer = existing_participation.answer
        answer1 = 'NO'
        answer2 = 'YES'
        self.assertNotEqual(answer1, old_answer)

        # Submit new answers for the two events
        self.driver.find_element_by_id('DropAnswerEvent1').click()
        radio = WebDriverWait(self.driver, 15).until(
            EC.presence_of_element_located((By.ID, "Answer"+answer1+"Event1"))
        )
        radio.click()
        self.driver.find_element_by_id('DropAnswerEvent2').click()
        radio = WebDriverWait(self.driver, 15).until(
            EC.presence_of_element_located((By.ID, "Answer"+answer2+"Event2"))
        )
        radio.click()
        self.driver.find_element_by_id('submit_answers').click()

        # Assert the answer of the user for the first event has changed,
        # and the second event got a new participation
        existing_participation.refresh_from_db()
        new_answer = existing_participation.answer
        self.assertNotEqual(old_answer, new_answer)
        self.assertEqual(answer1, new_answer)
        created_participation = Participation.objects.get(
            participant=self.user, event=event2)
        self.assertEqual(answer2, created_participation.answer)
