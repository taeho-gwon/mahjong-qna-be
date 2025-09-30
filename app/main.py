import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.answer import router as answer_router
from app.api.question import router as question_router
from app.db.database import test_connection


# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    logger.info("애플리케이션 시작...")

    # 모든 모델을 import해서 메타데이터에 등록되도록 함
    from app.models.answer import Answer  # noqa: F401
    from app.models.question import Question  # noqa: F401

    if await test_connection():
        logger.info("데이터베이스 연결 성공!")
    else:
        logger.error("데이터베이스 연결 실패!")

    yield

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

app.include_router(question_router)

app.include_router(answer_router)


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
