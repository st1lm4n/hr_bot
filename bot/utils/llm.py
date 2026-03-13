import json
import asyncio
import logging
import hashlib
import time
from openai import AsyncOpenAI
from bot.config import OPENAI_API_KEY

# ===== CONFIG =====
MODEL = "gpt-4o-mini"
MAX_RETRIES = 3
CACHE_TTL_SECONDS = 60 * 60  # 1 час

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is not set. Проверь .env файл.")

client = AsyncOpenAI(api_key=OPENAI_API_KEY)

# ===== IN-MEMORY CACHE =====
_CACHE = {}


def _make_cache_key(text: str) -> str:
    normalized = " ".join(text.strip().lower().split())
    return hashlib.sha256(normalized.encode()).hexdigest()


def _get_from_cache(key: str):
    item = _CACHE.get(key)
    if not item:
        return None
    if time.time() - item["time"] > CACHE_TTL_SECONDS:
        del _CACHE[key]
        return None
    return item["data"]


def _save_to_cache(key: str, data: dict):
    _CACHE[key] = {"data": data, "time": time.time()}


# ===== PROMPT =====
SYSTEM_PROMPT = """
Ты — строгий HR-эксперт.

Оцени кандидата объективно.
НЕ ставь 5 без конкретных технических деталей.

Ответы:

{qa_text}

Верни строго JSON:

{{
  "depth_score": number,
  "depth_explanation": "string",
  "critical_score": number,
  "critical_explanation": "string",
  "creativity_score": number,
  "creativity_explanation": "string",
  "summary": "краткий профиль кандидата (3-4 предложения)",
  "recommendation": "Hire" или "Maybe" или "Reject"
}}
"""


async def evaluate_answers(questions_answers: list) -> dict:
    qa_text = "\n".join(questions_answers)
    cache_key = _make_cache_key(qa_text)

    # ===== CACHE =====
    cached = _get_from_cache(cache_key)
    if cached:
        logging.info("LLM CACHE HIT")
        return cached

    logging.info("LLM CACHE MISS")

    prompt = SYSTEM_PROMPT.format(qa_text=qa_text)

    delay = 1

    for attempt in range(MAX_RETRIES):
        try:
            response = await client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "system", "content": prompt}],
                temperature=0.2,
                max_tokens=400,
                response_format={"type": "json_object"},
            )

            content = response.choices[0].message.content
            result = json.loads(content)

            # Минимальная валидация
            required_fields = [
                "depth_score",
                "depth_explanation",
                "critical_score",
                "critical_explanation",
                "creativity_score",
                "creativity_explanation",
            ]

            for field in required_fields:
                if field not in result:
                    raise ValueError(f"Missing field: {field}")

            # Приводим оценки к int
            result["depth_score"] = int(result["depth_score"])
            result["critical_score"] = int(result["critical_score"])
            result["creativity_score"] = int(result["creativity_score"])

            # ===== COST LOGGING =====
            try:
                usage = response.usage
                if usage:
                    prompt_tokens = usage.prompt_tokens
                    completion_tokens = usage.completion_tokens
                    total_tokens = usage.total_tokens

                    # Примерный расчёт стоимости (проверь актуальные цены!)
                    input_cost = prompt_tokens * 0.00000015
                    output_cost = completion_tokens * 0.0000006
                    total_cost = input_cost + output_cost

                    logging.info(f"Tokens: {total_tokens} | Cost ≈ ${total_cost:.6f}")
            except Exception as cost_error:
                logging.warning(f"Cost logging failed: {cost_error}")

            # ===== SAVE CACHE =====
            _save_to_cache(cache_key, result)

            return result

        except Exception as e:

            logging.warning(f"OpenAI attempt {attempt + 1} failed: {e}")

            # 🔥 Fallback при исчерпании квоты

            if "insufficient_quota" in str(e) or "429" in str(e):
                logging.error("Quota exceeded. Returning fallback response.")

                return {
                    "depth_score": 0,
                    "depth_explanation": "Система временно недоступна.",
                    "critical_score": 0,
                    "critical_explanation": "Система временно недоступна.",
                    "creativity_score": 0,
                    "creativity_explanation": "Система временно недоступна.",
                    "summary": "Оценка временно недоступна из-за технических ограничений.",
                    "recommendation": "Maybe",
                }

            if attempt == MAX_RETRIES - 1:
                raise Exception(f"OpenAI API error: {e}")

            await asyncio.sleep(delay)

            delay *= 2
