"""
Pydantic 데이터 모델 정의

API 요청/응답 스키마를 정의합니다.
"""

from typing import Optional

from pydantic import BaseModel, Field

from app.models.actions import Action


# ============================================================
# 공통 응답 모델
# ============================================================

class ErrorResponse(BaseModel):
    """에러 응답 모델"""
    error: str = Field(..., description="에러 메시지")
    detail: Optional[str] = Field(None, description="상세 에러 정보")


# ============================================================
# STT 모델
# ============================================================

class STTResponse(BaseModel):
    """STT 응답 모델"""
    text: str = Field(..., description="인식된 텍스트")
    language: str = Field("ko", description="언어 코드")
    confidence: float = Field(0.0, description="인식 신뢰도 (0.0 ~ 1.0)")
    duration_ms: float = Field(0.0, description="처리 소요 시간 (밀리초)")
    error: Optional[str] = Field(None, description="에러 메시지 (성공 시 None)")


# ============================================================
# Agent 모델
# ============================================================

class AgentRequest(BaseModel):
    """Agent 요청 모델"""
    text: str = Field(..., description="사용자 입력 텍스트")
    session_id: Optional[str] = Field(None, description="세션 ID (대화 컨텍스트 유지)")
    context: Optional[dict] = Field(None, description="추가 컨텍스트 정보")


class AgentResponse(BaseModel):
    """Agent 응답 모델"""
    text: str = Field(..., description="에이전트 응답 텍스트")
    actions: list[Action] = Field(default_factory=list, description="실행할 액션 목록")
    feedback: str = Field("", description="사용자에게 전달할 피드백 메시지")
    session_id: Optional[str] = Field(None, description="세션 ID")


# ============================================================
# TTS 모델
# ============================================================

class TTSRequest(BaseModel):
    """TTS 요청 모델"""
    text: str = Field(..., description="변환할 텍스트")
    voice: Optional[str] = Field(None, description="음성 이름 (None이면 기본값 사용)")
    speed: float = Field(1.0, description="재생 속도 (0.5 ~ 2.0)", ge=0.5, le=2.0)


class TTSResponse(BaseModel):
    """TTS 응답 모델"""
    task_id: str = Field(..., description="TTS 작업 ID")
    status: str = Field(..., description="작업 상태")
    message: str = Field("", description="상태 메시지")


# ============================================================
# 자동화 모델
# ============================================================

class AutomationRequest(BaseModel):
    """자동화 실행 요청 모델"""
    task_id: str = Field(..., description="작업 ID")
    intent: str = Field("", description="사용자 의도 설명")
    actions: list[Action] = Field(..., description="실행할 액션 목록")
    feedback: str = Field("", description="사용자에게 전달할 피드백")


class AutomationStatusResponse(BaseModel):
    """자동화 실행 상태 응답 모델"""
    task_id: str = Field(..., description="작업 ID")
    status: str = Field(..., description="실행 상태 (pending/running/completed/failed/cancelled)")
    message: str = Field("", description="상태 메시지")
    completed_actions: int = Field(0, description="완료된 액션 수")
    total_actions: int = Field(0, description="전체 액션 수")
    error: Optional[str] = Field(None, description="에러 정보")


# ============================================================
# 설정 모델
# ============================================================

class AppSettings(BaseModel):
    """애플리케이션 설정 모델"""
    stt_provider: str = Field("openai", description="STT 프로바이더")
    tts_provider: str = Field("edge_tts", description="TTS 프로바이더")
    tts_voice: str = Field("ko-KR-SunHiNeural", description="TTS 음성")
    llm_provider: str = Field("openai", description="LLM 프로바이더")
    llm_model: str = Field("gpt-4o", description="LLM 모델")
    browser_type: str = Field("chromium", description="브라우저 타입")
    browser_headless: bool = Field(False, description="헤드리스 모드 여부")
