# exceptions.py

class BotError(Exception):
    """Базовое исключение бота — есть сообщение для пользователя в Telegram."""
    user_message = "Произошла ошибка"

    def __init__(self, message: str | None = None):
        super().__init__(message or self.user_message)
        if message:
            self.user_message = message


class UserNotFoundError(BotError):
    user_message = "Пользователь не найден"


class ASICConnectionError(BotError):
    user_message = "Не удалось подключиться к ASIC"


class ASICInvalidResponseError(BotError):
    user_message = "Некорректный ответ от устройства"


class ValidationError(BotError):
    def __init__(self, message: str):
        self.user_message = message
        super().__init__(message)