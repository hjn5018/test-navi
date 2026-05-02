"""
액션 모델 정의

LLM이 생성하고 자동화 엔진이 실행하는 구조화된 액션 명령을 정의합니다.
"""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class ActionType(str, Enum):
    """액션 타입 열거형"""
    BROWSER = "browser"
    APP = "app"
    SYSTEM = "system"


# ============================================================
# 브라우저 액션
# ============================================================

class BrowserAction(str, Enum):
    """브라우저 액션 종류"""
    NAVIGATE = "navigate"
    CLICK = "click"
    TYPE = "type"
    WAIT = "wait"
    WAIT_AND_CLICK = "wait_and_click"
    SCROLL = "scroll"
    READ_TEXT = "read_text"
    SCREENSHOT = "screenshot"
    GO_BACK = "go_back"
    GO_FORWARD = "go_forward"


# ============================================================
# 앱 액션
# ============================================================

class AppAction(str, Enum):
    """앱 액션 종류"""
    LAUNCH = "launch"
    CLOSE = "close"
    FOCUS = "focus"
    SEND_KEYS = "send_keys"
    MENU_CLICK = "menu_click"
    UI_CLICK = "ui_click"
    UI_TYPE = "ui_type"


# ============================================================
# 시스템 액션
# ============================================================

class SystemAction(str, Enum):
    """시스템 액션 종류"""
    SET_VOLUME = "set_volume"
    SET_BRIGHTNESS = "set_brightness"
    OPEN_SETTINGS = "open_settings"
    SWITCH_WINDOW = "switch_window"
    LIST_WINDOWS = "list_windows"
    FILE_OPEN = "file_open"
    FILE_SEARCH = "file_search"


# ============================================================
# 통합 액션 모델
# ============================================================

class Action(BaseModel):
    """통합 액션 모델 — LLM이 생성하는 구조화된 명령"""
    type: ActionType = Field(..., description="액션 타입 (browser/app/system)")
    action: str = Field(..., description="액션 이름")
    params: dict = Field(default_factory=dict, description="액션 파라미터")
    description: Optional[str] = Field(None, description="액션 설명 (디버깅/로깅용)")
    timeout: Optional[int] = Field(None, description="타임아웃 (밀리초)")


class ActionResult(BaseModel):
    """액션 실행 결과 모델"""
    action: Action = Field(..., description="실행된 액션")
    success: bool = Field(..., description="성공 여부")
    result: Optional[dict] = Field(None, description="실행 결과 데이터")
    error: Optional[str] = Field(None, description="에러 메시지")
    elapsed_ms: float = Field(0.0, description="실행 소요 시간 (밀리초)")
