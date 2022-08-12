"""photo_tagger app URL Configuration."""
from django.urls import path, re_path

from .views import IndexView, get_survey_submission, tag_photos, upload_photos

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    re_path(
        "survey/(?P<action>upload|tag)/",
        get_survey_submission,
        name="get_survey_submission",
    ),
    path(
        "upload/<int:submission_id>/",
        upload_photos,
        name="upload_photos",
    ),
    path("tag/<int:submission_id>/", tag_photos, name="tag_photos"),
]
