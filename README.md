# HR-скрининг Telegram Bot

Бот для первичного скрининга кандидатов на позицию AI-first разработчика. Задаёт вопросы, оценивает ответы через OpenAI GPT, сохраняет результаты в Google Sheets и уведомляет админов о горячих кандидатах.

## Функциональность

- Приветствие и опрос из 7 вопросов.
- Валидация ссылки на проект.
- Оценка ответов по трём критериям с объяснением.
- Сохранение в Google Sheets.
- Уведомление админов о кандидатах с суммой баллов выше порога.
- Админ-команды для просмотра статистики и списка горячих кандидатов.

## Технологии

- Python 3.11
- aiogram 3.x
- OpenAI API 
- Google Sheets API (gspread)
- Docker

## Установка и запуск

### Локально

1. Клонируйте репозиторий:
```bash
git clone <url>
cd hr_bot
```

2. Создайте виртуальное окружение и установите зависимости:
```bash
python -m venv venv
source venv/bin/activate  # или venv\Scripts\activate на Windows
pip install -r requirements.txt
```

3. Создайте файл `.env` на основе `.env.example` и заполните свои токены.
4. Положите **JSON**-ключ сервисного аккаунта **Google** в `credentials/google_service_account.json`.
5. Запустите бота:
```bash
python -m bot.main
```
### Через Docker

1. Убедитесь, что заполнен `.env` и есть `credentials/google_service_account.json`.

2. Выполните:

```bash
docker-compose up --build
```

### Переменные окружения

|Переменная|Описание|
|:-:|:-:|
|BOT_TOKEN|Токен Telegram бота|
|OPENAI_API_KEY|Ключ API OpenAI|
|GOOGLE_SHEETS_CREDENTIALS|	Путь к JSON-файлу сервисного аккаунта|
|GOOGLE_SHEETS_URL|	URL Google таблицы|
|ADMIN_IDS	|Список Telegram ID администраторов через запятую|
|HOT_THRESHOLD	|Порог суммы баллов для горячего кандидата|


### Админ-команды
`/admin` — справка по админ-командам

`/admin_stats` — общая статистика и топ-3 кандидата

`/admin_hot` — список горячих кандидатов

### Обоснование вопросов
См. файл `QUESTIONS.md`.


### Архитектура

                    Candidate
                       │
                       ▼
                Telegram Bot
                       │
                       ▼
                   aiogram
                       │
                       ▼
                Screening Logic
                       │
            ┌──────────┴──────────┐
            ▼                     ▼
         OpenAI              Google Sheets
            │                     │
            ▼                     ▼
       AI Evaluation          Candidates DB
            │
            ▼
        Hot Candidate
            │
            ▼
        Admin Notification
