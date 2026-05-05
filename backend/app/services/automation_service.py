"""
자동화 서비스 및 인터페이스

브라우저/앱/시스템 자동화 액션의 실행을 조율하는 서비스 계층입니다.
Playwright를 이용한 웹 브라우저 제어 구현체를 포함합니다.
"""

from abc import ABC, abstractmethod
from typing import Optional, List
import asyncio

from loguru import logger
from playwright.async_api import async_playwright, Browser, BrowserContext, Page, Playwright

from app.config import settings
from app.models.actions import Action, ActionResult, ActionType, BrowserAction


class BrowserAutomationBase(ABC):
    """웹 브라우저 자동화 베이스 인터페이스"""

    @abstractmethod
    async def start(self) -> None:
        """브라우저 및 컨텍스트 초기화"""
        pass

    @abstractmethod
    async def stop(self) -> None:
        """브라우저 리소스 해제"""
        pass

    @abstractmethod
    async def execute_action(self, action: Action) -> ActionResult:
        """단일 브라우저 액션 실행"""
        pass


class PlaywrightBrowserService(BrowserAutomationBase):
    """Playwright 기반 브라우저 제어 서비스"""

    def __init__(self, headless: bool = False):
        self.headless = headless
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self._lock = asyncio.Lock()

    async def start(self) -> None:
        """브라우저 및 페이지 시작"""
        async with self._lock:
            if self.playwright is None:
                logger.info("Playwright 서비스 시작 중...")
                self.playwright = await async_playwright().start()
                self.browser = await self.playwright.chromium.launch(headless=self.headless)
                self.context = await self.browser.new_context()
                self.page = await self.context.new_page()
                logger.info(f"Playwright 서비스 시작 완료 (headless={self.headless})")

    async def stop(self) -> None:
        """브라우저 종료 및 리소스 해제"""
        async with self._lock:
            if self.page:
                await self.page.close()
                self.page = None
            if self.context:
                await self.context.close()
                self.context = None
            if self.browser:
                await self.browser.close()
                self.browser = None
            if self.playwright:
                await self.playwright.stop()
                self.playwright = None
            logger.info("Playwright 서비스 종료 완료")

    async def _get_page(self) -> Page:
        """현재 페이지 객체 반환, 없으면 시작"""
        if self.page is None:
            await self.start()
        return self.page

    async def execute_action(self, action: Action) -> ActionResult:
        """단일 브라우저 액션 실행"""
        start_time = asyncio.get_event_loop().time()
        success = False
        error_msg = None
        result_data = None
        
        logger.info(f"브라우저 액션 실행: {action.action} (params: {action.params})")
        
        try:
            page = await self._get_page()
            timeout = action.timeout or 30000  # 기본 타임아웃 30초
            
            if action.action == BrowserAction.NAVIGATE:
                url = action.params.get("url")
                if not url:
                    raise ValueError("navigate 액션에 'url' 파라미터가 필요합니다.")
                await page.goto(url, timeout=timeout)
                result_data = {"url": page.url}
                
            elif action.action == BrowserAction.CLICK:
                selector = action.params.get("selector")
                if not selector:
                    raise ValueError("click 액션에 'selector' 파라미터가 필요합니다.")
                await page.click(selector, timeout=timeout)
                
            elif action.action == BrowserAction.TYPE:
                selector = action.params.get("selector")
                text = action.params.get("text")
                if not selector or text is None:
                    raise ValueError("type 액션에 'selector'와 'text' 파라미터가 필요합니다.")
                await page.fill(selector, text, timeout=timeout)
                
            elif action.action == BrowserAction.WAIT:
                duration_ms = action.params.get("duration_ms", 1000)
                await page.wait_for_timeout(duration_ms)
                
            elif action.action == BrowserAction.WAIT_AND_CLICK:
                selector = action.params.get("selector")
                if not selector:
                    raise ValueError("wait_and_click 액션에 'selector' 파라미터가 필요합니다.")
                await page.wait_for_selector(selector, timeout=timeout)
                await page.click(selector, timeout=timeout)
                
            elif action.action == BrowserAction.SCROLL:
                direction = action.params.get("direction", "down")
                amount = action.params.get("amount", 500)
                if direction == "down":
                    await page.mouse.wheel(0, amount)
                else:
                    await page.mouse.wheel(0, -amount)
                    
            elif action.action == BrowserAction.READ_TEXT:
                selector = action.params.get("selector")
                if not selector:
                    raise ValueError("read_text 액션에 'selector' 파라미터가 필요합니다.")
                text = await page.locator(selector).inner_text(timeout=timeout)
                result_data = {"text": text}
                
            else:
                raise ValueError(f"지원하지 않는 브라우저 액션: {action.action}")
                
            success = True
            logger.info(f"브라우저 액션 완료: {action.action}")
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"브라우저 액션 실행 실패: {error_msg}")
            
        elapsed_ms = (asyncio.get_event_loop().time() - start_time) * 1000
        
        return ActionResult(
            action=action,
            success=success,
            result=result_data,
            error=error_msg,
            elapsed_ms=elapsed_ms
        )


class AutomationService:
    """자동화 서비스 — 액션 실행 조율 및 Executor 역할 수행"""

    def __init__(self, browser_service: Optional[BrowserAutomationBase] = None):
        logger.info("자동화 서비스 초기화")
        self.browser_service = browser_service or PlaywrightBrowserService(
            headless=getattr(settings, "browser_headless", False)
        )

    async def execute_actions(
        self,
        task_id: str,
        actions: list[Action],
    ) -> list[ActionResult]:
        """
        액션 리스트를 순차적으로 실행합니다.

        Args:
            task_id: 작업 ID
            actions: 실행할 액션 목록

        Returns:
            액션 실행 결과 목록
        """
        results = []
        logger.info(f"작업 {task_id}: {len(actions)}개 액션 실행 시작")

        for i, action in enumerate(actions):
            logger.info(f"작업 {task_id}: [{i+1}/{len(actions)}] {action.type}.{action.action}")

            if action.type == ActionType.BROWSER:
                result = await self.browser_service.execute_action(action)
                results.append(result)
                
                if not result.success:
                    logger.warning(f"작업 {task_id}: 액션 {i+1} 실패 — {result.error}")
                    break
            else:
                error_msg = f"지원하지 않는 액션 타입: {action.type} (현재 Browser만 지원)"
                logger.error(error_msg)
                result = ActionResult(
                    action=action,
                    success=False,
                    error=error_msg,
                    elapsed_ms=0.0
                )
                results.append(result)
                break

        return results

    async def cleanup(self):
        """사용된 리소스 정리"""
        if self.browser_service:
            await self.browser_service.stop()

# 의존성 주입을 위한 헬퍼
def get_automation_service() -> AutomationService:
    return AutomationService()
