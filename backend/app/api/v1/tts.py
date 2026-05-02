"""
TTS (Text-to-Speech) API 엔드포인트

텍스트를 음성으로 변환하는 API를 제공합니다.
"""

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from loguru import logger

from app.models.schemas import TTSRequest, TTSResponse, ErrorResponse

router = APIRouter()


@router.post(
    "/synthesize",
    response_model=TTSResponse,
    responses={500: {"model": ErrorResponse}},
    summary="텍스트를 음성으로 변환",
    description="입력된 텍스트를 음성 오디오로 변환합니다.",
)
async def synthesize_speech(request: TTSRequest):
    """텍스트를 음성으로 변환하는 REST 엔드포인트"""
    logger.info(f"TTS 요청 수신: {request.text[:50]}...")

    # TODO: TTS 서비스 연동 (1.3.2 태스크)
    return TTSResponse(
        task_id="placeholder-task-id",
        status="pending",
        message="TTS 서비스 연동 대기 중",
    )


@router.get(
    "/stream/{task_id}",
    summary="TTS 오디오 스트리밍",
    description="생성된 TTS 오디오를 스트리밍합니다.",
)
async def stream_audio(task_id: str):
    """TTS 오디오를 스트리밍하는 엔드포인트"""
    logger.info(f"TTS 스트리밍 요청: task_id={task_id}")

    # TODO: TTS 오디오 스트리밍 구현 (1.3.4 태스크)
    async def placeholder_stream():
        yield b""

    return StreamingResponse(
        placeholder_stream(),
        media_type="audio/mpeg",
        headers={"X-Task-Id": task_id},
    )
