# Generated by Django 3.2.12 on 2022-03-28 21:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('manifests', '0043_alter_manifest_pid'),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name='manifest',
            name='manifests_m_search__bd83b2_gin',
        ),
    ]