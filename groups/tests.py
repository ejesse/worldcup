from collections import OrderedDict
from random import randint

from django.core.exceptions import ValidationError
from django.test import TestCase

from groups.models import Group, Fixture, ComparableTeam
from teams.tests import make_phony_team


def make_phony_group():

    team1 = make_phony_team()
    team2 = make_phony_team()
    team3 = make_phony_team()
    team4 = make_phony_team()

    group = Group()
    group.group_letter = 'A'
    group.save()

    group.teams = [team1, team2, team3, team4]

    fixture = Fixture()
    fixture.home_team = team1
    fixture.away_team = team2
    fixture.save()
    group.fixtures.add(fixture)

    fixture = Fixture()
    fixture.home_team = team3
    fixture.away_team = team4
    fixture.save()
    group.fixtures.add(fixture)

    fixture = Fixture()
    fixture.home_team = team1
    fixture.away_team = team3
    fixture.save()
    group.fixtures.add(fixture)

    fixture = Fixture()
    fixture.home_team = team2
    fixture.away_team = team4
    fixture.save()
    group.fixtures.add(fixture)

    fixture = Fixture()
    fixture.home_team = team1
    fixture.away_team = team4
    fixture.save()
    group.fixtures.add(fixture)

    fixture = Fixture()
    fixture.home_team = team2
    fixture.away_team = team3
    fixture.save()
    group.fixtures.add(fixture)

    group.save()
    return group


def make_results(group):

    fixtures = group.fixtures.all()

    fixture1 = fixtures[0]
    fixture1.home_team_score = randint(0,4) #team1
    fixture1.away_team_score = randint(0,4) #team2
    fixture1.save()

    fixture2 = fixtures[1]
    fixture2.home_team_score = randint(0,4) #team3
    fixture2.away_team_score = randint(0,4) #team4
    fixture2.save()

    fixture3 = fixtures[2]
    fixture3.home_team_score = randint(0,4) #team1
    fixture3.away_team_score = randint(0,4) #team3
    fixture3.save()

    fixture4 = fixtures[3]
    fixture4.home_team_score = randint(0,4) #team2
    fixture4.away_team_score = randint(0,4) #team4
    fixture4.save()

    fixture5 = fixtures[4]
    fixture5.home_team_score = randint(0,4) #team1
    fixture5.away_team_score = randint(0,4) #team4
    fixture5.save()

    fixture6 = fixtures[5]
    fixture6.home_team_score = randint(0,4) #team2
    fixture6.away_team_score = randint(0,4) #team3
    fixture6.save()


class TestFixtures(TestCase):

    def test_valid_scoring(self):

        team1 = make_phony_team()
        team2 = make_phony_team()

        fixture = Fixture()
        fixture.home_team = team1
        fixture.away_team = team2
        fixture.home_team_score = 2
        self.assertRaises(ValidationError, fixture.save)
        fixture.home_team_score = None
        fixture.away_team_score = 1
        self.assertRaises(ValidationError, fixture.save)

    def test_team_cannot_play_itself(self):

        team1 = make_phony_team()

        fixture = Fixture()
        fixture.home_team = team1
        fixture.away_team = team1
        self.assertRaises(ValidationError, fixture.save)

    def test_team_in_fixture(self):

        team1 = make_phony_team()
        team2 = make_phony_team()
        team3 = make_phony_team()

        fixture = Fixture()
        fixture.home_team = team1
        fixture.away_team = team2
        fixture.save()

        self.assertTrue(fixture.team_in_fixture(team1))
        self.assertTrue(fixture.team_in_fixture(team2))
        self.assertFalse(fixture.team_in_fixture(team3))

    def test_get_result_for_team(self):

        team1 = make_phony_team()
        team2 = make_phony_team()
        team3 = make_phony_team()

        fixture = Fixture()
        fixture.home_team = team1
        fixture.away_team = team2
        fixture.home_team_score = 2
        fixture.away_team_score = 0
        fixture.save()

        self.assertRaises(ValueError, fixture.get_result_for_team, team3)
        self.assertEqual(fixture.get_result_for_team(team1), Fixture.WIN)
        self.assertEqual(fixture.get_result_for_team(team2), Fixture.LOSS)

        fixture.home_team_score = 1
        fixture.away_team_score = 1
        fixture.save()

        self.assertEqual(fixture.get_result_for_team(team1), Fixture.DRAW)
        self.assertEqual(fixture.get_result_for_team(team2), Fixture.DRAW)

        fixture.home_team_score = None
        fixture.away_team_score = None
        fixture.save()

        self.assertEqual(fixture.get_result_for_team(team1), None)
        self.assertEqual(fixture.get_result_for_team(team2), None)

    def test_get_points_for_team(self):

        team1 = make_phony_team()
        team2 = make_phony_team()
        team3 = make_phony_team()

        fixture = Fixture()
        fixture.home_team = team1
        fixture.away_team = team2
        fixture.home_team_score = 2
        fixture.away_team_score = 0
        fixture.save()

        self.assertRaises(ValueError, fixture.get_result_for_team, team3)
        self.assertEqual(fixture.get_points_for_team(team1), 3)
        self.assertEqual(fixture.get_points_for_team(team2), 0)

        self.assertRaises(ValueError, fixture.get_result_for_team, team3)
        self.assertEqual(fixture.get_points_for_team(team1, win=2), 2)
        self.assertEqual(fixture.get_points_for_team(team2), 0)

        fixture.home_team_score = 1
        fixture.away_team_score = 1
        fixture.save()

        self.assertEqual(fixture.get_points_for_team(team1), 1)
        self.assertEqual(fixture.get_points_for_team(team2, draw=2), 2)

        fixture.home_team_score = None
        fixture.away_team_score = None
        fixture.save()

        self.assertEqual(fixture.get_points_for_team(team1), 0)
        self.assertEqual(fixture.get_points_for_team(team2), 0)


