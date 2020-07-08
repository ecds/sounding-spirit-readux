# Generated by Django 2.2.10 on 2020-07-07 13:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('canvases', '0003_canvas_default_ocr'),
        ('manifests', '0008_auto_20200224_2038'),
    ]

    operations = [
        migrations.AddField(
            model_name='manifest',
            name='start_canvas',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='start_canvas', to='canvases.Canvas'),
        ),
    ]
