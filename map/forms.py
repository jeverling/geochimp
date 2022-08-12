from django import forms
from django.conf import settings
from django.core.cache import cache
from geochimp.utils.arcgis import get_submissions_df


def get_submission_choices():
    # @TODO: Think about how to cache this
    # depends on how often submissions are expected to change
    # But we don't want to retrieve submission list every time
    submission_choices = cache.get_or_set(
        "submission-choices", retrieve_submission_choices, 120
    )
    return submission_choices


def retrieve_submission_choices():
    submissions_df = get_submissions_df()
    submissions_dicts = submissions_df.to_dict("records")
    date_fmt = settings.CAMERA_SETUP_DATE_FORMAT
    camera_date_field = "date_and_time_of_camera_setup_o"

    submission_choices = []
    for submission in submissions_dicts:
        camera_folder = (
            f"{submission['camera_id']}_"
            f"{submission[camera_date_field].strftime(date_fmt)}"
        )
        submission_choices.append((camera_folder, camera_folder))

    return submission_choices


class SubmissionChoiceForm(forms.Form):
    submission_choices = forms.MultipleChoiceField(
        choices=get_submission_choices, label="Survey123 submission choice"
    )
