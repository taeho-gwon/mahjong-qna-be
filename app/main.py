# app/main.py (업데이트)
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.db.database import test_connection


# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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

    # 모든 모델을 import해서 메타데이터에 등록되도록 함
    import app.models.user  # noqa: F401

    # 데이터베이스 연결 테스트
    if await test_connection():
        logger.info("데이터베이스 연결 성공!")
    else:
        logger.error("데이터베이스 연결 실패!")

    yield

    # 종료 시 실행
    logger.info("애플리케이션 종료...")


app = FastAPI(
    title="MahjongQnA API",
    description="Mahjong Questions & Answers Community Backend API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
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
            "message": "Welcome to MahjongQnA API! 🀄️",
            "description": "Mahjong Questions & Answers Community",
            "version": "1.0.0",
            "docs": "/docs",
            "redoc": "/redoc",
        }
    )
