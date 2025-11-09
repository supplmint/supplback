from sqlalchemy import create_engine, Column, BigInteger, Text, JSON, DateTime, func
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings
import os
from typing import Optional

Base = declarative_base()

# Lazy initialization of database engine
_engine = None
_SessionLocal = None


def get_database_url() -> str:
    """Get database URL from settings
    
    Поддерживает два способа:
    1. DATABASE_URL - connection string из Supabase (предпочтительно)
    2. Отдельные параметры (PGHOST, PGUSER, PGPASSWORD, PGDATABASE)
    """
    # Способ 1: Использовать DATABASE_URL если он указан
    if settings.DATABASE_URL:
        return settings.DATABASE_URL
    
    # Способ 2: Собрать из отдельных параметров
    if all([settings.PGUSER, settings.PGPASSWORD, settings.PGHOST, settings.PGDATABASE]):
        return f"postgresql://{settings.PGUSER}:{settings.PGPASSWORD}@{settings.PGHOST}:{settings.PGPORT}/{settings.PGDATABASE}"
    
    raise ValueError(
        "Database configuration is incomplete. "
        "Please set either DATABASE_URL (preferred) or "
        "PGUSER, PGPASSWORD, PGHOST, and PGDATABASE environment variables."
    )


def get_engine():
    """Get or create database engine"""
    global _engine
    if _engine is None:
        database_url = get_database_url()
        
        # SSL configuration for production (Supabase requires SSL)
        # Если DATABASE_URL уже содержит параметры SSL, они будут использованы
        # Иначе добавляем sslmode=require для Supabase
        connect_args = {}
        
        # Проверяем, есть ли уже SSL параметры в URL
        if "sslmode" not in database_url.lower() and "ssl" not in database_url.lower():
            # Для Supabase всегда требуется SSL в production
            if settings.NODE_ENV == "production" or "supabase" in database_url.lower():
                connect_args["sslmode"] = "require"
        
        _engine = create_engine(database_url, connect_args=connect_args)
    return _engine


def get_session_local():
    """Get or create session maker"""
    global _SessionLocal
    if _SessionLocal is None:
        engine = get_engine()
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return _SessionLocal


class HealthApp(Base):
    __tablename__ = "health_app"
    
    id = Column(BigInteger, primary_key=True, index=True)
    tgid = Column(Text, unique=True, nullable=False, index=True)
    profile = Column(JSON, default={})
    analyses = Column(JSON, default={})
    recommendations = Column(JSON, default={})
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


def get_db():
    """Get database session"""
    try:
        SessionLocal = get_session_local()
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
    except ValueError as e:
        # Database not configured
        raise Exception(f"Database not configured: {str(e)}") from e


def init_db():
    """Initialize database - create tables"""
    try:
        engine = get_engine()
        Base.metadata.create_all(bind=engine)
    except ValueError as e:
        print(f"Warning: Could not initialize database: {str(e)}")
        raise

