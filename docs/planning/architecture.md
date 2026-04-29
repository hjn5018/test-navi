# 🏗️ Test-Navi 아키텍처 상세

## 1. 데이터 흐름 (End-to-End)

```
사용자 음성 입력
       │
       ▼
┌──────────────┐     ┌────────────────┐
│ Flutter App  │────▶│ FastAPI Server │
│ (Audio PCM)  │     │                │
└──────────────┘     └───────┬────────┘
                             │
                    ┌────────▼─────────┐
                    │   STT Service    │
                    │ (Whisper/Cloud)  │
                    └────────┬─────────┘
                             │ 텍스트
                    ┌────────▼─────────┐
                    │  Orchestrator    │
                    │    Agent         │
                    │ (의도 분석)       │
                    └────┬───┬───┬─────┘
                         │   │   │
              ┌──────────┘   │   └──────────┐
              ▼              ▼              ▼
        ┌──────────┐  ┌──────────┐  ┌──────────┐
        │ Browser  │  │   App    │  │ System   │
        │  Agent   │  │  Agent   │  │  Agent   │
        └────┬─────┘  └────┬─────┘  └────┬─────┘
             │              │              │
             ▼              ▼              ▼
        ┌──────────────────────────────────────┐
        │         Action Executor              │
        │  (Playwright / pywinauto / subprocess)│
        └──────────────┬───────────────────────┘
                       │ 실행 결과
              ┌────────▼─────────┐
              │   TTS Service    │
              │ (Edge TTS 등)    │
              └────────┬─────────┘
                       │ 오디오
              ┌────────▼─────────┐
              │   Flutter App    │
              │  (Audio 재생)     │
              └──────────────────┘
                       │
                       ▼
                  사용자 음성 응답
```

## 2. 통신 프로토콜

### 2.1 Flutter ↔ FastAPI

| 프로토콜 | 용도 | 이유 |
|---------|------|------|
| REST (HTTP) | 설정 변경, 단발성 요청 | 단순하고 디버깅 용이 |
| WebSocket | 실시간 음성 스트리밍, 에이전트 응답 스트리밍 | 양방향 실시간 통신 필요 |

### 2.2 실시간 대화 세션 흐름

```
Flutter                     FastAPI
  │                            │
  │──── WS Connect ──────────▶│
  │                            │
  │──── Audio Chunks ────────▶│ → STT 처리
  │                            │
  │◀─── Transcription ────────│ (중간 텍스트)
  │                            │
  │                            │ → LLM Agent 처리
  │◀─── Agent Response ───────│ (액션 계획 설명)
  │                            │
  │                            │ → Automation 실행
  │◀─── Execution Status ─────│ (단계별 진행)
  │                            │
  │◀─── TTS Audio ────────────│ (결과 음성)
  │                            │
  │──── WS Disconnect ───────▶│
```

## 3. 액션 타입 정의

### 3.1 Browser Actions

| Action | 설명 | Parameters |
|--------|------|------------|
| `navigate` | URL로 이동 | `url: string` |
| `click` | 요소 클릭 | `selector: string` |
| `type` | 텍스트 입력 | `selector: string, text: string` |
| `wait` | 요소 대기 | `selector: string, timeout: int` |
| `wait_and_click` | 대기 후 클릭 | `selector: string, timeout: int` |
| `scroll` | 스크롤 | `direction: up/down, amount: int` |
| `read_text` | 텍스트 읽기 | `selector: string` |
| `screenshot` | 스크린샷 | `full_page: bool` |
| `go_back` | 뒤로 가기 | - |
| `go_forward` | 앞으로 가기 | - |

### 3.2 App Actions

| Action | 설명 | Parameters |
|--------|------|------------|
| `launch` | 앱 실행 | `app_name: string, path: string` |
| `close` | 앱 종료 | `app_name: string` |
| `focus` | 앱 창 포커스 | `window_title: string` |
| `send_keys` | 키 입력 | `keys: string` |
| `menu_click` | 메뉴 클릭 | `menu_path: string[]` |
| `ui_click` | UI 요소 클릭 | `control_type: string, name: string` |
| `ui_type` | UI 요소에 텍스트 입력 | `control_type: string, name: string, text: string` |

### 3.3 System Actions

| Action | 설명 | Parameters |
|--------|------|------------|
| `set_volume` | 볼륨 설정 | `level: int (0-100)` |
| `set_brightness` | 밝기 설정 | `level: int (0-100)` |
| `open_settings` | 설정 열기 | `section: string` |
| `switch_window` | 창 전환 | `window_title: string` |
| `list_windows` | 열린 창 목록 | - |
| `file_open` | 파일 열기 | `path: string` |
| `file_search` | 파일 검색 | `query: string, location: string` |

## 4. 보안 아키텍처

```
┌───────────────────────────────────────────┐
│           Security Layer                   │
│                                           │
│  ┌─────────────────────────────────────┐  │
│  │     Action Whitelist Filter         │  │
│  │  (허용된 액션 타입만 통과)             │  │
│  └──────────────┬──────────────────────┘  │
│                 │                         │
│  ┌──────────────▼──────────────────────┐  │
│  │     Parameter Validator             │  │
│  │  (URL, 셀렉터, 경로 검증)             │  │
│  └──────────────┬──────────────────────┘  │
│                 │                         │
│  ┌──────────────▼──────────────────────┐  │
│  │     Rate Limiter                    │  │
│  │  (API 호출 빈도 제한)                 │  │
│  └──────────────┬──────────────────────┘  │
│                 │                         │
│  ┌──────────────▼──────────────────────┐  │
│  │     Audit Logger                    │  │
│  │  (모든 액션 실행 기록)                │  │
│  └─────────────────────────────────────┘  │
└───────────────────────────────────────────┘
```

### 4.1 URL 화이트리스트 (기본값)

```python
ALLOWED_DOMAINS = [
    "youtube.com", "www.youtube.com",
    "map.naver.com", "naver.com", "www.naver.com",
    "google.com", "www.google.com",
    # 사용자가 추가 가능
]
```

### 4.2 위험 명령 차단

```python
BLOCKED_PATTERNS = [
    r"rm\s+-rf",
    r"del\s+/[fqs]",
    r"format\s+[a-z]:",
    r"shutdown",
    r"taskkill\s+/f",
    # 시스템 파괴적 명령 차단
]
```

## 5. 에러 처리 전략

| 에러 유형 | 처리 방식 | 사용자 피드백 |
|----------|---------|-------------|
| STT 인식 실패 | 재시도 요청 | "죄송합니다, 다시 말씀해 주세요" |
| LLM 응답 오류 | 폴백 LLM으로 전환 | "잠시 처리에 문제가 있었습니다" |
| 자동화 실행 실패 | 액션 재시도 + 대안 경로 | "해당 작업을 수행하는 중 문제가 발생했습니다" |
| 네트워크 오류 | 오프라인 모드 전환 | "인터넷 연결을 확인해 주세요" |
| 요소 찾기 실패 | 대체 셀렉터 시도 | "화면 요소를 찾는 중입니다" |
