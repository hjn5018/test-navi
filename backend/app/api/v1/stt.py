"""
STT (Speech-to-Text) API 엔드포인트

음성 데이터를 텍스트로 변환하는 API를 제공합니다.

태스크: 1.2.4 (REST), 1.2.5 (WebSocket)
"""

from fastapi import APIRouter, UploadFile, File, Query, WebSocket, WebSocketDisconnect
from loguru import logger

from app.models.schemas import STTResponse, ErrorResponse
from app.services.stt_service import (
    create_stt_service,
    SUPPORTED_EXTENSIONS,
    get_file_extension,
)

router = APIRouter()


# 싱글톤 STT 서비스 인스턴스 (지연 초기화)
_stt_service = None


def _get_stt_service():
    """STT 서비스 인스턴스를 반환합니다 (싱글톤)."""
    global _stt_service
    if _stt_service is None:
        _stt_service = create_stt_service()
    return _stt_service


@router.post(
    "/transcribe",
    response_model=STTResponse,
    responses={
        400: {"model": ErrorResponse, "description": "잘못된 요청"},
        500: {"model": ErrorResponse, "description": "서버 에러"},
        503: {"model": ErrorResponse, "description": "서비스 비활성"},
    },
    summary="음성을 텍스트로 변환",
    description=(
        "업로드된 오디오 파일을 텍스트로 변환합니다.\n\n"
        "지원 포맷: WAV, MP3, MP4, M4A, WebM, OGG, FLAC"
    ),
)
async def transcribe_audio(
    file: UploadFile = File(..., description="오디오 파일 (wav, mp3, webm 등)"),
    language: str = Query(
        "ko",
        description="ISO-639-1 언어 코드 (예: ko, en, ja)",
        min_length=2,
        max_length=5,
    ),
):
    """음성 파일을 텍스트로 변환하는 REST 엔드포인트 (태스크 1.2.4)"""
    stt_service = _get_stt_service()

    # 서비스 가용성 확인
    if not stt_service.is_available():
        logger.warning("STT 서비스 비활성 상태")
        return STTResponse(
            text="",
            language=language,
            confidence=0.0,
            error="STT 서비스가 비활성 상태입니다. API 키를 설정해주세요.",
        )

    # 파일 확장자 검증
    ext = get_file_extension(file.filename, file.content_type)
    if ext not in SUPPORTED_EXTENSIONS:
        logger.warning(f"지원되지 않는 파일 형식: {file.filename} ({file.content_type})")
        return STTResponse(
            text="",
            language=language,
            confidence=0.0,
            error=f"지원되지 않는 오디오 형식입니다. 지원 형식: {', '.join(sorted(SUPPORTED_EXTENSIONS))}",
        )

    logger.info(f"🎙️ STT 요청 수신: {file.filename}, 언어: {language}")

    # 오디오 데이터 읽기
    audio_data = await file.read()

    if not audio_data or len(audio_data) < 100:
        logger.warning(f"오디오 데이터가 너무 작습니다: {len(audio_data)} bytes")
        return STTResponse(
            text="",
            language=language,
            confidence=0.0,
            error="오디오 데이터가 비어있거나 너무 작습니다.",
        )

    # STT 변환 수행
    result = await stt_service.transcribe(
        audio_data=audio_data,
        language=language,
        filename=file.filename or "upload.wav",
        content_type=file.content_type or "audio/wav",
    )

    return STTResponse(
        text=result.get("text", ""),
        language=result.get("language", language),
        confidence=result.get("confidence", 0.0),
        duration_ms=result.get("duration_ms", 0.0),
        error=result.get("error"),
    )


@router.websocket("/stream")
async def stt_stream(websocket: WebSocket):
    """실시간 음성 스트리밍 STT WebSocket 엔드포인트 (태스크 1.2.5)

    프로토콜:
    - 클라이언트 → 서버: 오디오 청크 (바이너리)
    - 서버 → 클라이언트: JSON {"type": "transcription", "text": str, "is_final": bool}
    - 연결 종료: 클라이언트가 WebSocket 닫기
    """
    await websocket.accept()
    logger.info("🎧 STT 스트리밍 세션 시작")

    stt_service = _get_stt_service()

    if not stt_service.is_available():
        await websocket.send_json({
            "type": "error",
            "message": "STT 서비스가 비활성 상태입니다. API 키를 설정해주세요.",
        })
        await websocket.close(code=1008, reason="STT service unavailable")
        return

    # 오디오 버퍼 (청크를 모아서 일괄 처리)
    audio_buffer = bytearray()
    # 약 3초 분량의 오디오 (16kHz, 16bit, mono = 96,000 bytes)
    BUFFER_THRESHOLD = 96000
    # 최소 전송 크기 (너무 작은 청크는 무시)
    MIN_CHUNK_SIZE = 1000

    try:
        while True:
            # 클라이언트로부터 오디오 청크 수신
            data = await websocket.receive_bytes()

            if len(data) < MIN_CHUNK_SIZE:
                continue

            audio_buffer.extend(data)

            # 버퍼가 충분히 쌓이면 STT 처리
            if len(audio_buffer) >= BUFFER_THRESHOLD:
                result = await stt_service.transcribe(
                    audio_data=bytes(audio_buffer),
                    language="ko",
                    filename="stream_chunk.wav",
                )
                audio_buffer.clear()

                text = result.get("text", "")
                if text:
                    await websocket.send_json({
                        "type": "transcription",
                        "text": text,
                        "is_final": False,
                        "confidence": result.get("confidence", 0.0),
                    })

    except WebSocketDisconnect:
        logger.info("🔌 STT 스트리밍 세션 종료 (클라이언트 연결 해제)")

        # 남은 버퍼 처리
        if audio_buffer and len(audio_buffer) >= MIN_CHUNK_SIZE:
            result = await stt_service.transcribe(
                audio_data=bytes(audio_buffer),
                language="ko",
                filename="stream_final.wav",
            )
            text = result.get("text", "")
            if text:
                try:
                    await websocket.send_json({
                        "type": "transcription",
                        "text": text,
                        "is_final": True,
                    })
                except Exception:
                    pass  # 이미 연결이 닫혔을 수 있음

    except Exception as e:
        logger.error(f"❌ STT 스트리밍 오류: {e}")
        try:
            await websocket.send_json({
                "type": "error",
                "message": f"STT 처리 오류: {str(e)}",
            })
            await websocket.close(code=1011, reason="Internal error")
        except Exception:
            pass
