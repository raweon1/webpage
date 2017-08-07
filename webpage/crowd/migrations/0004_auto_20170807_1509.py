# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-07 13:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crowd', '0003_auto_20170802_1559'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='trap',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='answerchoices',
            name='choice',
            field=models.CharField(max_length=25),
        ),
        migrations.AlterField(
            model_name='rating_block',
            name='answer_type',
            field=models.CharField(choices=[('acr', 'ACR'), ('text', 'Text'), ('multiple_choice', 'Multiple Choice')], max_length=10),
        ),
    ]
