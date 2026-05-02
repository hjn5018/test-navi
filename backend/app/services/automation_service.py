"""
자동화 서비스

브라우저/앱/시스템 자동화 액션의 실행을 조율하는 서비스 계층입니다.
"""

from typing import Optional

from loguru import logger

from app.models.actions import Action, ActionResult, ActionType


class AutomationService:
    """자동화 서비스 — 액션 실행 조율"""

    def __init__(self):
        logger.info("자동화 서비스 초기화")

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

            # TODO: 실제 액션 실행 (1.5.4 태스크)
            result = ActionResult(
                action=action,
                success=False,
                error="자동화 엔진 연동 대기 중",
                elapsed_ms=0.0,
            )
            results.append(result)

            # 실패 시 중단
            if not result.success:
                logger.warning(f"작업 {task_id}: 액션 {i+1} 실패 — {result.error}")
                break

        return results
