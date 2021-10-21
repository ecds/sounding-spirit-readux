# Generated by Django 2.2.24 on 2021-10-18 19:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('manifests', '0029_auto_20211012_1612'),
    ]

    operations = [
        migrations.AlterField(
            model_name='manifest',
            name='label',
            field=models.CharField(max_length=1000),
        ),
        migrations.AlterField(
            model_name='manifest',
            name='pid',
            field=models.CharField(default='2qnj9psx', help_text="Unique ID. Do not use _'s or spaces in the pid.", max_length=255),
        ),
    ]
