# Generated by Django 2.1.15 on 2020-02-24 20:38

from django.db import migrations
import modelcluster.fields


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0003_auto_20200128_1721'),
    ]

    operations = [
        migrations.AlterField(
            model_name='homepage',
            name='featured_collections',
            field=modelcluster.fields.ParentalManyToManyField(blank=True, to='kollections.Collection'),
        ),
        migrations.AlterField(
            model_name='homepage',
            name='featured_volumes',
            field=modelcluster.fields.ParentalManyToManyField(blank=True, to='manifests.Manifest'),
        ),
    ]