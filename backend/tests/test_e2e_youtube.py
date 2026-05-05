import pytest
from app.services.llm_service import LLMFactory
from app.services.automation_service import AutomationService, PlaywrightBrowserService
from app.models.schemas import AgentRequest

pytestmark = pytest.mark.asyncio

class TestE2EYoutube:
    """유튜브 검색 및 재생 E2E 시나리오 테스트"""
    
    @pytest.mark.skip(reason="실제 브라우저를 띄우고 네트워크를 사용하므로 CI에서는 생략합니다.")
    async def test_youtube_search_and_play(self):
        """
        사용자 발화: '유튜브에서 침착맨 검색해서 첫번째 영상 틀어줘'
        LLM이 액션을 생성하고, AutomationService가 이를 실행하는지 검증
        """
        # 1. LLM에 사용자 의도 전달하여 액션 추출
        llm_service = LLMFactory.get_service()
        agent_req = AgentRequest(text="유튜브에서 침착맨 검색해서 아무 영상이나 틀어줘")
        agent_res = await llm_service.process(agent_req)
        
        actions = agent_res.actions
        assert len(actions) > 0
        
        # 2. Automation Service로 브라우저 실행
        # 로컬 테스트 시 확인하기 쉽도록 headless=False로 설정 가능
        browser_service = PlaywrightBrowserService(headless=True)
        automation_service = AutomationService(browser_service=browser_service)
        
        try:
            results = await automation_service.execute_actions("e2e_youtube_task", actions)
            
            # 3. 결과 검증
            assert len(results) == len(actions)
            assert all(r.success for r in results)
        finally:
            await automation_service.cleanup()
