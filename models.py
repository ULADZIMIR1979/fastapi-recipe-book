"""
Модуль с моделями данных (таблицами базы данных)
Определяет структуру таблиц и связи между ними
"""

from sqlalchemy import Column, Integer, String, Text, Table, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

print("📊 Создаем модели данных...")

# Промежуточная таблица для связи многие-ко-многим между рецептами и ингредиентами
# Каждый рецепт может иметь много ингредиентов, каждый ингредиент может быть во многих рецептах
recipe_ingredient = Table(
    'recipe_ingredient',  # название таблицы
    Base.metadata,        # метаданные базового класса
    Column('recipe_id', Integer, ForeignKey('recipes.id')),      # внешний ключ к рецептам
    Column('ingredient_id', Integer, ForeignKey('ingredients.id')) # внешний ключ к ингредиентам
)

print("✅ Создана промежуточная таблица recipe_ingredient")


class Recipe(Base):
    """
    Модель рецепта - основная таблица с рецептами

    Атрибуты:
        id: уникальный идентификатор рецепта
        title: название рецепта
        cooking_time: время готовки в минутах
        description: текстовое описание рецепта
        views: количество просмотров (для популярности)
        ingredients: список ингредиентов этого рецепта
    """
    __tablename__ = "recipes"  # название таблицы в базе данных

    print("🍳 Создаем модель Recipe...")

    id = Column(Integer, primary_key=True, index=True)  # первичный ключ с индексом
    title = Column(String(100), nullable=False, index=True)  # название, обязательно, с индексом
    cooking_time = Column(Integer, nullable=False)  # время готовки в минутах, обязательно
    description = Column(Text, nullable=False)  # описание, обязательно
    views = Column(Integer, default=0, nullable=False)  # количество просмотров, по умолчанию 0

    # Связь многие-ко-многим с ингредиентами
    # secondary - указывает промежуточную таблицу
    # back_populates - создает обратную связь в модели Ingredient
    ingredients = relationship(
        "Ingredient",
        secondary=recipe_ingredient,
        back_populates="recipes"
    )

    print("✅ Модель Recipe создана!")

    def __repr__(self):
        return f"<Recipe(id={self.id}, title='{self.title}', views={self.views})>"


class Ingredient(Base):
    """
    Модель ингредиента - таблица с ингредиентами

    Атрибуты:
        id: уникальный идентификатор ингредиента
        name: название ингредиента
        recipes: список рецептов, в которых используется этот ингредиент
    """
    __tablename__ = "ingredients"

    print("🥕 Создаем модель Ingredient...")

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True, index=True)  # уникальное название

    # Обратная связь многие-ко-многим с рецептами
    recipes = relationship(
        "Recipe",
        secondary=recipe_ingredient,
        back_populates="ingredients"
    )

    print("✅ Модель Ingredient создана!")

    def __repr__(self):
        return f"<Ingredient(id={self.id}, name='{self.name}')>"


print("✅ Все модели данных созданы!")