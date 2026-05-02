"""
Test-Navi 애플리케이션 설정 관리

환경 변수와 .env 파일을 통해 설정을 관리합니다.
"""

from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


# 프로젝트 루트 디렉토리
BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """애플리케이션 전역 설정"""

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- 앱 기본 설정 ---
    app_name: str = "Test-Navi"
    app_version: str = "0.1.0"
    debug: bool = True

    # --- 서버 설정 ---
    host: str = "127.0.0.1"
    port: int = 8000

    # --- CORS 설정 ---
    cors_origins: list[str] = ["*"]

    # --- API 키 ---
    openai_api_key: Optional[str] = None
    google_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None

    # --- STT 설정 ---
    stt_provider: str = "openai"  # "openai" | "faster_whisper"
    whisper_model: str = "whisper-1"
    faster_whisper_model: str = "large-v3"

    # --- TTS 설정 ---
    tts_provider: str = "edge_tts"  # "edge_tts" | "google_cloud"
    edge_tts_voice: str = "ko-KR-SunHiNeural"  # 한국어 여성 음성

    # --- LLM 설정 ---
    llm_provider: str = "openai"  # "openai" | "gemini" | "claude" | "ollama"
    openai_model: str = "gpt-4o"
    llm_temperature: float = 0.3
    llm_max_tokens: int = 2048

    # --- 자동화 설정 ---
    browser_headless: bool = False  # 접근성 목적이므로 기본 headful
    browser_type: str = "chromium"  # "chromium" | "firefox" | "webkit"
    action_timeout: int = 30000  # 밀리초
    allowed_domains: list[str] = [
        "youtube.com",
        "www.youtube.com",
        "map.naver.com",
        "naver.com",
        "www.naver.com",
        "google.com",
        "www.google.com",
    ]

    # --- 보안 설정 ---
    rate_limit_per_minute: int = 60

    # --- 로깅 설정 ---
    log_level: str = "INFO"
    log_file: Optional[str] = "logs/test_navi.log"


# 싱글톤 설정 인스턴스
settings = Settings()
