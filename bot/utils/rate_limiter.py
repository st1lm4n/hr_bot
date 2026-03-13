import time
from collections import defaultdict

_user_requests = defaultdict(list)
WINDOW_SECONDS = 60  # промежуток времени, в котором считаем запросы
USER_LIMIT = 5  # максимум запросов за окно
BLOCK_TIME = 300  # время блокировки при превышении (5 минут)
_blocked_users = {}


def is_allowed(user_id: int) -> bool:
    now = time.time()

    # Проверка, заблокирован ли пользователь
    if user_id in _blocked_users:
        if now < _blocked_users[user_id]:
            return False
        else:
            del _blocked_users[user_id]

    # Очистка старых запросов
    timestamps = _user_requests.get(user_id, [])
    timestamps = [t for t in timestamps if now - t < WINDOW_SECONDS]

    if len(timestamps) >= USER_LIMIT:
        _blocked_users[user_id] = now + BLOCK_TIME
        return False

    timestamps.append(now)
    _user_requests[user_id] = timestamps
    return True
