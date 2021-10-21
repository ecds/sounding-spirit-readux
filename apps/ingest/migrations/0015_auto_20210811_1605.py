# Generated by Django 2.2.10 on 2021-08-11 16:05

import apps.ingest.models
import apps.ingest.storages
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ingest', '0011_auto_20210805_1748'),
    ]

    operations = [
        migrations.AlterField(
            model_name='local',
            name='bundle',
            field=models.FileField(storage=apps.ingest.storages.TmpStorage(), upload_to=''),
        ),
        migrations.AlterField(
            model_name='volume',
            name='volume_file',
            field=models.FileField(storage=apps.ingest.storages.TmpStorage(), upload_to=apps.ingest.models.bulk_path),
        ),
    ]
