# Generated by Django 2.2.6 on 2019-10-23 23:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ontask', '0053_auto_20191024_1013'),
    ]

    operations = [
        migrations.AlterField(
            model_name='workflow',
            name='description_text',
            field=models.CharField(blank=True, default='', max_length=2048, verbose_name='description'),
        ),
        migrations.AlterField(
            model_name='workflow',
            name='name',
            field=models.CharField(max_length=512, verbose_name='name'),
        ),
    ]
