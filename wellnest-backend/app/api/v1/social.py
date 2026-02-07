"""
Social Feed API - Share meals, copy meals, likes and comments

The "Add Same" feature allows users to copy another user's meal
with all nutritional data to their own food log.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from datetime import datetime
import json

from app.db import get_db
from app.models import User, SocialPost, PostLike, PostComment, FoodLog, UserProfile
from app.api.deps import get_current_user
from app.services.gamification import GamificationService
from pydantic import BaseModel

router = APIRouter()


# ============================================
# Schemas
# ============================================

class FoodItemSchema(BaseModel):
    food_name: str
    calories: int
    protein: float = 0
    carbs: float = 0
    fat: float = 0
    fiber: float = 0
    serving_size: float = 1
    serving_unit: str = "portion"


class PostCreate(BaseModel):
    content: Optional[str] = None
    image_url: Optional[str] = None
    meal_type: Optional[str] = None
    food_items: Optional[List[FoodItemSchema]] = None


class PostResponse(BaseModel):
    id: str
    user_id: str
    username: Optional[str]
    avatar_url: Optional[str]
    content: Optional[str]
    image_url: Optional[str]
    meal_type: Optional[str]
    food_items: Optional[List[dict]]
    total_calories: int
    total_protein: float
    total_carbs: float
    total_fat: float
    likes_count: int
    copies_count: int
    comments_count: int
    is_liked: bool = False
    created_at: datetime

    class Config:
        from_attributes = True


class CommentCreate(BaseModel):
    content: str


class CommentResponse(BaseModel):
    id: str
    user_id: str
    username: Optional[str]
    content: str
    created_at: datetime


class CopyMealResponse(BaseModel):
    success: bool
    message: str
    foods_added: int
    total_calories: int
    xp_earned: int = 0


# ============================================
# Endpoints
# ============================================

@router.get("/feed", response_model=List[PostResponse])
def get_feed(
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get social feed with recent meal posts."""
    posts = db.query(SocialPost).filter(
        SocialPost.is_public == True
    ).order_by(desc(SocialPost.created_at)).offset(offset).limit(limit).all()

    # Get user's liked posts
    user_likes = db.query(PostLike.post_id).filter(
        PostLike.user_id == current_user.id
    ).all()
    liked_post_ids = {like.post_id for like in user_likes}

    result = []
    for post in posts:
        # Get author info
        profile = db.query(UserProfile).filter(UserProfile.user_id == post.user_id).first()

        result.append(PostResponse(
            id=post.id,
            user_id=post.user_id,
            username=post.user.username or (f"{profile.first_name}" if profile and profile.first_name else f"User{post.user_id[:6]}"),
            avatar_url=profile.avatar_url if profile else None,
            content=post.content,
            image_url=post.image_url,
            meal_type=post.meal_type,
            food_items=json.loads(post.food_items) if post.food_items else None,
            total_calories=post.total_calories,
            total_protein=post.total_protein,
            total_carbs=post.total_carbs,
            total_fat=post.total_fat,
            likes_count=post.likes_count,
            copies_count=post.copies_count,
            comments_count=post.comments_count,
            is_liked=post.id in liked_post_ids,
            created_at=post.created_at
        ))

    return result


