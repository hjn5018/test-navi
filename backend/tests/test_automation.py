import pytest
from app.models.actions import Action, ActionType, BrowserAction
from app.services.automation_service import PlaywrightBrowserService, AutomationService

pytestmark = pytest.mark.asyncio

class TestAutomationService:
    async def test_playwright_navigate(self):
        """Playwright 브라우저 탐색 기본 테스트"""
        service = PlaywrightBrowserService(headless=True)
        try:
            action = Action(
                type=ActionType.BROWSER,
                action=BrowserAction.NAVIGATE,
                params={"url": "https://example.com"}
            )
            result = await service.execute_action(action)
            assert result.success is True
            assert result.result["url"] == "https://example.com/"
        finally:
            await service.stop()

    async def test_automation_service_chain(self):
        """AutomationService 액션 체인 테스트"""
        service = AutomationService()
        # headless는 테스트 시 항상 True가 되도록 내부 PlaywrightBrowserService를 설정해야 함
        service.browser_service = PlaywrightBrowserService(headless=True)
        
        actions = [
            Action(
                type=ActionType.BROWSER,
                action=BrowserAction.NAVIGATE,
                params={"url": "https://example.com"}
            ),
            Action(
                type=ActionType.BROWSER,
                action=BrowserAction.READ_TEXT,
                params={"selector": "h1"}
            )
        ]
        
        try:
            results = await service.execute_actions("test_task", actions)
            assert len(results) == 2
            assert all(r.success for r in results)
            assert "Example Domain" in results[1].result["text"]
        finally:
            await service.cleanup()
