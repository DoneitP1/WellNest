from sqlalchemy import Column, String, Float, ForeignKey, Integer, DateTime, Boolean, Date, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.db import Base
import datetime
import uuid
import enum


def generate_uuid():
    return str(uuid.uuid4())


# ============================================
# Enums
# ============================================

class UserRole(str, enum.Enum):
    USER = "user"
    ATHLETE = "athlete"
    DOCTOR = "doctor"
    DIETICIAN = "dietician"
    ADMIN = "admin"


class FastingType(str, enum.Enum):
    FASTING_16_8 = "16:8"
    FASTING_18_6 = "18:6"
    FASTING_20_4 = "20:4"
    FASTING_OMAD = "OMAD"
    FASTING_5_2 = "5:2"
    CUSTOM = "custom"


class WorkoutType(str, enum.Enum):
    STRENGTH = "strength"
    CARDIO = "cardio"
    HIIT = "hiit"
    YOGA = "yoga"
    SWIMMING = "swimming"
    CYCLING = "cycling"
    RUNNING = "running"
    WALKING = "walking"
    SPORTS = "sports"
    OTHER = "other"


# ============================================
# User Models
# ============================================

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True, default=generate_uuid)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    username = Column(String, unique=True, index=True, nullable=True)

    # Role-Based Access Control
    role = Column(String, default=UserRole.USER.value)  # user, athlete, doctor, dietician, admin
    is_verified = Column(Boolean, default=False)  # For doctor/dietician verification

    # Gamification
    xp = Column(Integer, default=0)
    level = Column(Integer, default=1)
    streak_days = Column(Integer, default=0)
    last_activity_date = Column(Date, nullable=True)

    # Status
    is_athlete = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    weight_logs = relationship("WeightLog", back_populates="user", cascade="all, delete-orphan")
    food_logs = relationship("FoodLog", back_populates="user", cascade="all, delete-orphan")
    water_logs = relationship("WaterLog", back_populates="user", cascade="all, delete-orphan")
    daily_stats = relationship("DailyStat", back_populates="user", cascade="all, delete-orphan")
    athlete_metrics = relationship("AthleteMetric", back_populates="user", cascade="all, delete-orphan")
    health_integrations = relationship("HealthIntegration", back_populates="user", cascade="all, delete-orphan")

    # New Relationships
    fasting_logs = relationship("FastingLog", back_populates="user", cascade="all, delete-orphan")
    workouts = relationship("Workout", back_populates="user", cascade="all, delete-orphan")
    posts = relationship("SocialPost", back_populates="user", cascade="all, delete-orphan")
    post_likes = relationship("PostLike", back_populates="user", cascade="all, delete-orphan")
    blog_posts = relationship("BlogPost", back_populates="author", cascade="all, delete-orphan")
    xp_logs = relationship("XPLog", back_populates="user", cascade="all, delete-orphan")
    achievements = relationship("UserAchievement", back_populates="user", cascade="all, delete-orphan")


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(String, primary_key=True, index=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)

    # Basic Info
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)
    bio = Column(Text, nullable=True)

    # Physical Metrics
    height = Column(Float, nullable=True)  # cm
    current_weight = Column(Float, nullable=True)  # kg
    target_weight = Column(Float, nullable=True)  # kg
    birth_date = Column(Date, nullable=True)
    gender = Column(String, nullable=True)  # male, female, other

    # Activity & Goals
    activity_level = Column(String, default="moderate")
    goal_type = Column(String, default="maintain")

    # Calculated Goals
    bmr = Column(Float, nullable=True)
    tdee = Column(Float, nullable=True)
    daily_calorie_goal = Column(Integer, nullable=True)
    protein_goal = Column(Float, nullable=True)
    carbs_goal = Column(Float, nullable=True)
    fat_goal = Column(Float, nullable=True)
    daily_water_goal = Column(Integer, default=2500)

    # Preferences
    preferred_unit = Column(String, default="metric")
    timezone = Column(String, default="UTC")

    # Privacy Settings
    profile_public = Column(Boolean, default=True)
    show_meals_public = Column(Boolean, default=True)
    show_weight_public = Column(Boolean, default=False)

    # Onboarding Status
    onboarding_completed = Column(Boolean, default=False)
    onboarding_step = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationship
    user = relationship("User", back_populates="profile")


# ============================================
# Gamification Models
# ============================================

class XPLog(Base):
    """Tracks XP earned for various activities."""
    __tablename__ = "xp_logs"

    id = Column(String, primary_key=True, index=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    xp_amount = Column(Integer, nullable=False)
    action_type = Column(String, nullable=False)  # meal_logged, workout_completed, streak_bonus, etc.
    description = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="xp_logs")


