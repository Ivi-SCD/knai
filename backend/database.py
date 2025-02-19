
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.declarative import declarative_base

# Project directories
from config import global_settings

DBBaseModel = declarative_base()

async_engine: AsyncEngine = create_async_engine(f'postgresql+asyncpg://{global_settings.DB_USER}:{global_settings.DB_PASSWORD}@{global_settings.DB_HOST}:{global_settings.DB_PORT}/{global_settings.DB_NAME}')

sync_engine = create_engine(f'postgresql://{global_settings.DB_USER}:{global_settings.DB_PASSWORD}@{global_settings.DB_HOST}:{global_settings.DB_PORT}/{global_settings.DB_NAME}')

# Session factory for async session
Session: AsyncSession = sessionmaker(
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
    class_=AsyncSession,
    bind=async_engine
)