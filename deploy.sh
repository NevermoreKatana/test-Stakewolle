#!/usr/bin/env bash

poetry install
poetry run python manage.py collectstatic --no-input
poetry run python manage.py migrate