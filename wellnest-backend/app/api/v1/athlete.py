"""
WellNest Athlete API Endpoints

Handles athlete-specific metrics, recovery scores, and performance tracking.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime, date, timedelta

from app.db import get_db
from app.models import User, AthleteMetric, DailyStat, UserProfile
from app.schemas import (
    AthleteMetricsCreate, AthleteMetricsResponse,
    RecoveryScoreResponse
)
from app.api.deps import get_current_user
from app.core.calculations import calculate_recovery_score, calculate_readiness_score

router = APIRouter()


def require_athlete(current_user: User):
    """Dependency to ensure user is an athlete."""
    if not current_user.is_athlete:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This feature is only available for athletes. Update your profile to enable athlete mode."
        )
    return current_user


@router.post("/metrics", response_model=AthleteMetricsResponse)
def log_athlete_metrics(
    data: AthleteMetricsCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Log athlete training and recovery metrics.
    Automatically calculates recovery and readiness scores.
    """
    require_athlete(current_user)

    # Check if entry for this date already exists
    existing = db.query(AthleteMetric).filter(
        AthleteMetric.user_id == current_user.id,
        AthleteMetric.date == data.date
    ).first()

    if existing:
        # Update existing entry
        metric = existing
        for field, value in data.model_dump(exclude_unset=True).items():
            if value is not None:
                setattr(metric, field, value)
    else:
        # Create new entry
        metric = AthleteMetric(
            user_id=current_user.id,
            **data.model_dump()
        )
        db.add(metric)

    # Calculate training load if RPE and duration provided
    if data.rpe_score and data.training_duration_min:
        metric.training_load = data.rpe_score * data.training_duration_min

    # Calculate acute and chronic load
    seven_days_ago = data.date - timedelta(days=7)
    twentyeight_days_ago = data.date - timedelta(days=28)

    # Get training loads for the past 7 days
    acute_loads = db.query(func.avg(AthleteMetric.training_load)).filter(
        AthleteMetric.user_id == current_user.id,
        AthleteMetric.date >= seven_days_ago,
        AthleteMetric.date <= data.date,
        AthleteMetric.training_load.isnot(None)
    ).scalar()

    # Get training loads for the past 28 days
    chronic_loads = db.query(func.avg(AthleteMetric.training_load)).filter(
        AthleteMetric.user_id == current_user.id,
        AthleteMetric.date >= twentyeight_days_ago,
        AthleteMetric.date <= data.date,
        AthleteMetric.training_load.isnot(None)
    ).scalar()

    metric.acute_load = acute_loads
    metric.chronic_load = chronic_loads

    # Calculate ACWR (Acute:Chronic Workload Ratio)
    if chronic_loads and chronic_loads > 0:
        metric.acwr = round(acute_loads / chronic_loads, 2) if acute_loads else 0

    # Calculate recovery score if we have the necessary data
    if data.sleep_hours and data.resting_hr:
        # Get baseline resting HR (average of last 7 days)
        baseline_hr = db.query(func.avg(AthleteMetric.resting_hr)).filter(
            AthleteMetric.user_id == current_user.id,
            AthleteMetric.date >= seven_days_ago,
            AthleteMetric.date < data.date,
            AthleteMetric.resting_hr.isnot(None)
        ).scalar() or data.resting_hr

        recovery = calculate_recovery_score(
            sleep_hours=data.sleep_hours,
            resting_hr=data.resting_hr,
            baseline_resting_hr=int(baseline_hr),
            hrv_ms=int(data.hrv_score) if data.hrv_score else None,
            baseline_hrv=None,
            muscle_soreness=data.muscle_soreness,
            fatigue_level=data.fatigue_level,
            stress_level=data.stress_level
        )
        metric.recovery_score = recovery

    # Calculate readiness score
    if metric.recovery_score and metric.acute_load is not None and metric.chronic_load is not None:
        # Get average sleep hours
        avg_sleep = db.query(func.avg(AthleteMetric.sleep_hours)).filter(
            AthleteMetric.user_id == current_user.id,
            AthleteMetric.date >= seven_days_ago,
            AthleteMetric.sleep_hours.isnot(None)
        ).scalar() or 7.5

        readiness = calculate_readiness_score(
            recovery_score=metric.recovery_score,
            training_load_7day=metric.acute_load or 0,
            training_load_28day=metric.chronic_load or 1,
            sleep_hours=data.sleep_hours or 7,
            avg_sleep_hours=avg_sleep
        )
        metric.readiness_score = readiness

    db.commit()
    db.refresh(metric)
    return metric


