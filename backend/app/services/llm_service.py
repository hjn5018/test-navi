"""
LLM 서비스 인터페이스 및 구현

LLM 기반 의도 분석 및 액션 생성 서비스의 추상 클래스와 구현체를 제공합니다.
"""

from abc import ABC, abstractmethod
from typing import AsyncGenerator, Optional

from loguru import logger

from app.models.actions import Action


class LLMServiceBase(ABC):
    """LLM 서비스 추상 베이스 클래스"""

    @abstractmethod
    async def process(
        self,
        user_input: str,
        context: Optional[dict] = None,
        history: Optional[list[dict]] = None,
    ) -> dict:
        """
        사용자 입력을 처리하여 응답과 액션을 생성합니다.

        Args:
            user_input: 사용자 텍스트 입력
            context: 추가 컨텍스트 정보
            history: 대화 이력

        Returns:
            {"text": str, "actions": list[Action], "feedback": str}
        """
        ...

    @abstractmethod
    async def stream_process(
        self,
        user_input: str,
        context: Optional[dict] = None,
        history: Optional[list[dict]] = None,
    ) -> AsyncGenerator[dict, None]:
        """
        사용자 입력을 처리하고 응답을 스트리밍합니다.

        Yields:
            {"text": str, "actions": list[Action], "is_final": bool}
        """
        ...


class OpenAILLMService(LLMServiceBase):
    """OpenAI GPT 기반 LLM 서비스"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4o",
        temperature: float = 0.3,
    ):
        self.model = model
        self.temperature = temperature
        # TODO: OpenAI 클라이언트 초기화 (1.4.2 태스크)
        logger.info(f"OpenAI LLM 서비스 초기화: model={model}")

    async def process(
        self,
        user_input: str,
        context: Optional[dict] = None,
        history: Optional[list[dict]] = None,
    ) -> dict:
        """GPT-4o를 사용한 사용자 입력 처리"""
        # TODO: 실제 GPT-4o API 호출 구현 (1.4.2 태스크)
        logger.info(f"LLM 처리 요청: {user_input[:50]}...")
        return {
            "text": "[OpenAI LLM 연동 대기]",
            "actions": [],
            "feedback": "LLM 서비스 연동이 필요합니다.",
        }

    async def stream_process(
        self,
        user_input: str,
        context: Optional[dict] = None,
        history: Optional[list[dict]] = None,
    ) -> AsyncGenerator[dict, None]:
        """GPT-4o 스트리밍 응답"""
        # TODO: 스트리밍 LLM 구현 (1.4.6 태스크)
        yield {
            "text": "[스트리밍 LLM 연동 대기]",
            "actions": [],
            "is_final": False,
        }
