"""
Calorie Deficit Tracker API

Calculates and tracks calorie balance:
Net Deficit = Calories In - (BMR + Activity + Workouts)

Provides real-time deficit tracking that updates with every meal or workout.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, date, timedelta
from typing import Optional
from pydantic import BaseModel

from app.db import get_db
from app.models import User, UserProfile, FoodLog, Workout, DailyStat, WaterLog
from app.api.deps import get_current_user
from app.core.calculations import calculate_bmr, calculate_tdee

router = APIRouter()


# ============================================
# Schemas
# ============================================

class DeficitSummary(BaseModel):
    """Real-time calorie deficit summary."""
    date: str

    # Calories In
    calories_consumed: int
    meals_logged: int

    # Calories Out (Breakdown)
    bmr: int  # Basal Metabolic Rate
    activity_calories: int  # NEAT - Non-Exercise Activity
    workout_calories: int  # Exercise calories

    # Totals
    total_calories_out: int
    net_balance: int  # Positive = surplus, Negative = deficit

    # Goals
    calorie_goal: Optional[int]
    target_deficit: Optional[int]
    actual_vs_target: Optional[int]

    # Status
    status: str  # "deficit", "surplus", "maintenance"
    on_track: bool

    # Macros
    protein_consumed: float
    carbs_consumed: float
    fat_consumed: float

    # Progress
    deficit_percentage: Optional[float]


class WeeklyDeficitSummary(BaseModel):
    """Weekly calorie deficit analysis."""
    week_start: str
    week_end: str

    total_calories_in: int
    total_calories_out: int
    total_net_balance: int

    avg_daily_deficit: int
    days_in_deficit: int
    days_in_surplus: int

    projected_weight_change_kg: float  # Based on 7700 cal = 1kg
    daily_breakdown: list


# ============================================
# Helper Functions
# ============================================

def get_activity_multiplier(activity_level: str) -> float:
    """Get NEAT (Non-Exercise Activity) multiplier."""
    multipliers = {
        "sedentary": 1.2,
        "light": 1.375,
        "moderate": 1.55,
        "active": 1.725,
        "very_active": 1.9
    }
    return multipliers.get(activity_level, 1.55)


def calculate_daily_deficit(
    db: Session,
    user: User,
    target_date: date
) -> dict:
    """Calculate deficit for a specific date."""
    # Get user profile
    profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()

    # Calculate BMR (or use stored value)
    if profile and profile.bmr:
        bmr = int(profile.bmr)
    elif profile and profile.current_weight and profile.height and profile.birth_date and profile.gender:
        age = (date.today() - profile.birth_date).days // 365
        bmr = int(calculate_bmr(profile.current_weight, profile.height, age, profile.gender))
    else:
        bmr = 1800  # Default fallback

    # Get activity level multiplier
    activity_level = profile.activity_level if profile else "moderate"
    activity_mult = get_activity_multiplier(activity_level)

    # Activity calories = (TDEE - BMR) but we'll estimate as percentage of BMR
    activity_calories = int(bmr * (activity_mult - 1))

    # Get food logs for the date
    day_start = datetime.combine(target_date, datetime.min.time())
    day_end = datetime.combine(target_date + timedelta(days=1), datetime.min.time())

    food_logs = db.query(FoodLog).filter(
        FoodLog.user_id == user.id,
        FoodLog.logged_at >= day_start,
        FoodLog.logged_at < day_end
    ).all()

    calories_consumed = sum(f.calories for f in food_logs)
    protein = sum(f.protein or 0 for f in food_logs)
    carbs = sum(f.carbs or 0 for f in food_logs)
    fat = sum(f.fat or 0 for f in food_logs)

    # Get workout calories for the date
    workouts = db.query(Workout).filter(
        Workout.user_id == user.id,
        Workout.start_time >= day_start,
        Workout.start_time < day_end
    ).all()

    workout_calories = sum(w.calories_burned or 0 for w in workouts)

    # Calculate totals
    total_out = bmr + activity_calories + workout_calories
    net_balance = calories_consumed - total_out

    # Get calorie goal
    calorie_goal = profile.daily_calorie_goal if profile else None
    target_deficit = None
    actual_vs_target = None

    if calorie_goal:
        # Target deficit = TDEE - Goal
        tdee = bmr + activity_calories
        target_deficit = tdee - calorie_goal
        actual_deficit = -net_balance
        actual_vs_target = actual_deficit - target_deficit

    # Determine status
    if net_balance < -100:
        status = "deficit"
    elif net_balance > 100:
        status = "surplus"
    else:
        status = "maintenance"

    # Check if on track (within 200 cal of goal)
    on_track = True
    if calorie_goal:
        on_track = abs(calories_consumed - calorie_goal) <= 200

    return {
        "date": target_date.isoformat(),
        "calories_consumed": calories_consumed,
        "meals_logged": len(food_logs),
        "bmr": bmr,
        "activity_calories": activity_calories,
        "workout_calories": workout_calories,
        "total_calories_out": total_out,
        "net_balance": net_balance,
        "calorie_goal": calorie_goal,
        "target_deficit": target_deficit,
        "actual_vs_target": actual_vs_target,
        "status": status,
        "on_track": on_track,
        "protein_consumed": round(protein, 1),
        "carbs_consumed": round(carbs, 1),
        "fat_consumed": round(fat, 1),
        "deficit_percentage": round((abs(net_balance) / total_out) * 100, 1) if net_balance < 0 else None
    }


# ============================================
# Endpoints
# ============================================

@router.get("/today", response_model=DeficitSummary)
def get_today_deficit(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get today's calorie deficit summary.

    This updates in real-time as meals and workouts are logged.
    """
    result = calculate_daily_deficit(db, current_user, date.today())
    return DeficitSummary(**result)


