"""Extend base.py settings file which contains the minimum for Docker build."""
from .base import BASE_DIR, INSTALLED_APPS, STATIC_ROOT, STATIC_URL  # noqa: F401
import environ


env = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)
env.escape_proxy = True


DEBUG = env("DEBUG")
SECRET_KEY = env("SECRET_KEY")
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS")


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "geochimp.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "geochimp.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    "default": env.db_url(
        "DATABASE_URL", default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}"
    )
}


# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttribute"
        "SimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


MEDIA_ROOT = BASE_DIR / "media"
MEDIA_URL = "/media/"


INTERNAL_IPS = [
    "127.0.0.1",
]


# django-tailwind settings begin
TAILWIND_APP_NAME = "theme"
if DEBUG:
    INSTALLED_APPS += ["django_browser_reload"]
    MIDDLEWARE += [
        "django_browser_reload.middleware.BrowserReloadMiddleware",
    ]
# django-tailwind settings end


# crispy-tailwind config begin
CRISPY_ALLOWED_TEMPLATE_PACKS = "tailwind"
CRISPY_TEMPLATE_PACK = "tailwind"
# crispy-tailwind config end


# photo_tagger settings begin
# whether to use e.g. CAMERA1_20220801 or CAMERA1_4_08_2022
CAMERAFOLDER_REGEX = env("CAMERAFOLDER_REGEX")
# depending on format chosen above, we have to parse
# e.g. 20220801 or 4_08_2022 to identify Survey123 submission
CAMERA_SETUP_DATE_FORMAT = env("CAMERA_SETUP_DATE_FORMAT")

# which fields from survey123 submissions to set on photo metadata, mapped
# to label for metadata attribute (e.g. `project_name` will be set as "Project Name")
# When parsed by django-environ, the variable below will be a dict like:
# {'project_name': 'Project Name', 'your_name': 'Forest Monitor name', ...}
# If a value is a choice field with "other" option, use the field name with "_other".
# this way, we don't need to check all fields if there is an "other" option, but rather
# just have to handle those.
# If a value contains a mapping of values, like `SHAPE`, provide the attributes you
# want to extract separated by ~, e.g. SHAPE=x~y
METADATA_ATTRIBUTES = env.dict("METADATA_ATTRIBUTES")
# MediaValet only supports a restricted set of attributes, like X,Y (GPS coordinates)
# Unless more attributes are added in MediaValet config, we can only set those.
# For now, we will set all fields in METADATA_ATTRIBUTES_DIRECT directly. Fields in
# METADATA_ATTRIBUTES but not in METADATA_ATTRIBUTES_DIRECT will be added to the
# "Description" field
METADATA_ATTRIBUTES_DIRECT = env.list("METADATA_ATTRIBUTES_DIRECT")
# in case this attribute gets renamed
METADATA_DESCRIPTION_ATTRIBUTE = env("METADATA_DESCRIPTION_ATTRIBUTE")

# whether to overwrite existing assets when adding GPS attributes
# If yes, asset files will be deleted and re-uploaded with GPS coordinates metadata
# If no, only the attributes will be updated in MediaValet, files will remain untouched
# This could be preferred if e.g. the asset IDs are already used somewhere
# @TODO: is it possible to update assets in-place? Or download->delete->upload?
# @TODO: actually implement this
OVERWRITE_ASSETS_WITH_GPS_EXIF = env.bool("OVERWRITE_ASSETS_WITH_GPS_EXIF")
# to be able to allow updating of assets without decision-maker sign-off
REQUIRE_DOCUSIGN_FOR_ASSET_TAGGING = env.bool("REQUIRE_DOCUSIGN_FOR_ASSET_TAGGING")
# @TODO: actually implement this
REQUIRE_DOCUSIGN_FOR_ASSET_UPLOAD = env.bool("REQUIRE_DOCUSIGN_FOR_ASSET_UPLOAD")
# photo_tagger settings end


# 3rd-party config begin
DOCUSIGN_API_ACCOUNT_ID = env("DOCUSIGN_API_ACCOUNT_ID")
DOCUSIGN_USER_ID = env("DOCUSIGN_USER_ID")
DOCUSIGN_INTEGRATION_KEY = env("DOCUSIGN_INTEGRATION_KEY")
DOCUSIGN_OAUTH_HOST_NAME = env("DOCUSIGN_OAUTH_HOST_NAME")
DOCUSIGN_BASE_URL = env("DOCUSIGN_BASE_URL")
# to be used to specify which decision-maker should sign which form
# should be a mapping later, to specify different recipients for
# different workflows
# @TODO: actually use this setting
DOCUSIGN_RECIPIENTS = env.list("DOCUSIGN_RECIPIENTS")
DOCUSIGN_ASSET_TAGGING_POWERFORM_URL = env("DOCUSIGN_ASSET_TAGGING_POWERFORM_URL")
DOCUSIGN_MAP_PUBLISH_POWERFORM_URL = env("DOCUSIGN_MAP_PUBLISH_POWERFORM_URL")

ESRI_SURVEY_ID = env("ESRI_SURVEY_ID")
ESRI_USERNAME = env("ESRI_USERNAME")
ESRI_PASSWORD = env("ESRI_PASSWORD")

# which category/folder to use as parent for new categories (folders)
MEDIAVAULT_BASE_CATEGORY = env("MEDIAVAULT_BASE_CATEGORY")
MEDIAVALET_SUBSCRIPTION_KEY = env("MEDIAVALET_SUBSCRIPTION_KEY")
MEDIAVALET_CLIENT_ID = env("MEDIAVALET_CLIENT_ID")
MEDIAVALET_CLIENT_SECRET = env("MEDIAVALET_CLIENT_SECRET")
MEDIAVALET_USERNAME = env("MEDIAVALET_USERNAME")
MEDIAVALET_PASSWORD = env("MEDIAVALET_PASSWORD")
# 3rd-party config end
