# -*- coding: utf-8 -*-
# Generated by Django 1.11.14 on 2018-08-26 09:23
from __future__ import unicode_literals

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('scheduler', '0025_auto_20180826_1830'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scheduledaction',
            name='payload',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict, null=True, verbose_name='payload'),
        ),
    ]