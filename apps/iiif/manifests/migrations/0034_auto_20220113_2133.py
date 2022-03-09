# Generated by Django 2.2.24 on 2022-01-13 21:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('manifests', '0033_auto_20220112_2229'),
    ]

    operations = [
        migrations.AlterField(
            model_name='manifest',
            name='pid',
            field=models.CharField(default='2r0m5dfj', help_text="Unique ID. Do not use _'s or spaces in the pid.", max_length=255),
        ),
    ]