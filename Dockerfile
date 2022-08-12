FROM python:3.10-slim
LABEL maintainer="Jesaja Everling <jeverling@gmail.com>"

RUN useradd --create-home geochimp

RUN apt-get update --yes --quiet && apt-get install --yes --quiet --no-install-recommends \
    build-essential \
    # necessary for arcgis/gssapi packages
    libkrb5-dev \
    # pillow dependencies
    libjpeg62-turbo-dev zlib1g-dev libtiff-opengl libtiff-tools libfreetype6-dev liblcms-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN mkdir /app/static /app/media && chown geochimp:geochimp /app/static /app/media

USER geochimp

COPY requirements/base.txt /tmp/requirements.txt

RUN pip install --no-cache-dir --no-warn-script-location -r /tmp/requirements.txt

COPY --chown=geochimp:geochimp . /app

# use bare-bones settings file for running management commands during Docker build,
# without requiring all environment variables passed as build ARGs
RUN DJANGO_SETTINGS_MODULE=geochimp.settings.base python manage.py collectstatic --noinput --clear

CMD set -xe; python manage.py migrate --noinput; /home/geochimp/.local/bin/gunicorn -b 0.0.0.0:8000 -t 300 geochimp.wsgi:application
