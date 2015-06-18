from collections import OrderedDict

from django.core.exceptions import ValidationError
from django.db import models

from teams.models import Team


# Create your models here.
class Fixture(models.Model):

    WIN = 'WIN'
    DRAW = 'DRAW'
    LOSS = 'LOSS'

    home_team = models.ForeignKey(Team, related_name='home_team')
    away_team = models.ForeignKey(Team, related_name='away_team')
    home_team_score = models.IntegerField(null=True, blank=True)
    away_team_score = models.IntegerField(null=True, blank=True)
    start_time = models.DateTimeField(null=True, blank=True)

    def save(self, force_insert=False, force_update=False, using=None,
        update_fields=None):
        if self.home_team_score is not None and self.away_team_score is None:
            raise ValidationError("Must have a value for both scores or neither, found 1: home_team_score: %s away_team_score %s" % (self.home_team_score, self.away_team_score))
        if self.home_team_score is None and self.away_team_score is not None:
            raise ValidationError("Must have a value for both scores or neither, found 1: home_team_score: %s away_team_score %s" % (self.home_team_score, self.away_team_score))
        if self.home_team == self.away_team:
            raise ValidationError("Self and away team are the same, a team cannot play itself!")
        return models.Model.save(self, force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)

    def __unicode__(self):
        if self.home_team_score is None:
            return u'%s v %s' % (self.home_team, self.away_team)
        else:
            return u'%s %s : %s %s' % (self.home_team, self.home_team_score, self.away_team_score, self.away_team)

    def __str__(self):
        return self.__unicode__()

    def team_in_fixture(self, team):
        if team == self.home_team or team == self.away_team:
            return True
        return False

    def get_result_for_team(self, team):
        if not self.team_in_fixture(team):
            raise ValueError("Team %s is not in this fixture" % team)

        if self.home_team_score is None:
            return None

        if team == self.home_team:
            if self.home_team_score > self.away_team_score:
                return Fixture.WIN
            elif self.home_team_score < self.away_team_score:
                return Fixture.LOSS
            return Fixture.DRAW
        else:
            if self.home_team_score < self.away_team_score:
                return Fixture.WIN
            elif self.home_team_score > self.away_team_score:
                return Fixture.LOSS
            return Fixture.DRAW

    def get_points_for_team(self, team, win=3, draw=1):
        if not self.team_in_fixture(team):
            raise ValueError("Team %s is not in this fixture" % team)

        points = 0

        result = self.get_result_for_team(team)
        if result is not None:
            if result == Fixture.WIN:
                points = points + win
            elif result == Fixture.DRAW:
                points = points + draw

        return points

class Group(models.Model):

    group_letter = models.CharField(max_length=1, unique=True)
    group_size = models.IntegerField(default=4)
    teams = models.ManyToManyField(Team)
    fixtures = models.ManyToManyField(Fixture)

    def save(self, force_insert=False, force_update=False, using=None,
        update_fields=None):
        if self.id is not None:
            if self.teams.count() != self.group_size:
                raise ValidationError("Number of teams must equal group size")
        return models.Model.save(self, force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)

    def __unicode__(self):
        return u'Group %s' % (self.group_letter)

    def __str__(self):
        return self.__unicode__()

    def check_teams_in_group(self, teams):
        if not isinstance(teams,list):
            teams = [teams]
        invalid_teams = []
        for team in teams:
            if team not in self.teams.all():
                invalid_teams.append(team)

        if len(invalid_teams) > 0:
            raise ValueError("Teams %s is not in group %s" % (invalid_teams, self.group_letter))

    def get_fixtures_for_team(self, team):
        fixtures = []
        for fixture in self.fixtures.all():
            if fixture.team_in_fixture(team):
                fixtures.append(fixture)
        return fixtures

    def standings(self):
        pass

    def get_points_for_team(self, team):

        self.check_teams_in_group(team)

        points = 0

        for f in self.get_fixtures_for_team(team):
            points = points + f.get_points_for_team(team)

        return points

    def get_goal_differential_for_team(self, team):

        self.check_teams_in_group(team)

        gd = 0

        for fixture in self.get_fixtures_for_team(team):
            if fixture.home_team_score is not None:
                if fixture.home_team == team:
                    gd = gd + (fixture.home_team_score - fixture.away_team_score)
                else:
                    gd = gd + (fixture.away_team_score - fixture.home_team_score)

        return gd

    def get_head_to_head_goal_differential(self, team1, team2):

        self.check_teams_in_group([team1,team2])

        gd = 0

        head_to_head_fixtures = []

        for fixture in self.get_fixtures_for_team(team1):
            if fixture.team_in_fixture(team2):
                head_to_head_fixtures.append(fixture)

        for fixture in head_to_head_fixtures:
            if fixture.home_team_score is not None:
                if fixture.home_team == team1:
                    gd = gd + (fixture.home_team_score - fixture.away_team_score)
                else:
                    gd = gd + (fixture.away_team_score - fixture.home_team_score)

        return gd

    def get_goals_for_team(self, team):

        self.check_teams_in_group(team)

        fixtures = self.get_fixtures_for_team(team)

        goals = 0

        for fixture in fixtures:
            if fixture.home_team_score is not None:
                if team == fixture.home_team:
                    goals = goals + fixture.home_team_score
                else:
                    goals = goals + fixture.away_team_score

        return goals

    def get_counted_fixtures_from_subset(self, team, other_teams):
        all_teams = [team]
        all_teams.extend(other_teams)
        self.check_teams_in_group(all_teams)

        team_fixtures = self.get_fixtures_for_team(team)
        counted_fixtures = []

        for fixture in team_fixtures:
            for other_team in other_teams:
                if fixture.team_in_fixture(other_team):
                    counted_fixtures.append(fixture)
        return counted_fixtures

    def get_points_for_team_from_subset(self, team, other_teams):

        points = 0

        for fixture in self.get_counted_fixtures_from_subset(team, other_teams):
            points = points + fixture.get_points_for_team(team)

        return points

    def get_goal_differential_for_team_from_subset(self, team, other_teams):

        gd = 0

        for fixture in self.get_counted_fixtures_from_subset(team, other_teams):
            if team == fixture.home_team:
                gd = gd + (fixture.home_team_score - fixture.away_team_score)
            else:
                gd = gd + (fixture.away_team_score - fixture.home_team_score)

        return gd

    def get_goals_for_team_from_subset(self, team, other_teams):

        goals = 0

        for fixture in self.get_counted_fixtures_from_subset(team, other_teams):
            if team == fixture.home_team:
                goals = goals + fixture.home_team_score
            else:
                goals = goals + fixture.away_team_score

        return goals

    def get_standings(self):
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

        """
        return OrderedDict()


