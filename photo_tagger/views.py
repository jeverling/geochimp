# import logging
import uuid
from urllib.parse import urlencode

from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import TemplateView

from photo_tagger.models import Submission

from .forms import CameraFolderForm, UploadForm
from .models import Photo
from geochimp.utils.arcgis import clean_submission, get_submissions_for_camera_folder
from geochimp.utils.common import write_gps_coordinates_to_exif
from geochimp.utils.mediavalet import (
    get_mediavalet_assets,
    get_mediavalet_folder_id,
    tag_mediavalet_attributes,
    upload_submission_photos_to_mediavalet,
)

# @ TODO: setup logging properly
# logging.basicConfig(
#     level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
# )


class IndexView(TemplateView):
    template_name = "photo_tagger/index.html"


def get_survey_submission(request, action):
    if request.method == "POST":
        form = CameraFolderForm(request.POST)
        if form.is_valid():
            camera_folder = form.cleaned_data["camera_folder"]
            # we have the name of the folder, that is used in MediaValet
            # we need to identify the matching submission[s], so we can
            # use submission data for tagging the photos
            submissions = get_submissions_for_camera_folder(camera_folder)
            # logging.debug(
            #     'Retrieved %s submissions for "%s"', len(submissions), camera_folder
            # )

            if len(submissions) == 0:
                form.add_error(
                    field="camera_folder",
                    error="No submission for the combination of CAMERAID + DATE found!",
                )
            else:
                # @TODO: let user choose when >1 submissions - for now we use latest
                submission_raw = submissions.sort_values("CreationDate").to_dict(
                    "records"
                )[-1]
                submission_cleaned = clean_submission(submission_raw)

                # @TOOD: decide whether to always create a new submission object for the
                # same camera_folder, or re-use existing objects.
                # Guess this depends on whether Survey123 data could ever be edited.
                # If yes, it's better to use multiple submission objects for same
                # camera_folder, to keep track of different states.
                # If not, or we can easily check if a submission was edited, we could
                # reuse the same object to save time and make some things easier, for
                # example we could use ModelChoiceField etc.
                submission = Submission.objects.create(
                    camera_folder=camera_folder,
                    submission_raw=submission_raw,
                    submission_cleaned=submission_cleaned,
                )
                if action == "upload":
                    return HttpResponseRedirect(
                        reverse(
                            "upload_photos", kwargs={"submission_id": submission.id}
                        )
                    )
                if action == "tag":
                    return HttpResponseRedirect(
                        reverse("tag_photos", kwargs={"submission_id": submission.id})
                    )
    else:
        form = CameraFolderForm()

    return render(
        request,
        # @TODO: add description to template what will happen when request is sent
        template_name="photo_tagger/camerafolder_form.html",
        context={"form": form},
    )


def upload_photos(request, submission_id):
    # @TODO: Depending on whether we allow multiple submission objects for the
    # same camera_folder, we need to decide what to do if the current one
    # already has images attached
    submission = Submission.objects.get(pk=submission_id)

    if request.method == "POST":
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            for attachment in form.cleaned_data["attachments"]:
                Photo.objects.create(submission=submission, photo=attachment)

            if form.cleaned_data["tag_exif"] is True:
                # add exif GPSTags to photos
                lat_lon = {
                    "x": submission.submission_cleaned["x"][1],
                    "y": submission.submission_cleaned["y"][1],
                }
                for photo in submission.photos.all():
                    write_gps_coordinates_to_exif(lat_lon, photo.photo.path)

            # @TODO: only upload photos to MediaValet after DocuSign sign-off
            upload_submission_photos_to_mediavalet(submission)

            # delete photos uploaded by user. From here on, if we work with photos
            # we'll retrieve them from MediaValet, in case they got updated there
            submission.photos.all().delete()

            return HttpResponseRedirect(
                reverse("tag_photos", kwargs={"submission_id": submission.id})
            )

    else:
        form = UploadForm()

    return render(
        request,
        # @TODO: add a nice drop target
        template_name="photo_tagger/upload.html",
        context={"submission": submission, "form": form},
    )


def tag_photos(request, submission_id):
    submission = Submission.objects.get(pk=submission_id)
    mediavalet_folder = get_mediavalet_folder_id(submission.camera_folder)
    # we have the ID of the folder named like camera
    try:
        asset_list = get_mediavalet_assets(mediavalet_folder)
    except KeyError:
        return HttpResponse(
            "Folder doesn't exist in MediaValet. Please make sure it's created first."
        )
    asset_titles = tuple(x["title"] for x in asset_list)
    asset_ids = tuple(x["id"] for x in asset_list)

    cleaned_data = submission.submission_cleaned
    attributes_direct = settings.METADATA_ATTRIBUTES_DIRECT
    attributes_to_tag = {}

    # handle attributes we set directly, like x, y
    for attribute in attributes_direct:
        # do not include attribute in rest of attributes that will be
        # added to "Description" field
        # cleaned_data contains (label, value) pairs as values
        label, value = cleaned_data.pop(attribute)
        attributes_to_tag[label] = value

    # handle all other attributes
    description_text_parts = []
    for label, value in cleaned_data.values():
        description_text_parts.append(f"{label}: {value}")

    attributes_to_tag[settings.METADATA_DESCRIPTION_ATTRIBUTE] = "\n".join(
        description_text_parts
    )

    if request.method == "POST":
        if settings.REQUIRE_DOCUSIGN_FOR_ASSET_TAGGING is False:
            # @TODO: add optional replacing of assets with updated exif GPS tags
            # However, this means downloading the assets, deleting them and re-uploading
            tag_mediavalet_attributes(attributes_to_tag, asset_ids)
            return render(
                request,
                template_name="photo_tagger/success.html",
                context={
                    "message": f"Successfully tagged assets for "
                    f"{submission.camera_folder}",
                },
            )
        else:
            # store unique powerform_submission_id, in case there are multiple tagging
            # iterations
            powerform_submission_id = uuid.uuid4()
            powerform_url = settings.DOCUSIGN_ASSET_TAGGING_POWERFORM_URL
            attribute_querystring = urlencode(attributes_to_tag)
            assets_querystring = urlencode({"assets": "\n".join(asset_titles)})
            complete_url = (
                f"{powerform_url}&EnvelopeField_powerform_submission_id="
                f"{powerform_submission_id}&{attribute_querystring}&camera_folder="
                f"{submission.camera_folder}&{assets_querystring}"
            )
            submission.tag_requests.create(
                powerform_submission_id=powerform_submission_id,
                powerform_data_orig=complete_url,
            )
            return HttpResponseRedirect(complete_url)

    return render(
        request,
        # @TODO: add description to template what will happen when request is sent
        template_name="photo_tagger/tag.html",
        context={
            "submission": submission,
            "mediavalet_folder": mediavalet_folder,
            "attributes_to_tag": attributes_to_tag,
            "asset_titles": asset_titles,
            "require_docusign": settings.REQUIRE_DOCUSIGN_FOR_ASSET_TAGGING is True,
        },
    )
