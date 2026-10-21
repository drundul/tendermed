from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    decode_access_token,
)
from app.db.models import User
from app.models.schemas import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
    UserResponse,
)

router = APIRouter(prefix="/api/auth", tags=["auth"])
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """Dependency: извлекает текущего пользователя из JWT токена."""
    token = credentials.credentials
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительный или истекший токен авторизации",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    email = payload["sub"]
    user = db.query(User).filter(User.email == email).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден или заблокирован",
        )
    return user


DISPOSABLE_DOMAINS = {
    "temp-mail.org", "tempmail.com", "temp-mail.io", "guerrillamail.com",
    "10minutemail.com", "mailinator.com", "trashmail.com", "yopmail.com",
    "fakeinbox.com", "dispostable.com", "getairmail.com", "mohmal.com",
    "dropmail.me", "crazymailing.com", "throwawaymail.com", "sharklasers.com",
    "grr.la", "guerrillamail.biz", "guerrillamail.net", "guerrillamail.org",
}


@router.post("/register", response_model=TokenResponse)
def register(payload: UserRegisterRequest, db: Session = Depends(get_db)):
    """Регистрация нового пользователя с начислением 3 бесплатных аудитов."""
    clean_email = payload.email.lower().strip()

    # Защита от регистрации через временные почты (temp-mail)
    if "@" in clean_email:
        domain = clean_email.split("@")[1]
        if domain in DISPOSABLE_DOMAINS or any(kw in domain for kw in ["temp-mail", "tempmail", "throwaway", "dispostable", "fakeinbox"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Регистрация с временных почтовых сервисов (temp-mail) ограничена. Пожалуйста, укажите постоянную рабочую или личную почту (например, @mail.ru, @yandex.ru, @gmail.com или корпоративную).",
            )

    existing_user = db.query(User).filter(User.email == clean_email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже зарегистрирован",
        )

    if len(payload.password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пароль должен содержать не менее 6 символов",
        )

    hashed = get_password_hash(payload.password)
    user = User(
        email=payload.email.lower().strip(),
        hashed_password=hashed,
        company_name=payload.company_name.strip() if payload.company_name else None,
        available_credits=3,  # 3 бесплатных аудита при регистрации
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": user.email, "user_id": user.id})
    return TokenResponse(
        access_token=token,
        available_credits=user.available_credits,
        email=user.email,
    )


@router.post("/login", response_model=TokenResponse)
def login(payload: UserLoginRequest, db: Session = Depends(get_db)):
    """Вход пользователя по email и паролю."""
    user = db.query(User).filter(User.email == payload.email.lower().strip()).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Аккаунт заблокирован",
        )

    token = create_access_token({"sub": user.email, "user_id": user.id})
    return TokenResponse(
        access_token=token,
        available_credits=user.available_credits,
        email=user.email,
    )


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Получение информации о текущем пользователе и балансе проверок."""
    return current_user
