# Generated by Django 2.2.23 on 2021-09-22 19:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ingest', '0026_remote_metadata'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='local',
            name='local_bundle_path',
        ),
    ]