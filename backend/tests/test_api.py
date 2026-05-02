"""
FastAPI 앱 기본 테스트

서버 상태 및 API 엔드포인트의 기본 동작을 검증합니다.
"""

import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app


@pytest.fixture
async def client():
    """비동기 테스트 클라이언트"""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """서버 상태 확인 테스트"""
    response = await client.get("/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "healthy"
    assert data["app"] == "Test-Navi"


@pytest.mark.asyncio
async def test_stt_transcribe_endpoint(client: AsyncClient):
    """STT 엔드포인트 기본 동작 테스트"""
    # 빈 파일로 테스트 (서비스 미연동 상태에서 엔드포인트 확인)
    files = {"file": ("test.wav", b"dummy_audio_data", "audio/wav")}
    response = await client.post("/api/v1/stt/transcribe", files=files)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_agent_process_endpoint(client: AsyncClient):
    """Agent 엔드포인트 기본 동작 테스트"""
    response = await client.post(
        "/api/v1/agent/process",
        json={"text": "유튜브에서 고양이 영상 검색해줘"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "text" in data
    assert "actions" in data


@pytest.mark.asyncio
async def test_tts_synthesize_endpoint(client: AsyncClient):
    """TTS 엔드포인트 기본 동작 테스트"""
    response = await client.post(
        "/api/v1/tts/synthesize",
        json={"text": "안녕하세요, 테스트입니다."},
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_automation_execute_endpoint(client: AsyncClient):
    """Automation 엔드포인트 기본 동작 테스트"""
    response = await client.post(
        "/api/v1/automation/execute",
        json={
            "task_id": "test-task-001",
            "intent": "test",
            "actions": [
                {
                    "type": "browser",
                    "action": "navigate",
                    "params": {"url": "https://www.youtube.com"},
                }
            ],
        },
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_settings_get_endpoint(client: AsyncClient):
    """Settings 조회 엔드포인트 테스트"""
    response = await client.get("/api/v1/settings")
    assert response.status_code == 200
    data = response.json()
    assert "stt_provider" in data
    assert "llm_provider" in data
