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


# Белый список доверенных почтовых сервисов РФ и международных провайдеров
TRUSTED_EMAIL_DOMAINS = {
    # Яндекс
    "yandex.ru", "ya.ru", "yandex.com", "yandex.by", "yandex.kz",
    # VK / Mail.ru Group
    "mail.ru", "bk.ru", "inbox.ru", "list.ru", "internet.ru", "vk.com",
    # Google
    "gmail.com", "googlemail.com",
    # Rambler Group
    "rambler.ru", "lenta.ru", "autorambler.ru", "myrambler.ru", "ro.ru",
    # Microsoft
    "outlook.com", "hotmail.com", "live.com", "msn.com",
    # Apple
    "icloud.com", "me.com", "mac.com",
    # Yahoo / Proton
    "yahoo.com", "proton.me", "protonmail.com",
    # Тестовые домены для разработки
    "test.com", "example.com",
}

DISPOSABLE_KEYWORDS = [
    "temp", "dispos", "throwaway", "fake", "trash", "drop", "shark", "guerrilla",
    "mailinator", "10minute", "mohmal", "crazymail", "grr", "vebux", "fextbox",
    "disbox", "inboxkitten", "burner", "anon", "nowmymail", "generator"
]


def is_allowed_email(email: str) -> bool:
    """
    Проверяет email на соответствие политике безопасности:
    1. Известные почтовые сервисы (Яндекс, Mail.ru, Gmail, Rambler, Outlook, iCloud и др.)
    2. Надежные национальные корпоративные домены (.ru, .рф, .su), если они не содержат признаков одноразовых почт
    3. Случайные noname международные домены (.com, .org, .net, .io, .site, etc.), не входящие в белый список, блокируются.
    """
    if "@" not in email:
        return False
    parts = email.split("@")
    if len(parts) != 2:
        return False
    domain = parts[1].lower().strip()

    if any(kw in domain for kw in DISPOSABLE_KEYWORDS):
        return False

    # 1. Если домен в прямом белом списке известных сервисов
    if domain in TRUSTED_EMAIL_DOMAINS:
        return True

    # 2. Если домен в национальной зоне РФ (.ru, .рф, .su) и имеет формат корпоративного сайта
    if domain.endswith((".ru", ".рф", ".su")):
        domain_name = domain.rsplit(".", 1)[0]
        if len(domain_name) >= 3 and not any(kw in domain_name for kw in DISPOSABLE_KEYWORDS):
            return True

    return False


@router.post("/register", response_model=TokenResponse)
def register(payload: UserRegisterRequest, db: Session = Depends(get_db)):
    """Регистрация нового пользователя с начислением 3 бесплатных аудитов."""
    clean_email = payload.email.lower().strip()

    # Защита от регистрации через временные и одноразовые почты (temp-mail и noname домены)
    if not is_allowed_email(clean_email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Регистрация разрешена только с официальных почтовых сервисов "
                "(Яндекс, Mail.ru, Gmail, Rambler, Outlook, VK, iCloud) или корпоративных почт российских компаний (.ru / .рф). "
                "Использование временных и анонимных почтовых ящиков ограничено для защиты сервиса."
            ),
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
