# Generated by Django 3.0.6 on 2020-05-16 16:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('plannings', '0002_event'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='time',
            field=models.TimeField(blank=True, null=True),
        ),
    ]