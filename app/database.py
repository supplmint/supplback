from sqlalchemy import create_engine, Column, BigInteger, Text, JSON, DateTime, func
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings
import os

# Database URL
DATABASE_URL = f"postgresql://{settings.PGUSER}:{settings.PGPASSWORD}@{settings.PGHOST}:{settings.PGPORT}/{settings.PGDATABASE}"

# SSL configuration for production (Supabase requires SSL)
connect_args = {
    "sslmode": "require"
} if settings.NODE_ENV == "production" else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


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
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database - create tables"""
    Base.metadata.create_all(bind=engine)

