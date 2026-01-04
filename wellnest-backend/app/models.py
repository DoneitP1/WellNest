from sqlalchemy import Column, String, Float, ForeignKey, Integer, DateTime
from sqlalchemy.orm import relationship
from app.db import Base
import datetime
import uuid

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    profile = relationship("Profile", back_populates="user", uselist=False)
    weight_logs = relationship("WeightLog", back_populates="user")
    food_logs = relationship("FoodLog", back_populates="user")

class Profile(Base):
    __tablename__ = "profiles"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    height = Column(Float, nullable=True)
    weight = Column(Float, nullable=True)
    user = relationship("User", back_populates="profile")

class WeightLog(Base):
    __tablename__ = "weight_logs"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    weight = Column(Float, nullable=False)
    date = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="weight_logs")

class FoodLog(Base):
    __tablename__ = "food_logs"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    food_name = Column(String, nullable=False)
    calories = Column(Integer, nullable=False)
    protein = Column(Float, nullable=True)
    carbs = Column(Float, nullable=True)
    fat = Column(Float, nullable=True)
    meal_type = Column(String, nullable=True)
    date = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="food_logs")