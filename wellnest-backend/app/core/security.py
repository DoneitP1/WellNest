import bcrypt
import passlib.handlers.bcrypt

# Monkey patch for passlib 1.7.4 compatibility with bcrypt 4.0.0+
# This fixes "AttributeError: module 'bcrypt' has no attribute '__about__'"
if not hasattr(bcrypt, "__about__"):
    try:
        class About:
            pass
        bcrypt.__about__ = About()
        bcrypt.__about__.__version__ = bcrypt.__version__
        
        # Patch bcrypt.hashpw to handle the "ValueError: password cannot be longer..." issue
        # by explicitly truncating the password to 72 bytes, which is the standard BCrypt limit.
        # Passlib expects this behavior or a wrap bug, but bcrypt 4.0+ raises an error instead.
        _original_hashpw = bcrypt.hashpw
        def patched_hashpw(password, salt):
            try:
                return _original_hashpw(password, salt)
            except ValueError:
                # If password is too long, we simulate the standard bcrypt behavior by truncating
                if len(password) > 72:
                    return _original_hashpw(password[:72], salt)
                raise
        bcrypt.hashpw = patched_hashpw
    except Exception:
        pass

from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)