# Generated by Django 2.2 on 2019-04-18 11:08

from django.db import migrations
from django.contrib.auth import get_user_model
from core.models import OnTaskUser

def create_ontask_user_info(apps, schema_editor):

    # Get all the existing ontask users first
    ousers_id = [x.user.id for x in OnTaskUser.objects.all()]

    # Get the regular users with not corresponding ontask user
    users = get_user_model().objects.exclude(id__in=ousers_id)

    # Remaining users in list need to have an OnTask element
    for user in users:
        ouser = OnTaskUser(user=user)
        ouser.save()

def reverse_migration(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20190418_1541'),
    ]

    operations = [
        migrations.RunPython(create_ontask_user_info, reverse_migration),
    ]