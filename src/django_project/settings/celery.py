from celery.schedules import crontab

from django_project.settings import TIME_ZONE, env

CELERY_BROKER_URL = env("CELERY_BROKER_URL")
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_TIME_LIMIT = env.int("CELERY_TASK_TIME_LIMIT")
CELERY_TASK_ACKS_LATE = False
CELERY_RESULT_BACKEND = None
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_TASK_DEFAULT_EXCHANGE_TYPE = "direct"
CELERY_BROKER_TRANSPORT_OPTIONS = {
    "visibility_timeout": env.int("CELERY_VISIBILITY_TIMEOUT"),
    "polling_interval": env.float("CELERY_POLLING_INTERVAL"),
}
CELERY_BEAT_SCHEDULE = {
    "run-weekly-scans": {
        "task": "scans.run_weekly",
        "schedule": crontab(day_of_week="saturday", hour=0, minute=0),
    },
}
CELERY_IMPORTS = [
    "services.celery_tasks.dummy",
    "services.celery_tasks.scans",
]
