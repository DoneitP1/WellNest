"""
Intermittent Fasting API - Track fasting sessions

Supports popular fasting protocols: 16:8, 18:6, 20:4, OMAD, 5:2
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel

from app.db import get_db
from app.models import User, FastingLog, FastingType
from app.api.deps import get_current_user
from app.services.gamification import GamificationService

router = APIRouter()


# ============================================
# Schemas
# ============================================

class FastingStart(BaseModel):
    fasting_type: str = "16:8"
    custom_hours: Optional[float] = None
    notes: Optional[str] = None
    mood_before: Optional[int] = None  # 1-5


class FastingEnd(BaseModel):
    notes: Optional[str] = None
    mood_after: Optional[int] = None  # 1-5


class FastingResponse(BaseModel):
    id: str
    fasting_type: str
    start_time: datetime
    planned_end_time: datetime
    actual_end_time: Optional[datetime]
    is_active: bool
    completed: bool
    cancelled: bool
    target_hours: float
    actual_hours: Optional[float]
    progress_percentage: float
    time_remaining_seconds: Optional[int]
    notes: Optional[str]
    mood_before: Optional[int]
    mood_after: Optional[int]
    created_at: datetime


class FastingStats(BaseModel):
    total_fasts: int
    completed_fasts: int
    total_hours_fasted: float
    average_fast_duration: float
    longest_fast: float
    current_streak: int
    completion_rate: float
    favorite_type: Optional[str]


# ============================================
# Helper Functions
# ============================================

FASTING_HOURS = {
    "16:8": 16,
    "18:6": 18,
    "20:4": 20,
    "OMAD": 23,
    "5:2": 24,  # Full day fast
    "custom": 0
}


def calculate_progress(fast: FastingLog) -> dict:
    """Calculate fasting progress and time remaining."""
    now = datetime.utcnow()

    if fast.actual_end_time:
        # Fast is completed
        elapsed = (fast.actual_end_time - fast.start_time).total_seconds()
        progress = min(100, (elapsed / (fast.target_hours * 3600)) * 100)
        return {
            "progress_percentage": round(progress, 1),
            "time_remaining_seconds": 0
        }

    if fast.cancelled:
        elapsed = (now - fast.start_time).total_seconds()
        progress = min(100, (elapsed / (fast.target_hours * 3600)) * 100)
        return {
            "progress_percentage": round(progress, 1),
            "time_remaining_seconds": 0
        }

    # Active fast
    elapsed = (now - fast.start_time).total_seconds()
    total_seconds = fast.target_hours * 3600
    remaining = max(0, total_seconds - elapsed)
    progress = min(100, (elapsed / total_seconds) * 100)

    return {
        "progress_percentage": round(progress, 1),
        "time_remaining_seconds": int(remaining)
    }


# ============================================
# Endpoints
# ============================================

@router.get("/current", response_model=Optional[FastingResponse])
def get_current_fast(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get the user's currently active fast, if any."""
    fast = db.query(FastingLog).filter(
        FastingLog.user_id == current_user.id,
        FastingLog.is_active == True
    ).first()

    if not fast:
        return None

    progress = calculate_progress(fast)

    return FastingResponse(
        id=fast.id,
        fasting_type=fast.fasting_type,
        start_time=fast.start_time,
        planned_end_time=fast.planned_end_time,
        actual_end_time=fast.actual_end_time,
        is_active=fast.is_active,
        completed=fast.completed,
        cancelled=fast.cancelled,
        target_hours=fast.target_hours,
        actual_hours=fast.actual_hours,
        progress_percentage=progress["progress_percentage"],
        time_remaining_seconds=progress["time_remaining_seconds"],
        notes=fast.notes,
        mood_before=fast.mood_before,
        mood_after=fast.mood_after,
        created_at=fast.created_at
    )


