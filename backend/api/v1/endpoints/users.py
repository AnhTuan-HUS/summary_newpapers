from fastapi import APIRouter, HTTPException, status
from jose import jwt
from passlib.context import CryptContext

from backend.schemas import UserLoginRequest, UserRegisterRequest
from backend.db_operations import (
    create_user,
    get_user_by_email,
    update_last_login,
)


router = APIRouter(prefix="/auth", tags=["Authentication"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# JWT configuration
SECRET_KEY = "your-secret-key-change-this"
ALGORITHM = "HS256"


def create_access_token(user_id: int) -> str:
    """Tạo JWT access token cho người dùng."""
    payload = {
        "sub": str(user_id),
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(data: UserRegisterRequest):
    """API Đăng ký tài khoản người dùng mới."""

    if get_user_by_email(data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email đã được sử dụng.",
        )

    password_hash = pwd_context.hash(data.password)

    new_user = create_user(
        email=data.email,
        password_hash=password_hash,
        name=data.name,
    )

    return {
        "message": "Đăng ký thành công!",
        "user": new_user,
    }


@router.post("/login")
def login(data: UserLoginRequest):
    """API Đăng nhập hệ thống."""

    user = get_user_by_email(data.email)

    if not user or not pwd_context.verify(
        data.password,
        user["password_hash"],
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email hoặc mật khẩu không chính xác.",
        )

    update_last_login(user["id"])

    access_token = create_access_token(user["id"])

    return {
        "message": "Đăng nhập thành công!",
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "email": user["email"],
            "name": user.get("name"),
        },
    }