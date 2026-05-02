"""
보안 유틸리티

URL 화이트리스트, 위험 명령 차단, 파라미터 검증 등 보안 관련 유틸리티를 제공합니다.
"""

import re
from urllib.parse import urlparse

from loguru import logger

from app.config import settings


# 위험 명령 패턴 (차단 대상)
BLOCKED_PATTERNS = [
    r"rm\s+-rf",
    r"del\s+/[fqs]",
    r"format\s+[a-z]:",
    r"shutdown",
    r"taskkill\s+/f",
    r"reg\s+delete",
    r"net\s+user",
    r"powershell\s+-enc",
]

_blocked_regex = [re.compile(p, re.IGNORECASE) for p in BLOCKED_PATTERNS]


def is_url_allowed(url: str) -> bool:
    """
    URL이 허용 도메인 목록에 포함되어 있는지 확인합니다.

    Args:
        url: 확인할 URL

    Returns:
        허용 여부
    """
    try:
        parsed = urlparse(url)
        domain = parsed.hostname or ""

        for allowed in settings.allowed_domains:
            if domain == allowed or domain.endswith(f".{allowed}"):
                return True

        logger.warning(f"허용되지 않은 도메인: {domain}")
        return False

    except Exception as e:
        logger.error(f"URL 검증 실패: {url} — {e}")
        return False


def is_command_safe(command: str) -> bool:
    """
    명령어가 안전한지 확인합니다 (위험 패턴 차단).

    Args:
        command: 확인할 명령어

    Returns:
        안전 여부
    """
    for pattern in _blocked_regex:
        if pattern.search(command):
            logger.warning(f"위험 명령 차단됨: {command}")
            return False
    return True


def validate_selector(selector: str) -> bool:
    """
    CSS 셀렉터가 유효한지 기본 검증합니다.

    Args:
        selector: CSS 셀렉터

    Returns:
        유효 여부
    """
    if not selector or len(selector) > 500:
        return False

    # 스크립트 인젝션 차단
    dangerous = ["<script", "javascript:", "onerror=", "onload="]
    for d in dangerous:
        if d.lower() in selector.lower():
            logger.warning(f"위험 셀렉터 차단: {selector}")
            return False

    return True
