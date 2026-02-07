"""
WellNest User API Endpoints

Handles user profile management and onboarding.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import date

from app.db import get_db
from app.models import User, UserProfile
from app.schemas import (
    UserResponse, UserWithProfile, UserProfileResponse,
    OnboardingData, ProfileUpdate, NutritionGoalsResponse
)
from app.api.deps import get_current_user
from app.core.calculations import (
    calculate_all_nutrition_goals, calculate_age,
    Gender, ActivityLevel, GoalType
)

router = APIRouter()


@router.get("/me", response_model=UserWithProfile)
def get_current_user_info(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current user's information with profile."""
    profile = db.query(UserProfile).filter(
        UserProfile.user_id == current_user.id
    ).first()

    return {
        "id": current_user.id,
        "email": current_user.email,
        "is_athlete": current_user.is_athlete,
        "created_at": current_user.created_at,
        "profile": profile
    }


@router.get("/profile", response_model=UserProfileResponse)
def get_user_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's profile."""
    profile = db.query(UserProfile).filter(
        UserProfile.user_id == current_user.id
    ).first()

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found. Please complete onboarding."
        )

    return profile


@router.put("/profile", response_model=UserProfileResponse)
def update_profile(
    data: ProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update user profile."""
    profile = db.query(UserProfile).filter(
        UserProfile.user_id == current_user.id
    ).first()

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )

    # Update fields if provided
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            setattr(profile, field, value)

    # Recalculate nutrition goals if relevant fields changed
    needs_recalculation = any(
        field in update_data
        for field in ['current_weight', 'height', 'activity_level', 'goal_type']
    )

    if needs_recalculation and profile.birth_date and profile.gender:
        goals = calculate_all_nutrition_goals(
            weight_kg=profile.current_weight,
            height_cm=profile.height,
            birth_date=profile.birth_date,
            gender=Gender(profile.gender),
            activity_level=ActivityLevel(profile.activity_level),
            goal_type=GoalType(profile.goal_type),
            is_athlete=current_user.is_athlete
        )

        profile.bmr = goals["bmr"]
        profile.tdee = goals["tdee"]
        profile.daily_calorie_goal = goals["daily_calories"]
        profile.protein_goal = goals["protein_grams"]
        profile.carbs_goal = goals["carbs_grams"]
        profile.fat_goal = goals["fat_grams"]
        profile.daily_water_goal = goals["water_ml"]

    db.commit()
    db.refresh(profile)
    return profile


@router.post("/onboarding", response_model=UserProfileResponse)
def complete_onboarding(
    data: OnboardingData,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Complete user onboarding by setting up profile with physical metrics
    and calculating personalized nutrition goals.
    """
    # Check if profile already exists
    existing_profile = db.query(UserProfile).filter(
        UserProfile.user_id == current_user.id
    ).first()

    if existing_profile and existing_profile.onboarding_completed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Onboarding already completed. Use /profile to update."
        )

    # Calculate nutrition goals
    goals = calculate_all_nutrition_goals(
        weight_kg=data.current_weight,
        height_cm=data.height,
        birth_date=data.birth_date,
        gender=Gender(data.gender),
        activity_level=ActivityLevel(data.activity_level),
        goal_type=GoalType(data.goal_type),
        is_athlete=data.is_athlete
    )

    # Update user's athlete status
    if data.is_athlete != current_user.is_athlete:
        current_user.is_athlete = data.is_athlete

    # Create or update profile
    if existing_profile:
        profile = existing_profile
    else:
        profile = UserProfile(user_id=current_user.id)
        db.add(profile)

    # Set profile data
    profile.first_name = data.first_name
    profile.last_name = data.last_name
    profile.height = data.height
    profile.current_weight = data.current_weight
    profile.target_weight = data.target_weight
    profile.birth_date = data.birth_date
    profile.gender = data.gender
    profile.activity_level = data.activity_level
    profile.goal_type = data.goal_type
    profile.preferred_unit = data.preferred_unit

    # Set calculated goals
    profile.bmr = goals["bmr"]
    profile.tdee = goals["tdee"]
    profile.daily_calorie_goal = goals["daily_calories"]
    profile.protein_goal = goals["protein_grams"]
    profile.carbs_goal = goals["carbs_grams"]
    profile.fat_goal = goals["fat_grams"]
    profile.daily_water_goal = goals["water_ml"]

    # Mark onboarding as complete
    profile.onboarding_completed = True
    profile.onboarding_step = 5

    db.commit()
    db.refresh(profile)
    return profile


@router.get("/onboarding/status")
def get_onboarding_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Check if user has completed onboarding."""
    profile = db.query(UserProfile).filter(
        UserProfile.user_id == current_user.id
    ).first()

    return {
        "completed": profile.onboarding_completed if profile else False,
        "step": profile.onboarding_step if profile else 0
    }


@router.post("/calculate-goals", response_model=NutritionGoalsResponse)
def calculate_goals_preview(
    data: OnboardingData,
    current_user: User = Depends(get_current_user)
):
    """
    Preview calculated nutrition goals without saving.
    Useful for showing users their goals during onboarding before confirming.
    """
    goals = calculate_all_nutrition_goals(
        weight_kg=data.current_weight,
        height_cm=data.height,
        birth_date=data.birth_date,
        gender=Gender(data.gender),
        activity_level=ActivityLevel(data.activity_level),
        goal_type=GoalType(data.goal_type),
        is_athlete=data.is_athlete
    )

    return NutritionGoalsResponse(
        bmr=goals["bmr"],
        tdee=goals["tdee"],
        daily_calories=goals["daily_calories"],
        protein_grams=goals["protein_grams"],
        carbs_grams=goals["carbs_grams"],
        fat_grams=goals["fat_grams"],
        water_ml=goals["water_ml"]
    )


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: str, db: Session = Depends(get_db)):
    """Get user by ID (public endpoint)."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user
