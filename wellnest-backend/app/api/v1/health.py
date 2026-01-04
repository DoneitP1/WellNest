from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db import get_db
from app.models import WeightLog, FoodLog, User
from app.schemas import WeightLogCreate, WeightLogResponse, FoodLogCreate, FoodLogResponse
from app.api.deps import get_current_user
import datetime
import uuid

router = APIRouter()

@router.post("/weight", response_model=WeightLogResponse)
def log_weight(log: WeightLogCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_log = WeightLog(
        weight=log.weight,
        user_id=current_user.id,
        date=log.date or datetime.datetime.utcnow()
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

@router.get("/weight", response_model=List[WeightLogResponse])
def get_weight_logs(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(WeightLog).filter(WeightLog.user_id == current_user.id).order_by(WeightLog.date.desc()).all()

@router.post("/food", response_model=FoodLogResponse)
def log_food(log: FoodLogCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db_log = FoodLog(
        user_id=current_user.id,
        food_name=log.food_name,
        calories=log.calories,
        protein=log.protein,
        carbs=log.carbs,
        fat=log.fat,
        meal_type=log.meal_type,
        date=log.date or datetime.datetime.utcnow()
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

@router.get("/food", response_model=List[FoodLogResponse])
def get_food_logs(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(FoodLog).filter(FoodLog.user_id == current_user.id).order_by(FoodLog.date.desc()).all()

@router.get("/dashboard")
def get_dashboard_summary(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    today = datetime.datetime.utcnow().date()
    today_start = datetime.datetime.combine(today, datetime.time.min)
    today_end = datetime.datetime.combine(today, datetime.time.max)
    
    todays_food = db.query(FoodLog).filter(
        FoodLog.user_id == current_user.id,
        FoodLog.date >= today_start,
        FoodLog.date <= today_end
    ).all()
    
    total_calories = sum(f.calories for f in todays_food)
    
    latest_weight_log = db.query(WeightLog).filter(WeightLog.user_id == current_user.id).order_by(WeightLog.date.desc()).first()
    latest_weight = latest_weight_log.weight if latest_weight_log else None
    
    return {
        "today_calories": total_calories,
        "current_weight": latest_weight
    }