@router.get("/metrics", response_model=List[AthleteMetricsResponse])
def get_athlete_metrics(
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get athlete metrics history."""
    require_athlete(current_user)

    start_date = date.today() - timedelta(days=days)

    return db.query(AthleteMetric).filter(
        AthleteMetric.user_id == current_user.id,
        AthleteMetric.date >= start_date
    ).order_by(AthleteMetric.date.desc()).all()


@router.get("/metrics/{target_date}", response_model=AthleteMetricsResponse)
def get_athlete_metrics_by_date(
    target_date: date,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get athlete metrics for a specific date."""
    require_athlete(current_user)

    metric = db.query(AthleteMetric).filter(
        AthleteMetric.user_id == current_user.id,
        AthleteMetric.date == target_date
    ).first()

    if not metric:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No metrics found for {target_date}"
        )

    return metric


@router.get("/recovery", response_model=RecoveryScoreResponse)
def get_recovery_score(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get today's recovery and readiness scores with recommendations.
    """
    require_athlete(current_user)

    today = date.today()

    # Get today's metrics
    todays_metric = db.query(AthleteMetric).filter(
        AthleteMetric.user_id == current_user.id,
        AthleteMetric.date == today
    ).first()

    # Get daily stats for additional data
    daily_stat = db.query(DailyStat).filter(
        DailyStat.user_id == current_user.id,
        DailyStat.date == today
    ).first()

    recovery_score = 0
    readiness_score = 0
    sleep_hours = None
    resting_hr = None
    hrv_ms = None

    if todays_metric:
        recovery_score = todays_metric.recovery_score or 0
        readiness_score = todays_metric.readiness_score or 0
        sleep_hours = todays_metric.sleep_hours
        resting_hr = todays_metric.resting_hr
        hrv_ms = int(todays_metric.hrv_score) if todays_metric.hrv_score else None

    elif daily_stat:
        # Fallback to daily stats if no athlete metrics logged
        sleep_hours = daily_stat.sleep_hours
        resting_hr = daily_stat.resting_heart_rate
        hrv_ms = daily_stat.hrv_ms

        # Calculate basic recovery score from daily stats
        if sleep_hours and resting_hr:
            seven_days_ago = today - timedelta(days=7)
            baseline_hr = db.query(func.avg(DailyStat.resting_heart_rate)).filter(
                DailyStat.user_id == current_user.id,
                DailyStat.date >= seven_days_ago,
                DailyStat.resting_heart_rate.isnot(None)
            ).scalar() or resting_hr

            recovery_score = calculate_recovery_score(
                sleep_hours=sleep_hours,
                resting_hr=resting_hr,
                baseline_resting_hr=int(baseline_hr),
                hrv_ms=hrv_ms
            )
            readiness_score = recovery_score  # Simplified

    # Generate recommendation based on scores
    recommendation = _generate_recommendation(recovery_score, readiness_score)

    return RecoveryScoreResponse(
        recovery_score=recovery_score,
        readiness_score=readiness_score,
        sleep_hours=sleep_hours,
        resting_hr=resting_hr,
        hrv_ms=hrv_ms,
        recommendation=recommendation
    )


def _generate_recommendation(recovery_score: int, readiness_score: int) -> str:
    """Generate training recommendation based on scores."""
    if readiness_score >= 80:
        return "Excellent recovery! You're ready for high-intensity training or competition."
    elif readiness_score >= 60:
        return "Good recovery. Moderate to high intensity training is appropriate."
    elif readiness_score >= 40:
        return "Fair recovery. Consider lighter training or active recovery today."
    elif readiness_score >= 20:
        return "Low recovery. Rest or very light activity recommended."
    else:
        return "Very low recovery. Focus on rest, nutrition, and sleep today."


@router.get("/performance/summary")
def get_performance_summary(
    days: int = 28,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get performance summary and trends for the athlete.
    """
    require_athlete(current_user)

    start_date = date.today() - timedelta(days=days)

    # Get metrics for the period
    metrics = db.query(AthleteMetric).filter(
        AthleteMetric.user_id == current_user.id,
        AthleteMetric.date >= start_date
    ).order_by(AthleteMetric.date).all()

    if not metrics:
        return {
            "period_days": days,
            "total_training_days": 0,
            "avg_training_load": 0,
            "avg_recovery_score": 0,
            "avg_readiness_score": 0,
            "avg_sleep_hours": 0,
            "current_acwr": None,
            "acwr_status": "unknown",
            "trend": "insufficient_data"
        }

    # Calculate averages
    training_days = len([m for m in metrics if m.training_load])
    avg_load = sum(m.training_load or 0 for m in metrics) / len(metrics) if metrics else 0
    avg_recovery = sum(m.recovery_score or 0 for m in metrics) / len(metrics) if metrics else 0
    avg_readiness = sum(m.readiness_score or 0 for m in metrics) / len(metrics) if metrics else 0
    sleep_data = [m.sleep_hours for m in metrics if m.sleep_hours]
    avg_sleep = sum(sleep_data) / len(sleep_data) if sleep_data else 0

    # Get current ACWR
    latest_metric = metrics[-1] if metrics else None
    current_acwr = latest_metric.acwr if latest_metric else None

    # Determine ACWR status
    if current_acwr is None:
        acwr_status = "unknown"
    elif 0.8 <= current_acwr <= 1.3:
        acwr_status = "optimal"
    elif current_acwr < 0.8:
        acwr_status = "undertrained"
    else:
        acwr_status = "high_injury_risk"

    # Determine trend (comparing first half to second half of period)
    mid_point = len(metrics) // 2
    if mid_point > 0:
        first_half_readiness = sum(m.readiness_score or 0 for m in metrics[:mid_point]) / mid_point
        second_half_readiness = sum(m.readiness_score or 0 for m in metrics[mid_point:]) / (len(metrics) - mid_point)

        if second_half_readiness > first_half_readiness + 5:
            trend = "improving"
        elif second_half_readiness < first_half_readiness - 5:
            trend = "declining"
        else:
            trend = "stable"
    else:
        trend = "insufficient_data"

    return {
        "period_days": days,
        "total_training_days": training_days,
        "avg_training_load": round(avg_load, 1),
        "avg_recovery_score": round(avg_recovery, 1),
        "avg_readiness_score": round(avg_readiness, 1),
        "avg_sleep_hours": round(avg_sleep, 2),
        "current_acwr": current_acwr,
        "acwr_status": acwr_status,
        "trend": trend
    }


@router.get("/workload/chart")
def get_workload_chart_data(
    days: int = 28,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get workload data formatted for charting.
    Returns daily training load, ACWR, and recovery scores.
    """
    require_athlete(current_user)

    start_date = date.today() - timedelta(days=days)

    metrics = db.query(AthleteMetric).filter(
        AthleteMetric.user_id == current_user.id,
        AthleteMetric.date >= start_date
    ).order_by(AthleteMetric.date).all()

    chart_data = []
    for metric in metrics:
        chart_data.append({
            "date": metric.date.isoformat(),
            "training_load": metric.training_load,
            "acute_load": metric.acute_load,
            "chronic_load": metric.chronic_load,
            "acwr": metric.acwr,
            "recovery_score": metric.recovery_score,
            "readiness_score": metric.readiness_score
        })

    return chart_data
