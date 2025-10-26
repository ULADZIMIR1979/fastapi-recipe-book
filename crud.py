"""
Модуль с CRUD операциями (Create, Read, Update, Delete)
Содержит функции для работы с базой данных
"""

import logging
from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models import Ingredient, Recipe
from schemas import RecipeCreate

logger = logging.getLogger(__name__)


class CRUDRecipe:
    """
    Класс с CRUD операциями для модели Recipe
    """

    async def get_recipes(
        self, db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> Sequence[Recipe]:
        """
        Получить все рецепты, отсортированные по популярности и времени готовки
        """
        logger.info("Получаем список рецептов (пропустить: %s, лимит: %s)", skip, limit)

        query = (
            select(Recipe)
            .options(selectinload(Recipe.ingredients))
            .order_by(Recipe.views.desc(), Recipe.cooking_time.asc())
            .offset(skip)
            .limit(limit)
        )

        result = await db.execute(query)
        recipes = result.scalars().all()

        logger.info("Найдено %s рецептов", len(recipes))
        return recipes

    async def get_recipe(self, db: AsyncSession, recipe_id: int) -> Optional[Recipe]:
        """
        Получить рецепт по ID и увеличить счетчик просмотров
        """
        logger.info("Ищем рецепт с ID: %s", recipe_id)

        query = select(Recipe).where(Recipe.id == recipe_id)  # type: ignore
        result = await db.execute(query)
        recipe = result.scalar_one_or_none()

        if recipe:
            logger.info(
                "Рецепт найден: '%s', просмотры: %s", recipe.title, recipe.views
            )
            recipe.views += 1  # type: ignore
            await db.commit()
            await db.refresh(recipe)
            logger.info("Увеличили счетчик просмотров до: %s", recipe.views)
        else:
            logger.warning("Рецепт с ID %s не найден", recipe_id)

        return recipe

    async def create_recipe(self, db: AsyncSession, recipe: RecipeCreate) -> Recipe:
        """
        Создать новый рецепт с ингредиентами
        """
        logger.info("Создаем новый рецепт: '%s'", recipe.title)
        logger.info("Ингредиенты: %s", recipe.ingredient_names)

        # Сначала создаем все ингредиенты
        ingredients = []
        for ingredient_name in recipe.ingredient_names:
            logger.info("Обрабатываем ингредиент: '%s'", ingredient_name)

            # Проверяем существет ли ингредиент
            query = select(Ingredient).where(Ingredient.name == ingredient_name)
            result = await db.execute(query)
            existing_ingredient = result.scalar_one_or_none()

            if existing_ingredient:
                logger.info("Ингредиент '%s' уже существует", ingredient_name)
                ingredients.append(existing_ingredient)
            else:
                # Создаем новый ингредиент
                logger.info("Создаем новый ингредиент: '%s'", ingredient_name)
                new_ingredient = Ingredient(name=ingredient_name)
                db.add(new_ingredient)
                await db.flush()
                ingredients.append(new_ingredient)

        # Создаем рецепт
        logger.info("Создаем объект рецепта...")
        db_recipe = Recipe(
            title=recipe.title,
            cooking_time=recipe.cooking_time,
            description=recipe.description,
            ingredients=ingredients,
        )
        db.add(db_recipe)
        await db.commit()
        await db.refresh(db_recipe)

        # Явно загружаем ингредиенты для возврата
        await db.refresh(db_recipe, ["ingredients"])

        logger.info("Рецепт '%s' успешно создан с ID: %s", recipe.title, db_recipe.id)
        return db_recipe

    async def get_ingredients(self, db: AsyncSession) -> Sequence[Ingredient]:
        """
        Получить все ингредиенты
        """
        logger.info("Получаем список всех ингредиентов...")
        query = select(Ingredient)
        result = await db.execute(query)
        ingredients = result.scalars().all()

        logger.info("Найдено %s ингредиентов", len(ingredients))
        return ingredients


# Создаем экземпляр класса для использования
recipe_crud = CRUDRecipe()
