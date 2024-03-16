docker-build:
	docker-compose up --build

install:
	./deploy.sh

start-dev:
	poetry run python manage.py runserver

secretkey:
	poetry run python -c 'from django.utils.crypto import get_random_string; print(get_random_string(100))'

start-production:
	make migration
	poetry run gunicorn -b 0.0.0.0:8000 testapi.wsgi:application

migration:
	poetry run python manage.py migrate

test:
	poetry run python manage.py test
cov:
	poetry run coverage run  manage.py test
	poetry run coverage xml -o cobertura.xml