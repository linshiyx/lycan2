# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_auto_20160805_0939'),
    ]

    operations = [
        migrations.AlterField(
            model_name='room',
            name='users',
            field=models.CharField(max_length=1000),
        ),
    ]
