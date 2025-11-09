from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Server
    NODE_ENV: str = "production"
    PORT: int = 3000
    
    # Telegram
    BOT_TOKEN: str
    
    # Database
    PGHOST: str
    PGPORT: int = 5432
    PGDATABASE: str
    PGUSER: str
    PGPASSWORD: str
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

