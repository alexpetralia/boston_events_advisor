from celery import Celery
from celery.schedules import crontab

celery = Celery('scraper')
celery.conf.update(
	BROKER_URL = "redis://",
	CELERY_RESULT_BACKEND = "redis://",
	CELERY_TASK_SERIALIZER = 'json',
	CELERY_RESULT_SERIALIZER = 'json',
	CELERY_ACCEPT_CONTENT = ['json'],
	CELERY_TIMEZONE = 'US/Eastern',
	CELERY_IMPORTS = ('scraper'),
	CONCURRENCY = 10,
	CELERY_BEAT_SCHEDULE = {
		'scraper': {
			'task': 'scraper.main',
			'schedule': crontab(hour=12, minute=0, day_of_week='sunday')
		}
	}
)