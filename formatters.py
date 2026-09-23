from services.providers.base import SearchResult


def format_text(answers: dict[str, list[SearchResult]]) -> str:
    results = ""

    for source, items in answers.items():
        text = f"<b>Данные по {source}:</b>\n\n"

        if isinstance(items, Exception):
            text += f"❗️Произошла ошибка при поиске {items.characters_written}\n"
        elif not items:
            text += "🔍 По запросу ничего не найдено\n"
        else:
            for item in items:
                text += item.render() + "\n"

        results += text + "\n"

    return results
