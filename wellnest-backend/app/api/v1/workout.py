"""
Workout/Training API - Track workouts and calories burned

Includes calorie burning calculations for different workout types.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List, Optional
from datetime import datetime, date, timedelta
from pydantic import BaseModel
import json

from app.db import get_db
from app.models import User, Workout, WorkoutProgram, UserProfile, DailyStat
from app.api.deps import get_current_user
from app.services.gamification import GamificationService

router = APIRouter()


# ============================================
# Schemas
# ============================================

class ExerciseSet(BaseModel):
    exercise_name: str
    sets: int
    reps: int
    weight_kg: Optional[float] = None


class WorkoutCreate(BaseModel):
    workout_type: str = "other"
    name: Optional[str] = None
    description: Optional[str] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    calories_burned: Optional[int] = None
    intensity: str = "moderate"
    avg_heart_rate: Optional[int] = None
    max_heart_rate: Optional[int] = None
    distance_km: Optional[float] = None
    steps: Optional[int] = None
    exercises: Optional[List[ExerciseSet]] = None
    notes: Optional[str] = None
    rpe_score: Optional[int] = None


class WorkoutResponse(BaseModel):
    id: str
    workout_type: str
    name: Optional[str]
    description: Optional[str]
    start_time: datetime
    end_time: Optional[datetime]
    duration_minutes: Optional[int]
    calories_burned: int
    calories_source: str
    intensity: str
    avg_heart_rate: Optional[int]
    max_heart_rate: Optional[int]
    distance_km: Optional[float]
    steps: Optional[int]
    exercises: Optional[List[dict]]
    notes: Optional[str]
    rpe_score: Optional[int]
    xp_earned: int = 0
    created_at: datetime


class WorkoutStats(BaseModel):
    total_workouts: int
    total_minutes: int
    total_calories_burned: int
    workouts_this_week: int
    avg_duration_minutes: float
    favorite_type: Optional[str]
    streak_days: int


class WorkoutProgramResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    difficulty: str
    duration_weeks: int
    workouts_per_week: int
    category: Optional[str]
    target_goals: Optional[str]


# ============================================
# Calorie Calculation
# ============================================

# MET values for different activities (Metabolic Equivalent of Task)
MET_VALUES = {
    "strength": 6.0,
    "cardio": 7.0,
    "hiit": 10.0,
    "yoga": 3.0,
    "swimming": 8.0,
    "cycling": 7.5,
    "running": 9.8,
    "walking": 3.8,
    "sports": 7.0,
    "other": 5.0
}

INTENSITY_MULTIPLIERS = {
    "low": 0.8,
    "moderate": 1.0,
    "high": 1.25,
    "very_high": 1.5
}


def calculate_calories_burned(
    workout_type: str,
    duration_minutes: int,
    weight_kg: float,
    intensity: str = "moderate"
) -> int:
    """
    Calculate calories burned using MET formula.

    Calories = MET × Weight(kg) × Duration(hours)
    """
    met = MET_VALUES.get(workout_type, 5.0)
    intensity_mult = INTENSITY_MULTIPLIERS.get(intensity, 1.0)

    duration_hours = duration_minutes / 60
    calories = met * weight_kg * duration_hours * intensity_mult

    return int(calories)


# ============================================
# Endpoints
# ============================================

@router.post("/", response_model=WorkoutResponse)
def log_workout(
    workout_data: WorkoutCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Log a completed workout."""
    # Calculate duration if not provided
    duration = workout_data.duration_minutes
    if not duration and workout_data.end_time:
        delta = workout_data.end_time - workout_data.start_time
        duration = int(delta.total_seconds() / 60)

    # Get user weight for calorie calculation
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    weight_kg = profile.current_weight if profile and profile.current_weight else 70

    # Calculate or use provided calories
    calories_source = "manual"
    if workout_data.calories_burned:
        calories = workout_data.calories_burned
    elif duration:
        calories = calculate_calories_burned(
            workout_data.workout_type,
            duration,
            weight_kg,
            workout_data.intensity
        )
        calories_source = "calculated"
    else:
        calories = 0

    # Prepare exercises JSON
    exercises_json = None
    if workout_data.exercises:
        exercises_json = json.dumps([e.dict() for e in workout_data.exercises])

    workout = Workout(
        user_id=current_user.id,
        workout_type=workout_data.workout_type,
        name=workout_data.name or f"{workout_data.workout_type.title()} Workout",
        description=workout_data.description,
        start_time=workout_data.start_time,
        end_time=workout_data.end_time,
        duration_minutes=duration,
        calories_burned=calories,
        calories_source=calories_source,
        intensity=workout_data.intensity,
        avg_heart_rate=workout_data.avg_heart_rate,
        max_heart_rate=workout_data.max_heart_rate,
        distance_km=workout_data.distance_km,
        steps=workout_data.steps,
        exercises_data=exercises_json,
        notes=workout_data.notes,
        rpe_score=workout_data.rpe_score
    )

    db.add(workout)

    # Update daily stats with workout calories
    today = date.today()
    daily_stat = db.query(DailyStat).filter(
        DailyStat.user_id == current_user.id,
        DailyStat.date == today
    ).first()

    if daily_stat:
        daily_stat.workout_calories = (daily_stat.workout_calories or 0) + calories
        daily_stat.exercise_minutes = (daily_stat.exercise_minutes or 0) + (duration or 0)
    else:
        daily_stat = DailyStat(
            user_id=current_user.id,
            date=today,
            workout_calories=calories,
            exercise_minutes=duration or 0
        )
        db.add(daily_stat)

    # Award XP
    gamification = GamificationService(db)

    # Base XP for workout
    xp_earned, leveled_up, new_level = gamification.add_xp(
        current_user,
        "workout_completed",
        f"Completed {workout_data.workout_type} workout"
    )

    # Bonus XP for duration
    if duration and duration >= 60:
        bonus_xp, _, _ = gamification.add_xp(current_user, "workout_60_min")
        xp_earned += bonus_xp
    elif duration and duration >= 30:
        bonus_xp, _, _ = gamification.add_xp(current_user, "workout_30_min")
        xp_earned += bonus_xp

    # Bonus for 5km+ cardio
    if workout_data.distance_km and workout_data.distance_km >= 5:
        bonus_xp, _, _ = gamification.add_xp(current_user, "cardio_5km")
        xp_earned += bonus_xp

    gamification.update_streak(current_user)
    gamification.check_achievements(current_user)

    db.commit()
    db.refresh(workout)

    return WorkoutResponse(
        id=workout.id,
        workout_type=workout.workout_type,
        name=workout.name,
        description=workout.description,
        start_time=workout.start_time,
        end_time=workout.end_time,
        duration_minutes=workout.duration_minutes,
        calories_burned=workout.calories_burned,
        calories_source=workout.calories_source,
        intensity=workout.intensity,
        avg_heart_rate=workout.avg_heart_rate,
        max_heart_rate=workout.max_heart_rate,
        distance_km=workout.distance_km,
        steps=workout.steps,
        exercises=json.loads(workout.exercises_data) if workout.exercises_data else None,
        notes=workout.notes,
        rpe_score=workout.rpe_score,
        xp_earned=xp_earned,
        created_at=workout.created_at
    )


