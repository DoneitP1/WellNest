"""
WellNest Calorie & Macro Calculation Module

This module implements the Mifflin-St Jeor equation for BMR calculation
and provides comprehensive macro nutrient calculations for both regular
users and professional athletes.
"""

from datetime import date, datetime
from typing import Optional, Literal, TypedDict
from enum import Enum


class Gender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class ActivityLevel(str, Enum):
    SEDENTARY = "sedentary"          # Little to no exercise
    LIGHT = "light"                  # Light exercise 1-3 days/week
    MODERATE = "moderate"            # Moderate exercise 3-5 days/week
    ACTIVE = "active"                # Heavy exercise 6-7 days/week
    VERY_ACTIVE = "very_active"      # Professional athlete/very heavy exercise


class GoalType(str, Enum):
    LOSE_WEIGHT = "lose_weight"
    MAINTAIN = "maintain"
    GAIN_MUSCLE = "gain_muscle"
    IMPROVE_HEALTH = "improve_health"


# Activity level multipliers for TDEE calculation
ACTIVITY_MULTIPLIERS = {
    ActivityLevel.SEDENTARY: 1.2,
    ActivityLevel.LIGHT: 1.375,
    ActivityLevel.MODERATE: 1.55,
    ActivityLevel.ACTIVE: 1.725,
    ActivityLevel.VERY_ACTIVE: 1.9,
}

# Calorie adjustments based on goals
GOAL_CALORIE_ADJUSTMENTS = {
    GoalType.LOSE_WEIGHT: -500,      # 500 calorie deficit for ~0.5kg/week loss
    GoalType.MAINTAIN: 0,
    GoalType.GAIN_MUSCLE: 300,       # 300 calorie surplus for lean muscle gain
    GoalType.IMPROVE_HEALTH: 0,
}


class MacroDistribution(TypedDict):
    protein_grams: float
    protein_percentage: float
    carbs_grams: float
    carbs_percentage: float
    fat_grams: float
    fat_percentage: float


class NutritionGoals(TypedDict):
    bmr: float
    tdee: float
    daily_calories: int
    protein_grams: float
    carbs_grams: float
    fat_grams: float
    water_ml: int


def calculate_age(birth_date: date) -> int:
    """Calculate age from birth date."""
    today = date.today()
    age = today.year - birth_date.year
    # Adjust if birthday hasn't occurred this year
    if (today.month, today.day) < (birth_date.month, birth_date.day):
        age -= 1
    return age


def calculate_bmr(
    weight_kg: float,
    height_cm: float,
    age: int,
    gender: Gender
) -> float:
    """
    Calculate Basal Metabolic Rate using Mifflin-St Jeor Equation.

    The Mifflin-St Jeor equation is considered the most accurate for
    estimating BMR in most individuals.

    Formula:
        Male:   BMR = (10 × weight[kg]) + (6.25 × height[cm]) - (5 × age) + 5
        Female: BMR = (10 × weight[kg]) + (6.25 × height[cm]) - (5 × age) - 161

    Args:
        weight_kg: Body weight in kilograms
        height_cm: Height in centimeters
        age: Age in years
        gender: Gender (male, female, or other)

    Returns:
        BMR in calories per day
    """
    base_bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age)

    if gender == Gender.MALE:
        return base_bmr + 5
    elif gender == Gender.FEMALE:
        return base_bmr - 161
    else:
        # For 'other', use average of male and female
        return base_bmr - 78  # Average of +5 and -161


def calculate_tdee(bmr: float, activity_level: ActivityLevel) -> float:
    """
    Calculate Total Daily Energy Expenditure.

    TDEE = BMR × Activity Multiplier

    Args:
        bmr: Basal Metabolic Rate
        activity_level: Physical activity level

    Returns:
        TDEE in calories per day
    """
    multiplier = ACTIVITY_MULTIPLIERS.get(activity_level, 1.55)
    return bmr * multiplier


def calculate_daily_calories(
    tdee: float,
    goal_type: GoalType,
    custom_adjustment: Optional[int] = None
) -> int:
    """
    Calculate daily calorie goal based on TDEE and fitness goal.

    Args:
        tdee: Total Daily Energy Expenditure
        goal_type: User's fitness goal
        custom_adjustment: Optional custom calorie adjustment

    Returns:
        Daily calorie goal
    """
    if custom_adjustment is not None:
        adjustment = custom_adjustment
    else:
        adjustment = GOAL_CALORIE_ADJUSTMENTS.get(goal_type, 0)

    daily_calories = tdee + adjustment

    # Ensure minimum safe calorie intake
    # Generally, 1200 for women and 1500 for men is considered minimum
    return max(int(daily_calories), 1200)


