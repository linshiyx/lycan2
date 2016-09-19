# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0016_remove_room_has_started'),
    ]

    operations = [
        migrations.AddField(
            model_name='room',
            name='has_started',
            field=models.BooleanField(default=False),
        ),
    ]
