# Generated by Django 3.2.25 on 2025-03-04 15:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('readux', '0011_auto_20230925_2040'),
    ]

    operations = [
        migrations.AddField(
            model_name='userannotation',
            name='raw_content',
            field=models.TextField(blank=True, default=' ', null=True),
        ),
    ]
