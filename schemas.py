"""
Модуль с Pydantic схемами для валидации данных
Схемы определяют структуру данных для API запросов и ответов
"""

from typing import List, Optional

from pydantic import BaseModel, Field


class IngredientBase(BaseModel):
    """Базовая схема для ингредиента"""

    name: str = Field(..., max_length=50, description="Название ингредиента")


class IngredientCreate(IngredientBase):
    """Схема для создания нового ингредиента"""


class IngredientResponse(IngredientBase):
    """Схема для ответа с данными ингредиента"""

    id: int

    class Config:
        from_attributes = True


class RecipeBase(BaseModel):
    """Базовая схема для рецепта"""

    title: str = Field(..., max_length=100, description="Название рецепта")
    cooking_time: int = Field(..., ge=1, description="Время готовки в минутах")
    description: str = Field(..., description="Подробное описание рецепта")


class RecipeCreate(RecipeBase):
    """Схема для создания нового рецепта"""

    ingredient_names: List[str] = Field(..., description="Список названий ингредиентов")


class RecipeUpdate(BaseModel):
    """Схема для обновления рецепта"""

    title: Optional[str] = Field(None, max_length=100)
    cooking_time: Optional[int] = Field(None, ge=1)
    description: Optional[str] = Field(None)


class RecipeListResponse(BaseModel):
    """
    Схема для ответа со списком рецептов (используется в таблице рецептов)
    """

    id: int
    title: str
    views: int
    cooking_time: int

    class Config:
        from_attributes = True


class RecipeDetailResponse(RecipeBase):
    """
    Схема для детального ответа с информацией о рецепте
    """

    id: int
    views: int
    ingredients: List[IngredientResponse]

    class Config:
        from_attributes = True
