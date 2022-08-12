# Generated by Django 4.0.6 on 2022-08-04 10:02

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Submission",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("camera_folder", models.CharField(max_length=32)),
                ("submission_raw", models.JSONField()),
                ("submission_cleaned", models.JSONField()),
            ],
        ),
    ]
