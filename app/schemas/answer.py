from pydantic import BaseModel, ConfigDict, Field

from app.schemas.user import AuthorInfo


class AnswerCreate(BaseModel):
    content: str = Field(
        ...,
        min_length=10,
        description="답변 내용",
        examples=["마작은 4명이 하는 게임입니다. 기본 규칙은..."],
    )


class AnswerUpdate(BaseModel):
    content: str | None = Field(
        None,
        min_length=10,
        description="답변 내용",
        examples=["수정된 답변 내용입니다."],
    )


class AnswerResponse(BaseModel):
    id: int = Field(..., description="답변 ID")
    question_id: int = Field(..., description="질문 ID")
    content: str = Field(..., description="답변 내용")
    author: AuthorInfo = Field(..., description="작성자 정보")

    model_config = ConfigDict(from_attributes=True)


class AnswerListItem(BaseModel):
    id: int = Field(..., description="답변 ID")
    content: str = Field(..., description="답변 내용")
    author: AuthorInfo = Field(..., description="작성자 정보")

    model_config = ConfigDict(from_attributes=True)
