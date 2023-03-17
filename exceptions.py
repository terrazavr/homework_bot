class StatusError(Exception):
    """Исключение статуса домашней роботы."""

    pass


class APIErrorException(Exception):
    """Ошибка запроса к API."""

    pass


class OKStatusError(Exception):
    """Ошибка статуса 200."""

    pass
