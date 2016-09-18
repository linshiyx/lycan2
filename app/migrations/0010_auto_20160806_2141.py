# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0009_room_guarded'),
    ]

    operations = [
        migrations.AddField(
            model_name='room',
            name='badge',
            field=models.CharField(default=b'', max_length=20),
        ),
        migrations.AddField(
            model_name='room',
            name='lycan',
            field=models.CharField(default=b'', max_length=200),
        ),
        migrations.AddField(
            model_name='room',
            name='poison',
            field=models.CharField(default=b'{"poison": 3}', max_length=200),
        ),
    ]
