# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-02 13:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crowd', '0002_auto_20170802_1534'),
    ]

    operations = [
        migrations.AlterField(
            model_name='workerprogress',
            name='end_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]