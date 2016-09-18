# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0013_remove_room_dead'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='message',
            name='room',
        ),
        migrations.AlterField(
            model_name='room',
            name='can_talk',
            field=models.BooleanField(default=True),
        ),
        migrations.DeleteModel(
            name='Message',
        ),
    ]