def calculate_macros_standard(
    daily_calories: int,
    weight_kg: float,
    goal_type: GoalType
) -> MacroDistribution:
    """
    Calculate macro distribution for standard users.

    Standard macro splits:
        - Lose Weight: 40% protein, 30% carbs, 30% fat
        - Maintain: 30% protein, 40% carbs, 30% fat
        - Gain Muscle: 35% protein, 45% carbs, 20% fat
        - Improve Health: 25% protein, 45% carbs, 30% fat

    Args:
        daily_calories: Target daily calories
        weight_kg: Body weight in kg
        goal_type: User's fitness goal

    Returns:
        MacroDistribution with grams and percentages
    """
    # Define macro percentages based on goal
    macro_splits = {
        GoalType.LOSE_WEIGHT: {"protein": 0.40, "carbs": 0.30, "fat": 0.30},
        GoalType.MAINTAIN: {"protein": 0.30, "carbs": 0.40, "fat": 0.30},
        GoalType.GAIN_MUSCLE: {"protein": 0.35, "carbs": 0.45, "fat": 0.20},
        GoalType.IMPROVE_HEALTH: {"protein": 0.25, "carbs": 0.45, "fat": 0.30},
    }

    split = macro_splits.get(goal_type, macro_splits[GoalType.MAINTAIN])

    # Calculate calories from each macro
    protein_calories = daily_calories * split["protein"]
    carbs_calories = daily_calories * split["carbs"]
    fat_calories = daily_calories * split["fat"]

    # Convert to grams (protein: 4 cal/g, carbs: 4 cal/g, fat: 9 cal/g)
    protein_grams = protein_calories / 4
    carbs_grams = carbs_calories / 4
    fat_grams = fat_calories / 9

    return MacroDistribution(
        protein_grams=round(protein_grams, 1),
        protein_percentage=round(split["protein"] * 100, 1),
        carbs_grams=round(carbs_grams, 1),
        carbs_percentage=round(split["carbs"] * 100, 1),
        fat_grams=round(fat_grams, 1),
        fat_percentage=round(split["fat"] * 100, 1),
    )


def calculate_macros_athlete(
    daily_calories: int,
    weight_kg: float,
    training_type: Literal["strength", "endurance", "mixed", "power"],
    training_phase: Literal["building", "cutting", "maintenance", "competition"] = "maintenance"
) -> MacroDistribution:
    """
    Calculate macro distribution for professional athletes.

    Athletes have different protein requirements based on training type:
        - Strength: 1.6-2.2 g/kg body weight
        - Endurance: 1.2-1.6 g/kg body weight
        - Mixed: 1.4-1.8 g/kg body weight
        - Power: 1.8-2.4 g/kg body weight

    Args:
        daily_calories: Target daily calories
        weight_kg: Body weight in kg
        training_type: Type of training (strength, endurance, mixed, power)
        training_phase: Current training phase

    Returns:
        MacroDistribution with grams and percentages
    """
    # Protein requirements per kg of body weight
    protein_per_kg = {
        "strength": {"building": 2.2, "cutting": 2.4, "maintenance": 1.8, "competition": 2.0},
        "endurance": {"building": 1.4, "cutting": 1.6, "maintenance": 1.2, "competition": 1.4},
        "mixed": {"building": 1.8, "cutting": 2.0, "maintenance": 1.6, "competition": 1.8},
        "power": {"building": 2.4, "cutting": 2.6, "maintenance": 2.0, "competition": 2.2},
    }

    # Fat requirements (minimum for hormone health)
    fat_per_kg = {
        "strength": 0.8,
        "endurance": 0.7,
        "mixed": 0.75,
        "power": 0.85,
    }

    # Get protein requirement
    protein_grams = weight_kg * protein_per_kg[training_type][training_phase]
    protein_calories = protein_grams * 4

    # Get fat requirement (ensure minimum for hormone health)
    min_fat_grams = weight_kg * fat_per_kg[training_type]
    min_fat_calories = min_fat_grams * 9

    # Calculate remaining calories for carbs
    remaining_calories = daily_calories - protein_calories - min_fat_calories
    carbs_grams = max(remaining_calories / 4, 100)  # Minimum 100g carbs
    carbs_calories = carbs_grams * 4

    # Recalculate if carbs were floored
    if remaining_calories / 4 < 100:
        # Adjust fat to accommodate minimum carbs
        available_for_fat = daily_calories - protein_calories - 400  # 100g carbs = 400 cal
        fat_grams = max(available_for_fat / 9, min_fat_grams * 0.8)  # Allow 20% reduction
        fat_calories = fat_grams * 9
    else:
        fat_grams = min_fat_grams
        fat_calories = min_fat_calories

    # Calculate percentages
    total_calories = protein_calories + carbs_calories + fat_calories
    protein_pct = (protein_calories / total_calories) * 100
    carbs_pct = (carbs_calories / total_calories) * 100
    fat_pct = (fat_calories / total_calories) * 100

    return MacroDistribution(
        protein_grams=round(protein_grams, 1),
        protein_percentage=round(protein_pct, 1),
        carbs_grams=round(carbs_grams, 1),
        carbs_percentage=round(carbs_pct, 1),
        fat_grams=round(fat_grams, 1),
        fat_percentage=round(fat_pct, 1),
    )


