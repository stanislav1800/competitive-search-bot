class SearchError(Exception):
    user_message: str = "Сервис временно недоступен"


class SourceUnavailable(SearchError):
    user_message = "Источник временно недоступен"


class ServiceOverloaded(SearchError):
    user_message = "Бот сейчас перегружен, попробуйте позже"


class SourceRateLimited(SearchError):
    user_message = "Превышен лимит запросов, попробуйте через минуту"
