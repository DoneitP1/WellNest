"""
WellNest API - AI-Powered Health & Calorie Tracking

Main application entry point with gamification, social features, and expert content.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import auth, user, health, athlete, social, fasting, workout, blog, deficit, recipe
from app.db import Base, engine, SessionLocal
from app.services.gamification import init_default_achievements

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize default achievements
db = SessionLocal()
try:
    init_default_achievements(db)
finally:
    db.close()

app = FastAPI(
    title="WellNest API",
    description="""
    AI-Powered Health & Calorie Tracking API with:
    - 🎮 Gamification (XP, Levels, Achievements)
    - 📱 Social Feed with meal sharing
    - ⏰ Intermittent Fasting tracker
    - 🏋️ Workout tracking
    - 📊 Calorie deficit calculator
    - 📝 Expert blog by doctors & dieticians
    """,
    version="3.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration - allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(user.router, prefix="/users", tags=["Users"])
app.include_router(health.router, prefix="/health", tags=["Health Tracking"])
app.include_router(athlete.router, prefix="/athlete", tags=["Athlete Metrics"])
app.include_router(social.router, prefix="/social", tags=["Social Feed"])
app.include_router(fasting.router, prefix="/fasting", tags=["Intermittent Fasting"])
app.include_router(workout.router, prefix="/workouts", tags=["Workouts"])
app.include_router(blog.router, prefix="/blog", tags=["Expert Blog"])
app.include_router(deficit.router, prefix="/deficit", tags=["Calorie Deficit"])
app.include_router(recipe.router, prefix="/recipes", tags=["Recipes"])


@app.get("/")
def root():
    """Health check endpoint."""
    return {
        "message": "WellNest API is running!",
        "version": "3.0",
        "features": [
            "AI Food Analysis",
            "Gamification",
            "Social Feed",
            "Intermittent Fasting",
            "Workout Tracking",
            "Calorie Deficit",
            "Expert Blog"
        ],
        "docs": "/docs"
    }


@app.get("/health-check")
def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "database": "connected",
        "version": "3.0"
    }
