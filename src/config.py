from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv


load_dotenv()

class Settings(BaseSettings):
    DEBUG: bool = False
    BOT_TOKEN: str = ""
    ADMIN_IDS: list[int] = []
    

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()