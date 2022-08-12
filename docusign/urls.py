"""docusign app URL Configuration."""
from django.urls import path

from .views import map_powerform_check, tag_powerform_check

urlpatterns = [
    path(
        "tag/<uuid:powerform_submission_id>/",
        tag_powerform_check,
        name="tag_powerform_check",
    ),
    path(
        "map/<uuid:powerform_submission_id>/",
        map_powerform_check,
        name="map_powerform_check",
    ),
]
