from django.db import models

from photo_tagger.models import STATUS_CHOICES


class Map(models.Model):
    powerform_submission_id = models.UUIDField(blank=True, null=True)
    status = models.PositiveSmallIntegerField(choices=STATUS_CHOICES, default=0)
    requested_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    granted_at = models.DateTimeField(blank=True, null=True)
    # @TODO: how do we handle rejections?

    # @TODO: use this form powerform
    requested_by = models.CharField(max_length=255, default="")
    granted_by = models.CharField(max_length=255, default="")

    submission_attributes = models.JSONField(default=dict)
    webmap_url = models.CharField(max_length=1024, default="")
    # @TODO: this seems to be just /apps/mapviewer/index.html?webmap=<map_id>
    # should we get rid of it?
    webmap_public_url = models.CharField(max_length=1024, default="")
    webmap_json = models.JSONField(default=dict)

    def __str__(self):
        return f"Map for {', '.join(self.submission_attributes.keys())}"
