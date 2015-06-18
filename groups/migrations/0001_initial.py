# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('teams', '0002_auto_20150617_1553'),
    ]

    operations = [
        migrations.CreateModel(
            name='Fixture',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('home_team_score', models.IntegerField(blank=True, null=True)),
                ('away_team_score', models.IntegerField(blank=True, null=True)),
                ('start_time', models.DateTimeField()),
                ('away_team', models.ForeignKey(to='teams.Team', related_name='away_team')),
                ('home_team', models.ForeignKey(to='teams.Team', related_name='home_team')),
            ],
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('group_letter', models.CharField(max_length=1, unique=True)),
                ('group_size', models.IntegerField(default=4)),
                ('fixtures', models.ManyToManyField(to='groups.Fixture')),
                ('teams', models.ManyToManyField(to='teams.Team')),
            ],
        ),
    ]
