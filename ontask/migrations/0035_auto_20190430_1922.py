# Generated by Django 2.2 on 2019-04-30 09:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ontask', '0034_auto_20190422_1226'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='column',
            options={'ordering': ['position'], 'verbose_name': 'column', 'verbose_name_plural': 'columns'},
        ),
    ]