@router.get("/", response_model=List[WorkoutResponse])
def get_workouts(
    limit: int = 30,
    workout_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get workout history."""
    query = db.query(Workout).filter(Workout.user_id == current_user.id)

    if workout_type:
        query = query.filter(Workout.workout_type == workout_type)

    workouts = query.order_by(desc(Workout.start_time)).limit(limit).all()

    return [
        WorkoutResponse(
            id=w.id,
            workout_type=w.workout_type,
            name=w.name,
            description=w.description,
            start_time=w.start_time,
            end_time=w.end_time,
            duration_minutes=w.duration_minutes,
            calories_burned=w.calories_burned,
            calories_source=w.calories_source,
            intensity=w.intensity,
            avg_heart_rate=w.avg_heart_rate,
            max_heart_rate=w.max_heart_rate,
            distance_km=w.distance_km,
            steps=w.steps,
            exercises=json.loads(w.exercises_data) if w.exercises_data else None,
            notes=w.notes,
            rpe_score=w.rpe_score,
            created_at=w.created_at
        )
        for w in workouts
    ]


@router.get("/stats", response_model=WorkoutStats)
def get_workout_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get workout statistics."""
    workouts = db.query(Workout).filter(Workout.user_id == current_user.id).all()

    if not workouts:
        return WorkoutStats(
            total_workouts=0,
            total_minutes=0,
            total_calories_burned=0,
            workouts_this_week=0,
            avg_duration_minutes=0,
            favorite_type=None,
            streak_days=current_user.streak_days
        )

    # This week's workouts
    week_ago = datetime.utcnow() - timedelta(days=7)
    this_week = [w for w in workouts if w.start_time >= week_ago]

    total_minutes = sum(w.duration_minutes or 0 for w in workouts)
    total_calories = sum(w.calories_burned or 0 for w in workouts)

    # Find favorite type
    type_counts = {}
    for w in workouts:
        type_counts[w.workout_type] = type_counts.get(w.workout_type, 0) + 1
    favorite = max(type_counts, key=type_counts.get) if type_counts else None

    return WorkoutStats(
        total_workouts=len(workouts),
        total_minutes=total_minutes,
        total_calories_burned=total_calories,
        workouts_this_week=len(this_week),
        avg_duration_minutes=round(total_minutes / len(workouts), 1) if workouts else 0,
        favorite_type=favorite,
        streak_days=current_user.streak_days
    )


@router.get("/today-calories")
def get_today_workout_calories(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get total calories burned from workouts today."""
    today = date.today()
    today_start = datetime.combine(today, datetime.min.time())
    today_end = datetime.combine(today + timedelta(days=1), datetime.min.time())

    total = db.query(func.sum(Workout.calories_burned)).filter(
        Workout.user_id == current_user.id,
        Workout.start_time >= today_start,
        Workout.start_time < today_end
    ).scalar() or 0

    return {
        "date": today.isoformat(),
        "workout_calories_burned": total
    }


@router.delete("/{workout_id}")
def delete_workout(
    workout_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a workout."""
    workout = db.query(Workout).filter(
        Workout.id == workout_id,
        Workout.user_id == current_user.id
    ).first()

    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")

    db.delete(workout)
    db.commit()

    return {"message": "Workout deleted"}


# ============================================
# Workout Programs
# ============================================

@router.get("/programs", response_model=List[WorkoutProgramResponse])
def get_workout_programs(
    category: Optional[str] = None,
    difficulty: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get available workout programs."""
    query = db.query(WorkoutProgram).filter(WorkoutProgram.is_public == True)

    if category:
        query = query.filter(WorkoutProgram.category == category)
    if difficulty:
        query = query.filter(WorkoutProgram.difficulty == difficulty)

    programs = query.all()

    return [
        WorkoutProgramResponse(
            id=p.id,
            name=p.name,
            description=p.description,
            difficulty=p.difficulty,
            duration_weeks=p.duration_weeks,
            workouts_per_week=p.workouts_per_week,
            category=p.category,
            target_goals=p.target_goals
        )
        for p in programs
    ]


@router.get("/programs/{program_id}")
def get_program_details(
    program_id: str,
    db: Session = Depends(get_db)
):
    """Get detailed workout program."""
    program = db.query(WorkoutProgram).filter(WorkoutProgram.id == program_id).first()

    if not program:
        raise HTTPException(status_code=404, detail="Program not found")

    return {
        "id": program.id,
        "name": program.name,
        "description": program.description,
        "difficulty": program.difficulty,
        "duration_weeks": program.duration_weeks,
        "workouts_per_week": program.workouts_per_week,
        "category": program.category,
        "target_goals": program.target_goals,
        "program_data": json.loads(program.program_data) if program.program_data else None
    }
