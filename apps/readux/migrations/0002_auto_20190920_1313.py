# Generated by Django 2.1.2 on 2019-09-20 13:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('readux', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userannotation',
            name='svg',
            field=models.TextField(blank=True, null=True),
        ),
    ]