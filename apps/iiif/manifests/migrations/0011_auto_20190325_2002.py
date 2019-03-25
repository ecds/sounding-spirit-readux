# Generated by Django 2.1.2 on 2019-03-25 20:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('kollections', '0002_auto_20190320_1819'),
        ('manifests', '0010_auto_20190322_1747'),
    ]

    operations = [
        migrations.AddField(
            model_name='manifest',
            name='collections',
            field=models.ManyToManyField(related_name='manifests', to='kollections.Collection'),
        ),
        migrations.AlterField(
            model_name='manifest',
            name='collection',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='manifest', to='kollections.Collection'),
        ),
    ]
