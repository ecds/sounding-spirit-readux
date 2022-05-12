# Generated by Django 3.2.12 on 2022-03-28 21:14

from django.db import migrations, models


class Migration(migrations.Migration):
    """Migration to migrate old language field on Manifest to new Language model"""
    dependencies = [
        ("manifests", "0046_add_language_model"),
    ]

    operations = [
        migrations.AddField(
            model_name="manifest",
            name="languages",
            field=models.ManyToManyField(
                help_text="Languages present in the manifest.", to="manifests.Language"
            ),
        ),
        migrations.RemoveField(
            model_name="manifest",
            name="language",
        ),
    ]
