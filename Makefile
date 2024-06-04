.PHONY: setup_and_run load superuser run static

setup_and_run: static load superuser run

run:
	pipenv run celery --app core.celery worker --purge --beat --loglevel DEBUG --autoscale=0,10 --without-gossip --without-mingle --without-heartbeat & pipenv run ./manage.py runserver 0.0.0.0:8000

load:
	pipenv run python manage.py makemigrations
	pipenv run python manage.py migrate

static:
	pipenv run python manage.py collectstatic --noinput

superuser:
	pipenv run python manage.py shell -c "import os; from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@example.com', os.getenv('DJANGO_SUPERUSER_PASSWORD'))"