class TestGroups(TestCase):

    def test_group_size_restriction(self):

        group = Group()
        group.group_letter = 'A'

        teams = []

        for i in range(0,6):
            teams.append(make_phony_team())

        group.save()
        group.teams = teams

        self.assertRaises(ValidationError, group.save)

        teams = []

        for i in range(0,3):
            teams.append(make_phony_team())

        group.teams = teams

        self.assertRaises(ValidationError, group.save)

        teams = []

        for i in range(0,4):
            teams.append(make_phony_team())

        group.teams = teams

    def test_get_fixtures_for_team(self):

        group = make_phony_group()
        team = group.teams.all()[0]
        all_fixtures = group.fixtures.all()
        team_fixtures = group.get_fixtures_for_team(team)
        self.assertEqual(len(team_fixtures), 3)
        for tf in team_fixtures:
            self.assertTrue(tf.team_in_fixture(team))


    def test_points_for_team(self):

        group = make_phony_group()

        team5 = make_phony_team()

        # make sure we raise for points for a team not in group
        self.assertRaises(ValueError, group.get_points_for_team, team5)

        fixtures = group.fixtures.all()

        fixture1 = fixtures[0]
        fixture1.home_team_score = 1
        fixture1.away_team_score = 0
        fixture1.save()

        fixture2 = fixtures[1]
        fixture2.home_team_score = 0
        fixture2.away_team_score = 0
        fixture2.save()

        fixture3 = fixtures[2]
        fixture3.home_team_score = 0
        fixture3.away_team_score = 0
        fixture3.save()

        fixture4 = fixtures[3]
        fixture4.home_team_score = 0
        fixture4.away_team_score = 0
        fixture4.save()

        self.assertEqual(group.get_points_for_team(fixture1.home_team), 4)
        self.assertEqual(group.get_points_for_team(fixture1.away_team), 1)

        self.assertEqual(group.get_points_for_team(fixture2.home_team), 2)
        self.assertEqual(group.get_points_for_team(fixture2.away_team), 2)


    def test_get_goal_differential_for_team(self):

        group = make_phony_group()

        fixtures = group.fixtures.all()

        make_results(group)

        team1gd = (fixtures[0].home_team_score - fixtures[0].away_team_score) + \
            (fixtures[2].home_team_score - fixtures[2].away_team_score) + \
            (fixtures[4].home_team_score - fixtures[4].away_team_score)

        team2gd = (fixtures[0].away_team_score - fixtures[0].home_team_score) + \
            (fixtures[3].home_team_score - fixtures[3].away_team_score) + \
            (fixtures[5].home_team_score - fixtures[5].away_team_score)

        team3gd = (fixtures[1].home_team_score - fixtures[1].away_team_score) + \
            (fixtures[2].away_team_score - fixtures[2].home_team_score) + \
            (fixtures[5].away_team_score - fixtures[5].home_team_score)

        team4gd = (fixtures[1].away_team_score - fixtures[1].home_team_score) + \
            (fixtures[3].away_team_score - fixtures[3].home_team_score) + \
            (fixtures[4].away_team_score - fixtures[4].home_team_score)


        self.assertEqual(group.get_goal_differential_for_team(fixtures[0].home_team), team1gd)
        self.assertEqual(group.get_goal_differential_for_team(fixtures[0].away_team), team2gd)
        self.assertEqual(group.get_goal_differential_for_team(fixtures[1].home_team), team3gd)
        self.assertEqual(group.get_goal_differential_for_team(fixtures[1].away_team), team4gd)


    def test_get_head_to_head_goal_differential(self):

        group = make_phony_group()

        fixture1 = group.fixtures.all()[0]

        team1 = fixture1.home_team
        team2 = fixture1.away_team

        fixture1.home_team_score = randint(0,4)
        fixture1.away_team_score = randint(0,4)
        fixture1.save()

        self.assertEqual(group.get_head_to_head_goal_differential(team1, team2), fixture1.home_team_score - fixture1.away_team_score)
        self.assertEqual(group.get_head_to_head_goal_differential(team2, team1), fixture1.away_team_score - fixture1.home_team_score)

        # tests support for home and home round robin
        fixture2 = Fixture()
        fixture2.home_team = team2
        fixture2.away_team = team1
        fixture2.home_team_score = randint(0,4)
        fixture2.away_team_score = randint(0,4)
        fixture2.save()

        group.fixtures.add(fixture2)

        self.assertEqual(group.get_head_to_head_goal_differential(team1, team2), ((fixture1.home_team_score - fixture1.away_team_score) + (fixture2.away_team_score - fixture2.home_team_score)))
        self.assertEqual(group.get_head_to_head_goal_differential(team2, team1), ((fixture1.away_team_score - fixture1.home_team_score) + (fixture2.home_team_score - fixture2.away_team_score)))

    def test_get_goals_for_team(self):

        group = make_phony_group()

        fixtures = group.fixtures.all()

        make_results(group)

        team = fixtures[0].home_team

        self.assertEqual(group.get_goals_for_team(team), fixtures[0].home_team_score + fixtures[2].home_team_score + fixtures[4].home_team_score)

    def test_check_teams_in_group(self):

        group = make_phony_group()

        team1 = make_phony_team()
        team2 = make_phony_team()

        self.assertRaises(ValueError, group.check_teams_in_group, [group.teams.all()[1], team1, team2])

    def test_get_counted_fixtures_from_subset(self):

        group = make_phony_group()

        fixtures = group.fixtures.all()

        make_results(group)

        team1 = fixtures[0].home_team
        team2 = fixtures[0].away_team
        team3 = fixtures[2].away_team
        team1_points = 0
        team2_points = 0
        team3_points = 0

        # the way make_phony_group works we are looking at:
        # (commented code is for reference!!!)
        #fixtures[0].home_team_score = randint(0,4) #team1
        #fixtures[0].away_team_score = randint(0,4) #team2
        #fixtures[2].home_team_score = randint(0,4) #team1
        #fixtures[2].away_team_score = randint(0,4) #team3
        #fixtures[5].home_team_score = randint(0,4) #team2
        #fixtures[5].away_team_score = randint(0,4) #team3

        self.assertTrue(fixtures[0] in group.get_counted_fixtures_from_subset(team1, [team2, team3]))
        self.assertTrue(fixtures[2] in group.get_counted_fixtures_from_subset(team1, [team2, team3]))
        self.assertTrue(fixtures[0] in group.get_counted_fixtures_from_subset(team2, [team3, team1]))
        self.assertTrue(fixtures[5] in group.get_counted_fixtures_from_subset(team2, [team1, team3]))
        self.assertTrue(fixtures[2] in group.get_counted_fixtures_from_subset(team3, [team2, team1]))
        self.assertTrue(fixtures[5] in group.get_counted_fixtures_from_subset(team3, [team1, team3]))

    def test_get_points_for_team_from_subset(self):

        group = make_phony_group()

        fixtures = group.fixtures.all()

        make_results(group)

        team1 = fixtures[0].home_team
        team2 = fixtures[0].away_team
        team3 = fixtures[2].away_team
        team1_points = 0
        team2_points = 0
        team3_points = 0

        # the way make_phony_group works we are looking at:
        # (commented code is for reference!!!)
        #fixture1.home_team_score = randint(0,4) #team1
        #fixture1.away_team_score = randint(0,4) #team2
        #fixture3.home_team_score = randint(0,4) #team1
        #fixture3.away_team_score = randint(0,4) #team3
        #fixture6.home_team_score = randint(0,4) #team2
        #fixture6.away_team_score = randint(0,4) #team3

        #team1
        if fixtures[0].home_team_score > fixtures[0].away_team_score:
            team1_points = team1_points + 3
        elif fixtures[0].home_team_score == fixtures[0].away_team_score:
            team1_points = team1_points + 1
        if fixtures[2].home_team_score > fixtures[2].away_team_score:
            team1_points = team1_points + 3
        elif fixtures[2].home_team_score == fixtures[2].away_team_score:
            team1_points = team1_points + 1

        #team2
        if fixtures[0].home_team_score < fixtures[0].away_team_score:
            team2_points = team2_points + 3
        elif fixtures[0].home_team_score == fixtures[0].away_team_score:
            team2_points = team2_points + 1
        if fixtures[5].home_team_score > fixtures[5].away_team_score:
            team2_points = team2_points + 3
        elif fixtures[5].home_team_score == fixtures[5].away_team_score:
            team2_points = team2_points + 1

        #team3
        if fixtures[2].home_team_score < fixtures[2].away_team_score:
            team3_points = team3_points + 3
        elif fixtures[2].home_team_score == fixtures[2].away_team_score:
            team3_points = team3_points + 1
        if fixtures[5].home_team_score < fixtures[5].away_team_score:
            team3_points = team3_points + 3
        elif fixtures[5].home_team_score == fixtures[5].away_team_score:
            team3_points = team3_points + 1

        self.assertEqual(group.get_points_for_team_from_subset(team1, [team2, team3]), team1_points)
        self.assertEqual(group.get_points_for_team_from_subset(team2, [team1, team3]), team2_points)
        self.assertEqual(group.get_points_for_team_from_subset(team3, [team1, team2]), team3_points)

    def test_get_goal_differential_for_team_from_subset(self):
        group = make_phony_group()

        fixtures = group.fixtures.all()

        make_results(group)

        team1 = fixtures[0].home_team
        team2 = fixtures[0].away_team
        team3 = fixtures[2].away_team
        team1_gd = 0
        team2_gd = 0
        team3_gd = 0

        # the way make_phony_group works we are looking at:
        # (commented code is for reference!!!)
        #fixtures[0].home_team_score = randint(0,4) #team1
        #fixtures[0].away_team_score = randint(0,4) #team2
        #fixtures[2].home_team_score = randint(0,4) #team1
        #fixtures[2].away_team_score = randint(0,4) #team3
        #fixtures[5].home_team_score = randint(0,4) #team2
        #fixtures[5].away_team_score = randint(0,4) #team3

        #team1
        team1_gd = team1_gd + (fixtures[0].home_team_score - fixtures[0].away_team_score)
        team1_gd = team1_gd + (fixtures[2].home_team_score - fixtures[2].away_team_score)

        #team2
        team2_gd = team2_gd + (fixtures[0].away_team_score - fixtures[0].home_team_score)
        team2_gd = team2_gd + (fixtures[5].home_team_score - fixtures[5].away_team_score)

        #team3
        team3_gd = team3_gd + (fixtures[2].away_team_score - fixtures[2].home_team_score)
        team3_gd = team3_gd + (fixtures[5].away_team_score - fixtures[5].home_team_score)

        self.assertEqual(group.get_goal_differential_for_team_from_subset(team1, [team2, team3]), team1_gd)
        self.assertEqual(group.get_goal_differential_for_team_from_subset(team2, [team3, team1]), team2_gd)
        self.assertEqual(group.get_goal_differential_for_team_from_subset(team3, [team2, team1]), team3_gd)


    def test_get_goals_for_team_from_subset(self):

        group = make_phony_group()

        fixtures = group.fixtures.all()

        make_results(group)

        team1 = fixtures[0].home_team
        team2 = fixtures[0].away_team
        team3 = fixtures[2].away_team
        team1_goals = 0
        team2_goals = 0
        team3_goals = 0

        # the way make_phony_group works we are looking at:
        # (commented code is for reference!!!)
        #fixtures[0].home_team_score = randint(0,4) #team1
        #fixtures[0].away_team_score = randint(0,4) #team2
        #fixtures[2].home_team_score = randint(0,4) #team1
        #fixtures[2].away_team_score = randint(0,4) #team3
        #fixtures[5].home_team_score = randint(0,4) #team2
        #fixtures[5].away_team_score = randint(0,4) #team3

        #team1
        team1_goals = team1_goals + fixtures[0].home_team_score
        team1_goals = team1_goals + fixtures[2].home_team_score

        #team2
        team2_goals = team2_goals + fixtures[0].away_team_score
        team2_goals = team2_goals + fixtures[5].home_team_score

        #team3
        team3_goals = team3_goals + fixtures[2].away_team_score
        team3_goals = team3_goals + fixtures[5].away_team_score

        self.assertEqual(group.get_goals_for_team_from_subset(team1, [team2, team3]), team1_goals)
        self.assertEqual(group.get_goals_for_team_from_subset(team2, [team3, team1]), team2_goals)
        self.assertEqual(group.get_goals_for_team_from_subset(team3, [team2, team1]), team3_goals)


