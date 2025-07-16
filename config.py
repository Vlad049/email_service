from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    sqlalchemy_uri: str = "mysql+aiomysql://127.0.0.1:5432/email_10"


settings = Settings()
