# Generated by Django 2.2.24 on 2021-10-26 17:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kollections', '0009_auto_20211018_1913'),
    ]

    operations = [
        migrations.AlterField(
            model_name='collection',
            name='pid',
            field=models.CharField(default='2qkw6szd', help_text="Unique ID. Do not use _'s or spaces in the pid.", max_length=255),
        ),
    ]
