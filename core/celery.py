import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

app = Celery("core")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')


app.conf.beat_schedule = {
    'delete-unused-files-every-30-minutes': {
        'task': 'qr.tasks.delete_unused_files_task',  # Замените на фактический путь к вашей задаче
        'schedule': crontab(minute='*/30'),  # Выполняется каждые 30 минут
    },
}