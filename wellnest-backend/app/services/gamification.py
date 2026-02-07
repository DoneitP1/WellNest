"""
Gamification Service - XP, Levels, Streaks, and Achievements

Handles all gamification logic for the WellNest app.
"""

from sqlalchemy.orm import Session
from datetime import datetime, date, timedelta
from typing import Optional, List, Tuple
import math

from app.models import User, XPLog, Achievement, UserAchievement


# ============================================
# XP Configuration
# ============================================

XP_CONFIG = {
    # Food Logging
    "meal_logged": 10,
    "meal_with_photo": 15,
    "meal_with_macros": 5,  # Bonus for logging all macros
    "first_meal_of_day": 5,

    # Workouts
    "workout_completed": 25,
    "workout_30_min": 10,
    "workout_60_min": 20,
    "cardio_5km": 15,

    # Water
    "water_goal_reached": 10,
    "water_logged": 2,

    # Weight
    "weight_logged": 5,

    # Streaks
    "streak_3_days": 25,
    "streak_7_days": 50,
    "streak_14_days": 100,
    "streak_30_days": 250,
    "streak_daily_bonus": 5,  # Per day of streak

    # Fasting
    "fasting_completed": 30,
    "fasting_16h": 20,
    "fasting_20h": 40,

    # Social
    "post_created": 10,
    "post_liked": 2,
    "meal_copied_by_others": 5,

    # Achievements
    "achievement_unlocked": 50,
}

# Level thresholds - XP needed to reach each level
LEVEL_THRESHOLDS = [
    0,      # Level 1
    100,    # Level 2
    250,    # Level 3
    500,    # Level 4
    850,    # Level 5
    1300,   # Level 6
    1900,   # Level 7
    2650,   # Level 8
    3550,   # Level 9
    4650,   # Level 10
    6000,   # Level 11
    7600,   # Level 12
    9500,   # Level 13
    11700,  # Level 14
    14200,  # Level 15
    17000,  # Level 16
    20200,  # Level 17
    23800,  # Level 18
    27800,  # Level 19
    32200,  # Level 20
]


