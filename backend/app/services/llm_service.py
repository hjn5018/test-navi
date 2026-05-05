"""
LLM 서비스 인터페이스 및 구현

LLM 기반 의도 분석 및 액션 생성 서비스의 추상 클래스와 구현체를 제공합니다.
"""

from abc import ABC, abstractmethod
from typing import AsyncGenerator, Optional

from loguru import logger
from openai import AsyncOpenAI

from app.models.actions import Action
from app.models.schemas import AgentResponse
from app.config import settings

SYSTEM_PROMPT = """You are a highly capable automation agent for the 'Test-Navi' application.
Your goal is to understand the user's intent and generate structured browser/app automation actions.
Translate the user's natural language request into a sequence of precise actions.
Always provide a friendly feedback message to the user explaining what you are going to do.

Available Action Types: "browser", "app", "system".
Browser Actions: "navigate", "click", "type", "wait", "wait_and_click", "scroll", "read_text", "screenshot", "go_back", "go_forward".
App Actions: "launch", "close", "focus", "send_keys", "menu_click", "ui_click", "ui_type".
System Actions: "set_volume", "set_brightness", "open_settings", "switch_window", "list_windows", "file_open", "file_search".

For example, if the user asks "Navigate to YouTube and search for cats":
actions should include:
- type: "browser", action: "navigate", params: {"url": "https://youtube.com"}
- type: "browser", action: "wait_and_click", params: {"selector": "input#search"}
- type: "browser", action: "type", params: {"selector": "input#search", "text": "cats"}
- type: "browser", action: "type", params: {"selector": "input#search", "key": "Enter"}
"""

class LLMServiceBase(ABC):
    """LLM 서비스 추상 베이스 클래스"""

    @abstractmethod
    async def process(
        self,
        user_input: str,
        context: Optional[dict] = None,
        history: Optional[list[dict]] = None,
    ) -> AgentResponse:
        """
        사용자 입력을 처리하여 응답과 액션을 생성합니다.

        Args:
            user_input: 사용자 텍스트 입력
            context: 추가 컨텍스트 정보
            history: 대화 이력

        Returns:
            AgentResponse: 에이전트 응답 객체
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
        self.api_key = api_key or settings.openai_api_key
        
        if self.api_key:
            self.client = AsyncOpenAI(api_key=self.api_key)
        else:
            self.client = None
            logger.warning("OpenAI API 키가 설정되지 않았습니다. LLM 서비스를 사용할 수 없습니다.")

        logger.info(f"OpenAI LLM 서비스 초기화: model={model}")

    def is_available(self) -> bool:
        return self.client is not None

    async def process(
        self,
        user_input: str,
        context: Optional[dict] = None,
        history: Optional[list[dict]] = None,
    ) -> AgentResponse:
        """GPT-4o를 사용한 사용자 입력 처리 (Structured Outputs 사용)"""
        if not self.is_available():
            raise ValueError("OpenAI API 키가 설정되지 않아 LLM 서비스를 사용할 수 없습니다.")

        logger.info(f"LLM 처리 요청: {user_input[:50]}...")
        
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        
        if history:
            for msg in history:
                messages.append(msg)
                
        # 현재 사용자 입력과 컨텍스트 추가
        content = f"User Request: {user_input}"
        if context:
            content += f"\nContext: {context}"
            
        messages.append({"role": "user", "content": content})

        try:
            # Structured Outputs 기능을 사용하여 AgentResponse 스키마에 맞춰 응답 강제
            completion = await self.client.beta.chat.completions.parse(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                response_format=AgentResponse,
            )
            
            response_obj = completion.choices[0].message.parsed
            logger.info(f"LLM 응답 생성 성공: {len(response_obj.actions)}개의 액션")
            return response_obj
            
        except Exception as e:
            logger.error(f"LLM 처리 중 오류 발생: {e}")
            raise

    async def stream_process(
        self,
        user_input: str,
        context: Optional[dict] = None,
        history: Optional[list[dict]] = None,
    ) -> AsyncGenerator[dict, None]:
        """GPT-4o 스트리밍 응답 (현재 구현 대기)"""
        # Structured Output은 스트리밍 파싱이 조금 더 복잡하므로, 
        # 우선 일반 텍스트 스트리밍 또는 부분 파싱을 향후(1.4.6)에 구현합니다.
        yield {
            "text": "[스트리밍 LLM 연동 대기]",
            "actions": [],
            "is_final": False,
        }


class LLMFactory:
    """LLM 서비스 인스턴스를 관리하는 팩토리 클래스"""
    
    _instance: Optional[LLMServiceBase] = None
    
    @classmethod
    def get_service(cls) -> LLMServiceBase:
        """설정에 따른 LLM 서비스 싱글톤 인스턴스를 반환합니다."""
        if cls._instance is None:
            provider = settings.llm_provider.lower()
            if provider == "openai":
                cls._instance = OpenAILLMService(
                    model=settings.openai_model,
                    temperature=settings.llm_temperature
                )
            else:
                # 기본값으로 OpenAI 제공
                logger.warning(f"지원하지 않는 LLM 프로바이더({provider}). 기본값 OpenAI로 초기화합니다.")
                cls._instance = OpenAILLMService()
                
        return cls._instance
