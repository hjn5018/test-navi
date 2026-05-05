"""
자동화 (Automation) API 엔드포인트

브라우저/앱/시스템 자동화 실행을 관리하는 API를 제공합니다.
"""

from fastapi import APIRouter
from loguru import logger

from app.models.schemas import (
    AutomationRequest,
    AutomationStatusResponse,
    ErrorResponse,
)

router = APIRouter()


@router.post(
    "/execute",
    response_model=AutomationStatusResponse,
    responses={500: {"model": ErrorResponse}},
    summary="자동화 액션 실행",
    description="자동화 액션 체인을 실행합니다.",
)
async def execute_actions(request: AutomationRequest):
    """자동화 액션을 실행하는 REST 엔드포인트"""
    logger.info(f"자동화 실행 요청: {request.task_id}, 액션 수: {len(request.actions)}")

    from app.services.automation_service import get_automation_service
    service = get_automation_service()
    
    # 향후 백그라운드 작업으로 분리하거나 상태 관리를 추가해야 함
    # 현재는 요청 안에서 바로 실행
    results = await service.execute_actions(request.task_id, request.actions)
    
    # 임시 리소스 정리
    await service.cleanup()

    success_count = sum(1 for r in results if r.success)
    is_all_success = success_count == len(request.actions)
    
    status = "completed" if is_all_success else "failed"
    message = "모든 액션 실행 성공" if is_all_success else "일부 또는 전체 액션 실행 실패"
    
    last_error = None
    if not is_all_success:
        failed_results = [r for r in results if not r.success]
        if failed_results:
            last_error = failed_results[0].error

    return AutomationStatusResponse(
        task_id=request.task_id,
        status=status,
        message=message,
        completed_actions=success_count,
        total_actions=len(request.actions),
        error=last_error,
    )


@router.get(
    "/status/{task_id}",
    response_model=AutomationStatusResponse,
    responses={404: {"model": ErrorResponse}},
    summary="실행 상태 조회",
    description="자동화 실행 상태를 조회합니다.",
)
async def get_status(task_id: str):
    """자동화 실행 상태를 조회하는 엔드포인트"""
    logger.info(f"자동화 상태 조회: task_id={task_id}")

    # TODO: 상태 관리 구현
    return AutomationStatusResponse(
        task_id=task_id,
        status="unknown",
        message="상태 관리 시스템 연동 대기 중",
        completed_actions=0,
        total_actions=0,
    )


@router.post(
    "/cancel/{task_id}",
    response_model=AutomationStatusResponse,
    responses={404: {"model": ErrorResponse}},
    summary="실행 취소",
    description="진행 중인 자동화 실행을 취소합니다.",
)
async def cancel_execution(task_id: str):
    """자동화 실행을 취소하는 엔드포인트"""
    logger.info(f"자동화 취소 요청: task_id={task_id}")

    # TODO: 취소 로직 구현
    return AutomationStatusResponse(
        task_id=task_id,
        status="cancelled",
        message="실행이 취소되었습니다.",
        completed_actions=0,
        total_actions=0,
    )
