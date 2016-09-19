# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0015_room_has_started'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='room',
            name='has_started',
        ),
    ]
