"""
Expert Blog API - Blog posts by doctors and dieticians

Implements Role-Based Access Control (RBAC) to ensure only
verified doctors and dieticians can create blog posts.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
import re

from app.db import get_db
from app.models import User, BlogPost, UserProfile, UserRole
from app.api.deps import get_current_user

router = APIRouter()


# ============================================
# RBAC Middleware
# ============================================

def require_expert(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency that checks if user is an authorized expert (doctor or dietician).

    This implements RBAC for blog content creation.
    """
    allowed_roles = [UserRole.DOCTOR.value, UserRole.DIETICIAN.value, UserRole.ADMIN.value]

    if current_user.role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only verified doctors and dieticians can create blog posts"
        )

    # Additional check for verification status
    if current_user.role in [UserRole.DOCTOR.value, UserRole.DIETICIAN.value] and not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your expert account is pending verification"
        )

    return current_user


# ============================================
# Schemas
# ============================================

class BlogPostCreate(BaseModel):
    title: str
    summary: Optional[str] = None
    content: str
    cover_image_url: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[str] = None
    is_published: bool = False


class BlogPostUpdate(BaseModel):
    title: Optional[str] = None
    summary: Optional[str] = None
    content: Optional[str] = None
    cover_image_url: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[str] = None
    is_published: Optional[bool] = None


class BlogAuthor(BaseModel):
    id: str
    name: str
    role: str
    avatar_url: Optional[str]
    bio: Optional[str]


class BlogPostResponse(BaseModel):
    id: str
    title: str
    slug: str
    summary: Optional[str]
    content: str
    cover_image_url: Optional[str]
    category: Optional[str]
    tags: Optional[str]
    author: BlogAuthor
    is_published: bool
    published_at: Optional[datetime]
    views_count: int
    likes_count: int
    created_at: datetime
    updated_at: datetime


class BlogPostSummary(BaseModel):
    id: str
    title: str
    slug: str
    summary: Optional[str]
    cover_image_url: Optional[str]
    category: Optional[str]
    author_name: str
    author_role: str
    published_at: Optional[datetime]
    views_count: int
    likes_count: int


# ============================================
# Helper Functions
# ============================================

def generate_slug(title: str) -> str:
    """Generate URL-friendly slug from title."""
    # Convert to lowercase and replace spaces with hyphens
    slug = title.lower().strip()
    slug = re.sub(r'[^\w\s-]', '', slug)  # Remove special chars
    slug = re.sub(r'[\s_-]+', '-', slug)  # Replace spaces/underscores with hyphens
    slug = slug.strip('-')

    # Add timestamp to ensure uniqueness
    timestamp = int(datetime.utcnow().timestamp())
    return f"{slug}-{timestamp}"


def get_author_info(db: Session, user: User) -> BlogAuthor:
    """Get author information for blog post."""
    profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()

    name = user.username or "Anonymous"
    if profile and profile.first_name:
        name = f"{profile.first_name} {profile.last_name or ''}".strip()

    role_display = {
        "doctor": "Doctor",
        "dietician": "Dietician",
        "admin": "Admin"
    }

    return BlogAuthor(
        id=user.id,
        name=name,
        role=role_display.get(user.role, user.role.title()),
        avatar_url=profile.avatar_url if profile else None,
        bio=profile.bio if profile else None
    )


# ============================================
# Public Endpoints (Anyone can read)
# ============================================

