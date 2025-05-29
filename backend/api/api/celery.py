import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "api.settings.development")

app = Celery("api")
app.config_from_object("django.conf:settings", namespace="CELERY")

app.conf.enable_utc = False
app.conf.update(timezone="Asia/Dhaka")

app.autodiscover_tasks()
