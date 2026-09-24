from services.providers.base import ProviderResponse


def format_text(responses: list[ProviderResponse]) -> str:
    report = ""
    for resp in responses:
        text = f"<b>Данные по {resp.source}:</b>\n\n"
        if not resp.ok:
            text += f"❗️ {resp.error}\n"
        elif not resp.items:
            text += "🔍 По запросу ничего не найдено\n"
        else:
            for item in resp.items:
                text += item.render() + "\n"
        report += text + "\n"
    return report
