import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from httpx import AsyncClient, ASGITransport

from app.main import app
from app.models.actions import Action, ActionType, BrowserAction
from app.models.schemas import AgentResponse
from app.services.llm_service import OpenAILLMService, LLMFactory

pytestmark = pytest.mark.asyncio


class TestOpenAILLMService:
    """OpenAI LLM 서비스 단위 테스트"""

    def test_is_available_without_api_key(self):
        """API 키가 없으면 is_available이 False를 반환하는지 테스트"""
        with patch("app.services.llm_service.settings") as mock_settings:
            mock_settings.openai_api_key = None
            service = OpenAILLMService(api_key=None)
            assert not service.is_available()

    async def test_process_success(self):
        """정상적인 프로세스 호출 테스트"""
        with patch("app.services.llm_service.AsyncOpenAI") as MockClient:
            mock_client_instance = MagicMock()
            MockClient.return_value = mock_client_instance
            
            # 모의 응답 생성
            mock_message = MagicMock()
            mock_action = Action(
                type=ActionType.BROWSER,
                action=BrowserAction.NAVIGATE,
                params={"url": "https://example.com"}
            )
            mock_parsed = AgentResponse(
                text="테스트 응답입니다.",
                actions=[mock_action],
                feedback="이동합니다.",
                session_id=None
            )
            mock_message.parsed = mock_parsed
            
            mock_choice = MagicMock()
            mock_choice.message = mock_message
            
            mock_completion = MagicMock()
            mock_completion.choices = [mock_choice]
            
            mock_client_instance.beta.chat.completions.parse = AsyncMock(return_value=mock_completion)
            
            service = OpenAILLMService(api_key="fake-key")
            response = await service.process("테스트 프롬프트")
            
            assert response.text == "테스트 응답입니다."
            assert len(response.actions) == 1
            assert response.actions[0].type == ActionType.BROWSER


class TestAgentAPI:
    """Agent API 엔드포인트 단위 테스트"""

    async def test_process_input(self):
        """POST /process 엔드포인트 통합 테스트"""
        with patch("app.api.v1.agent.LLMFactory.get_service") as mock_get_service:
            mock_service = AsyncMock()
            mock_action = Action(
                type=ActionType.BROWSER,
                action=BrowserAction.NAVIGATE,
                params={"url": "https://example.com"}
            )
            mock_service.process.return_value = AgentResponse(
                text="테스트",
                actions=[mock_action],
                feedback="피드백",
                session_id="test_session"
            )
            mock_get_service.return_value = mock_service
            
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
                response = await client.post("/api/v1/agent/process", json={
                    "text": "유튜브로 가줘",
                    "session_id": "test_session"
                })
                
                assert response.status_code == 200
                data = response.json()
                assert data["text"] == "테스트"
                assert len(data["actions"]) == 1
                assert data["actions"][0]["type"] == "browser"
                assert data["actions"][0]["action"] == "navigate"
