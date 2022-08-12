import uuid

import requests
from django.conf import settings
from django.core.cache import cache
from django.core.files.base import ContentFile
from requests.auth import HTTPBasicAuth


def retrieve_mediavalet_token():
    res = requests.post(
        url="https://login.mediavalet.com/connect/token",
        data={
            "grant_type": "password",
            "username": settings.MEDIAVALET_USERNAME,
            "password": settings.MEDIAVALET_PASSWORD,
            "scope": "api",
        },
        auth=HTTPBasicAuth(
            settings.MEDIAVALET_CLIENT_ID, settings.MEDIAVALET_CLIENT_SECRET
        ),
    )
    return res.json()["access_token"]


def get_mediavalet_token():
    """Retrieve mediavalet-token from cache or set it.

    MediaValet auth token expires after 300s. We don't want to get a new token for
    each request, so we cache it and expire it after 240s, to avoid trying to use
    a stale token.
    """
    token = cache.get_or_set("mediavalet-token", retrieve_mediavalet_token, 240)
    return token


def create_mediavalet_folder(camera_folder):
    # @TODO: Ask user instead of just re-using existing folder
    existing_folder_id = get_mediavalet_folder_id(camera_folder)
    if existing_folder_id:
        return existing_folder_id

    new_folder_id = f"{uuid.uuid4()}"
    data = {
        "parentId": settings.MEDIAVAULT_BASE_CATEGORY,
        "description": camera_folder,
        "treeName": camera_folder,
        "categoryId": new_folder_id,
    }
    res = requests.post(
        "https://api.mediavalet.com/categories",
        headers={
            "Authorization": f"Bearer {get_mediavalet_token()}",
            "Ocp-Apim-Subscription-Key": settings.MEDIAVALET_SUBSCRIPTION_KEY,
        },
        data=data,
    )
    return new_folder_id if res.status_code == 201 else None


def delete_mediavalet_folder_by_id(folder_id):
    """Just for cleaning up.

    It looks like I can't delete categories/folders via the web interface?!
    """
    requests.delete(
        f"https://api.mediavalet.com/categories/{folder_id}",
        headers={
            "Authorization": f"Bearer {get_mediavalet_token()}",
            "Ocp-Apim-Subscription-Key": settings.MEDIAVALET_SUBSCRIPTION_KEY,
        },
    )


def get_mediavalet_folder_id(camera_folder):
    """Get MediaValet folder corresponsing to camera_folder from MediaValet API.

    MediaValet calls folders "Categories", and uses a UUID to identify them.
    There is a `treeName` attribute of folders that corresponds to their
    display name.
    It doesn't seem possible to search/retrieve by folder name, so we get a
    list of all subfolders of MEDIAVAULT_BASE_CATEGORY and iterate through
    the results to identify the correct category ID.
    """
    res = requests.get(
        f"https://api.mediavalet.com/folders/{settings.MEDIAVAULT_BASE_CATEGORY}/"
        f"subfolders",
        headers={
            "Authorization": f"Bearer {get_mediavalet_token()}",
            "Ocp-Apim-Subscription-Key": settings.MEDIAVALET_SUBSCRIPTION_KEY,
        },
    )
    subfolder_list = res.json()["payload"]
    try:
        category = next(x for x in subfolder_list if x["name"] == camera_folder)
    except StopIteration:
        return None

    return category["id"]


def get_mediavalet_assets(folder_id):
    """Retrieve a list of all assets belonging to a category/folder."""
    res = requests.get(
        f"https://api.mediavalet.com/categories/{folder_id}/assets",
        headers={
            "Authorization": f"Bearer {get_mediavalet_token()}",
            "Ocp-Apim-Subscription-Key": settings.MEDIAVALET_SUBSCRIPTION_KEY,
        },
    )
    asset_list = res.json()["payload"]["assets"]
    return asset_list


def get_attribute_ids_for_names(*args):
    """We have to look up the attribute IDs to be able to update attributes.

    Accepting multiple attribute names to avoid several calls.
    """
    res = requests.get(
        "https://api.mediavalet.com/attributes",
        headers={
            "Authorization": f"Bearer {get_mediavalet_token()}",
            "Ocp-Apim-Subscription-Key": settings.MEDIAVALET_SUBSCRIPTION_KEY,
        },
    )
    attribute_list = res.json()["payload"]

    attribute_ids = []
    for name in args:
        attribute_ids.append(next(x["id"] for x in attribute_list if x["name"] == name))
    return attribute_ids


def set_mediavalet_attribute(asset_id, attribute_id, value):
    """Set MediaValet attribute by attribute ID.

    Unfortunately, it seems there is a special case for "Description" (and
    other attributes?), which can't be set by /attributes/attribute_uuid
    like the other attributes have to be set, but rather by /description.
    """
    path = (
        f"/{settings.METADATA_DESCRIPTION_ATTRIBUTE.lower()}"
        if attribute_id == settings.METADATA_DESCRIPTION_ATTRIBUTE
        else f"/attributes/{attribute_id}"
    )
    requests.patch(
        f"https://api.mediavalet.com/assets/{asset_id}",
        headers={
            "Authorization": f"Bearer {get_mediavalet_token()}",
            "Ocp-Apim-Subscription-Key": settings.MEDIAVALET_SUBSCRIPTION_KEY,
        },
        json=[
            {
                "op": "replace",
                "path": path,
                "value": value,
            }
        ],
    )


