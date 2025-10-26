"""
Основной модуль FastAPI приложения
Содержит все endpoint'ы и настройки API
"""

from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from contextlib import asynccontextmanager

from database import get_db, init_db
from schemas import (
    RecipeCreate,
    RecipeListResponse,
    RecipeDetailResponse,
    IngredientResponse
)
from crud import recipe_crud

print("🚀 Запускаем FastAPI приложение...")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Современный способ обработки событий жизненного цикла приложения.
    Заменяет устаревший @app.on_event("startup")
    """
    print("🎬 Запускаем инициализацию базы данных...")
    await init_db()
    print("✅ Инициализация завершена, приложение готово к работе!")
    yield
    print("🔴 Приложение завершает работу...")

# Создаем экземпляр FastAPI приложения с метаданными и lifespan
app = FastAPI(
    title="Recipe Book API",
    description="API для управления кулинарной книгой с рецептами",
    version="1.0.0",
    docs_url="/docs",  # URL для Swagger документации
    redoc_url="/redoc",  # URL для ReDoc документации
    lifespan=lifespan
)

print("✅ FastAPI приложение создано!")


@app.get("/")
async def root():
    """
    Корневой endpoint с информацией о API

    Возвращает:
        dict: приветственное сообщение и информацию о API
    """
    print("🌐 Кто-то зашел на корневой endpoint!")
    return {
        "message": "Добро пожаловать в API Кулинарной книги!",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get(
    "/recipes",
    response_model=List[RecipeListResponse],
    summary="Получить все рецепты",
    description="Получить список всех рецептов, отсортированных по популярности и времени готовки"
)
async def get_recipes(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """
    Получить все рецепты для отображения в таблице

    - **skip**: Количество записей для пропуска (для пагинации)
    - **limit**: Максимальное количество возвращаемых записей (для пагинации)

    Возвращает список рецептов, отсортированных по:
    1. Просмотры (убывание) - самые популярные первые
    2. Время готовки (возрастание) - самые быстрые рецепты первые при равенстве просмотров
    """
    print(f"📋 Запрос списка рецептов (skip: {skip}, limit: {limit})")

    recipes = await recipe_crud.get_recipes(db, skip=skip, limit=limit)
    print(f"✅ Отправляем {len(recipes)} рецептов клиенту")
    return recipes


@app.get(
    "/recipes/{recipe_id}",
    response_model=RecipeDetailResponse,
    summary="Получить детали рецепта",
    description="Получить детальную информацию о конкретном рецепте и увеличить счетчик просмотров"
)
async def get_recipe(
    recipe_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Получить детальную информацию о конкретном рецепте

    - **recipe_id**: ID рецепта для получения

    Этот endpoint также увеличивает счетчик просмотров рецепта каждый раз при обращении,
    что влияет на сортировку по популярности в списке рецептов.

    Возвращает 404 если рецепт не найден.
    """
    print(f"🔍 Запрос деталей рецепта с ID: {recipe_id}")

    recipe = await recipe_crud.get_recipe(db, recipe_id)
    if recipe is None:
        print(f"❌ Рецепт с ID {recipe_id} не найден, возвращаем 404")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Рецепт не найден"
        )

    print(f"✅ Отправляем детали рецепта: '{recipe.title}'")
    return recipe


@app.post(
    "/recipes",
    response_model=RecipeDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создать новый рецепт",
    description="Создать новый рецепт с ингредиентами"
)
async def create_recipe(
    recipe: RecipeCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Создать новый рецепт

    - **title**: Название рецепта (максимум 100 символов)
    - **cooking_time**: Время готовки в минутах (минимум 1)
    - **description**: Подробное описание рецепта
    - **ingredient_names**: Список названий ингредиентов

    Ингредиенты, которые не существуют, будут созданы автоматически.
    Возвращает созданный рецепт со всеми деталями.
    """
    print(f"🆕 Запрос на создание нового рецепта: '{recipe.title}'")

    try:
        created_recipe = await recipe_crud.create_recipe(db, recipe)
        print(f"✅ Рецепт успешно создан с ID: {created_recipe.id}")
        return created_recipe
    except Exception as e:
        print(f"❌ Ошибка при создании рецепта: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при создании рецепта: {str(e)}"
        )


@app.get(
    "/ingredients",
    response_model=List[IngredientResponse],
    summary="Получить все ингредиенты",
    description="Получить список всех доступных ингредиентов"
)
async def get_ingredients(db: AsyncSession = Depends(get_db)):
    """
    Получить все ингредиенты

    Возвращает список всех ингредиентов, доступных в системе.
    """
    print("📦 Запрос списка всех ингредиентов")

    ingredients = await recipe_crud.get_ingredients(db)
    print(f"✅ Отправляем {len(ingredients)} ингредиентов клиенту")
    return ingredients


print("✅ Все endpoint'ы зарегистрированы!")

if __name__ == "__main__":
    print("🎯 Запускаем сервер с помощью uvicorn...")
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)