class Achievement(Base):
    """Available achievements in the system."""
    __tablename__ = "achievements"

    id = Column(String, primary_key=True, index=True, default=generate_uuid)

    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    icon = Column(String, nullable=True)
    xp_reward = Column(Integer, default=0)

    # Achievement criteria
    criteria_type = Column(String, nullable=False)  # streak, meals_logged, workouts, level, etc.
    criteria_value = Column(Integer, nullable=False)  # e.g., 7 for 7-day streak

    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user_achievements = relationship("UserAchievement", back_populates="achievement")


class UserAchievement(Base):
    """Tracks which achievements users have earned."""
    __tablename__ = "user_achievements"

    id = Column(String, primary_key=True, index=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    achievement_id = Column(String, ForeignKey("achievements.id", ondelete="CASCADE"), nullable=False)

    earned_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="achievements")
    achievement = relationship("Achievement", back_populates="user_achievements")


# ============================================
# Food & Nutrition Models
# ============================================

class FoodLog(Base):
    __tablename__ = "food_logs"

    id = Column(String, primary_key=True, index=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Food Information
    food_name = Column(String, nullable=False)
    brand = Column(String, nullable=True)

    # Nutritional Values
    calories = Column(Integer, nullable=False)
    protein = Column(Float, default=0)
    carbs = Column(Float, default=0)
    fat = Column(Float, default=0)
    fiber = Column(Float, default=0)
    sugar = Column(Float, default=0)
    sodium = Column(Float, default=0)

    # Serving Information
    serving_size = Column(Float, default=1)
    serving_unit = Column(String, default="portion")

    # Meal Classification
    meal_type = Column(String, default="snack")

    # AI Analysis Fields
    image_url = Column(String, nullable=True)
    ai_analyzed = Column(Boolean, default=False)
    ai_confidence_score = Column(Float, nullable=True)
    ai_raw_response = Column(Text, nullable=True)
    user_confirmed = Column(Boolean, default=True)

    # Social Features
    is_public = Column(Boolean, default=True)
    copied_from_post_id = Column(String, ForeignKey("social_posts.id"), nullable=True)

    # Timestamps
    logged_at = Column(DateTime, default=datetime.datetime.utcnow)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="food_logs")
    copied_from_post = relationship("SocialPost", foreign_keys=[copied_from_post_id])


# ============================================
# Intermittent Fasting Models
# ============================================

class FastingLog(Base):
    """Tracks intermittent fasting sessions."""
    __tablename__ = "fasting_logs"

    id = Column(String, primary_key=True, index=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Fasting Type
    fasting_type = Column(String, default=FastingType.FASTING_16_8.value)

    # Timing
    start_time = Column(DateTime, nullable=False)
    planned_end_time = Column(DateTime, nullable=False)
    actual_end_time = Column(DateTime, nullable=True)

    # Status
    is_active = Column(Boolean, default=True)
    completed = Column(Boolean, default=False)
    cancelled = Column(Boolean, default=False)

    # Stats
    target_hours = Column(Float, nullable=False)
    actual_hours = Column(Float, nullable=True)

    # Notes
    notes = Column(Text, nullable=True)
    mood_before = Column(Integer, nullable=True)  # 1-5
    mood_after = Column(Integer, nullable=True)  # 1-5

    # Timestamps
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    user = relationship("User", back_populates="fasting_logs")


# ============================================
# Workout Models
# ============================================

class Workout(Base):
    """Tracks workout sessions and calories burned."""
    __tablename__ = "workouts"

    id = Column(String, primary_key=True, index=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Workout Details
    workout_type = Column(String, default=WorkoutType.OTHER.value)
    name = Column(String, nullable=True)
    description = Column(Text, nullable=True)

    # Timing
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)
    duration_minutes = Column(Integer, nullable=True)

    # Calories
    calories_burned = Column(Integer, default=0)
    calories_source = Column(String, default="manual")  # manual, calculated, device

    # Intensity
    intensity = Column(String, default="moderate")  # low, moderate, high, very_high
    avg_heart_rate = Column(Integer, nullable=True)
    max_heart_rate = Column(Integer, nullable=True)

    # Distance/Steps (for cardio)
    distance_km = Column(Float, nullable=True)
    steps = Column(Integer, nullable=True)

    # Strength Training
    exercises_data = Column(Text, nullable=True)  # JSON string of exercises

    # Notes
    notes = Column(Text, nullable=True)
    rpe_score = Column(Integer, nullable=True)  # 1-10

    # Timestamps
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    user = relationship("User", back_populates="workouts")


class WorkoutProgram(Base):
    """Predefined workout programs users can follow."""
    __tablename__ = "workout_programs"

    id = Column(String, primary_key=True, index=True, default=generate_uuid)

    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    difficulty = Column(String, default="intermediate")  # beginner, intermediate, advanced
    duration_weeks = Column(Integer, default=4)
    workouts_per_week = Column(Integer, default=3)

    # Program details as JSON
    program_data = Column(Text, nullable=True)

    # Metadata
    category = Column(String, nullable=True)  # strength, cardio, hybrid, sports
    target_goals = Column(String, nullable=True)  # lose_weight, build_muscle, endurance

    is_public = Column(Boolean, default=True)
    created_by = Column(String, ForeignKey("users.id"), nullable=True)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)


