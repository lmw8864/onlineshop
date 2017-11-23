import os
from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'onlineshop.settings')

app = Celery('onlineshop')

app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

# python manage.py runserver
# rabbitmq-server
# celery -A onlineshop worker -l info
# celery flower -A onlineshop


# http://docs.celeryproject.org/en/latest/getting-started/next-steps.html#using-celery-in-your-application