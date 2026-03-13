import re


def is_valid_url(url: str) -> bool:
    """Простая проверка, что строка похожа на URL."""
    regex = re.compile(
        r"^(https?://)"  # http:// or https://
        r"([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}"  # domain
        r"(/.*)?$"  # path
    )
    return re.match(regex, url) is not None
