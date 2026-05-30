from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.deps import get_db, get_current_user, require_roles
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.schemas.user import UserRead, UserCreate, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=List[UserRead])
async def list_users(
    role: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER, UserRole.DISPATCHER)),
):
    q = select(User)
    if role:
        q = q.where(User.role == role)
    if is_active is not None:
        q = q.where(User.is_active == is_active)
    result = await db.execute(q.order_by(User.full_name))
    return result.scalars().all()


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(
    data: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
):
    existing = await db.execute(select(User).where(User.email == data.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        employee_number=data.employee_number,
        full_name=data.full_name,
        email=data.email,
        role=data.role,
        department=data.department,
        phone=data.phone,
        is_active=data.is_active,
        password_hash=get_password_hash(data.password),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@router.get("/{user_id}", response_model=UserRead)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.id != user_id and current_user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
        raise HTTPException(status_code=403, detail="Not authorized")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: int,
    data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        if field == "password":
            user.password_hash = get_password_hash(value)
        else:
            setattr(user, field, value)
    await db.commit()
    await db.refresh(user)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await db.delete(user)
    await db.commit()