@router.get("/date/{target_date}", response_model=DeficitSummary)
def get_date_deficit(
    target_date: date,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get calorie deficit for a specific date."""
    result = calculate_daily_deficit(db, current_user, target_date)
    return DeficitSummary(**result)


@router.get("/week", response_model=WeeklyDeficitSummary)
def get_weekly_deficit(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get weekly calorie deficit summary with weight change projection."""
    today = date.today()
    week_start = today - timedelta(days=6)

    daily_data = []
    total_in = 0
    total_out = 0
    days_deficit = 0
    days_surplus = 0

    for i in range(7):
        day = week_start + timedelta(days=i)
        day_data = calculate_daily_deficit(db, current_user, day)
        daily_data.append({
            "date": day.isoformat(),
            "calories_in": day_data["calories_consumed"],
            "calories_out": day_data["total_calories_out"],
            "net_balance": day_data["net_balance"],
            "status": day_data["status"]
        })

        total_in += day_data["calories_consumed"]
        total_out += day_data["total_calories_out"]

        if day_data["net_balance"] < 0:
            days_deficit += 1
        elif day_data["net_balance"] > 0:
            days_surplus += 1

    total_net = total_in - total_out
    avg_daily = total_net // 7

    # 7700 calories = ~1 kg of body weight
    projected_change = round(total_net / 7700, 2)

    return WeeklyDeficitSummary(
        week_start=week_start.isoformat(),
        week_end=today.isoformat(),
        total_calories_in=total_in,
        total_calories_out=total_out,
        total_net_balance=total_net,
        avg_daily_deficit=avg_daily,
        days_in_deficit=days_deficit,
        days_in_surplus=days_surplus,
        projected_weight_change_kg=projected_change,
        daily_breakdown=daily_data
    )


@router.get("/history/{days}")
def get_deficit_history(
    days: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get deficit history for the past N days."""
    if days > 90:
        days = 90

    history = []
    today = date.today()

    for i in range(days):
        day = today - timedelta(days=i)
        day_data = calculate_daily_deficit(db, current_user, day)
        history.append({
            "date": day.isoformat(),
            "calories_in": day_data["calories_consumed"],
            "calories_out": day_data["total_calories_out"],
            "net_balance": day_data["net_balance"],
            "workout_calories": day_data["workout_calories"],
            "status": day_data["status"]
        })

    return history


@router.get("/projection")
def get_weight_projection(
    weeks: int = 4,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Project weight change based on recent deficit trends.

    Uses the last 7 days to project future weight changes.
    """
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    current_weight = profile.current_weight if profile else None
    target_weight = profile.target_weight if profile else None

    # Get last 7 days deficit
    today = date.today()
    total_deficit = 0

    for i in range(7):
        day = today - timedelta(days=i)
        day_data = calculate_daily_deficit(db, current_user, day)
        total_deficit += day_data["net_balance"]

    avg_daily_deficit = total_deficit / 7

    # Project weight changes
    projections = []
    if current_weight:
        for week in range(1, weeks + 1):
            weekly_deficit = avg_daily_deficit * 7
            weight_change = weekly_deficit / 7700  # 7700 cal per kg
            projected_weight = current_weight + (weight_change * week)

            projections.append({
                "week": week,
                "projected_weight": round(projected_weight, 1),
                "projected_change": round(weight_change * week, 2)
            })

    # Days to reach target
    days_to_target = None
    if current_weight and target_weight and avg_daily_deficit != 0:
        weight_diff = current_weight - target_weight
        cal_needed = weight_diff * 7700
        days_to_target = int(abs(cal_needed / avg_daily_deficit))

    return {
        "current_weight": current_weight,
        "target_weight": target_weight,
        "avg_daily_deficit": round(avg_daily_deficit),
        "avg_weekly_deficit": round(avg_daily_deficit * 7),
        "projected_weekly_change_kg": round((avg_daily_deficit * 7) / 7700, 2),
        "projections": projections,
        "estimated_days_to_target": days_to_target
    }
