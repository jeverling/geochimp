import datetime
import json
from urllib.parse import urljoin, urlparse

import pyproj
from django.conf import settings
from map.map_template import map_template, single_feature_template

import arcgis
from arcgis.gis import GIS


def get_submissions_df():
    gis = GIS(username=settings.ESRI_USERNAME, password=settings.ESRI_PASSWORD)
    survey_manager = arcgis.apps.survey123.SurveyManager(gis)

    survey = survey_manager.get(settings.ESRI_SURVEY_ID)
    survey_data_df = survey.download("DF")
    return survey_data_df


def get_submissions_for_camera_folder(camera_folder):
    camera_id, date_str = camera_folder.split("_", 1)
    camera_setup_date = datetime.datetime.strptime(  # noqa: F841
        date_str, settings.CAMERA_SETUP_DATE_FORMAT
    ).date()

    survey_data_df = get_submissions_df()

    matching_submissions = survey_data_df.query(
        "camera_id == @camera_id and date_and_time_of_camera_setup_o.dt.date "
        "== @camera_setup_date"
    )
    return matching_submissions


def clean_submission(submission_raw):
    """Extract relevant fields from submission, store with labels.

    Store (label, value) tuples for every relevant field in submission
    e.g. {"name_of_the_area_deployed": ("Name of the area deployed",
                                        "Chimpanzee retreat zone 1")}

    There are two special cases.
    First, some choices can have "Other" options.
    For those, the code will determine whether one of the choices was picked
    or "Other" was provided

    The second special case are fields like `SHAPE`, which contain a map of values,
    e.g.  'SHAPE': {'x': -32.44150999999994, 'y': -3.849019999999944, ...}
    Here, `METADATA_ATTRIBUTES` should specify which values to extract.
    E.g. `SHAPE=x~y` will extract `x` and `y` from `SHAPE`, and store those with
    the uppercase key as label.
    """
    metadata_fields = settings.METADATA_ATTRIBUTES

    submission_cleaned = {}
    for submission_field, label in metadata_fields.items():
        if "~" in label:
            # we are dealing with a special value like SHAPE, have to extract values
            x, y = label.split("~")
            submission_cleaned[x] = (x.upper(), submission_raw[submission_field][x])
            submission_cleaned[y] = (y.upper(), submission_raw[submission_field][y])
            continue

        if submission_field.endswith("_other"):
            if submission_raw[submission_field]:
                # we have the "Other" option set, so use that
                value = submission_raw[submission_field]
            else:
                # we have to use the option without "_other",
                # e.g.  `camera_attached_to_` instead of `camera_attached_to__other`
                value = submission_raw[submission_field.removesuffix("_other")]
            submission_cleaned[submission_field] = (label, value)
            continue

        submission_cleaned[submission_field] = (
            label,
            submission_raw[submission_field],
        )

    return submission_cleaned


def convert_coordinates_for_arcgis_map(x, y):
    """Convert from GPS coordinates to arcgis map projections.

    e.g. (7.1396999999998805,50.69659999999914) => (794787.768416722, 6567800.23790998)
    """
    proj = pyproj.Transformer.from_crs(4326, 3857, always_xy=True)

    return proj.transform(x, y)


def interpolate_map_template(submission_attributes):
    """Returns map JSON with features for each submission."""
    feature_list = []
    for value_dict in submission_attributes.values():
        feature_str = single_feature_template % value_dict
        feature_list.append(json.loads(feature_str))

    map_dict = json.loads(map_template)
    map_dict["operationalLayers"][0]["featureCollection"]["layers"][0]["featureSet"][
        "features"
    ] = feature_list

    return map_dict
    # @TODO: remove this
    return json.dumps(map_dict)


def create_arcgis_webmap(map_json, title, tags, snippet):
    gis = GIS(username=settings.ESRI_USERNAME, password=settings.ESRI_PASSWORD)

    webmap_dict = {
        "type": "Web Map",
        "title": title,
        "tags": tags,
        "snippet": snippet,
        "text": map_json,
    }

    new_webmap = gis.content.add(item_properties=webmap_dict)
    return new_webmap


def publish_arcgis_webmap(map):
    """Publish a map object."""
    gis = GIS(username=settings.ESRI_USERNAME, password=settings.ESRI_PASSWORD)
    webmap_url = map.webmap_url
    webmap_id = urlparse(webmap_url).query.split("=")[-1]

    webmap = gis.content.get(webmap_id)
    webmap.share(everyone=True)

    # I couldn't get webmap.url, even after publishing. Maybe it takes time.
    # Anyway, we should be able to just compose it
    # private /home/item.html?id=<some_id>
    # public /apps/mapviewer/index.html?webmap=<some_id>
    webmap_public_url = urljoin(
        webmap_url, f"/apps/mapviewer/index.html?webmap={webmap_id}"
    )

    map.webmap_public_url = webmap_public_url
    map.save()

    return webmap_public_url
