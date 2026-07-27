from django_project.settings import env

TELEGRAM_BOT_TOKEN = env("TELEGRAM_BOT_TOKEN")
TELEGRAM_PAGE_SIZE = 5

TELEGRAM_ALLOWED_USER_IDS = env.list(
    "TELEGRAM_ALLOWED_USER_IDS", cast=int, default=[]
)
TELEGRAM_ALLOWED_CHAT_IDS = env.list(
    "TELEGRAM_ALLOWED_CHAT_IDS", cast=int, default=[]
)
