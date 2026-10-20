import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Конфигурация приложения TenderAI Med."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # API-ключ OpenAI
    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")

    # Базовый URL API OpenAI (для прокси или зеркал, напр. https://api.proxyapi.ru/openai/v1)
    openai_base_url: Optional[str] = Field(default=None, alias="OPENAI_BASE_URL")

    # Модели OpenAI для двухфазного пайплайна
    # Быстрая модель для фильтрации и таблиц (gpt-4.1-mini, gpt-4o-mini, gpt-5-mini)
    openai_model_fast: str = Field(default="gpt-4.1-mini", alias="OPENAI_MODEL_FAST")

    # Интеллектуальная модель для глубокого риск-аудита и генерации запросов (gpt-4.1, gpt-4o, gpt-5)
    openai_model_smart: str = Field(default="gpt-4.1", alias="OPENAI_MODEL_SMART")

    # Режим демонстрации (Mock) без вызова внешних API
    mock_mode: bool = Field(default=False, alias="MOCK_MODE")

    # Максимальный размер загружаемого архива/файла (в мегабайтах)
    max_file_size_mb: int = Field(default=100, alias="MAX_FILE_SIZE_MB")

    @property
    def has_api_key(self) -> bool:
        """Проверяет, задан ли валидный ключ OpenAI."""
        return bool(
            self.openai_api_key
            and self.openai_api_key.strip()
            and self.openai_api_key != "your_openai_api_key_here"
        )


# Синглтон настроек
settings = Settings()
