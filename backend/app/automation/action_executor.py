"""
액션 실행기 (Action Executor)

LLM이 생성한 구조화된 액션을 적절한 엔진으로 라우팅하고 순차 실행합니다.
"""

import time
from typing import Optional

from loguru import logger

from app.models.actions import Action, ActionResult, ActionType
from app.automation.browser_engine import BrowserEngine


class ActionExecutor:
    """
    액션 실행기

    액션 타입에 따라 적절한 자동화 엔진에 위임하고,
    실행 결과를 수집합니다.
    """

    def __init__(self):
        self._browser_engine = BrowserEngine()
        # TODO: AppEngine, SystemEngine 추가 (Phase 2)
        logger.info("액션 실행기 초기화")

    async def execute(self, action: Action) -> ActionResult:
        """
        단일 액션을 실행합니다.

        Args:
            action: 실행할 액션

        Returns:
            ActionResult: 실행 결과
        """
        start_time = time.perf_counter()

        try:
            if action.type == ActionType.BROWSER:
                result = await self._execute_browser_action(action)
            elif action.type == ActionType.APP:
                result = await self._execute_app_action(action)
            elif action.type == ActionType.SYSTEM:
                result = await self._execute_system_action(action)
            else:
                raise ValueError(f"알 수 없는 액션 타입: {action.type}")

            elapsed = (time.perf_counter() - start_time) * 1000
            return ActionResult(
                action=action,
                success=True,
                result=result,
                elapsed_ms=elapsed,
            )

        except Exception as e:
            elapsed = (time.perf_counter() - start_time) * 1000
            logger.error(f"액션 실행 실패: {action.type}.{action.action} — {e}")
            return ActionResult(
                action=action,
                success=False,
                error=str(e),
                elapsed_ms=elapsed,
            )

    async def execute_chain(self, actions: list[Action]) -> list[ActionResult]:
        """
        액션 체인을 순차적으로 실행합니다.
        하나의 액션이 실패하면 체인을 중단합니다.

        Args:
            actions: 실행할 액션 목록

        Returns:
            실행 결과 목록
        """
        results = []
        for i, action in enumerate(actions):
            logger.info(f"액션 [{i+1}/{len(actions)}]: {action.type}.{action.action}")
            result = await self.execute(action)
            results.append(result)

            if not result.success:
                logger.warning(f"액션 체인 중단: {result.error}")
                break

        return results

    async def _execute_browser_action(self, action: Action) -> Optional[dict]:
        """브라우저 액션 실행"""
        engine = self._browser_engine

        if not engine.is_running:
            await engine.start()

        method_map = {
            "navigate": lambda: engine.navigate(action.params.get("url", "")),
            "click": lambda: engine.click(action.params.get("selector", "")),
            "type": lambda: engine.type_text(
                action.params.get("selector", ""),
                action.params.get("text", ""),
            ),
            "wait": lambda: engine.wait_for(
                action.params.get("selector", ""),
                action.params.get("timeout", 30000),
            ),
            "wait_and_click": lambda: engine.wait_and_click(
                action.params.get("selector", ""),
                action.params.get("timeout", 30000),
            ),
            "scroll": lambda: engine.scroll(
                action.params.get("direction", "down"),
                action.params.get("amount", 300),
            ),
            "read_text": lambda: engine.read_text(action.params.get("selector", "")),
            "screenshot": lambda: engine.screenshot(action.params.get("full_page", False)),
            "go_back": lambda: engine.go_back(),
            "go_forward": lambda: engine.go_forward(),
        }

        handler = method_map.get(action.action)
        if handler is None:
            raise ValueError(f"알 수 없는 브라우저 액션: {action.action}")

        result = await handler()
        return {"result": result} if result else None

    async def _execute_app_action(self, action: Action) -> Optional[dict]:
        """앱 액션 실행 (Phase 2)"""
        raise NotImplementedError("앱 자동화는 Phase 2에서 구현됩니다.")

    async def _execute_system_action(self, action: Action) -> Optional[dict]:
        """시스템 액션 실행 (Phase 2)"""
        raise NotImplementedError("시스템 자동화는 Phase 2에서 구현됩니다.")

    async def cleanup(self):
        """리소스 정리"""
        if self._browser_engine.is_running:
            await self._browser_engine.stop()
