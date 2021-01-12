# Generated by Django 2.2.10 on 2020-10-29 15:21

import apps.ingest.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    replaces = [('ingest', '0001_initial'), ('ingest', '0002_auto_20201021_1610'), ('ingest', '0003_auto_20201027_1452'), ('ingest', '0004_auto_20201027_1605'), ('ingest', '0005_auto_20201027_1653')]

    initial = True

    dependencies = [
        ('manifests', '0012_auto_20200819_1608'),
        ('canvases', '0005_auto_20201027_1452'),
    ]

    operations = [
        migrations.CreateModel(
            name='Local',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bundle', models.FileField(upload_to='')),
                ('temp_file_path', models.FilePathField(default=apps.ingest.models.make_temp_file, path='/tmp/tmpz0h5pz94')),
                ('image_server', models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='canvases.IServer')),
                ('manifest', models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='manifests.Manifest')),
            ],
        ),
    ]