@router.get("/", response_model=List[BlogPostSummary])
def get_blog_posts(
    category: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Get published blog posts (public endpoint)."""
    query = db.query(BlogPost).filter(BlogPost.is_published == True)

    if category:
        query = query.filter(BlogPost.category == category)

    posts = query.order_by(desc(BlogPost.published_at)).offset(offset).limit(limit).all()

    result = []
    for post in posts:
        author = db.query(User).filter(User.id == post.author_id).first()
        profile = db.query(UserProfile).filter(UserProfile.user_id == post.author_id).first()

        author_name = author.username or "Anonymous"
        if profile and profile.first_name:
            author_name = f"{profile.first_name} {profile.last_name or ''}".strip()

        result.append(BlogPostSummary(
            id=post.id,
            title=post.title,
            slug=post.slug,
            summary=post.summary,
            cover_image_url=post.cover_image_url,
            category=post.category,
            author_name=author_name,
            author_role=author.role.title() if author else "Expert",
            published_at=post.published_at,
            views_count=post.views_count,
            likes_count=post.likes_count
        ))

    return result


@router.get("/categories")
def get_categories(db: Session = Depends(get_db)):
    """Get available blog categories with post counts."""
    posts = db.query(BlogPost).filter(BlogPost.is_published == True).all()

    categories = {}
    for post in posts:
        if post.category:
            categories[post.category] = categories.get(post.category, 0) + 1

    return [
        {"name": cat, "count": count}
        for cat, count in sorted(categories.items())
    ]


@router.get("/{slug}", response_model=BlogPostResponse)
def get_blog_post(
    slug: str,
    db: Session = Depends(get_db)
):
    """Get a single blog post by slug (public endpoint)."""
    post = db.query(BlogPost).filter(
        BlogPost.slug == slug,
        BlogPost.is_published == True
    ).first()

    if not post:
        raise HTTPException(status_code=404, detail="Blog post not found")

    # Increment view count
    post.views_count += 1
    db.commit()

    author = db.query(User).filter(User.id == post.author_id).first()
    author_info = get_author_info(db, author) if author else BlogAuthor(
        id="", name="Anonymous", role="Expert", avatar_url=None, bio=None
    )

    return BlogPostResponse(
        id=post.id,
        title=post.title,
        slug=post.slug,
        summary=post.summary,
        content=post.content,
        cover_image_url=post.cover_image_url,
        category=post.category,
        tags=post.tags,
        author=author_info,
        is_published=post.is_published,
        published_at=post.published_at,
        views_count=post.views_count,
        likes_count=post.likes_count,
        created_at=post.created_at,
        updated_at=post.updated_at
    )


# ============================================
# Expert-Only Endpoints (RBAC Protected)
# ============================================

@router.post("/", response_model=BlogPostResponse)
def create_blog_post(
    post_data: BlogPostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_expert)
):
    """
    Create a new blog post (Expert only).

    Only verified doctors, dieticians, and admins can create posts.
    """
    slug = generate_slug(post_data.title)

    # Check for duplicate slug
    existing = db.query(BlogPost).filter(BlogPost.slug == slug).first()
    if existing:
        slug = f"{slug}-{int(datetime.utcnow().timestamp())}"

    post = BlogPost(
        author_id=current_user.id,
        title=post_data.title,
        slug=slug,
        summary=post_data.summary,
        content=post_data.content,
        cover_image_url=post_data.cover_image_url,
        category=post_data.category,
        tags=post_data.tags,
        is_published=post_data.is_published,
        published_at=datetime.utcnow() if post_data.is_published else None
    )

    db.add(post)
    db.commit()
    db.refresh(post)

    author_info = get_author_info(db, current_user)

    return BlogPostResponse(
        id=post.id,
        title=post.title,
        slug=post.slug,
        summary=post.summary,
        content=post.content,
        cover_image_url=post.cover_image_url,
        category=post.category,
        tags=post.tags,
        author=author_info,
        is_published=post.is_published,
        published_at=post.published_at,
        views_count=0,
        likes_count=0,
        created_at=post.created_at,
        updated_at=post.updated_at
    )


@router.put("/{post_id}", response_model=BlogPostResponse)
def update_blog_post(
    post_id: str,
    post_data: BlogPostUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_expert)
):
    """Update a blog post (Expert only, own posts or admin)."""
    post = db.query(BlogPost).filter(BlogPost.id == post_id).first()

    if not post:
        raise HTTPException(status_code=404, detail="Blog post not found")

    # Check ownership (admins can edit any post)
    if post.author_id != current_user.id and current_user.role != UserRole.ADMIN.value:
        raise HTTPException(status_code=403, detail="You can only edit your own posts")

    # Update fields
    if post_data.title is not None:
        post.title = post_data.title
    if post_data.summary is not None:
        post.summary = post_data.summary
    if post_data.content is not None:
        post.content = post_data.content
    if post_data.cover_image_url is not None:
        post.cover_image_url = post_data.cover_image_url
    if post_data.category is not None:
        post.category = post_data.category
    if post_data.tags is not None:
        post.tags = post_data.tags
    if post_data.is_published is not None:
        was_published = post.is_published
        post.is_published = post_data.is_published
        if not was_published and post_data.is_published:
            post.published_at = datetime.utcnow()

    db.commit()
    db.refresh(post)

    author = db.query(User).filter(User.id == post.author_id).first()
    author_info = get_author_info(db, author) if author else BlogAuthor(
        id="", name="Anonymous", role="Expert", avatar_url=None, bio=None
    )

    return BlogPostResponse(
        id=post.id,
        title=post.title,
        slug=post.slug,
        summary=post.summary,
        content=post.content,
        cover_image_url=post.cover_image_url,
        category=post.category,
        tags=post.tags,
        author=author_info,
        is_published=post.is_published,
        published_at=post.published_at,
        views_count=post.views_count,
        likes_count=post.likes_count,
        created_at=post.created_at,
        updated_at=post.updated_at
    )


@router.delete("/{post_id}")
def delete_blog_post(
    post_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_expert)
):
    """Delete a blog post (Expert only, own posts or admin)."""
    post = db.query(BlogPost).filter(BlogPost.id == post_id).first()

    if not post:
        raise HTTPException(status_code=404, detail="Blog post not found")

    # Check ownership
    if post.author_id != current_user.id and current_user.role != UserRole.ADMIN.value:
        raise HTTPException(status_code=403, detail="You can only delete your own posts")

    db.delete(post)
    db.commit()

    return {"message": "Blog post deleted successfully"}


@router.get("/my/drafts", response_model=List[BlogPostSummary])
def get_my_drafts(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_expert)
):
    """Get current expert's unpublished drafts."""
    posts = db.query(BlogPost).filter(
        BlogPost.author_id == current_user.id,
        BlogPost.is_published == False
    ).order_by(desc(BlogPost.updated_at)).all()

    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    author_name = current_user.username or "Anonymous"
    if profile and profile.first_name:
        author_name = f"{profile.first_name} {profile.last_name or ''}".strip()

    return [
        BlogPostSummary(
            id=post.id,
            title=post.title,
            slug=post.slug,
            summary=post.summary,
            cover_image_url=post.cover_image_url,
            category=post.category,
            author_name=author_name,
            author_role=current_user.role.title(),
            published_at=post.published_at,
            views_count=post.views_count,
            likes_count=post.likes_count
        )
        for post in posts
    ]
