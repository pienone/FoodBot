from pydantic import BaseSettings

class Settings(BaseSettings):
    API_KEY_TELEGRAM_FOOD: str
    class Config:
        env_file = ".env"

settings=Settings()