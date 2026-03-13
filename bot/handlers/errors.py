from aiogram import Router
from aiogram.types import ErrorEvent
import logging

router = Router()


@router.errors()
async def error_handler(event: ErrorEvent):
    logging.error(f"Update {event.update} caused error {event.exception}")
    # Здесь можно добавить уведомление админу об ошибке, если нужно
