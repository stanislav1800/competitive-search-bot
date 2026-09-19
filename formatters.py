from services.providers.base import SearchResult

LABELS = {
    "stars": "Количество звёзд",
    "language": "Основной язык",
    "score": "Рейтинг",
    "answers": "Ответов",
    "answer_count": "Количество ответов",
    "is_answered": "Ответ принят",
    "description": "Описание"
}

def format_text(answers: dict[str, list[SearchResult]]) -> str:
    results = ""

    for source, items in answers.items():
        text = f"<b>Данные по {source}:</b>\n\n"

        if items is None:
            text += "❗️Данных не найдено\n"

        else:
            for item in items:
                text += (
                    f"""<a href="{item.url}"><b>{item.title}</b></a>\n"""
                )
                
                for label in LABELS:
                    if label in item.extra:
                        text += f"{LABELS[label]}: {item.extra[label]}\n"

                text += "\n"

        results += text + "\n\n"

    return results
