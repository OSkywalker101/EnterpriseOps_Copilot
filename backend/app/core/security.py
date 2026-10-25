from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_PREFIX}/auth/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None


# Import models inside function to avoid circular imports
def get_user_model():
    from app.models.user import User
    return User


async def get_current_user(
    token: str = Depends(oauth2_scheme),
) -> "User":
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_token(token)
    if payload is None or payload.get("type") != "access":
        raise credentials_exception
    user_id: int = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    # Import here to avoid circular import
    from app.db.base import get_db
    from app.models.user import Role
    User = get_user_model()
    
    async for db_session in get_db():
        result = await db_session.execute(select(User).where(User.id == user_id, User.is_active == True))
        user = result.scalar_one_or_none()
        break
    
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: "User" = Depends(get_current_user)) -> "User":
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def require_role(*allowed_roles: "Role"):
    async def role_checker(current_user: "User" = Depends(get_current_active_user)) -> "User":
        from app.models.user import Role
        if current_user.role not in allowed_roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user
    return role_checker


def require_permission(permission: str):
    async def permission_checker(current_user: "User" = Depends(get_current_active_user)) -> "User":
        from app.models.user import Role
        role_permissions = {
            Role.EMPLOYEE: ["read:own_data", "read:catalog"],
            Role.PROCUREMENT_SPECIALIST: ["read:procurement", "read:suppliers", "write:procurement", "read:catalog"],
            Role.INVENTORY_MANAGER: ["read:inventory", "write:inventory", "read:catalog"],
            Role.APPROVER: ["read:approvals", "write:approvals", "read:procurement"],
            Role.ADMINISTRATOR: ["*"],
        }
        permissions = role_permissions.get(current_user.role, [])
        if "*" not in permissions and permission not in permissions:
            raise HTTPException(status_code=403, detail=f"Permission required: {permission}")
        return current_user
    return permission_checker