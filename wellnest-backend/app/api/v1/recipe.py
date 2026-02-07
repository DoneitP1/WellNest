"""
Recipe Library API - Healthy recipes with calculated nutrition

Provides a searchable library of recipes with full nutritional information.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
import json

from app.db import get_db
from app.models import User, Recipe, UserProfile
from app.api.deps import get_current_user

router = APIRouter()


# ============================================
# Schemas
# ============================================

class IngredientSchema(BaseModel):
    name: str
    amount: float
    unit: str
    calories: Optional[int] = 0
    protein: Optional[float] = 0
    carbs: Optional[float] = 0
    fat: Optional[float] = 0


class RecipeCreate(BaseModel):
    name: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    prep_time_minutes: Optional[int] = None
    cook_time_minutes: Optional[int] = None
    servings: int = 1
    difficulty: str = "easy"
    ingredients: List[IngredientSchema]
    instructions: List[str]
    category: Optional[str] = None
    tags: Optional[str] = None
    cuisine: Optional[str] = None


class RecipeResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    image_url: Optional[str]
    prep_time_minutes: Optional[int]
    cook_time_minutes: Optional[int]
    total_time_minutes: Optional[int]
    servings: int
    difficulty: str
    ingredients: List[dict]
    instructions: List[str]
    calories_per_serving: int
    protein_per_serving: float
    carbs_per_serving: float
    fat_per_serving: float
    fiber_per_serving: float
    category: Optional[str]
    tags: Optional[str]
    cuisine: Optional[str]
    is_verified: bool
    saves_count: int
    rating_avg: float
    rating_count: int
    created_by: Optional[str]
    created_at: datetime


class RecipeSummary(BaseModel):
    id: str
    name: str
    description: Optional[str]
    image_url: Optional[str]
    total_time_minutes: Optional[int]
    difficulty: str
    calories_per_serving: int
    protein_per_serving: float
    category: Optional[str]
    tags: Optional[str]
    saves_count: int
    rating_avg: float


# ============================================
# Endpoints
# ============================================

@router.get("/", response_model=List[RecipeSummary])
def get_recipes(
    category: Optional[str] = None,
    tags: Optional[str] = None,
    cuisine: Optional[str] = None,
    difficulty: Optional[str] = None,
    max_calories: Optional[int] = None,
    min_protein: Optional[float] = None,
    search: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    Get recipes with optional filtering.

    Supports filtering by category, tags, cuisine, difficulty, and nutrition.
    """
    query = db.query(Recipe).filter(Recipe.is_public == True)

    if category:
        query = query.filter(Recipe.category == category)
    if cuisine:
        query = query.filter(Recipe.cuisine == cuisine)
    if difficulty:
        query = query.filter(Recipe.difficulty == difficulty)
    if max_calories:
        query = query.filter(Recipe.calories_per_serving <= max_calories)
    if min_protein:
        query = query.filter(Recipe.protein_per_serving >= min_protein)
    if tags:
        query = query.filter(Recipe.tags.contains(tags))
    if search:
        query = query.filter(
            or_(
                Recipe.name.ilike(f"%{search}%"),
                Recipe.description.ilike(f"%{search}%")
            )
        )

    recipes = query.order_by(desc(Recipe.saves_count)).offset(offset).limit(limit).all()

    return [
        RecipeSummary(
            id=r.id,
            name=r.name,
            description=r.description,
            image_url=r.image_url,
            total_time_minutes=(r.prep_time_minutes or 0) + (r.cook_time_minutes or 0) or None,
            difficulty=r.difficulty,
            calories_per_serving=r.calories_per_serving,
            protein_per_serving=r.protein_per_serving,
            category=r.category,
            tags=r.tags,
            saves_count=r.saves_count,
            rating_avg=r.rating_avg
        )
        for r in recipes
    ]


@router.get("/categories")
def get_recipe_categories(db: Session = Depends(get_db)):
    """Get available recipe categories with counts."""
    recipes = db.query(Recipe).filter(Recipe.is_public == True).all()

    categories = {}
    for r in recipes:
        if r.category:
            categories[r.category] = categories.get(r.category, 0) + 1

    return [
        {"name": cat, "count": count}
        for cat, count in sorted(categories.items())
    ]


@router.get("/tags")
def get_recipe_tags(db: Session = Depends(get_db)):
    """Get popular recipe tags."""
    recipes = db.query(Recipe).filter(Recipe.is_public == True).all()

    tags = {}
    for r in recipes:
        if r.tags:
            for tag in r.tags.split(","):
                tag = tag.strip()
                tags[tag] = tags.get(tag, 0) + 1

    return sorted(
        [{"name": tag, "count": count} for tag, count in tags.items()],
        key=lambda x: x["count"],
        reverse=True
    )[:20]


