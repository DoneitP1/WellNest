from app.db import SessionLocal
from app.crud import create_user
from app.schemas import UserCreate
import traceback

def debug_registration():
    db = SessionLocal()
    try:
        user_in = UserCreate(email="debug_script@example.com", password="password123")
        print("Attempting to create user...")
        # Note: create_user takes (db, email, password) strings, not schema, based on auth.py usage
        # let's verify signature in crud.py first.
        # auth.py: create_user(db, user.email, user.password)
        user = create_user(db, user_in.email, user_in.password)
        print(f"User created: {user.email}")
    except Exception as e:
        print("CRASH DETECTED:")
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    debug_registration()
