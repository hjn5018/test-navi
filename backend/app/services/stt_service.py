"""
STT 서비스 인터페이스 및 구현

음성-텍스트 변환 서비스의 추상 클래스와 구체 구현체를 제공합니다.

구현체:
- OpenAISTTService: OpenAI Whisper API 기반 (클라우드)
- (향후) FasterWhisperSTTService: Faster-Whisper 로컬 연동

태스크: 1.2.1, 1.2.2
"""

import io
import time
from abc import ABC, abstractmethod
from typing import AsyncGenerator, Optional

from loguru import logger

from app.config import settings


class STTServiceBase(ABC):
    """STT 서비스 추상 베이스 클래스

    모든 STT 구현체가 따라야 하는 인터페이스를 정의합니다.
    """

    @abstractmethod
    async def transcribe(
        self,
        audio_data: bytes,
        language: str = "ko",
        **kwargs,
    ) -> dict:
        """
        오디오 데이터를 텍스트로 변환합니다.

        Args:
            audio_data: 오디오 바이너리 데이터
            language: 언어 코드 (기본값: "ko")

        Returns:
            {"text": str, "confidence": float, "language": str, "duration_ms": float}
        """
        ...

    @abstractmethod
    async def stream_transcribe(
        self,
        audio_stream: AsyncGenerator[bytes, None],
        language: str = "ko",
        **kwargs,
    ) -> AsyncGenerator[dict, None]:
        """
        오디오 스트림을 실시간으로 텍스트로 변환합니다.

        Args:
            audio_stream: 오디오 청크의 비동기 제너레이터
            language: 언어 코드

        Yields:
            {"text": str, "is_final": bool}
        """
        ...

    @abstractmethod
    def is_available(self) -> bool:
        """서비스 사용 가능 여부를 반환합니다."""
        ...


# ============================================================
# 지원 오디오 포맷 정보
# ============================================================

SUPPORTED_AUDIO_FORMATS = {
    "audio/wav": ".wav",
    "audio/x-wav": ".wav",
    "audio/mpeg": ".mp3",
    "audio/mp3": ".mp3",
    "audio/mp4": ".mp4",
    "audio/m4a": ".m4a",
    "audio/webm": ".webm",
    "audio/ogg": ".ogg",
    "audio/flac": ".flac",
    "application/octet-stream": ".wav",  # fallback
}

SUPPORTED_EXTENSIONS = {".wav", ".mp3", ".mp4", ".m4a", ".webm", ".ogg", ".flac"}


def get_file_extension(filename: Optional[str], content_type: Optional[str]) -> str:
    """파일 확장자를 결정합니다."""
    if filename:
        for ext in SUPPORTED_EXTENSIONS:
            if filename.lower().endswith(ext):
                return ext

    if content_type and content_type in SUPPORTED_AUDIO_FORMATS:
        return SUPPORTED_AUDIO_FORMATS[content_type]

    return ".wav"  # 기본 fallback


# ============================================================
# OpenAI Whisper API 구현
# ============================================================


