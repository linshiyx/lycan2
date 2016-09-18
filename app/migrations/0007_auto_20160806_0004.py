# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0006_room_game_round'),
    ]

    operations = [
        migrations.AlterField(
            model_name='room',
            name='game_round',
            field=models.IntegerField(default=0),
        ),
    ]
