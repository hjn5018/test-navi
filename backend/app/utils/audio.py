"""
오디오 처리 유틸리티

오디오 파일 변환, 포맷 확인 등 오디오 관련 유틸리티를 제공합니다.
"""

from pathlib import Path
from typing import Optional

from loguru import logger


SUPPORTED_AUDIO_FORMATS = {".wav", ".mp3", ".webm", ".ogg", ".flac", ".m4a"}


def is_supported_format(filename: str) -> bool:
    """
    지원되는 오디오 포맷인지 확인합니다.

    Args:
        filename: 파일명

    Returns:
        지원 여부
    """
    ext = Path(filename).suffix.lower()
    return ext in SUPPORTED_AUDIO_FORMATS


def get_audio_duration(audio_data: bytes) -> Optional[float]:
    """
    오디오 데이터의 재생 시간을 반환합니다 (초).

    Args:
        audio_data: 오디오 바이너리 데이터

    Returns:
        재생 시간 (초) 또는 None
    """
    # TODO: soundfile을 사용한 구현
    logger.debug(f"오디오 길이 계산: {len(audio_data)} bytes")
    return None
