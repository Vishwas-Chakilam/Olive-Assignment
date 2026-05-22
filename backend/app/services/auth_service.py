import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.security import create_access_token, hash_password, verify_password
from app.db.models import User
from app.models.schemas import AuthToken, UserLogin, UserProfile, UserRegister, UserProfileUpdate


def user_to_profile(user: User) -> UserProfile:
    return UserProfile(
        id=user.id,
        email=user.email,
        username=user.username,
        display_name=user.display_name or user.username,
        bio=user.bio,
        avatar_url=user.avatar_url,
        theme=user.theme,
        default_provider=user.default_provider,
        default_model=user.default_model,
        created_at=user.created_at,
    )


async def register_user(db: AsyncSession, data: UserRegister) -> AuthToken:
    existing = await db.execute(
        select(User).where((User.email == data.email) | (User.username == data.username))
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email or username already taken")

    user = User(
        email=data.email.lower(),
        username=data.username.lower(),
        hashed_password=hash_password(data.password),
        display_name=data.display_name or data.username,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    token = create_access_token(str(user.id))
    return AuthToken(access_token=token, user=user_to_profile(user))


async def login_user(db: AsyncSession, data: UserLogin) -> AuthToken:
    result = await db.execute(select(User).where(User.email == data.email.lower()))
    user = result.scalar_one_or_none()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    token = create_access_token(str(user.id))
    return AuthToken(access_token=token, user=user_to_profile(user))


async def update_profile(db: AsyncSession, user: User, data: UserProfileUpdate) -> UserProfile:
    if data.display_name is not None:
        user.display_name = data.display_name
    if data.bio is not None:
        user.bio = data.bio
    if data.avatar_url is not None:
        user.avatar_url = data.avatar_url
    if data.theme is not None:
        user.theme = data.theme
    if data.default_provider is not None:
        user.default_provider = data.default_provider
    if data.default_model is not None:
        user.default_model = data.default_model
    await db.flush()
    await db.refresh(user)
    return user_to_profile(user)


async def get_user_by_id(db: AsyncSession, user_id: uuid.UUID) -> User | None:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()
