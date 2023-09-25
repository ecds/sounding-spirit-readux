# Generated by Django 3.2.15 on 2023-09-25 20:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('readux', '0010_auto_20220607_1453'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userannotation',
            name='oa_annotation',
            field=models.JSONField(default=dict),
        ),
        migrations.AlterField(
            model_name='userannotation',
            name='purpose',
            field=models.CharField(choices=[('AS', 'Assessing'), ('BM', 'Bookmarking'), ('CL', 'Classifying'), ('CM', 'Commenting'), ('DS', 'Describing'), ('ED', 'Editing'), ('HL', 'Highlighting'), ('ID', 'Identifying'), ('LK', 'Linking'), ('MO', 'Moderating'), ('PT', 'Painting'), ('QT', 'Questioning'), ('RE', 'Replying'), ('SP', 'Supplementing'), ('TG', 'Tagging')], default='SP', max_length=2),
        ),
    ]
