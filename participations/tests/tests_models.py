from django.test import TestCase
from django.db.utils import IntegrityError

from accounts.models import User
from participations.models import Participation
from plannings.models import Event


class ParticipationModelTestCase(TestCase):
    fixtures = ['users', 'plannings']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.participant = User.objects.get(first_name='Participant')
        cls.event = Event.objects.all()[0]

    def test_participation_creation(self):
        args = {
            'participant': self.participant,
            'event': self.event,
            'answer': 'YES'
        }
        participation = Participation.objects.create(**args)
        for key, value in args.items():
            self.assertEqual(getattr(participation, key), value)

    def test_unique_participant_event(self):
        args = {
            'participant': self.participant,
            'event': self.event,
            'answer': 'YES'
        }
        Participation.objects.create(**args)
        args['answer'] = 'NO'
        # Create a second participation with the same event and participant
        with self.assertRaises(IntegrityError):
            Participation.objects.create(**args)
