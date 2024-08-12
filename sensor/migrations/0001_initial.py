# Generated by Django 5.1 on 2024-08-12 14:18

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Equipment',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('equipmentId', models.CharField(max_length=255, verbose_name='Equipment ID')),
                ('timestamp', models.DateTimeField(default=datetime.datetime(2024, 8, 12, 14, 18, 29, 956190), verbose_name='Timestamp')),
                ('value', models.FloatField(verbose_name='Value')),
            ],
        ),
    ]
