from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List, Literal
from datetime import datetime, date


# ============================================
# User Schemas
# ============================================

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    is_athlete: bool = False


class UserResponse(BaseModel):
    id: str
    email: EmailStr
    is_athlete: bool = False
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserWithProfile(UserResponse):
    profile: Optional["UserProfileResponse"] = None


# ============================================
# Profile Schemas
# ============================================

class ProfileCreate(BaseModel):
    height: Optional[float] = None
    weight: Optional[float] = None


class ProfileResponse(ProfileCreate):
    id: str


class OnboardingData(BaseModel):
    """Data collected during onboarding."""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    height: float = Field(..., gt=0, lt=300, description="Height in cm")
    current_weight: float = Field(..., gt=0, lt=500, description="Weight in kg")
    target_weight: Optional[float] = Field(None, gt=0, lt=500)
    birth_date: date
    gender: Literal["male", "female", "other"]
    activity_level: Literal["sedentary", "light", "moderate", "active", "very_active"]
    goal_type: Literal["lose_weight", "maintain", "gain_muscle", "improve_health"]
    is_athlete: bool = False
    preferred_unit: Literal["metric", "imperial"] = "metric"


class UserProfileResponse(BaseModel):
    id: str
    user_id: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    height: Optional[float] = None
    current_weight: Optional[float] = None
    target_weight: Optional[float] = None
    birth_date: Optional[date] = None
    gender: Optional[str] = None
    activity_level: str = "moderate"
    goal_type: str = "maintain"
    bmr: Optional[float] = None
    tdee: Optional[float] = None
    daily_calorie_goal: Optional[int] = None
    protein_goal: Optional[float] = None
    carbs_goal: Optional[float] = None
    fat_goal: Optional[float] = None
    daily_water_goal: int = 2500
    onboarding_completed: bool = False

    class Config:
        from_attributes = True


class ProfileUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    height: Optional[float] = None
    current_weight: Optional[float] = None
    target_weight: Optional[float] = None
    activity_level: Optional[str] = None
    goal_type: Optional[str] = None


# ============================================
# Food Log Schemas
# ============================================

class FoodLogCreate(BaseModel):
    food_name: str
    calories: int
    protein: float = 0.0
    carbs: float = 0.0
    fat: float = 0.0
    fiber: float = 0.0
    serving_size: float = 1.0
    serving_unit: str = "portion"
    meal_type: Literal["breakfast", "lunch", "dinner", "snack", "pre_workout", "post_workout"] = "snack"
    logged_at: Optional[datetime] = None
    image_url: Optional[str] = None
    ai_analyzed: bool = False
    ai_confidence_score: Optional[float] = None


class FoodLogResponse(BaseModel):
    id: str
    food_name: str
    calories: int
    protein: float
    carbs: float
    fat: float
    fiber: float = 0.0
    serving_size: float = 1.0
    serving_unit: str = "portion"
    meal_type: str
    logged_at: datetime
    image_url: Optional[str] = None
    ai_analyzed: bool = False
    ai_confidence_score: Optional[float] = None

    class Config:
        from_attributes = True


class FoodAnalysisRequest(BaseModel):
    """Request for AI food analysis."""
    image_base64: str
    image_type: str = "image/jpeg"
    meal_type: Optional[str] = None
    additional_context: Optional[str] = None


class FoodItemAnalysis(BaseModel):
    """Single food item from AI analysis."""
    name: str
    name_tr: Optional[str] = None
    estimated_portion: str
    calories: int
    protein: float
    carbs: float
    fat: float
    fiber: float
    confidence: float


class FoodAnalysisResponse(BaseModel):
    """Response from AI food analysis."""
    success: bool
    food_items: List[FoodItemAnalysis] = []
    total_calories: int = 0
    total_protein: float = 0
    total_carbs: float = 0
    total_fat: float = 0
    total_fiber: float = 0
    meal_type_suggestion: str = "snack"
    confidence_level: str = "low"
    error_message: Optional[str] = None


# ============================================
# Weight Log Schemas
# ============================================

class WeightLogCreate(BaseModel):
    weight: float = Field(..., gt=0, lt=500, description="Weight in kg")
    body_fat_percentage: Optional[float] = Field(None, ge=0, le=100)
    muscle_mass: Optional[float] = None
    logged_at: Optional[datetime] = None
    source: str = "manual"


class WeightLogResponse(BaseModel):
    id: str
    weight: float
    body_fat_percentage: Optional[float] = None
    muscle_mass: Optional[float] = None
    logged_at: datetime
    source: str = "manual"

    class Config:
        from_attributes = True


# ============================================
# Water Log Schemas
# ============================================

class WaterLogCreate(BaseModel):
    amount_ml: int = Field(..., gt=0, lt=10000)
    logged_at: Optional[datetime] = None


class WaterLogResponse(BaseModel):
    id: str
    amount_ml: int
    logged_at: datetime

    class Config:
        from_attributes = True


# ============================================
# Daily Stats Schemas
# ============================================

class DailyStatsResponse(BaseModel):
    id: str
    date: date
    total_calories: int
    total_protein: float
    total_carbs: float
    total_fat: float
    total_water_ml: int
    steps: int
    active_calories: int
    sleep_hours: Optional[float] = None
    recovery_score: Optional[int] = None
    calorie_balance: Optional[int] = None

    class Config:
        from_attributes = True


