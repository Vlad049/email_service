from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    sqlalchemy_uri: str = "mysql+aiomysql://127.0.0.1:5432/email_10"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
