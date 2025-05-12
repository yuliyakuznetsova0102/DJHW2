from __future__ import absolute_import, unicode_literals
import os
from celery import Celery


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'DJHW2.settings')


app = Celery('config')


app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.beat_schedule = {
    'check-inactive-users': {
        'task': 'lms.tasks.check_inactive_users',
        'schedule': 86400,
    },
}