@router.post("/start", response_model=FastingResponse)
def start_fast(
    data: FastingStart,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Start a new fasting session."""
    # Check if user already has an active fast
    existing = db.query(FastingLog).filter(
        FastingLog.user_id == current_user.id,
        FastingLog.is_active == True
    ).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="You already have an active fast. End it before starting a new one."
        )

    # Determine fasting hours
    if data.fasting_type == "custom" and data.custom_hours:
        target_hours = data.custom_hours
    else:
        target_hours = FASTING_HOURS.get(data.fasting_type, 16)

    now = datetime.utcnow()
    planned_end = now + timedelta(hours=target_hours)

    fast = FastingLog(
        user_id=current_user.id,
        fasting_type=data.fasting_type,
        start_time=now,
        planned_end_time=planned_end,
        target_hours=target_hours,
        notes=data.notes,
        mood_before=data.mood_before,
        is_active=True
    )

    db.add(fast)
    db.commit()
    db.refresh(fast)

    return FastingResponse(
        id=fast.id,
        fasting_type=fast.fasting_type,
        start_time=fast.start_time,
        planned_end_time=fast.planned_end_time,
        actual_end_time=None,
        is_active=True,
        completed=False,
        cancelled=False,
        target_hours=target_hours,
        actual_hours=None,
        progress_percentage=0,
        time_remaining_seconds=int(target_hours * 3600),
        notes=fast.notes,
        mood_before=fast.mood_before,
        mood_after=None,
        created_at=fast.created_at
    )


@router.post("/end", response_model=FastingResponse)
def end_fast(
    data: FastingEnd,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """End the current fasting session."""
    fast = db.query(FastingLog).filter(
        FastingLog.user_id == current_user.id,
        FastingLog.is_active == True
    ).first()

    if not fast:
        raise HTTPException(status_code=404, detail="No active fast found")

    now = datetime.utcnow()
    actual_hours = (now - fast.start_time).total_seconds() / 3600

    # Update fast
    fast.actual_end_time = now
    fast.actual_hours = round(actual_hours, 2)
    fast.is_active = False
    fast.completed = actual_hours >= fast.target_hours * 0.9  # 90% completion counts
    fast.mood_after = data.mood_after
    if data.notes:
        fast.notes = (fast.notes or "") + f"\nEnd note: {data.notes}"

    # Award XP if completed
    if fast.completed:
        gamification = GamificationService(db)

        # Base XP for completing
        xp_action = "fasting_completed"
        if fast.target_hours >= 20:
            xp_action = "fasting_20h"
        elif fast.target_hours >= 16:
            xp_action = "fasting_16h"

        gamification.add_xp(current_user, xp_action, f"Completed {fast.fasting_type} fast")
        gamification.update_streak(current_user)
        gamification.check_achievements(current_user)

    db.commit()
    db.refresh(fast)

    progress = calculate_progress(fast)

    return FastingResponse(
        id=fast.id,
        fasting_type=fast.fasting_type,
        start_time=fast.start_time,
        planned_end_time=fast.planned_end_time,
        actual_end_time=fast.actual_end_time,
        is_active=False,
        completed=fast.completed,
        cancelled=False,
        target_hours=fast.target_hours,
        actual_hours=fast.actual_hours,
        progress_percentage=progress["progress_percentage"],
        time_remaining_seconds=0,
        notes=fast.notes,
        mood_before=fast.mood_before,
        mood_after=fast.mood_after,
        created_at=fast.created_at
    )


@router.post("/cancel")
def cancel_fast(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Cancel the current fasting session without completing it."""
    fast = db.query(FastingLog).filter(
        FastingLog.user_id == current_user.id,
        FastingLog.is_active == True
    ).first()

    if not fast:
        raise HTTPException(status_code=404, detail="No active fast found")

    now = datetime.utcnow()
    actual_hours = (now - fast.start_time).total_seconds() / 3600

    fast.actual_end_time = now
    fast.actual_hours = round(actual_hours, 2)
    fast.is_active = False
    fast.cancelled = True

    db.commit()

    return {"message": "Fast cancelled", "hours_completed": fast.actual_hours}


@router.get("/history", response_model=List[FastingResponse])
def get_fasting_history(
    limit: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get fasting history."""
    fasts = db.query(FastingLog).filter(
        FastingLog.user_id == current_user.id
    ).order_by(desc(FastingLog.created_at)).limit(limit).all()

    result = []
    for fast in fasts:
        progress = calculate_progress(fast)
        result.append(FastingResponse(
            id=fast.id,
            fasting_type=fast.fasting_type,
            start_time=fast.start_time,
            planned_end_time=fast.planned_end_time,
            actual_end_time=fast.actual_end_time,
            is_active=fast.is_active,
            completed=fast.completed,
            cancelled=fast.cancelled,
            target_hours=fast.target_hours,
            actual_hours=fast.actual_hours,
            progress_percentage=progress["progress_percentage"],
            time_remaining_seconds=progress["time_remaining_seconds"] if fast.is_active else 0,
            notes=fast.notes,
            mood_before=fast.mood_before,
            mood_after=fast.mood_after,
            created_at=fast.created_at
        ))

    return result


@router.get("/stats", response_model=FastingStats)
def get_fasting_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get fasting statistics."""
    fasts = db.query(FastingLog).filter(
        FastingLog.user_id == current_user.id,
        FastingLog.is_active == False
    ).all()

    if not fasts:
        return FastingStats(
            total_fasts=0,
            completed_fasts=0,
            total_hours_fasted=0,
            average_fast_duration=0,
            longest_fast=0,
            current_streak=0,
            completion_rate=0,
            favorite_type=None
        )

    completed = [f for f in fasts if f.completed]
    total_hours = sum(f.actual_hours or 0 for f in fasts)
    longest = max((f.actual_hours or 0 for f in fasts), default=0)

    # Calculate streak
    streak = 0
    sorted_fasts = sorted([f for f in fasts if f.completed], key=lambda x: x.created_at, reverse=True)
    for i, fast in enumerate(sorted_fasts):
        if i == 0:
            streak = 1
        else:
            prev_date = sorted_fasts[i-1].created_at.date()
            curr_date = fast.created_at.date()
            if (prev_date - curr_date).days <= 2:  # Allow 2 day gap
                streak += 1
            else:
                break

    # Find favorite type
    type_counts = {}
    for f in fasts:
        type_counts[f.fasting_type] = type_counts.get(f.fasting_type, 0) + 1
    favorite = max(type_counts, key=type_counts.get) if type_counts else None

    return FastingStats(
        total_fasts=len(fasts),
        completed_fasts=len(completed),
        total_hours_fasted=round(total_hours, 1),
        average_fast_duration=round(total_hours / len(fasts), 1) if fasts else 0,
        longest_fast=round(longest, 1),
        current_streak=streak,
        completion_rate=round((len(completed) / len(fasts)) * 100, 1) if fasts else 0,
        favorite_type=favorite
    )
