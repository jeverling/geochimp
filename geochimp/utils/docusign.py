import datetime
from urllib.parse import parse_qs, urlparse

import docusign_esign as ds
from django.conf import settings
from django.core.cache import cache


def retrieve_docusign_token():
    api_client = ds.ApiClient()
    token = api_client.request_jwt_user_token(
        client_id=settings.DOCUSIGN_INTEGRATION_KEY,
        user_id=settings.DOCUSIGN_USER_ID,
        oauth_host_name=settings.DOCUSIGN_OAUTH_HOST_NAME,
        private_key_bytes=open(settings.BASE_DIR / "private.key", "rb").read(),
        expires_in=3600,
    )
    return token.access_token


def get_docusign_token():
    """Retrieve DocuSign token from cache or set it.

    DocuSign auth token expires after 3600, regardless of what is passed as
    `expires_in`. We don't want to get a new token for each request, so we cache
    it and expire it after 3540s, to avoid trying to use a stale token.
    """
    token = cache.get_or_set("docusign-token", retrieve_docusign_token, 3540)
    return token


def get_powerform_id_from_url(powerform_url):
    power_form_id = parse_qs(urlparse(powerform_url).query)["PowerFormId"][0]
    return power_form_id


def get_api_client():
    api_client = ds.ApiClient(host=f"{settings.DOCUSIGN_BASE_URL}/restapi")
    api_client.set_default_header("Authorization", f"Bearer {get_docusign_token()}")
    return api_client


def search_envelope_by_custom_field(field_name, field_value):
    envelope_api = ds.apis.EnvelopesApi(get_api_client())
    envelope = envelope_api.list_status_changes(
        settings.DOCUSIGN_API_ACCOUNT_ID,
        custom_field=f"{field_name}={field_value}",
        # @TODO: Use a better value here, maybe the date of TagRequest object creation?
        from_date=datetime.datetime(2022, 1, 1),
        # @TODO: Think about whether we could end up with more than 1 envelopes here,
        # and how to handle this case
    ).envelopes[0]
    return envelope


def get_powerform_form_data_for_envelope_id(envelope_id):
    """Get powerform_data for envelope instance.

    We can search envelopes for custom envelope fields. With the envelope_id
    we can then filter the powerform submissions.
    """
    powerform_api = ds.PowerFormsApi(get_api_client())
    powerform_data = powerform_api.get_power_form_data(
        settings.DOCUSIGN_API_ACCOUNT_ID,
        # @TODO: cache this function
        get_powerform_id_from_url(settings.DOCUSIGN_ASSET_TAGGING_POWERFORM_URL),
    )
    powerform_submission = next(
        x for x in powerform_data.envelopes if x.to_dict()["envelope_id"] == envelope_id
    )

    # recipients should be ordered correctly
    form_data = {x.name: x.value for x in powerform_submission.recipients[0].form_data}

    return form_data