class TestGetStandings(TestCase):
    """
    FIFA standard ranking and tie breakers:

    The ranking of each team in each group will be determined as follows:

        - points obtained in all group matches;
        - goal difference in all group matches;
        - number of goals scored in all group matches;
        - If two or more teams are equal on the basis of the above three criteria, their rankings will be determined as follows:

        - points obtained in the group matches between the teams concerned;
        - goal difference in the group matches between the teams concerned;
        - number of goals scored in the group matches between the teams concerned;
        - drawing of lots by the FIFA Organising Committee.

    This is sufficiently complex that we need to contrive several tests for scenarios,
    all of which will test the various standings method on Group model

    """

    def test_get_standings(self):
        """
        The ComparableTeam will handle the following cases:
        - points obtained in all group matches;
        - goal difference in all group matches;
        - number of goals scored in all group matches;

        so we will contrive this setup:
        team         points    gd    gf
        team1        6        4      5
        team2        6        0      2
        team3        3        -2     2
        team4        3        -2     1

        this separates 1 and 2 from 3 and 4 on points
        then 1 and 2 on goal differential
        then 3 and 4 on goals for
        """
        group = make_phony_group()

        fixtures = group.fixtures.all()
        teams = group.teams.all()
        team1 = teams[0]
        team2 = teams[1]
        team3 = teams[2]
        team4 = teams[3]

        fixture1 = fixtures[0]
        fixture1.home_team_score = 2 #team1
        fixture1.away_team_score = 0 #team2
        fixture1.save()

        fixture2 = fixtures[1]
        fixture2.home_team_score = 2 #team3
        fixture2.away_team_score = 0 #team4
        fixture2.save()

        fixture3 = fixtures[2]
        fixture3.home_team_score = 3 #team1
        fixture3.away_team_score = 0 #team3
        fixture3.save()

        fixture4 = fixtures[3]
        fixture4.home_team_score = 1 #team2
        fixture4.away_team_score = 0 #team4
        fixture4.save()

        # should be 4,3,2,1 at this stage
        expected = OrderedDict()
        expected[team1] = 6
        expected[team3] = 3
        expected[team2] = 3
        expected[team4] = 0
        self.assertEqual(group.get_standings(), expected)

        fixture5 = fixtures[4]
        fixture5.home_team_score = 0 #team1
        fixture5.away_team_score = 1 #team4
        fixture5.save()

        fixture6 = fixtures[5]
        fixture6.home_team_score = 1 #team2
        fixture6.away_team_score = 0 #team3
        fixture6.save()

        expected = OrderedDict()
        expected[team1] = 6
        expected[team2] = 6
        expected[team3] = 3
        expected[team4] = 3

        self.assertEqual(group.get_standings(), expected)


