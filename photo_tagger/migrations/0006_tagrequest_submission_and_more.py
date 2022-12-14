# Generated by Django 4.0.6 on 2022-08-09 23:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("photo_tagger", "0005_tagrequest_granted_at_tagrequest_granted_by_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="tagrequest",
            name="submission",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="tag_requests",
                to="photo_tagger.submission",
            ),
        ),
        migrations.AlterField(
            model_name="tagrequest",
            name="powerform_data_orig",
            field=models.CharField(max_length=2550),
        ),
    ]
