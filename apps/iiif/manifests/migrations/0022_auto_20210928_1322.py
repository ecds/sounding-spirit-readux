# Generated by Django 2.2.23 on 2021-09-28 13:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('manifests', '0021_auto_20210928_1301'),
    ]

    operations = [
        migrations.AlterField(
            model_name='manifest',
            name='pid',
            field=models.CharField(default='2qkkn65b', help_text="Unique ID. Do not use -'s or spaces in the pid.", max_length=255, unique=True),
        ),
    ]
