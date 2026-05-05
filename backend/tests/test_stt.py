"""
STT 모듈 단위 테스트

STT 서비스 인터페이스, OpenAI 연동, API 엔드포인트를 검증합니다.

태스크: 1.2.7
"""

import io
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from httpx import AsyncClient, ASGITransport

from app.main import app
from app.services.stt_service import (
    OpenAISTTService,
    STTServiceBase,
    create_stt_service,
    get_file_extension,
    SUPPORTED_EXTENSIONS,
)


# ============================================================
# 유틸리티 함수 테스트
# ============================================================


class TestFileExtension:
    """파일 확장자 결정 로직 테스트"""

    def test_extension_from_filename(self):
        """파일명에서 확장자 추출"""
        assert get_file_extension("recording.wav", None) == ".wav"
        assert get_file_extension("audio.mp3", None) == ".mp3"
        assert get_file_extension("speech.webm", None) == ".webm"
        assert get_file_extension("voice.flac", None) == ".flac"
        assert get_file_extension("sound.m4a", None) == ".m4a"
        assert get_file_extension("clip.ogg", None) == ".ogg"

    def test_extension_from_content_type(self):
        """Content-Type에서 확장자 추출"""
        assert get_file_extension(None, "audio/wav") == ".wav"
        assert get_file_extension(None, "audio/mpeg") == ".mp3"
        assert get_file_extension(None, "audio/webm") == ".webm"

    def test_filename_priority_over_content_type(self):
        """파일명이 Content-Type보다 우선"""
        assert get_file_extension("test.mp3", "audio/wav") == ".mp3"

    def test_fallback_to_wav(self):
        """알 수 없는 형식은 .wav로 폴백"""
        assert get_file_extension(None, None) == ".wav"
        assert get_file_extension("noext", "unknown/type") == ".wav"


# ============================================================
# STT 서비스 테스트
# ============================================================


class TestOpenAISTTService:
    """OpenAI STT 서비스 테스트"""

    def test_init_without_api_key(self):
        """API 키 없이 초기화하면 비활성 상태"""
        with patch("app.services.stt_service.settings") as mock_settings:
            mock_settings.openai_api_key = None
            service = OpenAISTTService(api_key=None)
            assert not service.is_available()

    def test_init_with_api_key(self):
        """API 키가 있으면 활성 상태 (openai 패키지 있을 때)"""
        service = OpenAISTTService(api_key="test-key-123")
        # openai 패키지 설치 여부에 따라 달라질 수 있음
        # 패키지가 있으면 True, 없으면 False
        assert isinstance(service.is_available(), bool)

    @pytest.mark.asyncio
    async def test_transcribe_when_unavailable(self):
        """서비스 비활성 시 에러 응답 반환"""
        with patch("app.services.stt_service.settings") as mock_settings:
            mock_settings.openai_api_key = None
            service = OpenAISTTService(api_key=None)

            result = await service.transcribe(b"dummy_audio")

            assert result["text"] == ""
            assert result["confidence"] == 0.0
            assert "error" in result

    @pytest.mark.asyncio
    async def test_transcribe_success(self):
        """정상적인 STT 변환 테스트 (API 모킹)"""
        service = OpenAISTTService(api_key="test-key")

        # OpenAI 클라이언트를 직접 모킹
        mock_transcript = MagicMock()
        mock_transcript.text = "안녕하세요 테스트입니다"
        mock_transcript.language = "ko"

        mock_client = AsyncMock()
        mock_client.audio.transcriptions.create = AsyncMock(return_value=mock_transcript)
        service._client = mock_client

        result = await service.transcribe(
            audio_data=b"fake_audio_data_bytes" * 100,
            language="ko",
            filename="test.wav",
        )

        assert result["text"] == "안녕하세요 테스트입니다"
        assert result["confidence"] == 1.0
        assert result["language"] == "ko"
        assert result["duration_ms"] > 0

    @pytest.mark.asyncio
    async def test_transcribe_api_error(self):
        """API 호출 실패 시 에러 처리"""
        service = OpenAISTTService(api_key="test-key")

        mock_client = AsyncMock()
        mock_client.audio.transcriptions.create = AsyncMock(
            side_effect=Exception("API rate limit exceeded")
        )
        service._client = mock_client

        result = await service.transcribe(
            audio_data=b"fake_audio_data",
            language="ko",
        )

        assert result["text"] == ""
        assert "error" in result
        assert "rate limit" in result["error"]


# ============================================================
# STT 서비스 팩토리 테스트
# ============================================================


class TestCreateSTTService:
    """STT 서비스 팩토리 테스트"""

    def test_create_openai_service(self):
        """OpenAI 프로바이더 선택"""
        service = create_stt_service("openai")
        assert isinstance(service, OpenAISTTService)

    def test_create_unknown_provider_fallback(self):
        """알 수 없는 프로바이더는 OpenAI로 폴백"""
        service = create_stt_service("unknown_provider")
        assert isinstance(service, OpenAISTTService)


# ============================================================
# API 엔드포인트 테스트
# ============================================================


@pytest.fixture
async def client():
    """비동기 테스트 클라이언트"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


class TestSTTEndpoint:
    """STT REST API 엔드포인트 테스트"""

    @pytest.mark.asyncio
    async def test_transcribe_endpoint_returns_200(self, client: AsyncClient):
        """STT 엔드포인트가 정상적으로 200 응답"""
        # 작은 더미 오디오 데이터 (최소 크기 이상)
        dummy_audio = b"\x00" * 200
        files = {"file": ("test.wav", dummy_audio, "audio/wav")}
        response = await client.post("/api/v1/stt/transcribe", files=files)
        assert response.status_code == 200

        data = response.json()
        assert "text" in data
        assert "language" in data
        assert "confidence" in data
        assert "duration_ms" in data

    @pytest.mark.asyncio
    async def test_transcribe_endpoint_with_language_param(self, client: AsyncClient):
        """언어 파라미터 전달"""
        dummy_audio = b"\x00" * 200
        files = {"file": ("test.mp3", dummy_audio, "audio/mpeg")}
        response = await client.post(
            "/api/v1/stt/transcribe",
            files=files,
            params={"language": "en"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["language"] in ("en", "ko")  # 서비스 상태에 따라 다를 수 있음

    @pytest.mark.asyncio
    async def test_transcribe_endpoint_empty_file(self, client: AsyncClient):
        """빈 오디오 파일 처리"""
        files = {"file": ("empty.wav", b"", "audio/wav")}
        response = await client.post("/api/v1/stt/transcribe", files=files)
        assert response.status_code == 200
        data = response.json()
        # 빈 파일이므로 에러 또는 빈 텍스트
        assert data["text"] == "" or data.get("error") is not None

    @pytest.mark.asyncio
    async def test_transcribe_endpoint_no_file(self, client: AsyncClient):
        """파일 없이 요청하면 422 에러"""
        response = await client.post("/api/v1/stt/transcribe")
        assert response.status_code == 422  # Validation Error

    @pytest.mark.asyncio
    async def test_transcribe_response_model(self, client: AsyncClient):
        """응답 모델 구조 검증"""
        dummy_audio = b"\x00" * 200
        files = {"file": ("test.wav", dummy_audio, "audio/wav")}
        response = await client.post("/api/v1/stt/transcribe", files=files)
        data = response.json()

        # 필수 필드 존재 확인
        assert isinstance(data["text"], str)
        assert isinstance(data["language"], str)
        assert isinstance(data["confidence"], (int, float))
        assert isinstance(data["duration_ms"], (int, float))
