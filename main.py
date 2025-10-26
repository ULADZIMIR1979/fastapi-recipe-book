"""
Основной модуль FastAPI приложения
Содержит все endpoint'ы и настройки API
"""

import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator, List, Sequence

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from crud import recipe_crud
from database import get_db, init_db
from schemas import (
    IngredientResponse,
    RecipeCreate,
    RecipeDetailResponse,
    RecipeListResponse,
)

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """
    Современный способ обработки событий жизненного цикла приложения.
    Заменяет устаревший @app.on_event("startup")
    """
    logger.info("Запускаем инициализацию базы данных...")
    await init_db()
    logger.info("Инициализация завершена, приложение готово к работе!")
    yield
    logger.info("Приложение завершает работу...")


# Создаем экземпляр FastAPI приложения с метаданными и lifespan
app = FastAPI(
    title="Recipe Book API",
    description="API для управления кулинарной книгой с рецептами",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)


@app.get("/")
async def root() -> dict:
    """
    Корневой endpoint с информацией о API
    """
    logger.info("Кто-то зашел на корневой endpoint!")
    return {
        "message": "Добро пожаловать в API Кулинарной книги!",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get(
    "/recipes",
    response_model=List[RecipeListResponse],
    summary="Получить все рецепты",
    description="Получить список всех рецептов, отсортированных по популярности",
)
async def get_recipes(
    skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)
) -> Sequence[RecipeListResponse]:
    """
    Получить все рецепты для отображения в таблице
    """
    logger.info("Запрос списка рецептов (skip: %s, limit: %s)", skip, limit)
    recipes = await recipe_crud.get_recipes(db, skip=skip, limit=limit)
    logger.info("Отправляем %s рецептов клиенту", len(recipes))
    return recipes


@app.get(
    "/recipes/{recipe_id}",
    response_model=RecipeDetailResponse,
    summary="Получить детали рецепта",
    description="Получить детальную информацию о рецепте",
)
async def get_recipe(
    recipe_id: int, db: AsyncSession = Depends(get_db)
) -> RecipeDetailResponse:
    """
    Получить детальную информацию о конкретном рецепте
    """
    logger.info("Запрос деталей рецепта с ID: %s", recipe_id)
    recipe = await recipe_crud.get_recipe(db, recipe_id)
    if recipe is None:
        logger.warning("Рецепт с ID %s не найден", recipe_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Рецепт не найден"
        )
    logger.info("Отправляем детали рецепта: '%s'", recipe.title)
    return recipe


@app.post(
    "/recipes",
    response_model=RecipeDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новый рецепт",
    description="Создать новый рецепт с ингредиентами",
)
async def create_recipe(
    recipe: RecipeCreate, db: AsyncSession = Depends(get_db)
) -> RecipeDetailResponse:
    """
    Создать новый рецепт
    """
    logger.info("Запрос на создание нового рецепта: '%s'", recipe.title)
    try:
        created_recipe = await recipe_crud.create_recipe(db, recipe)
        logger.info("Рецепт успешно создан с ID: %s", created_recipe.id)
        return created_recipe
    except Exception as e:
        logger.error("Ошибка при создании рецепта: %s", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при создании рецепта",
        )


@app.get(
    "/ingredients",
    response_model=List[IngredientResponse],
    summary="Получить все ингредиенты",
    description="Получить список всех доступных ингредиентов",
)
async def get_ingredients(
    db: AsyncSession = Depends(get_db),
) -> Sequence[IngredientResponse]:
    """
    Получить все ингредиенты
    """
    logger.info("Запрос списка всех ингредиентов")
    ingredients = await recipe_crud.get_ingredients(db)
    logger.info("Отправляем %s ингредиентов клиенту", len(ingredients))
    return ingredients


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
