"""
TTS (Text-to-Speech) API 엔드포인트

텍스트를 음성으로 변환하는 API를 제공합니다.
"""

import uuid
from typing import Dict

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from loguru import logger

from app.models.schemas import TTSRequest, TTSResponse, ErrorResponse
from app.services.tts_service import TTSServiceBase, get_tts_service

router = APIRouter()

# 임시 작업 저장소 (실제 운영 환경에서는 Redis 등 사용 권장)
_tts_tasks: Dict[str, TTSRequest] = {}


@router.post(
    "/synthesize",
    response_model=TTSResponse,
    responses={500: {"model": ErrorResponse}},
    summary="텍스트를 음성으로 변환",
    description="입력된 텍스트를 변환하기 위한 작업을 등록합니다. 반환된 task_id로 /stream/{task_id}를 호출하세요.",
)
async def synthesize_speech(request: TTSRequest):
    """텍스트를 음성으로 변환하기 위한 작업을 생성하는 REST 엔드포인트"""
    logger.info(f"TTS 합성 작업 생성: text={request.text[:30]}..., voice={request.voice}, speed={request.speed}")

    task_id = str(uuid.uuid4())
    _tts_tasks[task_id] = request
    
    return TTSResponse(
        task_id=task_id,
        status="ready",
        message="TTS stream is ready. Use /api/v1/tts/stream/{task_id} to receive audio.",
    )


@router.get(
    "/stream/{task_id}",
    summary="TTS 오디오 스트리밍",
    description="생성된 TTS 오디오를 스트리밍합니다. (MP3 형식)",
)
async def stream_audio(
    task_id: str,
    tts_service: TTSServiceBase = Depends(get_tts_service)
):
    """지정된 task_id의 TTS 오디오를 스트리밍하는 엔드포인트"""
    logger.info(f"TTS 스트리밍 요청: task_id={task_id}")

    request = _tts_tasks.pop(task_id, None)
    if not request:
        logger.error(f"유효하지 않거나 이미 사용된 task_id: {task_id}")
        raise HTTPException(status_code=404, detail="유효하지 않은 task_id 이거나 이미 스트리밍이 완료되었습니다.")

    return StreamingResponse(
        tts_service.stream_synthesize(request.text, request.voice, request.speed),
        media_type="audio/mpeg",
        headers={"X-Task-Id": task_id, "Cache-Control": "no-cache"},
    )
