import asyncio
import datetime
import gspread
from google.oauth2.service_account import Credentials
from bot.config import GOOGLE_SHEETS_CREDENTIALS, GOOGLE_SHEETS_URL

# Необходимые права доступа для работы с Google Sheets
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


async def save_to_sheets(
    telegram_id: int,
    full_name: str,
    username: str,
    answers: list,
    scores: dict,
    total: int,
    hot: bool,
):
    """
    Сохраняет результаты опроса в Google Sheets.
    Выполняется в отдельном потоке, чтобы не блокировать асинхронный цикл.
    """

    def _sync():
        # Явно указываем scopes при создании учётных данных
        creds = Credentials.from_service_account_file(
            GOOGLE_SHEETS_CREDENTIALS, scopes=SCOPES
        )
        client = gspread.authorize(creds)
        sheet = client.open_by_url(GOOGLE_SHEETS_URL).sheet1

        # Подготовка строки
        row = [
            datetime.datetime.now().isoformat(),
            telegram_id,
            full_name,
            username,
            *answers,  # все ответы на вопросы (7 штук)
            scores.get("depth_score"),
            scores.get("critical_score"),
            scores.get("creativity_score"),
            total,
            "Да" if hot else "Нет",
        ]
        sheet.append_row(row)

    await asyncio.to_thread(_sync)
