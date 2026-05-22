from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.deps import get_current_user
from app.db.database import get_db
from app.db.models import User
from app.models.schemas import AuthToken, UserLogin, UserProfile, UserProfileUpdate, UserRegister
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=AuthToken)
async def register(data: UserRegister, db: AsyncSession = Depends(get_db)):
    return await auth_service.register_user(db, data)


@router.post("/login", response_model=AuthToken)
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    return await auth_service.login_user(db, data)


@router.get("/me", response_model=UserProfile)
async def me(user: User = Depends(get_current_user)):
    return auth_service.user_to_profile(user)


@router.patch("/me", response_model=UserProfile)
async def update_me(
    data: UserProfileUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await auth_service.update_profile(db, user, data)
