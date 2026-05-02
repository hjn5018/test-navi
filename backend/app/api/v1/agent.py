"""
LLM Agent API 엔드포인트

사용자 입력을 처리하고 자동화 액션을 생성하는 API를 제공합니다.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from loguru import logger

from app.models.schemas import AgentRequest, AgentResponse, ErrorResponse

router = APIRouter()


@router.post(
    "/process",
    response_model=AgentResponse,
    responses={500: {"model": ErrorResponse}},
    summary="사용자 입력 처리",
    description="사용자 텍스트 입력을 분석하고 자동화 액션을 생성합니다.",
)
async def process_input(request: AgentRequest):
    """사용자 입력을 처리하여 액션을 생성하는 REST 엔드포인트"""
    logger.info(f"Agent 요청 수신: {request.text[:50]}...")

    # TODO: LLM Agent 연동 (1.4.2 태스크)
    return AgentResponse(
        text="[LLM Agent 연동 대기]",
        actions=[],
        feedback="현재 Agent 서비스가 준비 중입니다.",
    )


@router.websocket("/stream")
async def agent_stream(websocket: WebSocket):
    """실시간 에이전트 응답 스트리밍 WebSocket 엔드포인트"""
    await websocket.accept()
    logger.info("Agent 스트리밍 세션 시작")

    try:
        while True:
            data = await websocket.receive_json()

            # TODO: Agent 스트리밍 처리 (1.4.6 태스크)
            await websocket.send_json({
                "type": "agent_response",
                "text": "[스트리밍 Agent 연동 대기]",
                "actions": [],
                "is_final": False,
            })

    except WebSocketDisconnect:
        logger.info("Agent 스트리밍 세션 종료")