@router.post("/posts", response_model=PostResponse)
def create_post(
    post_data: PostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new social post sharing a meal."""
    # Calculate totals from food items
    total_calories = 0
    total_protein = 0
    total_carbs = 0
    total_fat = 0

    food_items_json = None
    if post_data.food_items:
        food_items_list = []
        for item in post_data.food_items:
            total_calories += item.calories
            total_protein += item.protein
            total_carbs += item.carbs
            total_fat += item.fat
            food_items_list.append(item.dict())
        food_items_json = json.dumps(food_items_list)

    post = SocialPost(
        user_id=current_user.id,
        content=post_data.content,
        image_url=post_data.image_url,
        meal_type=post_data.meal_type,
        food_items=food_items_json,
        total_calories=total_calories,
        total_protein=round(total_protein, 1),
        total_carbs=round(total_carbs, 1),
        total_fat=round(total_fat, 1)
    )

    db.add(post)

    # Award XP for posting
    gamification = GamificationService(db)
    gamification.add_xp(current_user, "post_created", f"Shared a {post_data.meal_type or 'meal'}")
    gamification.update_streak(current_user)

    db.commit()
    db.refresh(post)

    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()

    return PostResponse(
        id=post.id,
        user_id=post.user_id,
        username=current_user.username or (f"{profile.first_name}" if profile and profile.first_name else f"User{current_user.id[:6]}"),
        avatar_url=profile.avatar_url if profile else None,
        content=post.content,
        image_url=post.image_url,
        meal_type=post.meal_type,
        food_items=json.loads(post.food_items) if post.food_items else None,
        total_calories=post.total_calories,
        total_protein=post.total_protein,
        total_carbs=post.total_carbs,
        total_fat=post.total_fat,
        likes_count=0,
        copies_count=0,
        comments_count=0,
        is_liked=False,
        created_at=post.created_at
    )


@router.post("/posts/{post_id}/like")
def like_post(
    post_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Like or unlike a post."""
    post = db.query(SocialPost).filter(SocialPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    existing_like = db.query(PostLike).filter(
        PostLike.post_id == post_id,
        PostLike.user_id == current_user.id
    ).first()

    if existing_like:
        # Unlike
        db.delete(existing_like)
        post.likes_count = max(0, post.likes_count - 1)
        action = "unliked"
    else:
        # Like
        like = PostLike(user_id=current_user.id, post_id=post_id)
        db.add(like)
        post.likes_count += 1
        action = "liked"

        # Award XP to post author (not self)
        if post.user_id != current_user.id:
            gamification = GamificationService(db)
            author = db.query(User).filter(User.id == post.user_id).first()
            if author:
                gamification.add_xp(author, "post_liked", "Your post was liked")

    db.commit()

    return {"action": action, "likes_count": post.likes_count}


@router.post("/posts/{post_id}/copy", response_model=CopyMealResponse)
def copy_meal(
    post_id: str,
    meal_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Copy a meal from a social post to the current user's food log.

    This is the "Aynısını Ekle" (Add Same) feature - copies all food items
    with their full nutritional data to the user's daily log.
    """
    post = db.query(SocialPost).filter(SocialPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if not post.food_items:
        raise HTTPException(status_code=400, detail="This post has no food items to copy")

    # Parse food items
    try:
        food_items = json.loads(post.food_items)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid food data in post")

    # Create food logs for each item
    total_calories = 0
    foods_added = 0
    now = datetime.utcnow()

    for item in food_items:
        food_log = FoodLog(
            user_id=current_user.id,
            food_name=item.get("food_name", "Unknown"),
            calories=item.get("calories", 0),
            protein=item.get("protein", 0),
            carbs=item.get("carbs", 0),
            fat=item.get("fat", 0),
            fiber=item.get("fiber", 0),
            serving_size=item.get("serving_size", 1),
            serving_unit=item.get("serving_unit", "portion"),
            meal_type=meal_type or post.meal_type or "snack",
            copied_from_post_id=post_id,
            logged_at=now
        )
        db.add(food_log)
        total_calories += item.get("calories", 0)
        foods_added += 1

    # Increment copy count on post
    post.copies_count += 1

    # Award XP for logging meals
    gamification = GamificationService(db)
    xp_earned, _, _ = gamification.add_xp(
        current_user,
        "meal_logged",
        f"Copied meal from social feed"
    )

    # Award XP to original poster
    if post.user_id != current_user.id:
        author = db.query(User).filter(User.id == post.user_id).first()
        if author:
            gamification.add_xp(author, "meal_copied_by_others", "Your meal was copied")

    # Update streak
    gamification.update_streak(current_user)

    db.commit()

    return CopyMealResponse(
        success=True,
        message=f"Added {foods_added} food items to your log",
        foods_added=foods_added,
        total_calories=total_calories,
        xp_earned=xp_earned
    )


@router.get("/posts/{post_id}/comments", response_model=List[CommentResponse])
def get_comments(
    post_id: str,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get comments for a post."""
    comments = db.query(PostComment).filter(
        PostComment.post_id == post_id
    ).order_by(PostComment.created_at.asc()).limit(limit).all()

    result = []
    for comment in comments:
        user = db.query(User).filter(User.id == comment.user_id).first()
        result.append(CommentResponse(
            id=comment.id,
            user_id=comment.user_id,
            username=user.username if user else "Unknown",
            content=comment.content,
            created_at=comment.created_at
        ))

    return result


@router.post("/posts/{post_id}/comments", response_model=CommentResponse)
def add_comment(
    post_id: str,
    comment_data: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add a comment to a post."""
    post = db.query(SocialPost).filter(SocialPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    comment = PostComment(
        user_id=current_user.id,
        post_id=post_id,
        content=comment_data.content
    )
    db.add(comment)
    post.comments_count += 1

    db.commit()
    db.refresh(comment)

    return CommentResponse(
        id=comment.id,
        user_id=comment.user_id,
        username=current_user.username or f"User{current_user.id[:6]}",
        content=comment.content,
        created_at=comment.created_at
    )


@router.delete("/posts/{post_id}")
def delete_post(
    post_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a post (only by owner)."""
    post = db.query(SocialPost).filter(SocialPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if post.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only delete your own posts")

    db.delete(post)
    db.commit()

    return {"message": "Post deleted successfully"}
