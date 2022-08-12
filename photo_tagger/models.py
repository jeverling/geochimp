from django.core.serializers.json import DjangoJSONEncoder
from django.db import models

STATUS_CHOICES = [
    # @TODO: For now we only care about sent, declined and completed
    # we use integers here because we don't want to store strings in the DB.
    # makes it harder to change the labels later, like this it's no issue.
    (0, "sent"),
    (1, "declined"),
    (2, "completed"),
]


class Submission(models.Model):
    camera_folder = models.CharField(max_length=32)
    # using DjangoJSONEncoder to serialize datetime objects correctly
    submission_raw = models.JSONField(encoder=DjangoJSONEncoder)
    submission_cleaned = models.JSONField(encoder=DjangoJSONEncoder)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return self.camera_folder


class Photo(models.Model):
    submission = models.ForeignKey(
        "Submission", related_name="photos", on_delete=models.CASCADE
    )
    # @TODO: make upload_to dynamic, so different photos with the same name
    # don't end up in the same folder. That's not a problem, but Django will
    # append some chars to make the filename unique like `IMG_0209_kOWLr7Y.JPG`
    # when `IMG_0209.JPG` already exists in the folder.
    # With a dynamic folder based e.g. on camera_folder that won't happen
    photo = models.ImageField(upload_to="photos")

    def __str__(self):
        return f"{self.submission.camera_folder}: {self.photo.name.split('/')[-1]}"


class TagRequest(models.Model):
    submission = models.ForeignKey(
        "Submission",
        related_name="tag_requests",
        on_delete=models.CASCADE,
        # @TODO: make this mandatory
        null=True,
        blank=True,
    )
    powerform_submission_id = models.UUIDField()
    # store the original data, before it may be edited by the requester
    # we will just store the URL as-is
    powerform_data_orig = models.CharField(max_length=2550)
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=0)
    requested_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    granted_at = models.DateTimeField(blank=True, null=True)
    # @TODO: how do we handle rejections?

    # we pull this from the powerform data
    powerform_data_edited = models.JSONField(default=dict)
    # @TODO: use this form powerform
    requested_by = models.CharField(max_length=255, default="")
    granted_by = models.CharField(max_length=255, default="")

    def __str__(self):
        return f"{self.submission.camera_folder}: {self.powerform_submission_id}"
