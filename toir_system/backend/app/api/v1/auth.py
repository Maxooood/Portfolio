from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.deps import get_db, get_current_user
from app.core.security import verify_password, create_access_token
from app.models.user import User
from app.schemas.user import Token, LoginRequest, UserRead

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=Token)
async def login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is inactive")

    user.last_login = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(user)

    token = create_access_token(subject=user.id)
    return Token(access_token=token, user=UserRead.model_validate(user))


@router.get("/me", response_model=UserRead)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user