def upload_file_to_mediavalet_folder(file_path, folder_id):
    """Uploading a file is a mult-step process."""
    filename = file_path.split("/")[-1]
    # filename without extension - filename could contain dots before extension
    file_title = ".".join(filename.split(".")[:-1])

    res = requests.post(
        "https://api.mediavalet.com/uploads",
        headers={
            "Authorization": f"Bearer {get_mediavalet_token()}",
            "Ocp-Apim-Subscription-Key": settings.MEDIAVALET_SUBSCRIPTION_KEY,
        },
        json={"filename": filename},
    )
    upload_url = res.json()["payload"]["uploadUrl"]
    new_asset_id = res.json()["payload"]["id"]

    # upload file to temporary Shared Access Signature (SAS) URL
    res = requests.put(
        upload_url,
        headers={"x-ms-blob-type": "BlockBlob", "Content-Type": "text/plain"},
        data=open(file_path, "rb").read(),
    )

    # add filename / title
    # @TODO: This step may be optional. Check if we need it
    res = requests.put(
        f"https://api.mediavalet.com/uploads/{new_asset_id}",
        headers={
            "Authorization": f"Bearer {get_mediavalet_token()}",
            "Ocp-Apim-Subscription-Key": settings.MEDIAVALET_SUBSCRIPTION_KEY,
        },
        json={"filename": filename, "title": file_title},
    )

    # add uploaded asset to category
    res = requests.post(
        f"https://api.mediavalet.com/uploads/{new_asset_id}/categories",
        headers={
            "Authorization": f"Bearer {get_mediavalet_token()}",
            "Ocp-Apim-Subscription-Key": settings.MEDIAVALET_SUBSCRIPTION_KEY,
        },
        json=[folder_id],
    )

    # "approve" uploaded asset
    res = requests.patch(
        f"https://api.mediavalet.com/uploads/{new_asset_id}",
        headers={
            "Authorization": f"Bearer {get_mediavalet_token()}",
            "Ocp-Apim-Subscription-Key": settings.MEDIAVALET_SUBSCRIPTION_KEY,
        },
        json=[{"op": "replace", "path": "/status", "value": 1}],
    )


def upload_submission_photos_to_mediavalet(submission):
    """Create folder for submission and upload photos"""
    new_folder_id = create_mediavalet_folder(submission.camera_folder)
    photos = submission.photos.all()
    for photo in photos:
        upload_file_to_mediavalet_folder(photo.photo.path, new_folder_id)


def tag_mediavalet_attributes(attributes_to_tag, asset_ids):
    """Tag MediaValet assets with attributes.

    attributes_to_tag is a dict with Attribute names and values.
    asset_ids is a list with IDs of assets we want to tag.
    """
    # we have to get attribute_ids for attribute names, can't use names directly.
    # Unfortunately, there seems to be a special case with "Description".
    # While the Description attribute has a ID as well, it seems that while
    # other attributes have to be set with `{"path": "/attribute/attribute_uuid"}`,
    # "Description" has to be set with `{"path": "/Description"}`.
    # So we have to replace replace the ID for "Description" attribute with
    # `"Description"``
    attribute_names = list(attributes_to_tag.keys())
    attribute_ids = get_attribute_ids_for_names(*attribute_names)
    descr_idx = attribute_names.index(settings.METADATA_DESCRIPTION_ATTRIBUTE)
    del attribute_ids[descr_idx]
    attribute_ids.insert(descr_idx, settings.METADATA_DESCRIPTION_ATTRIBUTE)

    attribute_label_id = {
        label: attribute_id
        for (label, attribute_id) in zip(attribute_names, attribute_ids)
    }

    for asset_id in asset_ids:
        for label, value in attributes_to_tag.items():
            set_mediavalet_attribute(asset_id, attribute_label_id[label], value)


def download_asset_from_mediavalet_by_id(asset_id):
    res = requests.post(
        "https://api.mediavalet.com/downloads/validate",
        headers={
            "Authorization": f"Bearer {get_mediavalet_token()}",
            "Ocp-Apim-Subscription-Key": settings.MEDIAVALET_SUBSCRIPTION_KEY,
        },
        json={"isDirectDownload": "true"},
    )
    download_link = res.json()["payload"]["downloadLink"]

    res = requests.post(
        f"https://api.mediavalet.com/{download_link}",
        headers={
            "Authorization": f"Bearer {get_mediavalet_token()}",
            "Ocp-Apim-Subscription-Key": settings.MEDIAVALET_SUBSCRIPTION_KEY,
        },
        json={
            "attributeIdValues": {},
            "assetId": asset_id,
        },
    )
    download_url = res.json()["payload"]["sasUrl"]

    res = requests.get(
        download_url,
        # @TODO: are these headers actually necessary?
        headers={"x-ms-blob-type": "BlockBlob", "Content-Type": "text/plain"},
    )
    return res.content
    # the MediaValet webinterface also does an empty request to
    # /assets/{asset_id}/downloaded
    # Don't think we have to do that here as it's not a user download


def download_mediavalet_folder_into_submission(submission):
    mediavalet_folder_id = get_mediavalet_folder_id(submission.camera_folder)
    asset_list = get_mediavalet_assets(mediavalet_folder_id)

    assets = ((x["file"]["fileName"], x["id"]) for x in asset_list)

    for asset_title, asset_id in assets:
        file_content = download_asset_from_mediavalet_by_id(asset_id)
        photo = submission.photos.create()
        photo.photo.save(asset_title, ContentFile(file_content))
