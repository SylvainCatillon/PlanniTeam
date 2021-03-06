# Generated by Django 3.0.6 on 2020-05-21 19:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('participations', '0002_auto_20200521_2100'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='participation',
            constraint=models.UniqueConstraint(fields=('event', 'participant'), name='unique_participant_event'),
        ),
    ]
