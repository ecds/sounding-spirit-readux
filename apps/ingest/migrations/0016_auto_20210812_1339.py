# Generated by Django 2.2.10 on 2021-08-12 13:39

import apps.ingest.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ingest', '0015_auto_20210811_1605'),
    ]

    operations = [
        migrations.AddField(
            model_name='local',
            name='bundle_local',
            field=models.BooleanField(default=False),
        )
    ]
