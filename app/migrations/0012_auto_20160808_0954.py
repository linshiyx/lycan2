# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0011_auto_20160808_0949'),
    ]

    operations = [
        migrations.AlterField(
            model_name='room',
            name='lycan',
            field=models.CharField(default=b'{"lycan_choice": {}}', max_length=200),
        ),
    ]
