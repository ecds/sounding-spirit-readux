# Generated by Django 2.2.24 on 2021-10-12 16:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kollections', '0007_auto_20211007_2031'),
    ]

    operations = [
        migrations.AlterField(
            model_name='collection',
            name='pid',
            field=models.CharField(default='2qmwbpfz', help_text="Unique ID. Do not use _'s or spaces in the pid.", max_length=255),
        ),
    ]
