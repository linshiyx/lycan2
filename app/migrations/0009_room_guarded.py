# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0008_auto_20160806_1114'),
    ]

    operations = [
        migrations.AddField(
            model_name='room',
            name='guarded',
            field=models.CharField(default=b'', max_length=20),
        ),
    ]