def calculate_water_intake(
    weight_kg: float,
    activity_level: ActivityLevel,
    is_athlete: bool = False
) -> int:
    """
    Calculate recommended daily water intake.

    Base formula: 30-35 ml per kg of body weight
    Athletes: Additional 500-1000ml depending on activity level

    Args:
        weight_kg: Body weight in kg
        activity_level: Physical activity level
        is_athlete: Whether user is a professional athlete

    Returns:
        Recommended water intake in ml
    """
    # Base water intake (ml per kg)
    base_ml_per_kg = {
        ActivityLevel.SEDENTARY: 30,
        ActivityLevel.LIGHT: 32,
        ActivityLevel.MODERATE: 35,
        ActivityLevel.ACTIVE: 38,
        ActivityLevel.VERY_ACTIVE: 40,
    }

    base_intake = weight_kg * base_ml_per_kg.get(activity_level, 35)

    # Additional water for athletes
    if is_athlete:
        athlete_bonus = {
            ActivityLevel.SEDENTARY: 300,
            ActivityLevel.LIGHT: 500,
            ActivityLevel.MODERATE: 700,
            ActivityLevel.ACTIVE: 900,
            ActivityLevel.VERY_ACTIVE: 1200,
        }
        base_intake += athlete_bonus.get(activity_level, 500)

    return int(base_intake)


def calculate_all_nutrition_goals(
    weight_kg: float,
    height_cm: float,
    birth_date: date,
    gender: Gender,
    activity_level: ActivityLevel,
    goal_type: GoalType,
    is_athlete: bool = False,
    training_type: Optional[str] = None,
    training_phase: Optional[str] = None
) -> NutritionGoals:
    """
    Calculate all nutrition goals for a user.

    This is the main function to call when setting up a user's nutrition plan.

    Args:
        weight_kg: Body weight in kg
        height_cm: Height in cm
        birth_date: User's birth date
        gender: User's gender
        activity_level: Physical activity level
        goal_type: User's fitness goal
        is_athlete: Whether user is a professional athlete
        training_type: Type of athletic training (if athlete)
        training_phase: Current training phase (if athlete)

    Returns:
        NutritionGoals with all calculated values
    """
    # Calculate age
    age = calculate_age(birth_date)

    # Calculate BMR
    bmr = calculate_bmr(weight_kg, height_cm, age, gender)

    # Calculate TDEE
    tdee = calculate_tdee(bmr, activity_level)

    # Calculate daily calories
    daily_calories = calculate_daily_calories(tdee, goal_type)

    # Calculate macros based on user type
    if is_athlete and training_type:
        macros = calculate_macros_athlete(
            daily_calories,
            weight_kg,
            training_type,
            training_phase or "maintenance"
        )
    else:
        macros = calculate_macros_standard(daily_calories, weight_kg, goal_type)

    # Calculate water intake
    water_ml = calculate_water_intake(weight_kg, activity_level, is_athlete)

    return NutritionGoals(
        bmr=round(bmr, 1),
        tdee=round(tdee, 1),
        daily_calories=daily_calories,
        protein_grams=macros["protein_grams"],
        carbs_grams=macros["carbs_grams"],
        fat_grams=macros["fat_grams"],
        water_ml=water_ml,
    )


