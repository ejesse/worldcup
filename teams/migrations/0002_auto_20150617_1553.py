# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('teams', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='team',
            name='full_name',
            field=models.CharField(unique=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='team',
            name='three_letter_name',
            field=models.CharField(unique=True, max_length=3),
        ),
    ]
