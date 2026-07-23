import asyncio
import os
from typing import TYPE_CHECKING

import django

if TYPE_CHECKING:
    from services.telegram.core.environment import configure_python_path
else:
    from core.environment import configure_python_path


def main() -> None:
    """Bootstrap Django and run the Telegram polling process."""
    configure_python_path()
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_project.settings")
    django.setup()

    from services.telegram.core.bot import run_bot

    asyncio.run(run_bot())


if __name__ == "__main__":
    main()
