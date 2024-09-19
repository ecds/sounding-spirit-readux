# Generated by Django 3.2.25 on 2024-09-13 16:25

from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ("cms", "0004_auto_20200224_2038"),
    ]

    operations = [
        migrations.AddField(
            model_name="homepage",
            name="featured_story_image",
            field=models.ForeignKey(
                blank=True,
                help_text="Thumbnail image for the featured story",
                null=True,
                on_delete=models.deletion.SET_NULL,
                related_name="+",
                to="wagtailimages.image",
            ),
        ),
        migrations.AddField(
            model_name="homepage",
            name="featured_story_summary",
            field=models.TextField(
                blank=True, help_text="A summary or excerpt of the featured story"
            ),
        ),
        migrations.AddField(
            model_name="homepage",
            name="featured_story_title",
            field=models.CharField(
                blank=True, help_text="Title of the featured story", max_length=255
            ),
        ),
        migrations.AddField(
            model_name="homepage",
            name="featured_story_url",
            field=models.URLField(blank=True, help_text="Link to the featured story"),
        ),
    ]
