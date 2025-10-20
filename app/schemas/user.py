from pydantic import BaseModel, ConfigDict, Field


class UserBase(BaseModel):
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="사용자 아이디",
        examples=["johndoe"],
    )
    password: str = Field(
        ...,
        min_length=4,
        description="비밀번호",
        examples=["mypassword123"],
    )


class UserResponse(BaseModel):
    id: int = Field(..., description="사용자 ID")
    username: str = Field(..., description="사용자 아이디")

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str = Field(..., description="JWT 액세스 토큰")
    token_type: str = Field(default="bearer", description="토큰 타입")


UserSignup = UserBase
UserLogin = UserBase
