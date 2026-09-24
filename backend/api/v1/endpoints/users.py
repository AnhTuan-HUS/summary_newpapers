from fastapi import APIRouter, Header, HTTPException, status
from passlib.context import CryptContext
from typing import Optional
from backend.schemas import UserLoginRequest, UserRegisterRequest
from backend.db_operations import get_user_by_email, create_user, update_last_login

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(data: UserRegisterRequest):
    """API Đăng ký tài khoản người dùng mới."""
    if get_user_by_email(data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email đã được sử dụng."
        )
    
    password_hash = pwd_context.hash(data.password)
    new_user = create_user(email=data.email, password_hash=password_hash, name=data.name)
    
    return {
        "message": "Đăng ký thành công!",
        "user": new_user
    }


@router.post("/login")
def login(data: UserLoginRequest):
    """API Đăng nhập hệ thống."""
    user = get_user_by_email(data.email)
    
    if not user or not pwd_context.verify(data.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email hoặc mật khẩu không chính xác."
        )
    
    update_last_login(user["id"])
    
    return {
        "message": "Đăng nhập thành công!",
        "user": {
            "id": user["id"],
            "email": user["email"],
            "name": user.get("name")
        }
    }


@router.post("/logout")
def logout(authorization: Optional[str] = Header(None)):
    """API Đăng xuất."""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Thiếu thông tin xác thực."
        )
    
    return {
        "message": "Đăng xuất thành công!"
    }