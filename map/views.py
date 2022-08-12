import datetime
from urllib.parse import urlencode
import uuid

from django.conf import settings
from django.shortcuts import render
from geochimp.utils.arcgis import (
    clean_submission,
    convert_coordinates_for_arcgis_map,
    create_arcgis_webmap,
    get_submissions_df,
    interpolate_map_template,
)
from geochimp.utils.mediavalet import download_mediavalet_folder_into_submission
from photo_tagger.models import Submission

from .forms import SubmissionChoiceForm
from .models import Map


def create_map(request):
    """Ask user to choose submissions and create map with corresponding photos."""

    form = SubmissionChoiceForm()

    if request.method == "POST":
        form = SubmissionChoiceForm(request.POST)
        if form.is_valid():
            # we have a list of submissions the user chose
            # the values are actually camera_folders, which are here
            # used to identify submissions
            camera_folders = form.cleaned_data["submission_choices"]

            submissions = []

            # @TODO: optimize the code below, make sure to follow DRY as far as
            # sensible
            # Also, if we can re-use submission objects safely depends on
            # whether submissions may change or not
            for camera_folder in camera_folders:
                # retrieve existing submission objects to access attributes
                submissions.append(
                    Submission.objects.filter(camera_folder=camera_folder).last()
                )

            if not all(submissions):
                # there are submissions in Survey123, that do not yet have corresponding
                # Submission objects. We need to fetch all submissions and update those.

                # get submission dataframe
                # @TODO: we already got this for the form, should cache and re-use
                submissions_df = get_submissions_df()

                # start over filling submissions with complete list
                submissions = []

                for camera_folder in camera_folders:
                    submission_obj = Submission.objects.filter(
                        camera_folder=camera_folder
                    ).last()
                    if submission_obj is None:
                        camera_id, date_str = camera_folder.split("_", 1)
                        camera_setup_date = datetime.datetime.strptime(  # noqa: F841
                            date_str, settings.CAMERA_SETUP_DATE_FORMAT
                        ).date()
                        matching_submissions = submissions_df.query(
                            "camera_id == @camera_id and date_and_time_of_camera_setup"
                            "_o.dt.date == @camera_setup_date"
                        )
                        submission_raw = matching_submissions.sort_values(
                            "CreationDate"
                        ).to_dict("records")[-1]
                        submission_cleaned = clean_submission(submission_raw)
                        submission = Submission.objects.create(
                            camera_folder=camera_folder,
                            submission_raw=submission_raw,
                            submission_cleaned=submission_cleaned,
                        )
                        submissions.append(submission)
                    else:
                        submissions.append(submission_obj)

            submission_attributes = {}
            for submission in submissions:
                # @TODO: attach multiple photos
                # For now we will just use the first, because it's not clear if it's
                # possible to attach multiple images to a webmap popup.
                # We can certainly find a way like composing an image ourselves,
                # but for now we will embed one image

                # @TODO: should we always download from MediaValet, regardless
                # of photo object exists?
                # Should we maybe never store photos at all?
                photo = submission.photos.first()
                if photo:
                    image_url = request.build_absolute_uri(photo.photo.url)
                else:
                    try:
                        # no photo object found, need to download from MediaValet
                        download_mediavalet_folder_into_submission(submission)
                        photo = submission.photos.first()
                        image_url = request.build_absolute_uri(photo.photo.url)
                    except KeyError:
                        # no photos yet in MediaValet
                        image_url = ""

                values = {}
                submission_attributes[submission.camera_folder] = values
                # submission_cleaned["x"][1] == ["X", -60.05227999999994]
                # we have to convert projection from map to globe
                values["x"], values["y"] = convert_coordinates_for_arcgis_map(
                    submission.submission_cleaned["x"][1],
                    submission.submission_cleaned["y"][1],
                )
                values["title"] = submission.camera_folder
                values["image_url"] = image_url
                values["description"] = submission.submission_cleaned["project_name"][1]

            map = Map.objects.create(submission_attributes=submission_attributes)
            map_json = interpolate_map_template(submission_attributes)
            map.webmap_json = map_json
            map.save()

            snippets = "\n".join(submission_attributes.keys())
            webmap = create_arcgis_webmap(
                map_json,
                title=f"Map for {', '.join(submission_attributes.keys())}",
                tags=list(submission_attributes.keys()),
                snippet=(
                    f"This map shows photos for the following camera traps: "
                    f"{snippets}"
                ),
            )

            map.webmap_url = webmap.homepage
            # store unique powerform_submission_id, to check powerform status
            powerform_submission_id = uuid.uuid4()
            map.powerform_submission_id = powerform_submission_id
            map.save()

            powerform_url = settings.DOCUSIGN_MAP_PUBLISH_POWERFORM_URL
            webmap_url_querystring = urlencode({"webmap_url": map.webmap_url})
            complete_powerform_url = (
                f"{powerform_url}&EnvelopeField_powerform_submission_id="
                f"{powerform_submission_id}&{webmap_url_querystring}"
            )

            return render(
                request,
                template_name="map/request.html",
                context={
                    "webmap_url": map.webmap_url,
                    "complete_powerform_url": complete_powerform_url,
                },
            )

    return render(
        request,
        # @TODO: add description to template what will happen when request is sent
        template_name="map/choose_submission_for_map.html",
        context={"form": form},
    )
