# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0007_auto_20160806_0004'),
    ]

    operations = [
        migrations.AddField(
            model_name='room',
            name='valentine',
            field=models.CharField(default=b'[]', max_length=50),
        ),
        migrations.AlterField(
            model_name='room',
            name='users',
            field=models.CharField(max_length=2000),
        ),
    ]
