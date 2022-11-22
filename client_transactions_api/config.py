from datetime import timezone
from typing import Optional

from pydantic import BaseSettings, Field, FilePath, PostgresDsn, SecretStr


class SettingsBase(BaseSettings):
    """
    App Base Settings

    Тo get a new secret key run:
        openssl rand -hex 32

    """

    TESTING: bool = Field(env='TESTING', default=True)
    DEBUG: bool = Field(env='DEBUG', default=False)
    LOGGING: bool = Field(env='LOGGING', default=False)
    LOG_PATH: str = Field(env='LOG_PATH', default='logs/app.log')

    SECRET_KEY: SecretStr = Field(env='SECRET_KEY', default='pl3seCh@nGeM3!')
    API_PATH: str = Field(env='API_PATH', default='/api')
    TIMEZONE: timezone = Field(timezone.utc)

    class Config:
        env_file = '.env'
        env_prefix = ''
        # case_sensitive = True


class DBSettings(SettingsBase):
    """"Database Settings"""

    FIRST_SUPERUSER: str = Field(
        env='FIRST_SUPERUSER', default='admin')
    FIRST_SUPERUSER_PASSWORD: SecretStr = Field(
        env='FIRST_SUPERUSER_PASSWORD', default='password')


class PostgresMixin(DBSettings):
    """"Postgres Settings Mixin"""

    POSTGRES_USER: str = Field(
        env='POSTGRES_USER', default='postgres')
    POSTGRES_PASSWORD: SecretStr = Field(
        env='POSTGRES_PASSWORD', default='postgres')
    POSTGRES_SERVER: str = Field(
        env='POSTGRES_SERVER', default='localhost')
    POSTGRES_PORT: int = Field(env='POSTGRES_PORT', default=5432)
    POSTGRES_DB: str = Field(env='POSTGRES_DB', default='postgres')

    @property
    def DATABASE_URL(self) -> str:
        url = f'postgresql+asyncpg://' \
            f'{self.POSTGRES_USER}:' \
            f'{self.POSTGRES_PASSWORD.get_secret_value()}' \
            f'@{self.POSTGRES_SERVER}:' \
            f'{self.POSTGRES_PORT}/{self.POSTGRES_DB}'
        return url


class AuthServiceMixin(SettingsBase):
    """Auth Service Settings Mixin"""

    CRYPT_ALGORITHM: str = Field(
        env='CRYPT_ALGORITHM', default='HS256')
    TOKEN_EXPIRE_MINUTES: int = Field(
        env='TOKEN_EXPIRE_MINUTES', default=60*24)


class Settings(
        PostgresMixin,
        AuthServiceMixin
):
    """Combined Settings with previous settings as mixins"""
    pass


settings = Settings()
