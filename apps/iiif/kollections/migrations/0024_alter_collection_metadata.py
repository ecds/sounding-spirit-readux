# Generated by Django 3.2.15 on 2023-09-25 20:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kollections', '0023_auto_20220607_1453'),
    ]

    operations = [
        migrations.AlterField(
            model_name='collection',
            name='metadata',
            field=models.JSONField(null=True),
        ),
    ]