"""
WellNest Health API Endpoints

Handles food logging, weight tracking, water intake, and AI food analysis.
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime, date, timedelta
import base64

from app.db import get_db
from app.models import WeightLog, FoodLog, WaterLog, User, UserProfile, DailyStat
from app.schemas import (
    WeightLogCreate, WeightLogResponse,
    FoodLogCreate, FoodLogResponse,
    WaterLogCreate, WaterLogResponse,
    FoodAnalysisRequest, FoodAnalysisResponse, FoodItemAnalysis,
    DashboardSummary, MacroBreakdown,
    FoodSearchResult, FoodSearchResponse
)
from app.api.deps import get_current_user
from app.services.ai_vision import FoodAnalyzer, AnalysisConfidence
from app.services.fatsecret import FatSecretClient

router = APIRouter()


# ============================================
# Weight Logging Endpoints
# ============================================

@router.post("/weight", response_model=WeightLogResponse)
def log_weight(
    log: WeightLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Log a weight entry."""
    db_log = WeightLog(
        weight=log.weight,
        user_id=current_user.id,
        body_fat_percentage=log.body_fat_percentage,
        muscle_mass=log.muscle_mass,
        source=log.source,
        logged_at=log.logged_at or datetime.utcnow()
    )
    db.add(db_log)

    # Update profile's current weight
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if profile:
        profile.current_weight = log.weight

    db.commit()
    db.refresh(db_log)
    return db_log


@router.get("/weight", response_model=List[WeightLogResponse])
def get_weight_logs(
    limit: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get weight history."""
    return db.query(WeightLog).filter(
        WeightLog.user_id == current_user.id
    ).order_by(WeightLog.logged_at.desc()).limit(limit).all()


@router.get("/weight/stats")
def get_weight_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get weight statistics and trends."""
    logs = db.query(WeightLog).filter(
        WeightLog.user_id == current_user.id
    ).order_by(WeightLog.logged_at.desc()).limit(90).all()

    if not logs:
        return {
            "current_weight": None,
            "weight_7_days_ago": None,
            "weight_30_days_ago": None,
            "change_7_days": None,
            "change_30_days": None,
            "trend": "stable"
        }

    current_weight = logs[0].weight

    # Find weights from 7 and 30 days ago
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)

    weight_7_days = None
    weight_30_days = None

    for log in logs:
        if log.logged_at <= seven_days_ago and weight_7_days is None:
            weight_7_days = log.weight
        if log.logged_at <= thirty_days_ago and weight_30_days is None:
            weight_30_days = log.weight
            break

    # Calculate changes
    change_7 = round(current_weight - weight_7_days, 2) if weight_7_days else None
    change_30 = round(current_weight - weight_30_days, 2) if weight_30_days else None

    # Determine trend
    if change_7 is not None:
        if change_7 < -0.5:
            trend = "losing"
        elif change_7 > 0.5:
            trend = "gaining"
        else:
            trend = "stable"
    else:
        trend = "insufficient_data"

    return {
        "current_weight": current_weight,
        "weight_7_days_ago": weight_7_days,
        "weight_30_days_ago": weight_30_days,
        "change_7_days": change_7,
        "change_30_days": change_30,
        "trend": trend
    }


# ============================================
# Food Search Endpoints
# ============================================

@router.get("/food/search", response_model=FoodSearchResponse)
def search_foods(
    query: str,
    max_results: int = 10,
    current_user: User = Depends(get_current_user)
):
    """
    Search for foods using FatSecret API.

    Returns nutritional information for matching foods.
    """
    if not query or len(query) < 2:
        raise HTTPException(
            status_code=400,
            detail="Search query must be at least 2 characters"
        )

    client = FatSecretClient()
    results = client.search_foods(query, max_results=max_results)

    return FoodSearchResponse(
        results=[
            FoodSearchResult(
                food_id=r.food_id,
                food_name=r.food_name,
                brand_name=r.brand_name,
                food_type=r.food_type,
                calories=r.calories,
                protein=r.protein,
                carbs=r.carbs,
                fat=r.fat,
                fiber=r.fiber,
                serving_size=r.serving_size,
                serving_description=r.serving_description
            )
            for r in results
        ],
        query=query,
        total_results=len(results)
    )


