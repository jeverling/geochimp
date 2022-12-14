# Generated by Django 4.0.6 on 2022-08-09 21:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("photo_tagger", "0003_photo_delete_image"),
    ]

    operations = [
        migrations.CreateModel(
            name="TagRequest",
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
                ("powerform_submission_id", models.UUIDField()),
                (
                    "status",
                    models.PositiveSmallIntegerField(
                        choices=[(0, "Requested"), (1, "Granted"), (2, "Rejected")],
                        default=0,
                    ),
                ),
            ],
        ),
        migrations.AlterField(
            model_name="photo",
            name="submission",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="photos",
                to="photo_tagger.submission",
            ),
        ),
    ]
