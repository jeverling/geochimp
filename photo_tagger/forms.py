from django import forms
from django.conf import settings
from multiupload.fields import MultiImageField


class ValidatedMultiImageField(MultiImageField):
    """Fix for validation bug.

    see https://github.com/Chive/django-multiupload/issues/23#issuecomment-322741888
    """

    def run_validators(self, value):
        value = value or []

        for item in value:
            super().run_validators(item)


class CameraFolderForm(forms.Form):
    camera_folder = forms.RegexField(
        regex=settings.CAMERAFOLDER_REGEX,
        label="CAMERAID_DATE",
        help_text="Please provide the combination of camera id and date"
        " according to folder naming convention, e.g. CAMERA2_20220408",
    )


class UploadForm(forms.Form):
    attachments = ValidatedMultiImageField(
        min_num=1, max_num=10, max_file_size=1024 * 1024 * 10
    )
    tag_exif = forms.BooleanField(
        label="Create EXIF GPS tag",
        required=False,
        initial=True,
        help_text="EXIF tag in photos can be updated, to include GPS "
        "coordinates from Survey123 submission.",
    )
