from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: EmailStr

    class Config:
        orm_mode = True

class ProfileCreate(BaseModel):
    height: Optional[float]
    weight: Optional[float]

class ProfileResponse(ProfileCreate):
    id: str

class WeightLogCreate(BaseModel):
    weight: float
    date: Optional[datetime] = None

class WeightLogResponse(BaseModel):
    id: str
    weight: float
    date: datetime
    
    class Config:
        orm_mode = True

class FoodLogCreate(BaseModel):
    food_name: str
    calories: int
    protein: Optional[float] = 0.0
    carbs: Optional[float] = 0.0
    fat: Optional[float] = 0.0
    meal_type: Optional[str] = "snack"
    date: Optional[datetime] = None

class FoodLogResponse(BaseModel):
    id: str
    food_name: str
    calories: int
    protein: float
    carbs: float
    fat: float
    meal_type: Optional[str]
    date: datetime

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str