# ============================================
# Dashboard Schemas
# ============================================

class DashboardSummary(BaseModel):
    """Dashboard summary response."""
    # Nutrition
    today_calories: int = 0
    calorie_goal: Optional[int] = None
    calories_remaining: Optional[int] = None
    calories_burned: int = 0

    # Macros
    today_protein: float = 0
    today_carbs: float = 0
    today_fat: float = 0
    protein_goal: Optional[float] = None
    carbs_goal: Optional[float] = None
    fat_goal: Optional[float] = None

    # Water
    today_water_ml: int = 0
    water_goal: int = 2500

    # Weight
    current_weight: Optional[float] = None
    target_weight: Optional[float] = None
    weight_change_week: Optional[float] = None

    # Activity
    steps: int = 0
    active_minutes: int = 0

    # Recovery (for athletes)
    recovery_score: Optional[int] = None
    sleep_hours: Optional[float] = None

    # Meals breakdown
    meals_logged: int = 0


class MacroBreakdown(BaseModel):
    """Detailed macro breakdown."""
    protein_grams: float
    protein_percentage: float
    carbs_grams: float
    carbs_percentage: float
    fat_grams: float
    fat_percentage: float
    fiber_grams: float


# ============================================
# Athlete Schemas
# ============================================

class AthleteMetricsCreate(BaseModel):
    date: date
    training_load: Optional[int] = None
    training_type: Optional[str] = None
    training_duration_min: Optional[int] = None
    rpe_score: Optional[int] = Field(None, ge=1, le=10)
    hrv_score: Optional[float] = None
    resting_hr: Optional[int] = None
    sleep_hours: Optional[float] = None
    sleep_quality: Optional[int] = Field(None, ge=0, le=100)
    muscle_soreness: Optional[int] = Field(None, ge=1, le=10)
    fatigue_level: Optional[int] = Field(None, ge=1, le=10)
    stress_level: Optional[int] = Field(None, ge=1, le=10)
    notes: Optional[str] = None


class AthleteMetricsResponse(BaseModel):
    id: str
    date: date
    training_load: Optional[int] = None
    training_type: Optional[str] = None
    training_duration_min: Optional[int] = None
    rpe_score: Optional[int] = None
    hrv_score: Optional[float] = None
    resting_hr: Optional[int] = None
    sleep_hours: Optional[float] = None
    sleep_quality: Optional[int] = None
    muscle_soreness: Optional[int] = None
    fatigue_level: Optional[int] = None
    stress_level: Optional[int] = None
    readiness_score: Optional[int] = None
    recovery_score: Optional[int] = None
    acute_load: Optional[float] = None
    chronic_load: Optional[float] = None
    acwr: Optional[float] = None
    notes: Optional[str] = None

    class Config:
        from_attributes = True


class RecoveryScoreResponse(BaseModel):
    """Recovery score response for athletes."""
    recovery_score: int
    readiness_score: int
    sleep_hours: Optional[float] = None
    resting_hr: Optional[int] = None
    hrv_ms: Optional[int] = None
    recommendation: str


# ============================================
# Health Integration Schemas
# ============================================

class HealthIntegrationCreate(BaseModel):
    platform: Literal["apple_healthkit", "google_fit", "fitbit", "garmin", "whoop", "oura"]
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None


class HealthIntegrationResponse(BaseModel):
    id: str
    platform: str
    is_connected: bool
    last_sync_at: Optional[datetime] = None
    sync_enabled: bool

    class Config:
        from_attributes = True


class HealthDataSync(BaseModel):
    """Health data sync payload from mobile app."""
    platform: str
    data_type: str
    samples: List[dict]


class SleepDataSync(BaseModel):
    """Sleep data sync payload."""
    platform: str
    start_time: datetime
    end_time: datetime
    total_hours: float
    deep_sleep_hours: Optional[float] = None
    light_sleep_hours: Optional[float] = None
    rem_sleep_hours: Optional[float] = None
    awake_hours: Optional[float] = None
    sleep_score: Optional[int] = None


# ============================================
# Auth Schemas
# ============================================

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


# ============================================
# Calculation Schemas
# ============================================

class NutritionGoalsResponse(BaseModel):
    """Calculated nutrition goals."""
    bmr: float
    tdee: float
    daily_calories: int
    protein_grams: float
    carbs_grams: float
    fat_grams: float
    water_ml: int


class CalorieCalculationRequest(BaseModel):
    """Request to calculate calories."""
    weight_kg: float
    height_cm: float
    age: int
    gender: Literal["male", "female", "other"]
    activity_level: Literal["sedentary", "light", "moderate", "active", "very_active"]
    goal_type: Literal["lose_weight", "maintain", "gain_muscle", "improve_health"]


# ============================================
# Food Search Schemas
# ============================================

class FoodSearchResult(BaseModel):
    """Food search result from FatSecret API."""
    food_id: str
    food_name: str
    brand_name: Optional[str] = None
    food_type: str = "Generic"
    calories: float
    protein: float
    carbs: float
    fat: float
    fiber: float
    serving_size: str
    serving_description: str


class FoodSearchResponse(BaseModel):
    """Response for food search."""
    results: List[FoodSearchResult]
    query: str
    total_results: int


# Update forward references
UserWithProfile.model_rebuild()
