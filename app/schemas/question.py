from pydantic import BaseModel, ConfigDict, Field


class QuestionCreate(BaseModel):
    title: str = Field(
        ...,
        min_length=5,
        max_length=200,
        description="질문 제목",
        examples=["마작 초보 질문입니다"],
    )
    content: str = Field(
        ...,
        min_length=10,
        description="질문 내용",
        examples=["마작은 어떻게 잘 치나요?"],
    )
    author_nickname: str = Field(
        ...,
        min_length=2,
        max_length=50,
        description="작성자 닉네임",
        examples=["햄버거"],
    )


class QuestionResponse(BaseModel):
    id: int = Field(..., description="질문 ID")
    model_config = ConfigDict(from_attributes=True)
