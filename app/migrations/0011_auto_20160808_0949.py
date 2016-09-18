# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0010_auto_20160806_2141'),
    ]

    operations = [
        migrations.AddField(
            model_name='room',
            name='can_talk',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='room',
            name='dead',
            field=models.CharField(default=b'[]', max_length=200),
        ),
        migrations.AddField(
            model_name='room',
            name='finish_talk',
            field=models.CharField(default=b'[]', max_length=500),
        ),
        migrations.AddField(
            model_name='room',
            name='talk_list',
            field=models.CharField(default=b'[]', max_length=500),
        ),
        migrations.AddField(
            model_name='room',
            name='vote_badge',
            field=models.CharField(default=b'{}', max_length=500),
        ),
        migrations.AddField(
            model_name='room',
            name='vote_dead',
            field=models.CharField(default=b'{}', max_length=500),
        ),
    ]
