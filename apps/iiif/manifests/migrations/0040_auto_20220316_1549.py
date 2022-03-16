# Generated by Django 2.2.24 on 2022-03-16 15:49

from django.db import migrations, models
import edtf.fields


class Migration(migrations.Migration):

    dependencies = [
        ('manifests', '0039_auto_20220316_1530'),
    ]

    operations = [
        migrations.AddField(
            model_name='manifest',
            name='date_earliest',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='manifest',
            name='date_latest',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='manifest',
            name='date_sort_ascending',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='manifest',
            name='date_sort_descending',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='manifest',
            name='published_date_edtf',
            field=edtf.fields.EDTFField(blank=True, help_text='Use standard EDTF dates. For examples go to https://github.com/ixc/python-edtf#natural-language-representation', lower_fuzzy_field='date_earliest', lower_strict_field='date_sort_ascending', natural_text_field='published_date', null=True, upper_fuzzy_field='date_latest', upper_strict_field='date_sort_descending', verbose_name='Date of creation (EDTF)'),
        ),
        migrations.AlterField(
            model_name='manifest',
            name='pdf',
            field=models.URLField(blank=True, help_text='Enter a link to an online pdf.', null=True),
        ),
        migrations.AlterField(
            model_name='manifest',
            name='pid',
            field=models.CharField(default='2r8kvr0m', help_text="Unique ID. Do not use _'s or spaces in the pid.", max_length=255),
        ),
        migrations.AlterField(
            model_name='manifest',
            name='published_date',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
