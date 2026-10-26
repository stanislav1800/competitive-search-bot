from services.providers.base import ProviderResponse

MESSAGE_LIMIT = 4096


def format_messages(responses: list[ProviderResponse]) -> list[str]:
    parts: list[str] = []
    for resp in responses:
        header = f"<b>Данные по {resp.source}:</b>\n\n"
        if not resp.ok:
            lines = [f"❗️ {resp.error}\n"]
        elif not resp.items:
            lines = ["🔍 По запросу ничего не найдено\n"]
        else:
            lines = [item.render() + "\n" for item in resp.items]
        lines[0] = header + lines[0]
        lines[-1] += "\n"
        parts.extend(lines)
    return _split(parts)


def _split(parts: list[str], limit: int = MESSAGE_LIMIT) -> list[str]:
    """Собирает части в сообщения не длиннее limit, не разрывая ни одну часть (и её HTML-теги)."""
    messages: list[str] = []
    current = ""
    for part in parts:
        if current and _tg_len(current + part) > limit:
            messages.append(current)
            current = ""
        current += part
    messages.append(current)
    return messages


def _tg_len(text: str) -> int:
    # Telegram считает длину в UTF-16 (эмодзи = 2), а сырой HTML с тегами длиннее видимого текста — оценка с запасом
    return len(text.encode("utf-16-le")) // 2