@router.get("/{recipe_id}", response_model=RecipeResponse)
def get_recipe(
    recipe_id: str,
    db: Session = Depends(get_db)
):
    """Get detailed recipe by ID."""
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()

    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    # Get creator info
    creator_name = None
    if recipe.created_by:
        profile = db.query(UserProfile).filter(UserProfile.user_id == recipe.created_by).first()
        if profile and profile.first_name:
            creator_name = f"{profile.first_name} {profile.last_name or ''}".strip()

    return RecipeResponse(
        id=recipe.id,
        name=recipe.name,
        description=recipe.description,
        image_url=recipe.image_url,
        prep_time_minutes=recipe.prep_time_minutes,
        cook_time_minutes=recipe.cook_time_minutes,
        total_time_minutes=(recipe.prep_time_minutes or 0) + (recipe.cook_time_minutes or 0) or None,
        servings=recipe.servings,
        difficulty=recipe.difficulty,
        ingredients=json.loads(recipe.ingredients) if recipe.ingredients else [],
        instructions=json.loads(recipe.instructions) if recipe.instructions else [],
        calories_per_serving=recipe.calories_per_serving,
        protein_per_serving=recipe.protein_per_serving,
        carbs_per_serving=recipe.carbs_per_serving,
        fat_per_serving=recipe.fat_per_serving,
        fiber_per_serving=recipe.fiber_per_serving,
        category=recipe.category,
        tags=recipe.tags,
        cuisine=recipe.cuisine,
        is_verified=recipe.is_verified,
        saves_count=recipe.saves_count,
        rating_avg=recipe.rating_avg,
        rating_count=recipe.rating_count,
        created_by=creator_name,
        created_at=recipe.created_at
    )


@router.post("/", response_model=RecipeResponse)
def create_recipe(
    recipe_data: RecipeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new recipe."""
    # Calculate nutrition from ingredients
    total_calories = 0
    total_protein = 0
    total_carbs = 0
    total_fat = 0
    total_fiber = 0

    ingredients_list = []
    for ing in recipe_data.ingredients:
        ingredients_list.append(ing.dict())
        total_calories += ing.calories or 0
        total_protein += ing.protein or 0
        total_carbs += ing.carbs or 0
        total_fat += ing.fat or 0

    # Per serving values
    servings = recipe_data.servings or 1
    cal_per_serving = total_calories // servings
    protein_per_serving = round(total_protein / servings, 1)
    carbs_per_serving = round(total_carbs / servings, 1)
    fat_per_serving = round(total_fat / servings, 1)
    fiber_per_serving = round(total_fiber / servings, 1)

    recipe = Recipe(
        created_by=current_user.id,
        name=recipe_data.name,
        description=recipe_data.description,
        image_url=recipe_data.image_url,
        prep_time_minutes=recipe_data.prep_time_minutes,
        cook_time_minutes=recipe_data.cook_time_minutes,
        servings=servings,
        difficulty=recipe_data.difficulty,
        ingredients=json.dumps(ingredients_list),
        instructions=json.dumps(recipe_data.instructions),
        calories_per_serving=cal_per_serving,
        protein_per_serving=protein_per_serving,
        carbs_per_serving=carbs_per_serving,
        fat_per_serving=fat_per_serving,
        fiber_per_serving=fiber_per_serving,
        category=recipe_data.category,
        tags=recipe_data.tags,
        cuisine=recipe_data.cuisine
    )

    db.add(recipe)
    db.commit()
    db.refresh(recipe)

    return RecipeResponse(
        id=recipe.id,
        name=recipe.name,
        description=recipe.description,
        image_url=recipe.image_url,
        prep_time_minutes=recipe.prep_time_minutes,
        cook_time_minutes=recipe.cook_time_minutes,
        total_time_minutes=(recipe.prep_time_minutes or 0) + (recipe.cook_time_minutes or 0) or None,
        servings=recipe.servings,
        difficulty=recipe.difficulty,
        ingredients=ingredients_list,
        instructions=recipe_data.instructions,
        calories_per_serving=recipe.calories_per_serving,
        protein_per_serving=recipe.protein_per_serving,
        carbs_per_serving=recipe.carbs_per_serving,
        fat_per_serving=recipe.fat_per_serving,
        fiber_per_serving=recipe.fiber_per_serving,
        category=recipe.category,
        tags=recipe.tags,
        cuisine=recipe.cuisine,
        is_verified=False,
        saves_count=0,
        rating_avg=0,
        rating_count=0,
        created_by=current_user.username,
        created_at=recipe.created_at
    )


@router.post("/{recipe_id}/save")
def save_recipe(
    recipe_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Save/bookmark a recipe."""
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()

    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    recipe.saves_count += 1
    db.commit()

    return {"message": "Recipe saved", "saves_count": recipe.saves_count}


@router.post("/{recipe_id}/log")
def log_recipe_as_meal(
    recipe_id: str,
    servings: float = 1,
    meal_type: str = "snack",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add a recipe to food log."""
    from app.models import FoodLog

    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()

    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    food_log = FoodLog(
        user_id=current_user.id,
        food_name=recipe.name,
        calories=int(recipe.calories_per_serving * servings),
        protein=round(recipe.protein_per_serving * servings, 1),
        carbs=round(recipe.carbs_per_serving * servings, 1),
        fat=round(recipe.fat_per_serving * servings, 1),
        fiber=round(recipe.fiber_per_serving * servings, 1),
        serving_size=servings,
        serving_unit="serving",
        meal_type=meal_type,
        logged_at=datetime.utcnow()
    )

    db.add(food_log)

    # Award XP
    from app.services.gamification import GamificationService
    gamification = GamificationService(db)
    gamification.add_xp(current_user, "meal_logged", f"Logged {recipe.name}")
    gamification.update_streak(current_user)

    db.commit()

    return {
        "message": f"Added {recipe.name} to your food log",
        "calories": food_log.calories,
        "food_log_id": food_log.id
    }
