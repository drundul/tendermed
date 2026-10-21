import os
from datetime import datetime, timedelta, timezone
from typing import Optional
import bcrypt
import jwt

SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "tendermed-super-secure-production-secret-key-2026")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 дней


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет соответствие пароля хэшу."""
    pwd_bytes = plain_password.encode("utf-8")[:72]
    return bcrypt.checkpw(pwd_bytes, hashed_password.encode("utf-8"))


def get_password_hash(password: str) -> str:
    """Генерирует bcrypt хэш пароля."""
    pwd_bytes = password.encode("utf-8")[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Создает JWT-токен авторизации."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """Декодирует и проверяет JWT-токен."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None
