import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.answer import (
    create_answer,
    delete_answer,
    read_answer_by_id,
    read_answers_by_question_id,
    update_answer,
)
from app.crud.question import create_question, delete_question
from app.schemas.answer import AnswerCreate, AnswerUpdate
from app.schemas.question import QuestionCreate


@pytest.mark.asyncio
class TestAnswerCRUD:
    """답변 CRUD 테스트"""

    @pytest.fixture
    async def question_id(
        self,
        db_session: AsyncSession,
        sample_question_data: dict,
    ) -> int:
        """테스트용 질문 생성 fixture"""
        question_in = QuestionCreate(**sample_question_data)
        question = await create_question(db_session, question_in)
        return question.id

    async def test_create_answer(
        self,
        db_session: AsyncSession,
        question_id: int,
        sample_answer_data: dict,
    ):
        """답변 생성 테스트"""
        # Given
        answer_in = AnswerCreate(**sample_answer_data)

        # When
        answer = await create_answer(db_session, question_id, answer_in)

        # Then
        assert answer.id is not None
        assert answer.question_id == question_id
        assert answer.content == sample_answer_data["content"]
        assert answer.author_nickname == sample_answer_data["author_nickname"]
        print(f"\n✅ 답변 생성 성공: ID={answer.id}, question_id={question_id}")

    async def test_read_answer_by_id_success(
        self,
        db_session: AsyncSession,
        question_id: int,
        sample_answer_data: dict,
    ):
        """ID로 답변 조회 성공 테스트"""
        # Given: 답변 생성
        answer_in = AnswerCreate(**sample_answer_data)
        created_answer = await create_answer(db_session, question_id, answer_in)

        # When: 생성된 답변 조회
        answer = await read_answer_by_id(db_session, created_answer.id)

        # Then: 조회 결과 검증
        assert answer is not None
        assert answer.id == created_answer.id
        assert answer.question_id == question_id
        assert answer.content == sample_answer_data["content"]
        print(f"\n✅ 답변 조회 성공: ID={answer.id}")

    async def test_read_answer_by_id_not_found(self, db_session: AsyncSession):
        """존재하지 않는 답변 조회 테스트"""
        # When: 존재하지 않는 ID로 조회
        answer = await read_answer_by_id(db_session, 999999)

        # Then: None 반환
        assert answer is None
        print("\n✅ 존재하지 않는 답변 조회 시 None 반환 확인")

    async def test_read_answers_by_question_id(
        self,
        db_session: AsyncSession,
        question_id: int,
        sample_answer_data: dict,
    ):
        """특정 질문의 답변 목록 조회 테스트"""
        # Given: 같은 질문에 여러 답변 생성
        num_answers = 3
        for i in range(num_answers):
            data = sample_answer_data.copy()
            data["content"] = f"답변 내용 {i + 1}번입니다. 최소 10자 이상."
            answer_in = AnswerCreate(**data)
            await create_answer(db_session, question_id, answer_in)

        # When: 특정 질문의 답변 조회
        answers, total = await read_answers_by_question_id(db_session, question_id)

        # Then: 결과 검증
        assert total == num_answers
        assert len(answers) == num_answers
        assert all(a.question_id == question_id for a in answers)
        print(f"\n✅ 답변 목록 조회 성공: total={total}, returned={len(answers)}")

    async def test_read_answers_pagination(
        self,
        db_session: AsyncSession,
        question_id: int,
        sample_answer_data: dict,
    ):
        """답변 목록 페이지네이션 테스트"""
        # Given: 5개의 답변 생성
        num_answers = 5
        for i in range(num_answers):
            data = sample_answer_data.copy()
            data["content"] = f"답변 {i + 1}번 - 최소 10자 이상의 내용."
            answer_in = AnswerCreate(**data)
            await create_answer(db_session, question_id, answer_in)

        # When: skip=1, limit=2로 조회
        answers, total = await read_answers_by_question_id(
            db_session,
            question_id,
            skip=1,
            limit=2,
        )

        # Then: 페이지네이션 결과 검증
        assert total == num_answers
        assert len(answers) == 2
        print(f"\n✅ 답변 페이지네이션 성공: skip=1, limit=2, total={total}")

    async def test_read_answers_empty(
        self,
        db_session: AsyncSession,
        question_id: int,
    ):
        """답변이 없는 질문 조회 테스트"""
        # When: 답변이 없는 질문의 답변 조회
        answers, total = await read_answers_by_question_id(db_session, question_id)

        # Then: 빈 리스트와 total=0 반환
        assert answers == []
        assert total == 0
        print("\n✅ 빈 답변 목록 조회 확인")

    async def test_read_answers_different_questions(
        self,
        db_session: AsyncSession,
        sample_question_data: dict,
        sample_answer_data: dict,
    ):
        """서로 다른 질문의 답변이 섞이지 않는지 테스트"""
        # Given: 두 개의 다른 질문 생성
        question1_in = QuestionCreate(**sample_question_data)
        question1 = await create_question(db_session, question1_in)

        data2 = sample_question_data.copy()
        data2["title"] = "두 번째 질문입니다"
        question2_in = QuestionCreate(**data2)
        question2 = await create_question(db_session, question2_in)

        # 각 질문에 답변 추가
        answer1_in = AnswerCreate(**sample_answer_data)
        await create_answer(db_session, question1.id, answer1_in)

        answer2_data = sample_answer_data.copy()
        answer2_data["content"] = "두 번째 질문에 대한 답변입니다. 최소 10자."
        answer2_in = AnswerCreate(**answer2_data)
        await create_answer(db_session, question2.id, answer2_in)

        # When: 각 질문의 답변 조회
        answers1, total1 = await read_answers_by_question_id(db_session, question1.id)
        answers2, total2 = await read_answers_by_question_id(db_session, question2.id)

        # Then: 각 질문은 자신의 답변만 가져옴
        assert total1 == 1
        assert total2 == 1
        assert answers1[0].question_id == question1.id
        assert answers2[0].question_id == question2.id
        print("\n✅ 질문별 답변 격리 확인")

    async def test_update_answer_success(
        self,
        db_session: AsyncSession,
        question_id: int,
        sample_answer_data: dict,
    ):
        """답변 수정 성공 테스트"""
        # Given: 답변 생성
        answer_in = AnswerCreate(**sample_answer_data)
        created_answer = await create_answer(db_session, question_id, answer_in)
        original_author = created_answer.author_nickname

        # When: 답변 내용 수정
        update_data = AnswerUpdate(content="수정된 답변 내용입니다. 최소 10자 이상.")
        updated_answer = await update_answer(
            db_session,
            created_answer.id,
            update_data,
        )

        # Then: 수정 결과 검증
        assert updated_answer is not None
        assert updated_answer.id == created_answer.id
        assert updated_answer.content == "수정된 답변 내용입니다. 최소 10자 이상."
        assert updated_answer.question_id == question_id
        assert updated_answer.author_nickname == original_author
        print(f"\n✅ 답변 수정 성공: ID={updated_answer.id}")

    async def test_update_answer_not_found(self, db_session: AsyncSession):
        """존재하지 않는 답변 수정 테스트"""
        # When: 존재하지 않는 답변 수정 시도
        update_data = AnswerUpdate(content="수정 시도 - 최소 10자 이상입니다.")
        updated_answer = await update_answer(db_session, 999999, update_data)

        # Then: None 반환
        assert updated_answer is None
        print("\n✅ 존재하지 않는 답변 수정 시 None 반환 확인")

    async def test_delete_answer_success(
        self,
        db_session: AsyncSession,
        question_id: int,
        sample_answer_data: dict,
    ):
        """답변 삭제 성공 테스트"""
        # Given: 답변 생성
        answer_in = AnswerCreate(**sample_answer_data)
        created_answer = await create_answer(db_session, question_id, answer_in)
        answer_id = created_answer.id

        # When: 답변 삭제
        result = await delete_answer(db_session, answer_id)

        # Then: 삭제 성공 및 조회 불가 확인
        assert result is True
        deleted_answer = await read_answer_by_id(db_session, answer_id)
        assert deleted_answer is None
        print(f"\n✅ 답변 삭제 성공: ID={answer_id}")

    async def test_delete_answer_not_found(self, db_session: AsyncSession):
        """존재하지 않는 답변 삭제 테스트"""
        # When: 존재하지 않는 답변 삭제 시도
        result = await delete_answer(db_session, 999999)

        # Then: False 반환
        assert result is False
        print("\n✅ 존재하지 않는 답변 삭제 시 False 반환 확인")

    async def test_cascade_delete_on_question_deletion(
        self,
        db_session: AsyncSession,
        sample_question_data: dict,
        sample_answer_data: dict,
    ):
        """질문 삭제 시 답변도 함께 삭제되는지 테스트 (CASCADE)"""
        # Given: 질문과 답변 생성
        question_in = QuestionCreate(**sample_question_data)
        question = await create_question(db_session, question_in)

        answer_in = AnswerCreate(**sample_answer_data)
        answer = await create_answer(db_session, question.id, answer_in)
        answer_id = answer.id

        # When: 질문 삭제
        await delete_question(db_session, question.id)

        # Then: 답변도 함께 삭제됨
        deleted_answer = await read_answer_by_id(db_session, answer_id)
        assert deleted_answer is None
        print("\n✅ CASCADE 삭제 확인: 질문 삭제 시 답변도 삭제됨")

    async def test_multiple_answers_for_same_question(
        self,
        db_session: AsyncSession,
        question_id: int,
        sample_answer_data: dict,
    ):
        """하나의 질문에 여러 답변을 달 수 있는지 테스트"""
        # Given & When: 같은 질문에 3개의 답변 생성
        answer_ids = []
        for i in range(3):
            data = sample_answer_data.copy()
            data["content"] = f"답변 {i + 1}번입니다. 최소 10자 이상."
            data["author_nickname"] = f"답변자{i + 1}"
            answer_in = AnswerCreate(**data)
            answer = await create_answer(db_session, question_id, answer_in)
            answer_ids.append(answer.id)

        # Then: 모든 답변이 성공적으로 생성되고 조회 가능
        answers, total = await read_answers_by_question_id(db_session, question_id)
        assert total == 3
        assert len(answers) == 3

        # 모든 답변이 같은 질문에 속함
        assert all(answer.question_id == question_id for answer in answers)

        # 모든 답변이 고유한 ID를 가짐
        assert len(answer_ids) == len(set(answer_ids))
        print(f"\n✅ 하나의 질문에 여러 답변 생성 성공: {len(answer_ids)}개")

    async def test_read_answers_with_skip_and_limit(
        self,
        db_session: AsyncSession,
        question_id: int,
        sample_answer_data: dict,
    ):
        """skip과 limit을 사용한 페이지네이션 상세 테스트"""
        # Given: 10개의 답변 생성
        for i in range(10):
            data = sample_answer_data.copy()
            data["content"] = f"페이지네이션 테스트 답변 {i + 1}번 내용."
            answer_in = AnswerCreate(**data)
            await create_answer(db_session, question_id, answer_in)

        # When & Then: 다양한 페이지네이션 조건 테스트
        # 첫 페이지 (0-2)
        page1, total = await read_answers_by_question_id(db_session, question_id, skip=0, limit=3)
        assert len(page1) == 3
        assert total == 10

        # 두 번째 페이지 (3-5)
        page2, total = await read_answers_by_question_id(db_session, question_id, skip=3, limit=3)
        assert len(page2) == 3
        assert total == 10

        # 마지막 페이지 (9)
        page_last, total = await read_answers_by_question_id(
            db_session, question_id, skip=9, limit=3
        )
        assert len(page_last) == 1
        assert total == 10

        print("\n✅ 답변 페이지네이션 상세 테스트 성공")