class GamificationService:
    """Service for handling XP, levels, and achievements."""

    def __init__(self, db: Session):
        self.db = db

    def add_xp(
        self,
        user: User,
        action_type: str,
        description: Optional[str] = None,
        custom_amount: Optional[int] = None
    ) -> Tuple[int, bool, Optional[int]]:
        """
        Add XP to a user for a specific action.

        Returns:
            Tuple of (xp_earned, leveled_up, new_level)
        """
        # Get XP amount
        xp_amount = custom_amount if custom_amount else XP_CONFIG.get(action_type, 0)

        if xp_amount <= 0:
            return (0, False, None)

        # Add streak bonus
        if user.streak_days > 0:
            streak_bonus = min(user.streak_days * XP_CONFIG["streak_daily_bonus"], 50)
            xp_amount += streak_bonus

        # Create XP log
        xp_log = XPLog(
            user_id=user.id,
            xp_amount=xp_amount,
            action_type=action_type,
            description=description
        )
        self.db.add(xp_log)

        # Update user XP
        old_level = user.level
        user.xp += xp_amount

        # Check for level up
        new_level = self.calculate_level(user.xp)
        leveled_up = new_level > old_level

        if leveled_up:
            user.level = new_level

        self.db.commit()

        return (xp_amount, leveled_up, new_level if leveled_up else None)

    def calculate_level(self, xp: int) -> int:
        """Calculate level based on XP."""
        level = 1
        for i, threshold in enumerate(LEVEL_THRESHOLDS):
            if xp >= threshold:
                level = i + 1
            else:
                break

        # For XP beyond level 20, use formula
        if xp >= LEVEL_THRESHOLDS[-1]:
            extra_xp = xp - LEVEL_THRESHOLDS[-1]
            extra_levels = int(extra_xp / 5000)  # 5000 XP per level after 20
            level = 20 + extra_levels

        return level

    def get_xp_for_next_level(self, user: User) -> Tuple[int, int]:
        """
        Get XP progress towards next level.

        Returns:
            Tuple of (current_xp_in_level, xp_needed_for_next_level)
        """
        current_level = user.level

        if current_level < len(LEVEL_THRESHOLDS):
            current_threshold = LEVEL_THRESHOLDS[current_level - 1]
            next_threshold = LEVEL_THRESHOLDS[current_level] if current_level < len(LEVEL_THRESHOLDS) else current_threshold + 5000
        else:
            current_threshold = LEVEL_THRESHOLDS[-1] + (current_level - 20) * 5000
            next_threshold = current_threshold + 5000

        xp_in_level = user.xp - current_threshold
        xp_needed = next_threshold - current_threshold

        return (xp_in_level, xp_needed)

    def update_streak(self, user: User) -> Tuple[int, bool]:
        """
        Update user's activity streak.

        Returns:
            Tuple of (new_streak, streak_milestone_reached)
        """
        today = date.today()
        milestone_reached = False

        if user.last_activity_date is None:
            # First activity
            user.streak_days = 1
        elif user.last_activity_date == today:
            # Already logged today, no change
            pass
        elif user.last_activity_date == today - timedelta(days=1):
            # Consecutive day
            user.streak_days += 1

            # Check for streak milestones
            streak_milestones = [3, 7, 14, 30, 60, 90, 180, 365]
            if user.streak_days in streak_milestones:
                milestone_reached = True
                # Award bonus XP
                bonus_xp = self._get_streak_bonus(user.streak_days)
                self.add_xp(user, f"streak_{user.streak_days}_days", custom_amount=bonus_xp)
        else:
            # Streak broken
            user.streak_days = 1

        user.last_activity_date = today
        self.db.commit()

        return (user.streak_days, milestone_reached)

    def _get_streak_bonus(self, streak_days: int) -> int:
        """Get bonus XP for streak milestones."""
        bonuses = {
            3: 25,
            7: 50,
            14: 100,
            30: 250,
            60: 500,
            90: 750,
            180: 1500,
            365: 5000
        }
        return bonuses.get(streak_days, 0)

    def check_achievements(self, user: User) -> List[Achievement]:
        """
        Check and award any earned achievements.

        Returns:
            List of newly earned achievements
        """
        new_achievements = []

        # Get user's existing achievements
        existing = self.db.query(UserAchievement).filter(
            UserAchievement.user_id == user.id
        ).all()
        existing_ids = {ua.achievement_id for ua in existing}

        # Get all achievements
        all_achievements = self.db.query(Achievement).all()

        for achievement in all_achievements:
            if achievement.id in existing_ids:
                continue

            # Check if criteria is met
            if self._check_achievement_criteria(user, achievement):
                # Award achievement
                user_achievement = UserAchievement(
                    user_id=user.id,
                    achievement_id=achievement.id
                )
                self.db.add(user_achievement)

                # Award bonus XP
                if achievement.xp_reward > 0:
                    self.add_xp(
                        user,
                        "achievement_unlocked",
                        f"Unlocked: {achievement.name}",
                        achievement.xp_reward
                    )

                new_achievements.append(achievement)

        self.db.commit()
        return new_achievements

    def _check_achievement_criteria(self, user: User, achievement: Achievement) -> bool:
        """Check if user meets achievement criteria."""
        criteria_type = achievement.criteria_type
        criteria_value = achievement.criteria_value

        if criteria_type == "streak":
            return user.streak_days >= criteria_value

        elif criteria_type == "level":
            return user.level >= criteria_value

        elif criteria_type == "meals_logged":
            count = len(user.food_logs)
            return count >= criteria_value

        elif criteria_type == "workouts":
            count = len(user.workouts)
            return count >= criteria_value

        elif criteria_type == "total_xp":
            return user.xp >= criteria_value

        elif criteria_type == "posts_created":
            count = len(user.posts)
            return count >= criteria_value

        elif criteria_type == "fasting_completed":
            count = len([f for f in user.fasting_logs if f.completed])
            return count >= criteria_value

        return False

    def get_leaderboard(self, limit: int = 10, timeframe: str = "all") -> List[dict]:
        """
        Get XP leaderboard.

        Args:
            limit: Number of users to return
            timeframe: "all", "week", "month"
        """
        query = self.db.query(User).filter(User.is_active == True)

        if timeframe == "all":
            users = query.order_by(User.xp.desc()).limit(limit).all()
        else:
            # For time-based leaderboards, we'd sum XP from xp_logs
            # Simplified version - just use total XP
            users = query.order_by(User.xp.desc()).limit(limit).all()

        leaderboard = []
        for rank, user in enumerate(users, 1):
            leaderboard.append({
                "rank": rank,
                "user_id": user.id,
                "username": user.username or f"User{user.id[:6]}",
                "xp": user.xp,
                "level": user.level,
                "streak_days": user.streak_days
            })

        return leaderboard

    def get_user_stats(self, user: User) -> dict:
        """Get comprehensive gamification stats for a user."""
        xp_progress, xp_needed = self.get_xp_for_next_level(user)

        # Count achievements
        achievement_count = self.db.query(UserAchievement).filter(
            UserAchievement.user_id == user.id
        ).count()

        total_achievements = self.db.query(Achievement).count()

        # Recent XP logs
        recent_xp = self.db.query(XPLog).filter(
            XPLog.user_id == user.id
        ).order_by(XPLog.created_at.desc()).limit(10).all()

        return {
            "xp": user.xp,
            "level": user.level,
            "xp_progress": xp_progress,
            "xp_needed": xp_needed,
            "progress_percentage": round((xp_progress / xp_needed) * 100, 1) if xp_needed > 0 else 100,
            "streak_days": user.streak_days,
            "achievements_earned": achievement_count,
            "achievements_total": total_achievements,
            "recent_xp": [
                {
                    "xp": log.xp_amount,
                    "action": log.action_type,
                    "description": log.description,
                    "timestamp": log.created_at.isoformat()
                }
                for log in recent_xp
            ]
        }