# ============================================
# Social Models
# ============================================

class SocialPost(Base):
    """Social feed posts where users share their meals."""
    __tablename__ = "social_posts"

    id = Column(String, primary_key=True, index=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Content
    content = Column(Text, nullable=True)
    image_url = Column(String, nullable=True)

    # Meal Data (for "Add Same" feature)
    meal_type = Column(String, nullable=True)
    food_items = Column(Text, nullable=True)  # JSON array of food items with full nutrition
    total_calories = Column(Integer, default=0)
    total_protein = Column(Float, default=0)
    total_carbs = Column(Float, default=0)
    total_fat = Column(Float, default=0)

    # Stats
    likes_count = Column(Integer, default=0)
    copies_count = Column(Integer, default=0)  # How many times meal was copied
    comments_count = Column(Integer, default=0)

    # Visibility
    is_public = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="posts")
    likes = relationship("PostLike", back_populates="post", cascade="all, delete-orphan")
    comments = relationship("PostComment", back_populates="post", cascade="all, delete-orphan")


class PostLike(Base):
    """Likes on social posts."""
    __tablename__ = "post_likes"

    id = Column(String, primary_key=True, index=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    post_id = Column(String, ForeignKey("social_posts.id", ondelete="CASCADE"), nullable=False)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="post_likes")
    post = relationship("SocialPost", back_populates="likes")


class PostComment(Base):
    """Comments on social posts."""
    __tablename__ = "post_comments"

    id = Column(String, primary_key=True, index=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    post_id = Column(String, ForeignKey("social_posts.id", ondelete="CASCADE"), nullable=False)

    content = Column(Text, nullable=False)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    post = relationship("SocialPost", back_populates="comments")


# ============================================
# Blog Models (Expert Content)
# ============================================

class BlogPost(Base):
    """Blog posts by verified experts (doctors, dieticians)."""
    __tablename__ = "blog_posts"

    id = Column(String, primary_key=True, index=True, default=generate_uuid)
    author_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Content
    title = Column(String, nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False)
    summary = Column(Text, nullable=True)
    content = Column(Text, nullable=False)
    cover_image_url = Column(String, nullable=True)

    # Categorization
    category = Column(String, nullable=True)  # nutrition, fitness, health, recipes
    tags = Column(String, nullable=True)  # Comma-separated tags

    # Status
    is_published = Column(Boolean, default=False)
    published_at = Column(DateTime, nullable=True)

    # Stats
    views_count = Column(Integer, default=0)
    likes_count = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    author = relationship("User", back_populates="blog_posts")


# ============================================
# Recipe Models
# ============================================

class Recipe(Base):
    """Healthy recipes with calculated nutrition."""
    __tablename__ = "recipes"

    id = Column(String, primary_key=True, index=True, default=generate_uuid)
    created_by = Column(String, ForeignKey("users.id"), nullable=True)

    # Basic Info
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    image_url = Column(String, nullable=True)

    # Cooking Info
    prep_time_minutes = Column(Integer, nullable=True)
    cook_time_minutes = Column(Integer, nullable=True)
    servings = Column(Integer, default=1)
    difficulty = Column(String, default="easy")  # easy, medium, hard

    # Ingredients (JSON array)
    ingredients = Column(Text, nullable=False)

    # Instructions (JSON array of steps)
    instructions = Column(Text, nullable=False)

    # Nutrition per serving
    calories_per_serving = Column(Integer, default=0)
    protein_per_serving = Column(Float, default=0)
    carbs_per_serving = Column(Float, default=0)
    fat_per_serving = Column(Float, default=0)
    fiber_per_serving = Column(Float, default=0)

    # Categorization
    category = Column(String, nullable=True)  # breakfast, lunch, dinner, snack, dessert
    tags = Column(String, nullable=True)  # keto, vegan, high-protein, low-carb, etc.
    cuisine = Column(String, nullable=True)  # turkish, mediterranean, asian, etc.

    # Status
    is_public = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)  # Verified by dietician

    # Stats
    saves_count = Column(Integer, default=0)
    rating_avg = Column(Float, default=0)
    rating_count = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


