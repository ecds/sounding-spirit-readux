# Generated by Django 2.2.23 on 2021-09-16 18:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ingest', '0022_auto_20210915_1651'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bulk',
            name='volume_files',
            field=models.FileField(upload_to=''),
        ),
        migrations.AlterField(
            model_name='local',
            name='bulk',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='local_uploads', to='ingest.Bulk'),
        ),
    ]
