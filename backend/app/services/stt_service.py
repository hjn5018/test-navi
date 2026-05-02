"""
STT 서비스 인터페이스 및 구현

음성-텍스트 변환 서비스의 추상 클래스와 구체 구현체를 제공합니다.
"""

from abc import ABC, abstractmethod
from typing import AsyncGenerator, Optional

from loguru import logger


class STTServiceBase(ABC):
    """STT 서비스 추상 베이스 클래스"""

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
            {"text": str, "confidence": float, "language": str}
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


class OpenAISTTService(STTServiceBase):
    """OpenAI Whisper API 기반 STT 서비스"""

    def __init__(self, api_key: Optional[str] = None, model: str = "whisper-1"):
        self.model = model
        # TODO: OpenAI 클라이언트 초기화 (1.2.2 태스크)
        logger.info(f"OpenAI STT 서비스 초기화: model={model}")

    async def transcribe(
        self,
        audio_data: bytes,
        language: str = "ko",
        **kwargs,
    ) -> dict:
        """Whisper API를 사용한 음성 인식"""
        # TODO: 실제 Whisper API 호출 구현 (1.2.2 태스크)
        logger.info(f"STT 변환 요청: {len(audio_data)} bytes, 언어: {language}")
        return {
            "text": "[OpenAI Whisper 연동 대기]",
            "confidence": 0.0,
            "language": language,
        }

    async def stream_transcribe(
        self,
        audio_stream: AsyncGenerator[bytes, None],
        language: str = "ko",
        **kwargs,
    ) -> AsyncGenerator[dict, None]:
        """Whisper API 스트리밍 (청크 단위 처리)"""
        # TODO: 스트리밍 STT 구현 (1.2.5 태스크)
        yield {
            "text": "[스트리밍 STT 연동 대기]",
            "is_final": False,
        }
