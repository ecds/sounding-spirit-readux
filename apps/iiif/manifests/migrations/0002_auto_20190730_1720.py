# Generated by Django 2.1.2 on 2019-07-30 17:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('manifests', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='manifest',
            name='collections',
            field=models.ManyToManyField(blank=True, null=True, related_name='manifests', to='kollections.Collection'),
        ),
    ]