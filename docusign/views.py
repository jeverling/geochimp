from django.conf import settings
from django.shortcuts import get_object_or_404, render
from geochimp.utils.arcgis import publish_arcgis_webmap
from geochimp.utils.common import get_choice_value_for_label
from geochimp.utils.docusign import (
    get_powerform_form_data_for_envelope_id,
    search_envelope_by_custom_field,
)
from geochimp.utils.mediavalet import (
    get_mediavalet_assets,
    get_mediavalet_folder_id,
    tag_mediavalet_attributes,
)
from map.models import Map
from photo_tagger.models import STATUS_CHOICES, TagRequest


def tag_powerform_check(request, powerform_submission_id):
    """Check if Powerform has been signed."""
    tr = get_object_or_404(TagRequest, powerform_submission_id=powerform_submission_id)

    envelope = search_envelope_by_custom_field(
        "powerform_submission_id", powerform_submission_id
    )
    envelope_status = envelope.status
    choice_value = get_choice_value_for_label(STATUS_CHOICES, envelope_status)
    tr.status = choice_value
    tr.save()

    # @TODO: Think about if this could ever change. VERY unlikely
    if envelope_status != "completed":
        return render(
            request,
            template_name="docusign/status_waiting.html",
            context={"envelope_status": envelope_status},
        )

    # we have a completed envelope, going to extract the potentially modified
    # form_data from it and use it to tag assets inside the camera_folder
    form_data = get_powerform_form_data_for_envelope_id(envelope.envelope_id)
    tr.powerform_data_edited = form_data
    tr.save()

    attributes_direct = settings.METADATA_ATTRIBUTES_DIRECT
    attributes_to_tag = {}

    # handle attributes we set directly, like x, y
    for attribute in attributes_direct:
        # we tag assets with `X,Y`, whereas in Survey123 it`s `x,y`
        # @TODO: make sure this works for attributes added later
        attribute_label = attribute.upper()
        attributes_to_tag[attribute_label] = form_data[attribute_label]
    attributes_to_tag[settings.METADATA_DESCRIPTION_ATTRIBUTE] = form_data[
        settings.METADATA_DESCRIPTION_ATTRIBUTE
    ]

    # @TODO: DRY all of this!
    submission = tr.submission
    mediavalet_folder = get_mediavalet_folder_id(submission.camera_folder)
    asset_list = get_mediavalet_assets(mediavalet_folder)
    asset_ids = tuple(x["id"] for x in asset_list)

    tag_mediavalet_attributes(attributes_to_tag, asset_ids)
    return render(
        request,
        template_name="photo_tagger/success.html",
        context={
            "message": f"Successfully tagged assets for " f"{submission.camera_folder}",
        },
    )


def map_powerform_check(request, powerform_submission_id):
    """Check if Powerform has been signed."""

    map = get_object_or_404(Map, powerform_submission_id=powerform_submission_id)

    envelope = search_envelope_by_custom_field(
        "powerform_submission_id", powerform_submission_id
    )
    envelope_status = envelope.status
    choice_value = get_choice_value_for_label(STATUS_CHOICES, envelope_status)
    map.status = choice_value
    map.save()

    # @TODO: Think about if this could ever change. VERY unlikely
    if envelope_status != "completed":
        return render(
            request,
            template_name="docusign/status_waiting.html",
            context={"envelope_status": envelope_status},
        )

    # we have a completed envelope, we can publish the map! :)
    publish_arcgis_webmap(map)

    return render(
        request,
        template_name="map/success.html",
        context={
            "message": "Map publish request was granted! Find your public map below.",
            "webmap_public_url": map.webmap_public_url,
        },
    )
