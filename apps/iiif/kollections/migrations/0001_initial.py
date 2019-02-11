# Generated by Django 2.1.2 on 2018-12-17 22:35

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Collection',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('label', models.CharField(max_length=255)),
                ('label_en', models.CharField(max_length=255, null=True)),
                ('label_de', models.CharField(max_length=255, null=True)),
                ('summary', models.TextField()),
                ('summary_en', models.TextField(null=True)),
                ('summary_de', models.TextField(null=True)),
                ('pid', models.CharField(max_length=255)),
                ('metadata', django.contrib.postgres.fields.jsonb.JSONField(null=True)),
                ('upload', models.FileField(null=True, upload_to='uploads/')),
            ],
        ),
    ]