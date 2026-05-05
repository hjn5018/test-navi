import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.services.tts_service import EdgeTTSService, TTSFactory

pytestmark = pytest.mark.asyncio


class TestTTSService:
    """TTS 서비스(Edge TTS) 단위 테스트"""

    async def test_edge_tts_synthesize(self):
        """전체 음성 합성 테스트"""
        service = EdgeTTSService()
        audio_bytes = await service.synthesize("안녕하세요, 테스트입니다.", speed=1.0)
        assert isinstance(audio_bytes, bytes)
        assert len(audio_bytes) > 0

    async def test_edge_tts_stream_synthesize(self):
        """스트리밍 음성 합성 테스트"""
        service = EdgeTTSService()
        chunks = []
        async for chunk in service.stream_synthesize("안녕하세요, 테스트입니다.", speed=1.0):
            chunks.append(chunk)
            
        assert len(chunks) > 0
        assert all(isinstance(c, bytes) for c in chunks)


class TestTTSAPI:
    """TTS API 엔드포인트 단위 테스트"""

    async def test_synthesize_and_stream(self):
        """synthesize 요청 후 stream을 통해 오디오 수신하는 통합 플로우 테스트"""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # 1. 작업 등록
            response = await client.post("/api/v1/tts/synthesize", json={
                "text": "안녕하세요, API 테스트입니다.",
                "voice": "ko-KR-SunHiNeural",
                "speed": 1.0
            })
            assert response.status_code == 200
            data = response.json()
            assert "task_id" in data
            assert data["status"] == "ready"
            
            task_id = data["task_id"]
            
            # 2. 스트리밍 오디오 수신
            stream_response = await client.get(f"/api/v1/tts/stream/{task_id}")
            assert stream_response.status_code == 200
            assert stream_response.headers["content-type"] == "audio/mpeg"
            
            content = stream_response.read()
            assert len(content) > 0

    async def test_stream_invalid_task_id(self):
        """유효하지 않은 task_id로 스트리밍 요청 시 404 에러 반환 테스트"""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            response = await client.get("/api/v1/tts/stream/invalid-task-id")
            assert response.status_code == 404