def calculate_recovery_score(
    sleep_hours: float,
    resting_hr: int,
    baseline_resting_hr: int,
    hrv_ms: Optional[int] = None,
    baseline_hrv: Optional[int] = None,
    muscle_soreness: Optional[int] = None,  # 1-10 scale
    fatigue_level: Optional[int] = None,    # 1-10 scale
    stress_level: Optional[int] = None      # 1-10 scale
) -> int:
    """
    Calculate recovery score for athletes.

    Recovery score is calculated based on:
        - Sleep quality/duration (35%)
        - Heart rate recovery (25%)
        - HRV if available (20%)
        - Subjective metrics (20%)

    Args:
        sleep_hours: Hours of sleep
        resting_hr: Current resting heart rate
        baseline_resting_hr: Average baseline resting heart rate
        hrv_ms: Heart Rate Variability in milliseconds (optional)
        baseline_hrv: Average baseline HRV (optional)
        muscle_soreness: Muscle soreness level 1-10 (optional)
        fatigue_level: Fatigue level 1-10 (optional)
        stress_level: Stress level 1-10 (optional)

    Returns:
        Recovery score from 0-100
    """
    scores = []
    weights = []

    # Sleep score (optimal: 7-9 hours)
    if 7 <= sleep_hours <= 9:
        sleep_score = 100
    elif sleep_hours < 7:
        sleep_score = max(0, (sleep_hours / 7) * 100)
    else:  # More than 9 hours might indicate fatigue
        sleep_score = max(0, 100 - (sleep_hours - 9) * 10)

    scores.append(sleep_score)
    weights.append(0.35)

    # Heart rate score (closer to baseline is better)
    hr_diff = abs(resting_hr - baseline_resting_hr)
    hr_score = max(0, 100 - hr_diff * 5)  # -5 points per BPM deviation
    scores.append(hr_score)
    weights.append(0.25)

    # HRV score (if available)
    if hrv_ms is not None and baseline_hrv is not None:
        hrv_ratio = hrv_ms / baseline_hrv
        if hrv_ratio >= 1:
            hrv_score = min(100, 80 + (hrv_ratio - 1) * 40)
        else:
            hrv_score = max(0, hrv_ratio * 80)
        scores.append(hrv_score)
        weights.append(0.20)
    elif hrv_ms is not None:
        # If no baseline, use absolute values (50-100ms is generally good)
        hrv_score = min(100, (hrv_ms / 80) * 100)
        scores.append(hrv_score)
        weights.append(0.10)

    # Subjective metrics (if available)
    subjective_scores = []
    if muscle_soreness is not None:
        subjective_scores.append((11 - muscle_soreness) * 10)  # Invert scale
    if fatigue_level is not None:
        subjective_scores.append((11 - fatigue_level) * 10)
    if stress_level is not None:
        subjective_scores.append((11 - stress_level) * 10)

    if subjective_scores:
        avg_subjective = sum(subjective_scores) / len(subjective_scores)
        scores.append(avg_subjective)
        weights.append(0.20)

    # Normalize weights
    total_weight = sum(weights)
    normalized_weights = [w / total_weight for w in weights]

    # Calculate weighted average
    recovery_score = sum(s * w for s, w in zip(scores, normalized_weights))

    return min(100, max(0, int(recovery_score)))


def calculate_readiness_score(
    recovery_score: int,
    training_load_7day: float,
    training_load_28day: float,
    sleep_hours: float,
    avg_sleep_hours: float = 7.5
) -> int:
    """
    Calculate training readiness score for athletes.

    Considers:
        - Recovery score (40%)
        - Acute:Chronic Workload Ratio (30%)
        - Recent sleep pattern (30%)

    ACWR sweet spot: 0.8 - 1.3
    Below 0.8: Undertrained
    Above 1.5: High injury risk

    Args:
        recovery_score: Current recovery score (0-100)
        training_load_7day: 7-day rolling average training load
        training_load_28day: 28-day rolling average training load
        sleep_hours: Last night's sleep
        avg_sleep_hours: Average sleep hours

    Returns:
        Readiness score from 0-100
    """
    scores = []

    # Recovery component (40%)
    scores.append(recovery_score * 0.40)

    # ACWR component (30%)
    if training_load_28day > 0:
        acwr = training_load_7day / training_load_28day
        if 0.8 <= acwr <= 1.3:
            acwr_score = 100
        elif acwr < 0.8:
            acwr_score = max(0, acwr / 0.8 * 100)
        else:  # > 1.3
            acwr_score = max(0, 100 - (acwr - 1.3) * 100)
    else:
        acwr_score = 50  # Neutral if no baseline

    scores.append(acwr_score * 0.30)

    # Sleep pattern component (30%)
    sleep_ratio = sleep_hours / avg_sleep_hours
    if sleep_ratio >= 1:
        sleep_pattern_score = 100
    else:
        sleep_pattern_score = max(0, sleep_ratio * 100)

    scores.append(sleep_pattern_score * 0.30)

    return min(100, max(0, int(sum(scores))))


# Utility functions for conversions

def kg_to_lbs(kg: float) -> float:
    """Convert kilograms to pounds."""
    return kg * 2.20462


def lbs_to_kg(lbs: float) -> float:
    """Convert pounds to kilograms."""
    return lbs / 2.20462


def cm_to_inches(cm: float) -> float:
    """Convert centimeters to inches."""
    return cm / 2.54


def inches_to_cm(inches: float) -> float:
    """Convert inches to centimeters."""
    return inches * 2.54


def feet_inches_to_cm(feet: int, inches: int) -> float:
    """Convert feet and inches to centimeters."""
    total_inches = feet * 12 + inches
    return inches_to_cm(total_inches)
