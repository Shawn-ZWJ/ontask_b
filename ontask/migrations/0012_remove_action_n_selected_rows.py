# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-05-15 12:35
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ontask', '0011_auto_20180515_2203'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='action',
            name='n_selected_rows',
        ),
    ]