def init_default_achievements(db: Session):
    """Initialize default achievements in the database."""
    default_achievements = [
        # Streak Achievements
        {"name": "Getting Started", "description": "Log activity for 3 days in a row", "icon": "🌱", "criteria_type": "streak", "criteria_value": 3, "xp_reward": 25},
        {"name": "Week Warrior", "description": "Maintain a 7-day streak", "icon": "🔥", "criteria_type": "streak", "criteria_value": 7, "xp_reward": 50},
        {"name": "Two Week Champion", "description": "Maintain a 14-day streak", "icon": "💪", "criteria_type": "streak", "criteria_value": 14, "xp_reward": 100},
        {"name": "Monthly Master", "description": "Maintain a 30-day streak", "icon": "🏆", "criteria_type": "streak", "criteria_value": 30, "xp_reward": 250},

        # Level Achievements
        {"name": "Level 5", "description": "Reach level 5", "icon": "⭐", "criteria_type": "level", "criteria_value": 5, "xp_reward": 50},
        {"name": "Level 10", "description": "Reach level 10", "icon": "🌟", "criteria_type": "level", "criteria_value": 10, "xp_reward": 100},
        {"name": "Level 20", "description": "Reach level 20", "icon": "💫", "criteria_type": "level", "criteria_value": 20, "xp_reward": 250},

        # Meal Logging Achievements
        {"name": "First Bite", "description": "Log your first meal", "icon": "🍽️", "criteria_type": "meals_logged", "criteria_value": 1, "xp_reward": 10},
        {"name": "Food Tracker", "description": "Log 50 meals", "icon": "📝", "criteria_type": "meals_logged", "criteria_value": 50, "xp_reward": 50},
        {"name": "Nutrition Pro", "description": "Log 500 meals", "icon": "🥗", "criteria_type": "meals_logged", "criteria_value": 500, "xp_reward": 250},

        # Workout Achievements
        {"name": "First Workout", "description": "Complete your first workout", "icon": "🏋️", "criteria_type": "workouts", "criteria_value": 1, "xp_reward": 15},
        {"name": "Fitness Enthusiast", "description": "Complete 25 workouts", "icon": "💪", "criteria_type": "workouts", "criteria_value": 25, "xp_reward": 100},
        {"name": "Gym Rat", "description": "Complete 100 workouts", "icon": "🦾", "criteria_type": "workouts", "criteria_value": 100, "xp_reward": 300},

        # Fasting Achievements
        {"name": "First Fast", "description": "Complete your first fast", "icon": "⏰", "criteria_type": "fasting_completed", "criteria_value": 1, "xp_reward": 20},
        {"name": "Fasting Regular", "description": "Complete 10 fasts", "icon": "🧘", "criteria_type": "fasting_completed", "criteria_value": 10, "xp_reward": 75},

        # Social Achievements
        {"name": "Social Butterfly", "description": "Share 5 meals", "icon": "🦋", "criteria_type": "posts_created", "criteria_value": 5, "xp_reward": 30},
    ]

    for ach_data in default_achievements:
        existing = db.query(Achievement).filter(Achievement.name == ach_data["name"]).first()
        if not existing:
            achievement = Achievement(**ach_data)
            db.add(achievement)

    db.commit()
