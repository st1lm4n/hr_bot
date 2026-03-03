from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from bot.states import Survey
from bot.keyboards import cancel_keyboard, remove_keyboard
from bot.utils.validators import is_valid_url
from bot.utils.llm import evaluate_answers
from bot.utils.sheets import save_to_sheets
from bot.config import HOT_THRESHOLD, ADMIN_IDS
from bot.handlers.start import QUESTIONS
from bot.utils.rate_limiter import is_allowed
import re
from bot.utils.scoring import calculate_total
from bot.utils.anti_cheat import detect_ai_like_text, is_low_effort

router = Router()


# Обработчики для каждого вопроса (FSM)
@router.message(Survey.q1)
async def answer_q1(message: Message, state: FSMContext):
    if not message.text or len(message.text.strip()) < 10:
        await message.answer(
            "Пожалуйста, дайте более развёрнутый ответ (минимум 10 символов)."
        )
        return
    await state.update_data(q1=message.text.strip())
    await state.set_state(Survey.q2)
    await message.answer(QUESTIONS[1])


@router.message(Survey.q2)
async def answer_q2(message: Message, state: FSMContext):
    if not message.text or len(message.text.strip()) < 10:
        await message.answer("Пожалуйста, дайте более развёрнутый ответ.")
        return
    await state.update_data(q2=message.text.strip())
    await state.set_state(Survey.q3)
    await message.answer(QUESTIONS[2])


@router.message(Survey.q3)
async def answer_q3(message: Message, state: FSMContext):
    if not message.text or len(message.text.strip()) < 10:
        await message.answer("Пожалуйста, дайте более развёрнутый ответ.")
        return
    await state.update_data(q3=message.text.strip())
    await state.set_state(Survey.q4)
    await message.answer(QUESTIONS[3])


@router.message(Survey.q4)
async def answer_q4(message: Message, state: FSMContext):
    if not message.text or len(message.text.strip()) < 10:
        await message.answer("Пожалуйста, дайте более развёрнутый ответ.")
        return
    await state.update_data(q4=message.text.strip())
    await state.set_state(Survey.q5)
    await message.answer(QUESTIONS[4])


@router.message(Survey.q5)
async def answer_q5(message: Message, state: FSMContext):
    if not message.text or len(message.text.strip()) < 10:
        await message.answer("Пожалуйста, дайте более развёрнутый ответ.")
        return
    await state.update_data(q5=message.text.strip())
    await state.set_state(Survey.q6)
    await message.answer(QUESTIONS[5])


@router.message(Survey.q6)
async def answer_q6(message: Message, state: FSMContext):
    if not message.text or len(message.text.strip()) < 10:
        await message.answer("Пожалуйста, дайте более развёрнутый ответ.")
        return
    await state.update_data(q6=message.text.strip())
    await state.set_state(Survey.link)
    await message.answer(QUESTIONS[6])


@router.message(Survey.link)
async def answer_link(message: Message, state: FSMContext):
    text = message.text.strip()
    if text.lower() in ["нет", "не хочу", "пропустить", "skip"]:
        # Можно разрешить пропуск, но лучше попросить ссылку, если возможно
        await message.answer(
            "Если у вас есть ссылка на проект, поделитесь ею. Это поможет лучше оценить ваш опыт. Если нет, напишите «нет»."
        )
        return

    # Проверка на ссылку или разрешаем пустой ответ (если пользователь настаивает)
    if text.lower() != "нет" and not is_valid_url(text):
        await message.answer(
            "Пожалуйста, пришлите корректную ссылку, начинающуюся с http:// или https://, либо напишите «нет»."
        )
        return

    # Сохраняем ссылку (или "нет")
    await state.update_data(link=text)

    # Получаем все данные
    data = await state.get_data()
    answers = [data[f"q{i}"] for i in range(1, 7)] + [data.get("link", "")]

    # Формируем пары вопрос-ответ для LLM
    qa_pairs = [f"{QUESTIONS[i]}: {answers[i]}" for i in range(7)]

    # Уведомление о начале обработки
    processing_msg = await message.answer(
        "⏳ Спасибо! Обрабатываю ваши ответы... (это может занять несколько секунд)"
    )

    if not is_allowed(message.from_user.id):
        await message.answer(
            "🚦 Слишком много попыток. Подождите минуту и попробуйте снова."
        )
        return

    try:
        scores = await evaluate_answers(qa_pairs)
        total_score = calculate_total(scores)
        recommendation = scores.get("recommendation", "Maybe")
        summary = scores.get("summary", "")

    except Exception as e:
        await processing_msg.delete()
        print("LLM ERROR:", e)
        await message.answer(f"❌ Ошибка при оценке:\n{str(e)}")
        await state.clear()
        return

    total_score = (
        scores.get("depth_score", 0)
        + scores.get("critical_score", 0)
        + scores.get("creativity_score", 0)
    )
    hot = total_score >= HOT_THRESHOLD

    # Сохраняем в Google Sheets
    try:
        await save_to_sheets(
            telegram_id=message.from_user.id,
            full_name=message.from_user.full_name,
            username=message.from_user.username,
            answers=answers,
            scores=scores,
            total=total_score,
            hot=hot,
        )
    except Exception as e:
        # Логируем, но не прерываем диалог с кандидатом
        print(f"Error saving to sheets: {e}")

    # Уведомление админам
    if hot:
        for admin_id in ADMIN_IDS:
            try:
                await message.bot.send_message(
                    admin_id,
                    f"🔥 <b>Hot кандидат!</b>\n"
                    f"Имя: {message.from_user.full_name}\n"
                    f"Username: @{message.from_user.username}\n"
                    f"ID: {message.from_user.id}\n"
                    f"Оценки: {scores}\n"
                    f"Сумма: {total_score}/15",
                    parse_mode="HTML",
                )
            except Exception as e:
                # Теперь мы увидим ошибку в консоли
                print(f"Failed to notify admin {admin_id}: {e}")

    # Формируем ответ кандидату
    explanation = (
        f"✅ <b>Ваши результаты:</b>\n\n"
        f"• <b>Глубина использования AI:</b> {scores['depth_score']}/5 — {scores['depth_explanation']}\n"
        f"• <b>Критическое мышление:</b> {scores['critical_score']}/5 — {scores['critical_explanation']}\n"
        f"• <b>Креативность и видение:</b> {scores['creativity_score']}/5 — {scores['creativity_explanation']}\n"
        f"\n<b>Общий балл:</b> {total_score}/15\n"
        f"\n<b>Профиль:</b>\n{summary}\n"
    )
    if hot:
        explanation += "\n🎉 Поздравляем! Вы прошли предварительный отбор. Наш HR свяжется с вами в ближайшее время."
    else:
        explanation += "\n🙏 Спасибо за участие! Мы сохранили ваши ответы и вернёмся к ним при необходимости."

    await processing_msg.delete()
    await message.answer(explanation, parse_mode="HTML", reply_markup=remove_keyboard)
    await state.clear()
