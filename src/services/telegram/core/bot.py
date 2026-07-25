from aiogram import Bot, Dispatcher
from django.conf import settings

from services.telegram.handlers.routes import router


async def run_bot() -> None:
    """Create the dispatcher and start Telegram long polling."""
    token = settings.TELEGRAM_BOT_TOKEN  # type: ignore[misc]
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not configured")

    bot = Bot(token=token)
    dispatcher = Dispatcher()
    dispatcher.include_router(router=router)

    try:
        await dispatcher.start_polling(bot)
    finally:
        await bot.session.close()
