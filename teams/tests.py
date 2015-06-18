import random
import string

from django.db.utils import IntegrityError
from django.test import TestCase

from teams.models import Team


def randomword(length=10):
    return ''.join(random.choice(string.ascii_lowercase) for i in range(length))


def make_phony_team():
    t = Team()
    t.full_name = randomword()
    t.three_letter_name = randomword(length=3)
    try:
        t.save()
    except IntegrityError:
        # keep trying in case we generate the same name/ 3 letter
        return make_phony_team()
    return t

# Create your tests here.
class TestTeams(TestCase):

    def test_uppercase_abbreviation_on_save(self):

        t = Team()
        t.full_name = 'United States of America'
        t.three_letter_name = 'usa'
        t.save()
        self.assertEqual(t.three_letter_name, 'USA')

    def test_make_phony_team(self):

        # just make sure we're making a valid model
        make_phony_team()
