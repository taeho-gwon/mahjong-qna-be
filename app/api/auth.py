from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.core.auth import create_access_token, verify_password
from app.crud.user import create_user, get_user_by_username
from app.db.database import get_session
from app.models.user import User
from app.schemas.user import Token, UserLogin, UserResponse, UserSignup


router = APIRouter(prefix="/auth", tags=["인증"])


@router.post(
    "/signup",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="회원가입",
    description="새로운 사용자를 등록합니다.",
)
async def signup(
    user_in: UserSignup,
    db: AsyncSession = Depends(get_session),
) -> UserResponse:
    existing_user = await get_user_by_username(db, user_in.username)

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 존재하는 아이디입니다",
        )

    user = await create_user(db, user_in)
    await db.commit()

    return UserResponse.model_validate(user)


@router.post(
    "/login",
    response_model=Token,
    status_code=status.HTTP_200_OK,
    summary="로그인",
    description="아이디와 비밀번호로 로그인하여 JWT 토큰을 발급받습니다.",
)
async def login(
    user_in: UserLogin,
    db: AsyncSession = Depends(get_session),
) -> Token:
    user = await get_user_by_username(db, user_in.username)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="아이디 또는 비밀번호가 잘못되었습니다",
        )

    if not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="아이디 또는 비밀번호가 잘못되었습니다",
        )

    access_token = create_access_token(data={"sub": user.id})

    return Token(access_token=access_token, token_type="bearer")


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="내 정보 조회",
    description="현재 로그인한 사용자의 정보를 조회합니다.",
)
async def get_me(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    return UserResponse.model_validate(current_user)