class OpenAISTTService(STTServiceBase):
    """OpenAI Whisper API 기반 STT 서비스

    OpenAI의 Whisper 모델을 사용하여 음성을 텍스트로 변환합니다.
    클라우드 기반이므로 인터넷 연결이 필요합니다.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "whisper-1",
    ):
        self.model = model
        self._api_key = api_key or settings.openai_api_key
        self._client = None

        if self._api_key:
            try:
                from openai import AsyncOpenAI

                self._client = AsyncOpenAI(api_key=self._api_key)
                logger.info(f"✅ OpenAI STT 서비스 초기화 완료: model={model}")
            except ImportError:
                logger.error("❌ openai 패키지가 설치되지 않았습니다.")
            except Exception as e:
                logger.error(f"❌ OpenAI 클라이언트 초기화 실패: {e}")
        else:
            logger.warning("⚠️ OpenAI API 키가 설정되지 않았습니다. STT 서비스 비활성 상태.")

    def is_available(self) -> bool:
        """OpenAI STT 서비스 사용 가능 여부"""
        return self._client is not None

    async def transcribe(
        self,
        audio_data: bytes,
        language: str = "ko",
        filename: str = "audio.wav",
        content_type: str = "audio/wav",
        **kwargs,
    ) -> dict:
        """
        Whisper API를 사용한 음성 인식

        Args:
            audio_data: 오디오 바이너리 데이터
            language: ISO-639-1 언어 코드 (기본: "ko")
            filename: 원본 파일명
            content_type: MIME 타입

        Returns:
            {"text": str, "confidence": float, "language": str, "duration_ms": float}
        """
        if not self.is_available():
            logger.warning("OpenAI STT 서비스 비활성 상태 — API 키를 확인하세요.")
            return {
                "text": "",
                "confidence": 0.0,
                "language": language,
                "duration_ms": 0.0,
                "error": "STT 서비스가 비활성 상태입니다. API 키를 설정해주세요.",
            }

        start_time = time.time()
        ext = get_file_extension(filename, content_type)
        safe_filename = f"upload{ext}"

        logger.info(
            f"🎙️ STT 변환 요청: {len(audio_data):,} bytes, "
            f"파일={filename}, 언어={language}"
        )

        try:
            # 바이트 데이터를 파일 객체로 감싸기
            audio_file = io.BytesIO(audio_data)
            audio_file.name = safe_filename

            # OpenAI Whisper API 호출
            transcript = await self._client.audio.transcriptions.create(
                model=self.model,
                file=audio_file,
                language=language,
                response_format="verbose_json",
            )

            elapsed_ms = (time.time() - start_time) * 1000
            text = transcript.text.strip() if transcript.text else ""

            logger.info(
                f"✅ STT 변환 완료: \"{text[:80]}...\" "
                f"({elapsed_ms:.0f}ms)"
            )

            return {
                "text": text,
                "confidence": 1.0,  # Whisper API는 confidence를 직접 제공하지 않음
                "language": getattr(transcript, "language", language),
                "duration_ms": elapsed_ms,
            }

        except Exception as e:
            elapsed_ms = (time.time() - start_time) * 1000
            logger.error(f"❌ STT 변환 실패: {e}")

            return {
                "text": "",
                "confidence": 0.0,
                "language": language,
                "duration_ms": elapsed_ms,
                "error": str(e),
            }

    async def stream_transcribe(
        self,
        audio_stream: AsyncGenerator[bytes, None],
        language: str = "ko",
        chunk_duration_ms: int = 3000,
        **kwargs,
    ) -> AsyncGenerator[dict, None]:
        """
        오디오 스트림을 청크 단위로 Whisper API에 전송하여 변환합니다.

        Note: OpenAI Whisper API는 네이티브 스트리밍을 지원하지 않으므로,
        오디오를 청크로 모아서 순차적으로 처리합니다.
        향후 1.2.5 태스크에서 VAD 통합 시 개선 예정.

        Args:
            audio_stream: 오디오 청크의 비동기 제너레이터
            language: 언어 코드
            chunk_duration_ms: 청크 단위 길이 (밀리초, 최소 전송 단위)

        Yields:
            {"text": str, "is_final": bool}
        """
        if not self.is_available():
            yield {
                "text": "",
                "is_final": True,
                "error": "STT 서비스가 비활성 상태입니다.",
            }
            return

        buffer = bytearray()
        # 대략적인 바이트 임계값 (16kHz, 16bit mono 기준)
        byte_threshold = int(16000 * 2 * (chunk_duration_ms / 1000))

        try:
            async for chunk in audio_stream:
                buffer.extend(chunk)

                if len(buffer) >= byte_threshold:
                    result = await self.transcribe(
                        bytes(buffer),
                        language=language,
                        filename="stream_chunk.wav",
                    )
                    buffer.clear()

                    if result.get("text"):
                        yield {
                            "text": result["text"],
                            "is_final": False,
                        }

            # 남은 버퍼 처리
            if buffer:
                result = await self.transcribe(
                    bytes(buffer),
                    language=language,
                    filename="stream_final.wav",
                )
                if result.get("text"):
                    yield {
                        "text": result["text"],
                        "is_final": True,
                    }

        except Exception as e:
            logger.error(f"❌ STT 스트리밍 처리 오류: {e}")
            yield {
                "text": "",
                "is_final": True,
                "error": str(e),
            }


# ============================================================
# 서비스 팩토리
# ============================================================


def create_stt_service(provider: Optional[str] = None) -> STTServiceBase:
    """설정에 따라 적절한 STT 서비스 인스턴스를 생성합니다.

    Args:
        provider: STT 프로바이더 이름. None이면 설정값 사용.

    Returns:
        STTServiceBase 구현체 인스턴스
    """
    provider = provider or settings.stt_provider

    if provider == "openai":
        return OpenAISTTService(
            api_key=settings.openai_api_key,
            model=settings.whisper_model,
        )
    # elif provider == "faster_whisper":
    #     return FasterWhisperSTTService(...)  # 1.2.3 태스크에서 구현
    else:
        logger.warning(f"⚠️ 알 수 없는 STT 프로바이더: {provider}. OpenAI로 폴백합니다.")
        return OpenAISTTService(
            api_key=settings.openai_api_key,
            model=settings.whisper_model,
        )
