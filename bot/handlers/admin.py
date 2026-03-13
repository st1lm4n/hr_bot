from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from bot.config import ADMIN_IDS, GOOGLE_SHEETS_CREDENTIALS, GOOGLE_SHEETS_URL
import gspread
from google.oauth2.service_account import Credentials

router = Router()

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def get_sheet_data():
    """Синхронно получает данные из таблицы."""
    creds = Credentials.from_service_account_file(
        GOOGLE_SHEETS_CREDENTIALS, scopes=SCOPES
    )
    client = gspread.authorize(creds)
    sheet = client.open_by_url(GOOGLE_SHEETS_URL).sheet1
    return sheet.get_all_values()


@router.message(Command("admin"), F.from_user.id.in_(ADMIN_IDS))
async def admin_help(message: Message):
    text = (
        "🔧 <b>Админ-команды:</b>\n"
        "/admin_stats — статистика по кандидатам\n"
        "/admin_hot — список горячих кандидатов"
    )
    await message.answer(text, parse_mode="HTML")


@router.message(Command("admin_stats"), F.from_user.id.in_(ADMIN_IDS))
async def admin_stats(message: Message):
    try:
        data = get_sheet_data()
        if len(data) <= 1:  # только заголовки
            await message.answer("Пока нет данных о кандидатах.")
            return
        # Заголовки: [timestamp, telegram_id, full_name, username, q1..q7, depth, critical, creativity, total, hot]
        # Индексы: total_score = -2, hot = -1
        total_scores = []
        hot_count = 0
        candidates = []
        for row in data[1:]:
            if len(row) < 11:
                continue
            try:
                total = int(row[-2])
                total_scores.append(total)
                if row[-1] == "Да":
                    hot_count += 1
                candidates.append(
                    {
                        "name": row[2],
                        "username": row[3],
                        "total": total,
                        "hot": row[-1] == "Да",
                    }
                )
            except:
                continue
        if not total_scores:
            await message.answer("Нет корректных записей.")
            return
        avg_score = sum(total_scores) / len(total_scores)
        # Топ-3 по убыванию total
        top3 = sorted(candidates, key=lambda x: x["total"], reverse=True)[:3]
        top_text = "\n".join(
            [
                f"{i + 1}. {c['name']} (@{c['username']}) — {c['total']} баллов"
                for i, c in enumerate(top3)
            ]
        )
        reply = (
            f"📊 <b>Статистика опросов</b>\n"
            f"Всего записей: {len(total_scores)}\n"
            f"Средний балл: {avg_score:.2f}\n"
            f"Горячих кандидатов: {hot_count}\n\n"
            f"🏆 <b>Топ-3 кандидата:</b>\n{top_text}"
        )
        await message.answer(reply, parse_mode="HTML")
    except Exception as e:
        await message.answer(f"Ошибка при получении статистики: {e}")


@router.message(Command("admin_hot"), F.from_user.id.in_(ADMIN_IDS))
async def admin_hot(message: Message):
    try:
        data = get_sheet_data()
        if len(data) <= 1:
            await message.answer("Нет данных.")
            return
        hot_list = []
        for row in data[1:]:
            if len(row) >= 11 and row[-1] == "Да":
                hot_list.append(f"{row[2]} (@{row[3]}) — {row[-2]} баллов")
        if hot_list:
            await message.answer(
                "🔥 <b>Горячие кандидаты:</b>\n" + "\n".join(hot_list),
                parse_mode="HTML",
            )
        else:
            await message.answer("Пока нет горячих кандидатов.")
    except Exception as e:
        await message.answer(f"Ошибка: {e}")
