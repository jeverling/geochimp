"""Minimal settings, to make Django management commands work during Docker build.

Most settings use variables, so Django won't run e.g. `collectstatic` without
those variables. Since we don't want to pass all of them as ARGs to the Dockerfile,
we use a base settings file, which includes the necessary things to allow
`collectstatic` during build.
We do need `INSTALLED_APPS` so the staticfiles framework can determine which files
to collect.
"""
from pathlib import Path

# required for Docker build, will be overwritten in settings.py file
SECRET_KEY = "my_secret_key"  # noqa: S105

BASE_DIR = Path(__file__).resolve().parent.parent.parent

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # 3rd-party apps
    "tailwind",
    "crispy_forms",
    "crispy_tailwind",
    # custom apps
    "theme",
    "photo_tagger",
    "docusign",
    "map",
]

STATIC_ROOT = BASE_DIR / "static"
STATIC_URL = "static/"
