# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0012_auto_20160808_0954'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='room',
            name='dead',
        ),
    ]
