"""
설정 (Settings) API 엔드포인트

애플리케이션 설정을 조회하고 변경하는 API를 제공합니다.
"""

from fastapi import APIRouter
from loguru import logger

from app.models.schemas import AppSettings, ErrorResponse

router = APIRouter()


@router.get(
    "",
    response_model=AppSettings,
    summary="설정 조회",
    description="현재 애플리케이션 설정을 조회합니다.",
)
async def get_settings():
    """현재 설정을 조회하는 엔드포인트"""
    logger.debug("설정 조회 요청")

    return AppSettings(
        stt_provider="openai",
        tts_provider="edge_tts",
        tts_voice="ko-KR-SunHiNeural",
        llm_provider="openai",
        llm_model="gpt-4o",
        browser_type="chromium",
        browser_headless=False,
    )


@router.put(
    "",
    response_model=AppSettings,
    responses={400: {"model": ErrorResponse}},
    summary="설정 변경",
    description="애플리케이션 설정을 변경합니다.",
)
async def update_settings(new_settings: AppSettings):
    """설정을 변경하는 엔드포인트"""
    logger.info(f"설정 변경 요청: {new_settings.model_dump()}")

    # TODO: 설정 저장 로직 구현
    return new_settings
