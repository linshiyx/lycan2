# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_auto_20160805_1548'),
    ]

    operations = [
        migrations.AddField(
            model_name='room',
            name='game_round',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]
