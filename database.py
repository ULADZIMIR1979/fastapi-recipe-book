"""
Модуль для настройки подключения к базе данных.
Создает асинхронное подключение к SQLite базе данных
"""

import logging
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

logger = logging.getLogger(__name__)

# URL для подключения к SQLite базе данных
DATABASE_URL = "sqlite+aiosqlite:///./recipes.db"

# Создаем движок для работы с базой данных
engine = create_async_engine(DATABASE_URL, echo=True)

# Создаем фабрику сессий для работы с базой данных
AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Базовый класс для всех моделей
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Функция-зависимость для получения сессии базы данных
    """
    logger.debug("Создаем новую сессию базы данных...")
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db() -> None:
    """
    Инициализация базы данных - создает все таблицы
    """
    logger.info("Начинаем создание таблиц в базе данных...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Таблицы успешно созданы!")
