# Generated by Django 2.2.24 on 2022-03-16 16:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('canvases', '0024_auto_20220316_1611'),
    ]

    operations = [
        migrations.AlterField(
            model_name='canvas',
            name='pid',
            field=models.CharField(default='2r84kvmd', help_text="Unique ID. Do not use _'s or spaces in the pid.", max_length=255),
        ),
    ]
