"""
Модуль с Pydantic схемами для валидации данных
Схемы определяют структуру данных для API запросов и ответов
"""

from pydantic import BaseModel, Field
from typing import List, Optional

print("📋 Создаем Pydantic схемы для валидации данных...")

class IngredientBase(BaseModel):
    """Базовая схема для ингредиента"""
    name: str = Field(..., max_length=50, description="Название ингредиента")

    print("✅ Создана базовая схема IngredientBase")


class IngredientCreate(IngredientBase):
    """Схема для создания нового ингредиента"""
    print("✅ Создана схема IngredientCreate для создания ингредиентов")


class IngredientResponse(IngredientBase):
    """Схема для ответа с данными ингредиента"""
    id: int

    class Config:
        from_attributes = True

    print("✅ Создана схема IngredientResponse для ответов API")


class RecipeBase(BaseModel):
    """Базовая схема для рецепта"""
    title: str = Field(..., max_length=100, description="Название рецепта")
    cooking_time: int = Field(..., ge=1, description="Время готовки в минутах")
    description: str = Field(..., description="Подробное описание рецепта")

    print("✅ Создана базовая схема RecipeBase")


class RecipeCreate(RecipeBase):
    """Схема для создания нового рецепта"""
    ingredient_names: List[str] = Field(..., description="Список названий ингредиентов")

    print("✅ Создана схема RecipeCreate для создания рецептов")


class RecipeUpdate(BaseModel):
    """Схема для обновления рецепта"""
    title: Optional[str] = Field(None, max_length=100)
    cooking_time: Optional[int] = Field(None, ge=1)
    description: Optional[str] = Field(None)

    print("✅ Создана схема RecipeUpdate для обновления рецептов")


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

    print("✅ Создана схема RecipeListResponse для списка рецептов")


class RecipeDetailResponse(RecipeBase):
    """
    Схема для детального ответа с информацией о рецепте
    """
    id: int
    views: int
    ingredients: List[IngredientResponse]

    class Config:
        from_attributes = True

    print("✅ Создана схема RecipeDetailResponse для детальной информации о рецепте")


print("✅ Все Pydantic схемы созданы!")