#!/usr/bin/env bash

poetry install
poetry run python manage.py migrate