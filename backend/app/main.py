"""
Test-Navi FastAPI 애플리케이션 진입점

시각 장애인 및 저시력 사용자를 위한
AI 음성 기반 브라우저 및 Windows 자동화 어시스턴트 백엔드 서버
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.config import settings
from app.api.v1 import router as api_v1_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 생명주기 관리"""
    # === Startup ===
    logger.info(f"🚀 {settings.app_name} v{settings.app_version} 시작")
    logger.info(f"🔧 디버그 모드: {settings.debug}")
    logger.info(f"🎙️ STT 프로바이더: {settings.stt_provider}")
    logger.info(f"🤖 LLM 프로바이더: {settings.llm_provider}")
    logger.info(f"🔊 TTS 프로바이더: {settings.tts_provider}")

    yield

    # === Shutdown ===
    logger.info(f"🛑 {settings.app_name} 종료")


def create_app() -> FastAPI:
    """FastAPI 애플리케이션 팩토리"""
    app = FastAPI(
        title=settings.app_name,
        description=(
            "시각 장애인 및 저시력 사용자를 위한 "
            "AI 음성 기반 브라우저 및 Windows 자동화 어시스턴트"
        ),
        version=settings.app_version,
        lifespan=lifespan,
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
    )

    # --- CORS 미들웨어 ---
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # --- API 라우터 등록 ---
    app.include_router(api_v1_router, prefix="/api/v1")

    return app


app = create_app()


@app.get("/health", tags=["Health"])
async def health_check():
    """서버 상태 확인 엔드포인트"""
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version,
    }
