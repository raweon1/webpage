# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-02 13:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crowd', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='workerprogress',
            name='finished',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='workerprogress',
            name='end_time',
            field=models.DateTimeField(blank=True),
        ),
    ]
