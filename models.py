"""
Модуль с моделями данных (таблицами базы данных)
Определяет структуру таблиц и связи между ними
"""

from sqlalchemy import Column, ForeignKey, Integer, String, Table, Text
from sqlalchemy.orm import relationship

from database import Base

# Промежуточная таблица для связи многие-ко-многим между рецептами и ингредиентами
recipe_ingredient = Table(
    "recipe_ingredient",
    Base.metadata,
    Column("recipe_id", Integer, ForeignKey("recipes.id")),
    Column("ingredient_id", Integer, ForeignKey("ingredients.id")),
)


class Recipe(Base):
    """
    Модель рецепта - основная таблица с рецептами
    """

    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False, index=True)
    cooking_time = Column(Integer, nullable=False)
    description = Column(Text, nullable=False)
    views = Column(Integer, default=0, nullable=False)

    ingredients = relationship(
        "Ingredient", secondary=recipe_ingredient, back_populates="recipes"
    )

    def __repr__(self) -> str:
        return f"<Recipe(id={self.id}, title='{self.title}', views={self.views})>"


class Ingredient(Base):
    """
    Модель ингредиента - таблица с ингредиентами
    """

    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True, index=True)

    recipes = relationship(
        "Recipe", secondary=recipe_ingredient, back_populates="ingredients"
    )

    def __repr__(self) -> str:
        return f"<Ingredient(id={self.id}, name='{self.name}')>"
