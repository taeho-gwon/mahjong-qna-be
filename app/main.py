import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.db.database import test_connection


# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# app/main.py의 lifespan 함수에 추가할 디버깅 코드


@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 라이프사이클 관리"""
    # 시작 시 실행
    logger.info("애플리케이션 시작...")

    # 설정 정보 출력 (디버깅용)
    from app.core.config import get_settings

    settings = get_settings()
    logger.info(
        f"데이터베이스 URL: {settings.database_url.replace(settings.postgres_password, '***')}"
    )
    logger.info(f"PostgreSQL 호스트: {settings.postgres_host}")
    logger.info(f"PostgreSQL 포트: {settings.postgres_port}")
    logger.info(f"PostgreSQL 데이터베이스: {settings.postgres_db}")
    logger.info(f"PostgreSQL 사용자: {settings.postgres_user}")

    # 모든 모델을 import해서 메타데이터에 등록되도록 함
    import app.models.event  # noqa: F401
    import app.models.task  # noqa: F401
    import app.models.user  # noqa: F401

    # 데이터베이스 연결 테스트
    if await test_connection():
        logger.info("데이터베이스 연결 성공!")
    else:
        logger.error("데이터베이스 연결 실패!")
        logger.error("PostgreSQL 컨테이너가 실행 중인지 확인하세요: docker-compose ps")
        logger.error("환경변수가 올바른지 확인하세요: .env 파일")

    yield

    # 종료 시 실행
    logger.info("애플리케이션 종료...")


app = FastAPI(
    title="Task Manager API",
    description="일정 관리 API 서버 (비동기)",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,  # 라이프사이클 설정
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return JSONResponse(
        content={
            "message": "Welcome to Task Manager API (Async)",
            "version": "1.0.0",
            "docs": "/docs",
            "redoc": "/redoc",
        }
    )
