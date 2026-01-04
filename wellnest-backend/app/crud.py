from sqlalchemy.orm import Session
from app.models import User
from app.core.security import get_password_hash

def create_user(db: Session, email: str, password: str):
    hashed_password = get_password_hash(password)
    db_user = User(email=email, password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()