"""
TTS 서비스 인터페이스 및 구현

텍스트-음성 변환 서비스의 추상 클래스와 구현체를 제공합니다.
"""

from abc import ABC, abstractmethod
from typing import AsyncGenerator, Optional

import edge_tts
from loguru import logger

from app.config import settings


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

    def __init__(self, voice: Optional[str] = None):
        self.default_voice = voice or settings.edge_tts_voice
        logger.info(f"Edge TTS 서비스 초기화: voice={self.default_voice}")

    def _get_rate_string(self, speed: float) -> str:
        """재생 속도를 Edge TTS 형식의 문자열로 변환 (예: +20%, -10%)"""
        rate_percent = int((speed - 1.0) * 100)
        return f"+{rate_percent}%" if rate_percent >= 0 else f"{rate_percent}%"

    async def synthesize(
        self,
        text: str,
        voice: Optional[str] = None,
        speed: float = 1.0,
    ) -> bytes:
        """Edge TTS를 사용한 음성 합성"""
        v = voice or self.default_voice
        rate = self._get_rate_string(speed)
        
        logger.debug(f"Edge TTS 합성 시작: voice={v}, rate={rate}, text_length={len(text)}")
        communicate = edge_tts.Communicate(text, v, rate=rate)
        
        audio_data = bytearray()
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data.extend(chunk["data"])
                
        logger.debug(f"Edge TTS 합성 완료: 오디오 크기={len(audio_data)} bytes")
        return bytes(audio_data)

    async def stream_synthesize(
        self,
        text: str,
        voice: Optional[str] = None,
        speed: float = 1.0,
    ) -> AsyncGenerator[bytes, None]:
        """Edge TTS 오디오 스트리밍"""
        v = voice or self.default_voice
        rate = self._get_rate_string(speed)
        
        logger.debug(f"Edge TTS 스트리밍 시작: voice={v}, rate={rate}, text_length={len(text)}")
        communicate = edge_tts.Communicate(text, v, rate=rate)
        
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                yield chunk["data"]
                
        logger.debug("Edge TTS 스트리밍 완료")


class TTSFactory:
    """TTS 서비스 팩토리"""
    
    _instance: Optional[TTSServiceBase] = None
    
    @classmethod
    def get_service(cls, provider: Optional[str] = None) -> TTSServiceBase:
        """설정된 프로바이더에 맞는 TTS 서비스 인스턴스 반환 (싱글톤)"""
        if cls._instance is not None:
            return cls._instance
            
        provider = provider or settings.tts_provider
        
        if provider == "edge_tts":
            cls._instance = EdgeTTSService()
        else:
            logger.warning(f"지원하지 않는 TTS 프로바이더: {provider}. 기본값(edge_tts)을 사용합니다.")
            cls._instance = EdgeTTSService()
            
        return cls._instance

# 의존성 주입을 위한 헬퍼 함수
def get_tts_service() -> TTSServiceBase:
    return TTSFactory.get_service()
