# Generated by Django 4.0.6 on 2022-08-12 10:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("photo_tagger", "0007_alter_tagrequest_status"),
    ]

    operations = [
        migrations.AddField(
            model_name="submission",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
