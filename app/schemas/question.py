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
    title: str = Field(..., description="질문 제목")
    content: str = Field(..., description="질문 내용")
    author_nickname: str = Field(..., description="작성자 닉네임")

    model_config = ConfigDict(from_attributes=True)


class QuestionListItem(BaseModel):
    id: int = Field(..., description="질문 ID")
    title: str = Field(..., description="질문 제목")
    author_nickname: str = Field(..., description="작성자 닉네임")

    model_config = ConfigDict(from_attributes=True)


class PaginationMeta(BaseModel):
    total: int = Field(..., description="전체 항목 수", examples=[100])
    page: int = Field(..., description="현재 페이지", examples=[1])
    size: int = Field(..., description="페이지당 항목 수", examples=[10])
    total_pages: int = Field(..., description="전체 페이지 수", examples=[10])


class QuestionListResponse(BaseModel):
    items: list[QuestionListItem] = Field(..., description="질문 목록")
    pagination: PaginationMeta = Field(..., description="페이지네이션 정보")
