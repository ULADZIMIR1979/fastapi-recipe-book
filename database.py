"""
Модуль для настройки подключения к базе данных.
Создает асинхронное подключение к SQLite базе данных
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

print("🔧 Настраиваем подключение к базе данных...")

# URL для подключения к SQLite базе данных
# aiosqlite - асинхронный драйвер для SQLite
DATABASE_URL = "sqlite+aiosqlite:///./recipes.db"

# Создаем движок для работы с базой данных
# echo=True показывает SQL запросы в консоли (удобно для отладки)
engine = create_async_engine(DATABASE_URL, echo=True)

# Создаем фабрику сессий для работы с базой данных.
# Используем async_sessionmaker вместо sessionmaker для асинхронности
AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Базовый класс для всех моделей (таблиц)
Base = declarative_base()

print("✅ Настройка базы данных завершена!")


async def get_db():
    """
    Функция-зависимость для получения сессии базы данных
    FastAPI будет вызывать эту функцию для каждого запроса
    и автоматически закрывать сессию после обработки
    """
    print("📝 Создаем новую сессию базы данных...")
    async with AsyncSessionLocal() as session:
        try:
            print("✅ Сессия создана, передаем в обработчик")
            yield session
        finally:
            print("🔒 Закрываем сессию базы данных")
            await session.close()


async def init_db():
    """
    Инициализация базы данных - создает все таблицы.
    Вызывается при старте приложения
    """
    print("🗃️ Начинаем создание таблиц в базе данных...")
    async with engine.begin() as conn:
        # Создаем все таблицы, определенные в моделях
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Таблицы успешно созданы!")