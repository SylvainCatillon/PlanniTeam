from json import dumps

from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from plannings.models import Planning, Event
from participations.models import Participation


class DisplayViewTestCase(TestCase):
    fixtures = ['users', 'plannings', 'participations']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.planning = Planning.objects.get(name='Test')
        cls.user = User.objects.get(first_name='Participant')
        cls.key = cls.planning.ekey

    def setUp(self):
        self.client.force_login(self.user)

    def test_redirect_if_not_logged(self):
        self.client.logout()
        response = self.client.get(reverse('participations:view', kwargs={
            'planning_ekey': self.key}))
        self.assertRedirects(
            response,
            f'/accounts/login/?next=/participations/view/{self.key}/')

    def test_inexistant_planning(self):
        response = self.client.get(reverse('participations:view', kwargs={
            'planning_ekey': "fakeEkey"}))
        self.assertEqual(response.status_code, 404)

    def test_get_page_by_url(self):
        response = self.client.get(
            f'/participations/view/{self.key}/')
        self.assertEqual(response.status_code, 200)

    def test_get_page_by_name(self):
        response = self.client.get(reverse('participations:view', kwargs={
            'planning_ekey': self.key}))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse('participations:view', kwargs={
            'planning_ekey': self.key}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,
                                'participations/view_planning.html')

    def test_creator_can_access_protected_planning(self):
        creator = User.objects.get(first_name='Creator')
        self.client.force_login(creator)
        response = self.client.get(reverse('participations:view', kwargs={
            'planning_ekey': self.key}))
        self.assertTemplateUsed(response,
                                'participations/view_planning.html')
        self.assertTemplateNotUsed(response,
                                   'participations/protected_planning.html')

    def test_stranger_cannot_access_protected_planning(self):
        stranger = User.objects.get(first_name='Stranger')
        self.client.force_login(stranger)
        response = self.client.get(reverse('participations:view', kwargs={
            'planning_ekey': self.key}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateNotUsed(response,
                                   'participations/view_planning.html')
        self.assertTemplateUsed(response,
                                'participations/protected_planning.html')

    def test_stranger_can_access_unprotected_planning(self):
        stranger = User.objects.get(first_name='Stranger')
        self.client.force_login(stranger)
        self.planning.protected = False
        self.planning.save()
        response = self.client.get(reverse('participations:view', kwargs={
            'planning_ekey': self.key}))
        self.assertTemplateUsed(response,
                                'participations/view_planning.html')
        self.assertTemplateNotUsed(response,
                                   'participations/protected_planning.html')

    def test_participants_in_context(self):
        response = self.client.get(reverse('participations:view', kwargs={
            'planning_ekey': self.key}))
        self.assertEqual(response.status_code, 200)
        events = Event.objects.filter(planning=self.planning)
        other_participants = []
        for user in User.objects.filter(event__in=events)\
                                .order_by('first_name'):
            if user != self.user and user not in other_participants:
                other_participants.append(user)
        self.assertIn('other_participants', response.context.keys())
        self.assertEqual(other_participants,
                         response.context['other_participants'])

    def test_events_in_context(self):
        response = self.client.get(reverse('participations:view', kwargs={
            'planning_ekey': self.key}))
        self.assertEqual(response.status_code, 200)
        self.assertIn('events', response.context)
        context_events = response.context['events']
        for event in Event.objects.filter(planning=self.planning):
            self.assertIn(event, context_events)
        parts_len = len(context_events[0].other_participations)
        for event in context_events:
            # Test the participations list have the same length that
            # for the other events
            self.assertEqual(len(event.other_participations), parts_len)

            # Test all event's participations are in the participations list
            for participation in event.participation_set.exclude(
                    participant=self.user):
                self.assertIn(participation, event.other_participations)

            # Test the current user's participation (or None) is in event
            self.assertEqual(
                event.participation_set.filter(participant=self.user).first(),
                event.user_participation
            )

            # Test a dict with the participations sorted by answers is in event
            for answer in ['YES', 'MAYBE', 'NO']:
                self.assertIn(answer, event.participations_summary.keys())
                for participation in event.participation_set.filter(
                        answer=answer):
                    self.assertIn(participation.participant.first_name,
                                  event.participations_summary[answer])


class ParticipateViewTestCase(TestCase):
    fixtures = ['users', 'plannings']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.events = Planning.objects.get(name='Test').event_set
        cls.user = User.objects.get(first_name='Participant')

    def setUp(self):
        self.client.force_login(self.user)

    def test_post_participate_returns_200(self):
        response = self.client.post(reverse('participations:participate'))
        self.assertEqual(200, response.status_code)

    def test_get_participate_returns_405(self):
        response = self.client.get(reverse('participations:participate'))
        self.assertEqual(405, response.status_code)

    def test_post_un_logged_returns_401(self):
        self.client.logout()
        response = self.client.post(reverse('participations:participate'))
        self.assertEqual(401, response.status_code)

    def test_post_by_stranger_protected_planning(self):
        self.client.force_login(User.objects.get(first_name='Stranger'))
        event = self.events.first()
        participation = {'answer': 'YES', 'event': str(event.pk)}
        response = self.client.post(reverse('participations:participate'),
                                    {'participation': [dumps(participation)]})
        self.assertEqual(403, response.status_code)

    def test_create_one_participation(self):
        event = self.events.first()
        with self.assertRaises(Participation.DoesNotExist):
            Participation.objects.get(participant=self.user, event=event)
        participation = {'answer': 'YES', 'event': str(event.pk)}
        response = self.client.post(reverse('participations:participate'),
                                    {'participation': [dumps(participation)]})
        self.assertEqual(response.status_code, 200)
        created_participation = Participation.objects.get(
            participant=self.user, event=event)
        self.assertEqual(participation['answer'], created_participation.answer)

    def test_update_one_participation(self):
        event = self.events.first()
        existing_participation = Participation.objects.create(
            participant=self.user, event=event, answer='YES')
        self.assertEqual(existing_participation.answer, 'YES')
        participation = {'answer': 'NO', 'event': str(event.pk)}
        response = self.client.post(reverse('participations:participate'),
                                    {'participation': [dumps(participation)]})
        self.assertEqual(response.status_code, 200)
        existing_participation.refresh_from_db()
        self.assertEqual(
            participation['answer'], existing_participation.answer)

    def test_create_two_participation(self):
        event1 = self.events.first()
        event2 = self.events.last()
        with self.assertRaises(Participation.DoesNotExist):
            Participation.objects.get(participant=self.user)
        participations = [{'answer': 'YES', 'event': str(event1.pk)},
                          {'answer': 'NO', 'event': str(event2.pk)}]
        json_participations = [dumps(part) for part in participations]
        response = self.client.post(reverse('participations:participate'),
                                    {'participation': json_participations})
        self.assertEqual(response.status_code, 200)
        for part in participations:
            created_part = Participation.objects.get(
                participant=self.user, event=part['event'])
            self.assertEqual(part['answer'], created_part.answer)

    def test_one_create_and_one_update(self):
        event1 = self.events.first()
        existing_participation = Participation.objects.create(
            participant=self.user, event=event1, answer='YES')
        self.assertEqual(existing_participation.answer, 'YES')
        event2 = self.events.last()
        with self.assertRaises(Participation.DoesNotExist):
            Participation.objects.get(participant=self.user, event=event2)
        participations = [{'answer': 'MAYBE', 'event': str(event1.pk)},
                          {'answer': 'NO', 'event': str(event2.pk)}]
        json_participations = [dumps(part) for part in participations]
        response = self.client.post(reverse('participations:participate'),
                                    {'participation': json_participations})
        self.assertEqual(response.status_code, 200)
        for part in participations:
            created_part = Participation.objects.get(
                participant=self.user, event=part['event'])
            self.assertEqual(part['answer'], created_part.answer)
