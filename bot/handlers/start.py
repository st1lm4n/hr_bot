from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from bot.keyboards import cancel_keyboard
from bot.states import Survey
from bot.keyboards import cancel_keyboard, remove_keyboard

router = Router()

# Список вопросов (индексируем с 0)
QUESTIONS = [
    "1. Расскажите о проекте, в котором вы использовали AI для ускорения разработки. Что именно делали и как AI помог?",
    "2. Какой AI-инструмент вы используете чаще всего и зачем? Приведите пример конкретной задачи.",
    "3. Опишите случай, когда сгенерированный AI код или ответ содержал ошибку. Как вы это обнаружили и исправили?",
    "4. Как бы вы использовали AI для улучшения функциональности этого Telegram-бота? Предложите 1–2 идеи.",
    "5. Как вы проверяете качество кода или текста, созданного AI? Есть ли у вас чек-лист или подход?",
    "6. Что вы думаете о будущем AI в разработке ПО? Какие задачи, по вашему мнению, AI никогда не сможет полностью заменить?",
    "7. (Опционально) Пришлите ссылку на что-то, что вы создали с активным использованием AI (код, статья, бот и т.п.).",
]


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "👋 Привет! Я бот для первичного скрининга AI-first разработчиков.\n\n"
        "Я задам несколько вопросов. Постарайтесь отвечать развёрнуто — это поможет точнее оценить ваш уровень.\n"
        "Если захотите прервать опрос, нажмите кнопку «Отменить опрос».",
        reply_markup=cancel_keyboard,
    )
    await state.set_state(Survey.q1)
    await message.answer(QUESTIONS[0])


@router.message(Command("cancel"))
@router.message(lambda message: message.text == "❌ Отменить опрос")
async def cmd_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Опрос отменён. Чтобы начать заново, введите /start.",
        reply_markup=remove_keyboard,
    )