# ============================================
# Existing Models (Updated)
# ============================================

class WeightLog(Base):
    __tablename__ = "weight_logs"

    id = Column(String, primary_key=True, index=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    weight = Column(Float, nullable=False)
    body_fat_percentage = Column(Float, nullable=True)
    muscle_mass = Column(Float, nullable=True)
    bone_mass = Column(Float, nullable=True)
    water_percentage = Column(Float, nullable=True)
    visceral_fat = Column(Integer, nullable=True)
    metabolic_age = Column(Integer, nullable=True)

    source = Column(String, default="manual")
    logged_at = Column(DateTime, default=datetime.datetime.utcnow)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="weight_logs")


class WaterLog(Base):
    __tablename__ = "water_logs"

    id = Column(String, primary_key=True, index=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    amount_ml = Column(Integer, nullable=False)

    logged_at = Column(DateTime, default=datetime.datetime.utcnow)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="water_logs")


class DailyStat(Base):
    __tablename__ = "daily_stats"

    id = Column(String, primary_key=True, index=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False)

    # Nutrition Summary
    total_calories = Column(Integer, default=0)
    total_protein = Column(Float, default=0)
    total_carbs = Column(Float, default=0)
    total_fat = Column(Float, default=0)
    total_fiber = Column(Float, default=0)
    total_water_ml = Column(Integer, default=0)

    # Activity Data
    steps = Column(Integer, default=0)
    distance_km = Column(Float, default=0)
    active_calories = Column(Integer, default=0)
    exercise_minutes = Column(Integer, default=0)

    # Workout calories (separate from daily activity)
    workout_calories = Column(Integer, default=0)

    # Health Metrics
    sleep_hours = Column(Float, nullable=True)
    sleep_quality_score = Column(Integer, nullable=True)
    avg_heart_rate = Column(Integer, nullable=True)
    resting_heart_rate = Column(Integer, nullable=True)
    hrv_ms = Column(Integer, nullable=True)

    # Calculated Scores
    recovery_score = Column(Integer, nullable=True)
    calorie_balance = Column(Integer, nullable=True)  # Calories In - Calories Out
    calorie_deficit = Column(Integer, nullable=True)  # Target deficit vs actual
    goal_adherence_score = Column(Integer, nullable=True)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    user = relationship("User", back_populates="daily_stats")


class AthleteMetric(Base):
    __tablename__ = "athlete_metrics"

    id = Column(String, primary_key=True, index=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False)

    training_load = Column(Integer, nullable=True)
    training_type = Column(String, nullable=True)
    training_duration_min = Column(Integer, nullable=True)
    rpe_score = Column(Integer, nullable=True)

    vo2_max_estimate = Column(Float, nullable=True)
    lactate_threshold_hr = Column(Integer, nullable=True)
    power_output_watts = Column(Float, nullable=True)
    pace_per_km = Column(String, nullable=True)

    hrv_score = Column(Float, nullable=True)
    resting_hr = Column(Integer, nullable=True)
    sleep_hours = Column(Float, nullable=True)
    sleep_quality = Column(Integer, nullable=True)
    muscle_soreness = Column(Integer, nullable=True)
    fatigue_level = Column(Integer, nullable=True)
    stress_level = Column(Integer, nullable=True)

    readiness_score = Column(Integer, nullable=True)
    acute_load = Column(Float, nullable=True)
    chronic_load = Column(Float, nullable=True)
    acwr = Column(Float, nullable=True)

    notes = Column(Text, nullable=True)
    injury_notes = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    user = relationship("User", back_populates="athlete_metrics")


class HealthIntegration(Base):
    __tablename__ = "health_integrations"

    id = Column(String, primary_key=True, index=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    platform = Column(String, nullable=False)
    is_connected = Column(Boolean, default=False)
    access_token = Column(Text, nullable=True)
    refresh_token = Column(Text, nullable=True)
    token_expires_at = Column(DateTime, nullable=True)

    sync_enabled = Column(Boolean, default=True)
    last_sync_at = Column(DateTime, nullable=True)
    sync_frequency_minutes = Column(Integer, default=60)

    sync_steps = Column(Boolean, default=True)
    sync_weight = Column(Boolean, default=True)
    sync_sleep = Column(Boolean, default=True)
    sync_heart_rate = Column(Boolean, default=True)
    sync_workouts = Column(Boolean, default=True)
    sync_nutrition = Column(Boolean, default=False)

    connected_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    user = relationship("User", back_populates="health_integrations")


# Keep old Profile model for backward compatibility
class Profile(Base):
    __tablename__ = "profiles"

    id = Column(String, primary_key=True, index=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    height = Column(Float, nullable=True)
    weight = Column(Float, nullable=True)
