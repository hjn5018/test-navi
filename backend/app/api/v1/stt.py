"""
STT (Speech-to-Text) API 엔드포인트

음성 데이터를 텍스트로 변환하는 API를 제공합니다.
"""

from fastapi import APIRouter, UploadFile, File, WebSocket, WebSocketDisconnect
from loguru import logger

from app.models.schemas import STTResponse, ErrorResponse

router = APIRouter()


@router.post(
    "/transcribe",
    response_model=STTResponse,
    responses={500: {"model": ErrorResponse}},
    summary="음성을 텍스트로 변환",
    description="업로드된 오디오 파일을 텍스트로 변환합니다.",
)
async def transcribe_audio(
    file: UploadFile = File(..., description="오디오 파일 (wav, mp3, webm 등)"),
    language: str = "ko",
):
    """음성 파일을 텍스트로 변환하는 REST 엔드포인트"""
    logger.info(f"STT 요청 수신: {file.filename}, 언어: {language}")

    # TODO: STT 서비스 연동 (1.2.2 태스크)
    return STTResponse(
        text="[STT 서비스 연동 대기]",
        language=language,
        confidence=0.0,
    )


@router.websocket("/stream")
async def stt_stream(websocket: WebSocket):
    """실시간 음성 스트리밍 STT WebSocket 엔드포인트"""
    await websocket.accept()
    logger.info("STT 스트리밍 세션 시작")

    try:
        while True:
            # 클라이언트로부터 오디오 청크 수신
            data = await websocket.receive_bytes()

            # TODO: STT 스트리밍 처리 (1.2.5 태스크)
            await websocket.send_json({
                "type": "transcription",
                "text": "[스트리밍 STT 연동 대기]",
                "is_final": False,
            })

    except WebSocketDisconnect:
        logger.info("STT 스트리밍 세션 종료")