class TestComparableTeam(TestCase):

    """
    The ComparableTeam will handle the following cases:
        - points obtained in all group matches;
        - goal difference in all group matches;
        - number of goals scored in all group matches;

    so we will contrive this setup:
    team         points    gd    gf
    team1        6        4      5
    team2        6        0      2
    team3        3        -2     2
    team4        3        -2     1

    this separates 1 and 2 from 3 and 4 on points
    then 1 and 2 on goal differential
    then 3 and 4 on goals for

    """

    def setUp(self):

        TestCase.setUp(self)
        self.group = make_phony_group()

        fixtures = self.group.fixtures.all()
        teams = self.group.teams.all()
        self.team1 = teams[0]
        self.team2 = teams[1]
        self.team3 = teams[2]
        self.team4 = teams[3]

        self.fixture1 = fixtures[0]
        self.fixture1.home_team_score = 2 #team1
        self.fixture1.away_team_score = 0 #team2
        self.fixture1.save()

        self.fixture2 = fixtures[1]
        self.fixture2.home_team_score = 2 #team3
        self.fixture2.away_team_score = 0 #team4
        self.fixture2.save()

        self.fixture3 = fixtures[2]
        self.fixture3.home_team_score = 3 #team1
        self.fixture3.away_team_score = 0 #team3
        self.fixture3.save()

        self.fixture4 = fixtures[3]
        self.fixture4.home_team_score = 1 #team2
        self.fixture4.away_team_score = 0 #team4
        self.fixture4.save()

        fixture5 = fixtures[4]
        fixture5.home_team_score = 0 #team1
        fixture5.away_team_score = 1 #team4
        fixture5.save()

        fixture6 = fixtures[5]
        fixture6.home_team_score = 1 #team2
        fixture6.away_team_score = 0 #team3
        fixture6.save()

        self.comparable_team1 = ComparableTeam(self.team1, self.group)
        self.comparable_team2 = ComparableTeam(self.team2, self.group)
        self.comparable_team3 = ComparableTeam(self.team3, self.group)
        self.comparable_team4 = ComparableTeam(self.team4, self.group)

    def test__lt__(self):
        self.assertFalse(self.comparable_team1.__lt__(self.comparable_team2))
        self.assertFalse(self.comparable_team2.__lt__(self.comparable_team3))
        self.assertFalse(self.comparable_team3.__lt__(self.comparable_team4))
        self.assertTrue(self.comparable_team4.__lt__(self.comparable_team3))
        self.assertTrue(self.comparable_team3.__lt__(self.comparable_team2))
        self.assertTrue(self.comparable_team2.__lt__(self.comparable_team1))

    def test__le__(self):
        self.assertRaises(NotImplementedError, self.comparable_team1.__le__, self.comparable_team2)

    def test__eq__(self):
        self.assertFalse(self.comparable_team1.__eq__(self.comparable_team2))
        self.assertFalse(self.comparable_team2.__eq__(self.comparable_team3))
        self.assertFalse(self.comparable_team3.__eq__(self.comparable_team4))
        self.assertFalse(self.comparable_team1.__eq__(self.comparable_team3))
        self.assertFalse(self.comparable_team1.__eq__(self.comparable_team4))
        self.assertFalse(self.comparable_team2.__eq__(self.comparable_team4))

    def test__ne__(self):
        self.assertTrue(self.comparable_team1.__ne__(self.comparable_team2))
        self.assertTrue(self.comparable_team2.__ne__(self.comparable_team3))
        self.assertTrue(self.comparable_team3.__ne__(self.comparable_team4))
        self.assertTrue(self.comparable_team1.__ne__(self.comparable_team3))
        self.assertTrue(self.comparable_team1.__ne__(self.comparable_team4))
        self.assertTrue(self.comparable_team2.__ne__(self.comparable_team4))

    def test__gt__(self):
        self.assertTrue(self.comparable_team1.__gt__(self.comparable_team2))
        self.assertTrue(self.comparable_team2.__gt__(self.comparable_team3))
        self.assertTrue(self.comparable_team3.__gt__(self.comparable_team4))
        self.assertFalse(self.comparable_team4.__gt__(self.comparable_team3))
        self.assertFalse(self.comparable_team3.__gt__(self.comparable_team2))
        self.assertFalse(self.comparable_team2.__gt__(self.comparable_team1))

    def test__ge__(self):
        self.assertRaises(NotImplementedError, self.comparable_team1.__le__, self.comparable_team2)

