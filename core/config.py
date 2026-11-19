from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class ConfigSetting(BaseSettings):
    # Настройка чтения .env-файла.
    # BaseSettings - класс, который сам может находить значения для переменных окружения.
    # SettingConfigDict - класс, который говорит BaseSettings, где искать и как обрабатывать переменные окружения.

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # Значение по умолчанию.
    sqlite_db_name: str = "bookings.db"

    @property
    def database_url(self) -> str:
        return f"sqlite+aiosqlite:///./{self.sqlite_db_name}"


# Используем декоратор lru_cache, для кеширования, создания настройки.
# Возвращает объект настройки.
@lru_cache
def get_config() -> ConfigSetting:
    return ConfigSetting()


config_set = get_config()
