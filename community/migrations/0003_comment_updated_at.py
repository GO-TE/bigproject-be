# Generated by Django 5.0.6 on 2024-07-02 06:04

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("community", "0002_alter_article_image_alter_image_user"),
    ]

    operations = [
        migrations.AddField(
            model_name="comment",
            name="updated_at",
            field=models.DateTimeField(auto_now=True),
        ),
    ]
