"""
API v1 라우터 패키지

모든 v1 API 엔드포인트를 통합합니다.
"""

from fastapi import APIRouter

from app.api.v1.stt import router as stt_router
from app.api.v1.agent import router as agent_router
from app.api.v1.tts import router as tts_router
from app.api.v1.automation import router as automation_router
from app.api.v1.settings import router as settings_router

router = APIRouter()

router.include_router(stt_router, prefix="/stt", tags=["STT"])
router.include_router(agent_router, prefix="/agent", tags=["Agent"])
router.include_router(tts_router, prefix="/tts", tags=["TTS"])
router.include_router(automation_router, prefix="/automation", tags=["Automation"])
router.include_router(settings_router, prefix="/settings", tags=["Settings"])
