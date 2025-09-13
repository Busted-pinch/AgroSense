import os
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv
from app.db.database import SessionLocal, User
from app.utils.logger import logger

# Load .env file
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "default_secret")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed: str) -> bool:
    return pwd_context.verify(plain_password, hashed)

def create_user(email: str, password: str):
    db = SessionLocal()
    try:
        if db.query(User).filter(User.email == email).first():
            logger.warning("Attempt to re-register email: %s", email)
            raise ValueError("Email already registered")

        user = User(email=email, password=hash_password(password))
        db.add(user)
        db.commit()
        db.refresh(user)

        logger.info("Created user id=%s email=%s", user.id, email)

    except Exception as e:
        logger.exception("Error creating user %s: %s", email, e)
        raise
    finally:
        db.close()


def authenticate_user(email: str, password: str):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user or not verify_password(password, user.password):
            return False
        return True
    finally:
        db.close()

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
