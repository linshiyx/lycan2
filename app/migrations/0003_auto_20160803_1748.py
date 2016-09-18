# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('handle', models.CharField(max_length=20)),
                ('message', models.CharField(max_length=20)),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now, db_index=True)),
            ],
        ),
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('room_id', models.CharField(max_length=20, db_index=True)),
            ],
        ),
        migrations.DeleteModel(
            name='Chat',
        ),
        migrations.AlterField(
            model_name='user',
            name='nick',
            field=models.CharField(max_length=50, db_index=True),
        ),
        migrations.AddField(
            model_name='message',
            name='room',
            field=models.ForeignKey(related_name='messages', to='app.Room'),
        ),
    ]
