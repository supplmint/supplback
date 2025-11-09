from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Server
    NODE_ENV: str = "development"
    PORT: int = 3000
    
    # Telegram
    BOT_TOKEN: Optional[str] = None
    
    # Webhook for file uploads
    ANALYSIS_WEBHOOK_URL: Optional[str] = "https://famimeprapud.beget.app/webhook-test/41cdfd57-0fc7-4e35-ba23-ffe0734fe412"
    
    # Database - можно использовать либо DATABASE_URL (проще), либо отдельные параметры
    DATABASE_URL: Optional[str] = None  # Supabase connection string (предпочтительно)
    
    # Альтернативный способ - отдельные параметры (для обратной совместимости)
    PGHOST: Optional[str] = None
    PGPORT: int = 5432
    PGDATABASE: Optional[str] = None
    PGUSER: Optional[str] = None
    PGPASSWORD: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

