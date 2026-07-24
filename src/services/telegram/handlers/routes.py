from aiogram import Router

from services.telegram.handlers.companies.routes import (
    router as companies_router,
)
from services.telegram.handlers.main.routes import router as main_router
from services.telegram.handlers.persons.routes import router as persons_router

router = Router(name="telegram")
router.include_router(main_router)
router.include_router(companies_router)
router.include_router(persons_router)