# ============================================
# Food Logging Endpoints
# ============================================

@router.post("/food", response_model=FoodLogResponse)
def log_food(
    log: FoodLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Log a food entry."""
    db_log = FoodLog(
        user_id=current_user.id,
        food_name=log.food_name,
        calories=log.calories,
        protein=log.protein,
        carbs=log.carbs,
        fat=log.fat,
        fiber=log.fiber,
        serving_size=log.serving_size,
        serving_unit=log.serving_unit,
        meal_type=log.meal_type,
        image_url=log.image_url,
        ai_analyzed=log.ai_analyzed,
        ai_confidence_score=log.ai_confidence_score,
        logged_at=log.logged_at or datetime.utcnow()
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log


@router.get("/food", response_model=List[FoodLogResponse])
def get_food_logs(
    date_filter: Optional[date] = None,
    meal_type: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get food logs with optional filtering."""
    query = db.query(FoodLog).filter(FoodLog.user_id == current_user.id)

    if date_filter:
        day_start = datetime.combine(date_filter, datetime.min.time())
        day_end = datetime.combine(date_filter + timedelta(days=1), datetime.min.time())
        query = query.filter(FoodLog.logged_at >= day_start, FoodLog.logged_at < day_end)

    if meal_type:
        query = query.filter(FoodLog.meal_type == meal_type)

    return query.order_by(FoodLog.logged_at.desc()).limit(limit).all()


@router.delete("/food/{food_id}")
def delete_food_log(
    food_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a food log entry."""
    food_log = db.query(FoodLog).filter(
        FoodLog.id == food_id,
        FoodLog.user_id == current_user.id
    ).first()

    if not food_log:
        raise HTTPException(status_code=404, detail="Food log not found")

    db.delete(food_log)
    db.commit()
    return {"message": "Food log deleted successfully"}


@router.post("/food/analyze", response_model=FoodAnalysisResponse)
async def analyze_food_image(
    request: FoodAnalysisRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Analyze a food image using Claude Vision AI.

    Returns identified foods with nutritional estimates.
    """
    try:
        # Decode base64 image
        image_data = base64.b64decode(request.image_base64)

        # Initialize analyzer
        analyzer = FoodAnalyzer()

        # Build context
        context = request.additional_context
        if request.meal_type:
            context = f"This is a {request.meal_type}. " + (context or "")

        # Analyze image
        result = await analyzer.analyze_food_image(
            image_data=image_data,
            image_type=request.image_type,
            additional_context=context
        )

        # Convert to response format
        food_items = [
            FoodItemAnalysis(
                name=item.name,
                name_tr=item.name_tr,
                estimated_portion=item.estimated_portion,
                calories=item.calories,
                protein=item.protein,
                carbs=item.carbs,
                fat=item.fat,
                fiber=item.fiber,
                confidence=item.confidence
            )
            for item in result.food_items
        ]

        return FoodAnalysisResponse(
            success=result.success,
            food_items=food_items,
            total_calories=result.total_calories,
            total_protein=result.total_protein,
            total_carbs=result.total_carbs,
            total_fat=result.total_fat,
            total_fiber=result.total_fiber,
            meal_type_suggestion=result.meal_type_suggestion,
            confidence_level=result.confidence_level.value,
            error_message=result.error_message
        )

    except Exception as e:
        return FoodAnalysisResponse(
            success=False,
            error_message=f"Analysis failed: {str(e)}"
        )


@router.post("/food/analyze/upload", response_model=FoodAnalysisResponse)
async def analyze_food_image_upload(
    file: UploadFile = File(...),
    meal_type: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Analyze a food image uploaded as a file.
    """
    try:
        # Read file content
        image_data = await file.read()

        # Determine image type
        content_type = file.content_type or "image/jpeg"

        # Initialize analyzer
        analyzer = FoodAnalyzer()

        # Build context
        context = None
        if meal_type:
            context = f"This is a {meal_type}."

        # Analyze image
        result = await analyzer.analyze_food_image(
            image_data=image_data,
            image_type=content_type,
            additional_context=context
        )

        # Convert to response format
        food_items = [
            FoodItemAnalysis(
                name=item.name,
                name_tr=item.name_tr,
                estimated_portion=item.estimated_portion,
                calories=item.calories,
                protein=item.protein,
                carbs=item.carbs,
                fat=item.fat,
                fiber=item.fiber,
                confidence=item.confidence
            )
            for item in result.food_items
        ]

        return FoodAnalysisResponse(
            success=result.success,
            food_items=food_items,
            total_calories=result.total_calories,
            total_protein=result.total_protein,
            total_carbs=result.total_carbs,
            total_fat=result.total_fat,
            total_fiber=result.total_fiber,
            meal_type_suggestion=result.meal_type_suggestion,
            confidence_level=result.confidence_level.value,
            error_message=result.error_message
        )

    except Exception as e:
        return FoodAnalysisResponse(
            success=False,
            error_message=f"Analysis failed: {str(e)}"
        )


# ============================================
# Water Tracking Endpoints
# ============================================

@router.post("/water", response_model=WaterLogResponse)
def log_water(
    log: WaterLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Log water intake."""
    db_log = WaterLog(
        user_id=current_user.id,
        amount_ml=log.amount_ml,
        logged_at=log.logged_at or datetime.utcnow()
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log


@router.get("/water", response_model=List[WaterLogResponse])
def get_water_logs(
    date_filter: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get water intake logs."""
    query = db.query(WaterLog).filter(WaterLog.user_id == current_user.id)

    if date_filter:
        day_start = datetime.combine(date_filter, datetime.min.time())
        day_end = datetime.combine(date_filter + timedelta(days=1), datetime.min.time())
        query = query.filter(WaterLog.logged_at >= day_start, WaterLog.logged_at < day_end)

    return query.order_by(WaterLog.logged_at.desc()).all()


@router.get("/water/today")
def get_today_water(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get today's total water intake."""
    today = datetime.utcnow().date()
    today_start = datetime.combine(today, datetime.min.time())
    today_end = datetime.combine(today + timedelta(days=1), datetime.min.time())

    total = db.query(func.sum(WaterLog.amount_ml)).filter(
        WaterLog.user_id == current_user.id,
        WaterLog.logged_at >= today_start,
        WaterLog.logged_at < today_end
    ).scalar() or 0

    # Get water goal from profile
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    water_goal = profile.daily_water_goal if profile else 2500

    return {
        "total_ml": total,
        "goal_ml": water_goal,
        "percentage": round((total / water_goal) * 100, 1) if water_goal > 0 else 0
    }


# ============================================
# Dashboard & Summary Endpoints
# ============================================

@router.get("/dashboard", response_model=DashboardSummary)
def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive dashboard summary."""
    today = datetime.utcnow().date()
    today_start = datetime.combine(today, datetime.min.time())
    today_end = datetime.combine(today + timedelta(days=1), datetime.min.time())

    # Get user profile for goals
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()

    # Today's food logs
    todays_food = db.query(FoodLog).filter(
        FoodLog.user_id == current_user.id,
        FoodLog.logged_at >= today_start,
        FoodLog.logged_at < today_end
    ).all()

    total_calories = sum(f.calories for f in todays_food)
    total_protein = sum(f.protein or 0 for f in todays_food)
    total_carbs = sum(f.carbs or 0 for f in todays_food)
    total_fat = sum(f.fat or 0 for f in todays_food)

    # Today's water intake
    total_water = db.query(func.sum(WaterLog.amount_ml)).filter(
        WaterLog.user_id == current_user.id,
        WaterLog.logged_at >= today_start,
        WaterLog.logged_at < today_end
    ).scalar() or 0

    # Latest weight
    latest_weight = db.query(WeightLog).filter(
        WeightLog.user_id == current_user.id
    ).order_by(WeightLog.logged_at.desc()).first()

    # Weight change over last week
    week_ago = datetime.utcnow() - timedelta(days=7)
    weight_week_ago = db.query(WeightLog).filter(
        WeightLog.user_id == current_user.id,
        WeightLog.logged_at <= week_ago
    ).order_by(WeightLog.logged_at.desc()).first()

    weight_change = None
    if latest_weight and weight_week_ago:
        weight_change = round(latest_weight.weight - weight_week_ago.weight, 2)

    # Get daily stats for activity data (if available)
    daily_stat = db.query(DailyStat).filter(
        DailyStat.user_id == current_user.id,
        DailyStat.date == today
    ).first()

    # Calculate calories remaining
    calorie_goal = profile.daily_calorie_goal if profile else None
    calories_remaining = calorie_goal - total_calories if calorie_goal else None

    return DashboardSummary(
        today_calories=total_calories,
        calorie_goal=calorie_goal,
        calories_remaining=calories_remaining,
        calories_burned=daily_stat.active_calories if daily_stat else 0,
        today_protein=round(total_protein, 1),
        today_carbs=round(total_carbs, 1),
        today_fat=round(total_fat, 1),
        protein_goal=profile.protein_goal if profile else None,
        carbs_goal=profile.carbs_goal if profile else None,
        fat_goal=profile.fat_goal if profile else None,
        today_water_ml=total_water,
        water_goal=profile.daily_water_goal if profile else 2500,
        current_weight=latest_weight.weight if latest_weight else None,
        target_weight=profile.target_weight if profile else None,
        weight_change_week=weight_change,
        steps=daily_stat.steps if daily_stat else 0,
        active_minutes=daily_stat.exercise_minutes if daily_stat else 0,
        recovery_score=daily_stat.recovery_score if daily_stat else None,
        sleep_hours=daily_stat.sleep_hours if daily_stat else None,
        meals_logged=len(todays_food)
    )


@router.get("/macros/today", response_model=MacroBreakdown)
def get_today_macros(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get detailed macro breakdown for today."""
    today = datetime.utcnow().date()
    today_start = datetime.combine(today, datetime.min.time())
    today_end = datetime.combine(today + timedelta(days=1), datetime.min.time())

    todays_food = db.query(FoodLog).filter(
        FoodLog.user_id == current_user.id,
        FoodLog.logged_at >= today_start,
        FoodLog.logged_at < today_end
    ).all()

    total_protein = sum(f.protein or 0 for f in todays_food)
    total_carbs = sum(f.carbs or 0 for f in todays_food)
    total_fat = sum(f.fat or 0 for f in todays_food)
    total_fiber = sum(f.fiber or 0 for f in todays_food)

    # Calculate total calories from macros
    total_macro_calories = (total_protein * 4) + (total_carbs * 4) + (total_fat * 9)

    # Calculate percentages
    if total_macro_calories > 0:
        protein_pct = (total_protein * 4 / total_macro_calories) * 100
        carbs_pct = (total_carbs * 4 / total_macro_calories) * 100
        fat_pct = (total_fat * 9 / total_macro_calories) * 100
    else:
        protein_pct = carbs_pct = fat_pct = 0

    return MacroBreakdown(
        protein_grams=round(total_protein, 1),
        protein_percentage=round(protein_pct, 1),
        carbs_grams=round(total_carbs, 1),
        carbs_percentage=round(carbs_pct, 1),
        fat_grams=round(total_fat, 1),
        fat_percentage=round(fat_pct, 1),
        fiber_grams=round(total_fiber, 1)
    )


@router.get("/history/{days}")
def get_nutrition_history(
    days: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get nutrition history for the past N days."""
    if days > 90:
        days = 90

    history = []
    for i in range(days):
        target_date = datetime.utcnow().date() - timedelta(days=i)
        day_start = datetime.combine(target_date, datetime.min.time())
        day_end = datetime.combine(target_date + timedelta(days=1), datetime.min.time())

        food_logs = db.query(FoodLog).filter(
            FoodLog.user_id == current_user.id,
            FoodLog.logged_at >= day_start,
            FoodLog.logged_at < day_end
        ).all()

        water_total = db.query(func.sum(WaterLog.amount_ml)).filter(
            WaterLog.user_id == current_user.id,
            WaterLog.logged_at >= day_start,
            WaterLog.logged_at < day_end
        ).scalar() or 0

        history.append({
            "date": target_date.isoformat(),
            "calories": sum(f.calories for f in food_logs),
            "protein": round(sum(f.protein or 0 for f in food_logs), 1),
            "carbs": round(sum(f.carbs or 0 for f in food_logs), 1),
            "fat": round(sum(f.fat or 0 for f in food_logs), 1),
            "water_ml": water_total,
            "meals_count": len(food_logs)
        })

    return history
