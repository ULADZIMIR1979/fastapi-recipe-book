"""
Модуль с CRUD операциями (Create, Read, Update, Delete)
Содержит функции для работы с базой данных
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from models import Recipe, Ingredient
from schemas import RecipeCreate
from typing import List, Optional

print("🛠️ Создаем CRUD операции для работы с базой данных...")


class CRUDRecipe:
    """
    Класс с CRUD операциями для модели Recipe
    """

    async def get_recipes(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100
    ) -> List[Recipe]:
        """
        Получить все рецепты, отсортированные по популярности и времени готовки
        """
        print(f"📖 Получаем список рецептов (пропустить: {skip}, лимит: {limit})")

        query = (
            select(Recipe)
            .options(selectinload(Recipe.ingredients))
            .order_by(Recipe.views.desc(), Recipe.cooking_time.asc())
            .offset(skip)
            .limit(limit)
        )

        result = await db.execute(query)
        recipes = result.scalars().all()

        print(f"✅ Найдено {len(recipes)} рецептов")
        return recipes

    async def get_recipe(self, db: AsyncSession, recipe_id: int) -> Optional[Recipe]:
        """
        Получить рецепт по ID и увеличить счетчик просмотров
        """
        print(f"🔍 Ищем рецепт с ID: {recipe_id}")

        query = (
            select(Recipe)
            .options(selectinload(Recipe.ingredients))
            .where(Recipe.id == recipe_id)
        )
        result = await db.execute(query)
        recipe = result.scalar_one_or_none()

        if recipe:
            print(f"✅ Рецепт найден: '{recipe.title}', текущие просмотры: {recipe.views}")
            recipe.views += 1
            await db.commit()
            await db.refresh(recipe)
            print(f"📈 Увеличили счетчик просмотров до: {recipe.views}")
        else:
            print(f"❌ Рецепт с ID {recipe_id} не найден")

        return recipe

    async def create_recipe(
        self,
        db: AsyncSession,
        recipe: RecipeCreate
    ) -> Recipe:
        """
        Создать новый рецепт с ингредиентами
        """
        print(f"🆕 Создаем новый рецепт: '{recipe.title}'")
        print(f"📝 Ингредиенты: {recipe.ingredient_names}")

        # Сначала создаем все ингредиенты
        ingredients = []
        for ingredient_name in recipe.ingredient_names:
            print(f"🔎 Обрабатываем ингредиент: '{ingredient_name}'")

            # Проверяем существет ли ингредиент
            query = select(Ingredient).where(Ingredient.name == ingredient_name)
            result = await db.execute(query)
            existing_ingredient = result.scalar_one_or_none()

            if existing_ingredient:
                print(f"✅ Ингредиент '{ingredient_name}' уже существует")
                ingredients.append(existing_ingredient)
            else:
                # Создаем новый ингредиент
                print(f"🆕 Создаем новый ингредиент: '{ingredient_name}'")
                new_ingredient = Ingredient(name=ingredient_name)
                db.add(new_ingredient)
                await db.flush()
                ingredients.append(new_ingredient)

        # Создаем рецепт
        print("🍳 Создаем объект рецепта...")
        db_recipe = Recipe(
            title=recipe.title,
            cooking_time=recipe.cooking_time,
            description=recipe.description,
            ingredients=ingredients
        )
        db.add(db_recipe)
        await db.commit()
        await db.refresh(db_recipe)

        # Явно загружаем ингредиенты для возврата
        await db.refresh(db_recipe, ['ingredients'])

        print(f"✅ Рецепт '{recipe.title}' успешно создан с ID: {db_recipe.id}")
        return db_recipe

    async def get_ingredients(self, db: AsyncSession) -> List[Ingredient]:
        """
        Получить все ингредиенты
        """
        print("📋 Получаем список всех ингредиентов...")
        query = select(Ingredient)
        result = await db.execute(query)
        ingredients = result.scalars().all()

        print(f"✅ Найдено {len(ingredients)} ингредиентов")
        return ingredients


# Создаем экземпляр класса для использования
recipe_crud = CRUDRecipe()
print("✅ CRUD операции созданы и готовы к использованию!")