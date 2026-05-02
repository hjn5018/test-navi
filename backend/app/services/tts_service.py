"""
TTS 서비스 인터페이스 및 구현

텍스트-음성 변환 서비스의 추상 클래스와 구현체를 제공합니다.
"""

from abc import ABC, abstractmethod
from typing import AsyncGenerator, Optional

from loguru import logger


class TTSServiceBase(ABC):
    """TTS 서비스 추상 베이스 클래스"""

    @abstractmethod
    async def synthesize(
        self,
        text: str,
        voice: Optional[str] = None,
        speed: float = 1.0,
    ) -> bytes:
        """
        텍스트를 음성 오디오로 변환합니다.

        Args:
            text: 변환할 텍스트
            voice: 음성 이름 (None이면 기본값)
            speed: 재생 속도

        Returns:
            오디오 바이너리 데이터 (MP3)
        """
        ...

    @abstractmethod
    async def stream_synthesize(
        self,
        text: str,
        voice: Optional[str] = None,
        speed: float = 1.0,
    ) -> AsyncGenerator[bytes, None]:
        """
        텍스트를 음성으로 변환하고 청크 단위로 스트리밍합니다.

        Yields:
            오디오 청크 바이너리 데이터
        """
        ...


class EdgeTTSService(TTSServiceBase):
    """Microsoft Edge TTS 기반 서비스 (무료, 고품질 한국어)"""

    def __init__(self, voice: str = "ko-KR-SunHiNeural"):
        self.default_voice = voice
        logger.info(f"Edge TTS 서비스 초기화: voice={voice}")

    async def synthesize(
        self,
        text: str,
        voice: Optional[str] = None,
        speed: float = 1.0,
    ) -> bytes:
        """Edge TTS를 사용한 음성 합성"""
        # TODO: Edge TTS 연동 구현 (1.3.2 태스크)
        logger.info(f"TTS 합성 요청: {text[:50]}...")
        return b""

    async def stream_synthesize(
        self,
        text: str,
        voice: Optional[str] = None,
        speed: float = 1.0,
    ) -> AsyncGenerator[bytes, None]:
        """Edge TTS 오디오 스트리밍"""
        # TODO: TTS 스트리밍 구현 (1.3.4 태스크)
        yield b""
