# Generated by Django 2.2.24 on 2022-01-12 22:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ingest', '0033_auto_20211028_1527'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bulk',
            name='collections',
            field=models.ManyToManyField(blank=True, help_text='Optional: Collections to attach to ALL volumes ingested in this form.', to='kollections.Collection'),
        ),
        migrations.AlterField(
            model_name='local',
            name='collections',
            field=models.ManyToManyField(blank=True, help_text='Optional: Collections to attach to the volume ingested in this form.', to='kollections.Collection'),
        ),
    ]