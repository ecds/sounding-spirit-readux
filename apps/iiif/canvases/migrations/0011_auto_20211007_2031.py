# Generated by Django 2.2.24 on 2021-10-07 20:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('canvases', '0010_auto_20210928_1301'),
    ]

    operations = [
        migrations.AlterField(
            model_name='canvas',
            name='pid',
            field=models.CharField(default='2qkqfvwv', help_text="Unique ID. Do not use _'s or spaces in the pid.", max_length=255),
        ),
    ]
