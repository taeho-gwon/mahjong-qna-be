import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.question import (
    create_question,
    delete_question,
    read_question_by_id,
    read_questions,
    update_question,
)
from app.schemas.question import QuestionCreate, QuestionUpdate


@pytest.mark.asyncio
class TestQuestionCRUD:
    """질문 CRUD 테스트"""

    async def test_create_question(
        self,
        db_session: AsyncSession,
        sample_question_data: dict,
    ):
        """질문 생성 테스트"""
        # Given
        question_in = QuestionCreate(**sample_question_data)

        # When
        question = await create_question(db_session, question_in)

        # Then
        assert question.id is not None
        assert question.title == sample_question_data["title"]
        assert question.content == sample_question_data["content"]
        assert question.author_nickname == sample_question_data["author_nickname"]
        print(f"\n✅ 질문 생성 성공: ID={question.id}")

    async def test_read_question_by_id_success(
        self,
        db_session: AsyncSession,
        sample_question_data: dict,
    ):
        """ID로 질문 조회 성공 테스트"""
        # Given: 질문 생성
        question_in = QuestionCreate(**sample_question_data)
        created_question = await create_question(db_session, question_in)

        # When: 생성된 질문 조회
        question = await read_question_by_id(db_session, created_question.id)

        # Then: 조회 결과 검증
        assert question is not None
        assert question.id == created_question.id
        assert question.title == sample_question_data["title"]
        assert question.content == sample_question_data["content"]
        print(f"\n✅ 질문 조회 성공: ID={question.id}")

    async def test_read_question_by_id_not_found(self, db_session: AsyncSession):
        """존재하지 않는 질문 조회 테스트"""
        # When: 존재하지 않는 ID로 조회
        question = await read_question_by_id(db_session, 999999)

        # Then: None 반환
        assert question is None
        print("\n✅ 존재하지 않는 질문 조회 시 None 반환 확인")

    async def test_read_questions_pagination(
        self,
        db_session: AsyncSession,
        sample_question_data: dict,
    ):
        """질문 목록 조회 및 페이지네이션 테스트"""
        # Given: 여러 개의 질문 생성
        num_questions = 5
        for i in range(num_questions):
            data = sample_question_data.copy()
            data["title"] = f"테스트 질문 {i + 1}번"
            question_in = QuestionCreate(**data)
            await create_question(db_session, question_in)

        # When: 페이지네이션으로 조회 (skip=1, limit=2)
        questions, total = await read_questions(db_session, skip=1, limit=2)

        # Then: 결과 검증
        assert total == num_questions
        assert len(questions) == 2
        print(f"\n✅ 질문 목록 조회 성공: total={total}, returned={len(questions)}")

    async def test_read_questions_empty(self, db_session: AsyncSession):
        """빈 질문 목록 조회 테스트"""
        # When: 질문이 없는 상태에서 조회
        questions, total = await read_questions(db_session)

        # Then: 빈 리스트와 total=0 반환
        assert questions == []
        assert total == 0
        print("\n✅ 빈 질문 목록 조회 확인")

    async def test_read_questions_default_limit(
        self,
        db_session: AsyncSession,
        sample_question_data: dict,
    ):
        """질문 목록 조회 기본 limit 테스트"""
        # Given: 15개의 질문 생성
        num_questions = 15
        for i in range(num_questions):
            data = sample_question_data.copy()
            data["title"] = f"테스트 질문 {i + 1}번"
            question_in = QuestionCreate(**data)
            await create_question(db_session, question_in)

        # When: limit을 지정하지 않고 조회 (기본값 10)
        questions, total = await read_questions(db_session)

        # Then: 전체 15개 중 10개만 반환
        assert total == num_questions
        assert len(questions) == 10
        print(f"\n✅ 기본 limit 동작 확인: total={total}, returned={len(questions)}")

    async def test_update_question_full(
        self,
        db_session: AsyncSession,
        sample_question_data: dict,
    ):
        """질문 전체 수정 테스트"""
        # Given: 질문 생성
        question_in = QuestionCreate(**sample_question_data)
        created_question = await create_question(db_session, question_in)

        # When: 질문 수정 (제목, 내용 모두 수정)
        update_data = QuestionUpdate(
            title="수정된 제목입니다",
            content="수정된 내용입니다. 최소 10자 이상이어야 합니다.",
        )
        updated_question = await update_question(
            db_session,
            created_question.id,
            update_data,
        )

        # Then: 수정 결과 검증
        assert updated_question is not None
        assert updated_question.id == created_question.id
        assert updated_question.title == "수정된 제목입니다"
        assert updated_question.content == "수정된 내용입니다. 최소 10자 이상이어야 합니다."
        assert updated_question.author_nickname == sample_question_data["author_nickname"]
        print(f"\n✅ 질문 전체 수정 성공: ID={updated_question.id}")

    async def test_update_question_partial_title(
        self,
        db_session: AsyncSession,
        sample_question_data: dict,
    ):
        """질문 부분 수정 테스트 (제목만)"""
        # Given: 질문 생성
        question_in = QuestionCreate(**sample_question_data)
        created_question = await create_question(db_session, question_in)
        original_content = created_question.content

        # When: 제목만 수정
        update_data = QuestionUpdate(title="제목만 수정했습니다")
        updated_question = await update_question(
            db_session,
            created_question.id,
            update_data,
        )

        # Then: 제목만 변경되고 내용은 유지
        assert updated_question is not None
        assert updated_question.title == "제목만 수정했습니다"
        assert updated_question.content == original_content
        print("\n✅ 질문 부분 수정 성공 (제목만 변경)")

    async def test_update_question_partial_content(
        self,
        db_session: AsyncSession,
        sample_question_data: dict,
    ):
        """질문 부분 수정 테스트 (내용만)"""
        # Given: 질문 생성
        question_in = QuestionCreate(**sample_question_data)
        created_question = await create_question(db_session, question_in)
        original_title = created_question.title

        # When: 내용만 수정
        update_data = QuestionUpdate(content="내용만 수정했습니다. 최소 10자 이상.")
        updated_question = await update_question(
            db_session,
            created_question.id,
            update_data,
        )

        # Then: 내용만 변경되고 제목은 유지
        assert updated_question is not None
        assert updated_question.title == original_title
        assert updated_question.content == "내용만 수정했습니다. 최소 10자 이상."
        print("\n✅ 질문 부분 수정 성공 (내용만 변경)")

    async def test_update_question_not_found(self, db_session: AsyncSession):
        """존재하지 않는 질문 수정 테스트"""
        # When: 존재하지 않는 질문 수정 시도
        update_data = QuestionUpdate(title="수정 시도")
        updated_question = await update_question(db_session, 999999, update_data)

        # Then: None 반환
        assert updated_question is None
        print("\n✅ 존재하지 않는 질문 수정 시 None 반환 확인")

    async def test_delete_question_success(
        self,
        db_session: AsyncSession,
        sample_question_data: dict,
    ):
        """질문 삭제 성공 테스트"""
        # Given: 질문 생성
        question_in = QuestionCreate(**sample_question_data)
        created_question = await create_question(db_session, question_in)
        question_id = created_question.id

        # When: 질문 삭제
        result = await delete_question(db_session, question_id)

        # Then: 삭제 성공 및 조회 불가 확인
        assert result is True
        deleted_question = await read_question_by_id(db_session, question_id)
        assert deleted_question is None
        print(f"\n✅ 질문 삭제 성공: ID={question_id}")

    async def test_delete_question_not_found(self, db_session: AsyncSession):
        """존재하지 않는 질문 삭제 테스트"""
        # When: 존재하지 않는 질문 삭제 시도
        result = await delete_question(db_session, 999999)

        # Then: False 반환
        assert result is False
        print("\n✅ 존재하지 않는 질문 삭제 시 False 반환 확인")

    async def test_create_multiple_questions(
        self,
        db_session: AsyncSession,
        sample_question_data: dict,
    ):
        """여러 질문 생성 테스트"""
        # Given & When: 3개의 질문 생성
        questions = []
        for i in range(3):
            data = sample_question_data.copy()
            data["title"] = f"테스트 질문 {i + 1}번"
            question_in = QuestionCreate(**data)
            question = await create_question(db_session, question_in)
            questions.append(question)

        # Then: 모든 질문이 고유한 ID를 가짐
        question_ids = [q.id for q in questions]
        assert len(question_ids) == len(set(question_ids))
        assert all(q.id is not None for q in questions)
        print(f"\n✅ 여러 질문 생성 성공: {len(questions)}개")

    async def test_read_questions_with_skip_and_limit(
        self,
        db_session: AsyncSession,
        sample_question_data: dict,
    ):
        """skip과 limit을 사용한 페이지네이션 상세 테스트"""
        # Given: 10개의 질문 생성
        for i in range(10):
            data = sample_question_data.copy()
            data["title"] = f"페이지네이션 테스트 질문 {i + 1}번"
            question_in = QuestionCreate(**data)
            await create_question(db_session, question_in)

        # When & Then: 다양한 페이지네이션 조건 테스트
        # 첫 페이지 (0-2)
        page1, total = await read_questions(db_session, skip=0, limit=3)
        assert len(page1) == 3
        assert total == 10

        # 두 번째 페이지 (3-5)
        page2, total = await read_questions(db_session, skip=3, limit=3)
        assert len(page2) == 3
        assert total == 10

        # 마지막 페이지 (9)
        page_last, total = await read_questions(db_session, skip=9, limit=3)
        assert len(page_last) == 1
        assert total == 10

        print("\n✅ 페이지네이션 상세 테스트 성공")
