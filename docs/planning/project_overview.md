# 🧭 Test-Navi: AI 음성 기반 브라우저 및 Windows 자동화 프로젝트

## 프로젝트 개요

**프로젝트명:** Test-Navi (가칭)  
**목표:** 시각 장애인 및 저시력 사용자를 위한 음성 기반 컴퓨터 자동화 어시스턴트  
**플랫폼:** Windows Desktop Application  
**기술 스택:** Flutter (Frontend) + FastAPI (Backend)

---

## 1. 프로젝트 비전

시각 장애인 및 저시력 사용자가 음성만으로 웹 브라우저 탐색, 응용 프로그램 실행 및 조작, 정보 검색 등 컴퓨터의 모든 기능을 활용할 수 있도록 하는 AI 어시스턴트입니다.

### 핵심 가치
- **접근성 (Accessibility):** 시각에 의존하지 않는 완전한 컴퓨터 사용 경험
- **자연어 인터페이스:** 복잡한 조작도 자연스러운 대화로 수행
- **자동화:** LLM 기반 지능형 작업 자동화

---

## 2. 타겟 사용자

| 구분 | 설명 |
|------|------|
| 1차 타겟 | 시각 장애인 (전맹, 저시력) |
| 2차 타겟 | 고령자, 컴퓨터 조작에 어려움을 겪는 사용자 |
| 3차 타겟 | 음성 기반 자동화를 원하는 일반 사용자 |

---

## 3. 핵심 사용 시나리오

### 3.1 웹 브라우저 자동화
- 유튜브에서 "고양이 춤 영상" 검색 및 재생
- 네이버 지도에서 출발지/도착지 입력 후 경로 탐색
- 웹 사이트 탐색, 검색, 정보 읽기

### 3.2 Windows 응용 프로그램 자동화
- 메모장, 엑셀, 동영상 플레이어 실행 및 조작
- 카카오톡 메시지 전송
- 파일 탐색기를 통한 파일 관리

### 3.3 시스템 제어
- 볼륨 조절, 화면 밝기 조절
- Wi-Fi, 블루투스 등 시스템 설정
- 앱 전환, 창 관리

---

## 4. 시스템 아키텍처

### 4.1 전체 구조

```
┌─────────────────────────────────────────────────────────────────┐
│                    Flutter Windows App                          │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────┐    │
│  │  System Tray  │  │   Main UI    │  │  Accessibility UI  │    │
│  │  (Wake Word)  │  │  (대화 화면)  │  │  (고대비/확대 등)   │    │
│  └──────┬───────┘  └──────┬───────┘  └────────────────────┘    │
│         │                 │                                     │
│  ┌──────▼─────────────────▼──────────────────────────────────┐  │
│  │              State Management (Riverpod/Bloc)              │  │
│  └──────────────────────┬────────────────────────────────────┘  │
│                         │ HTTP / WebSocket                      │
└─────────────────────────┼───────────────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────────────┐
│                     FastAPI Backend                              │
│  ┌─────────┐  ┌─────────┐  ┌──────────┐  ┌────────────────┐   │
│  │   STT   │  │   LLM   │  │   TTS    │  │  Automation    │   │
│  │ Service │  │  Agent   │  │ Service  │  │  Engine        │   │
│  └────┬────┘  └────┬────┘  └────┬─────┘  └───────┬────────┘   │
│       │            │            │                 │             │
│  ┌────▼────┐  ┌────▼────┐  ┌───▼──────┐  ┌──────▼─────────┐   │
│  │ Whisper │  │ GPT/    │  │ Edge TTS │  │  Playwright    │   │
│  │ Faster  │  │ Gemini/ │  │ / gTTS   │  │  + PyAutoGUI   │   │
│  │ Whisper │  │ Claude/ │  │ / Coqui  │  │  + pywinauto   │   │
│  │         │  │ Llama   │  │          │  │  + subprocess  │   │
│  └─────────┘  └─────────┘  └──────────┘  └────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 아키텍처 설계 근거 (원안 대비 변경 사항)

#### 변경 1: 자동화 엔진의 백엔드 이동

**원안:** Frontend(Flutter)가 직접 Playwright 등 자동화 도구를 실행  
**수정안:** Backend(FastAPI)에서 자동화 엔진을 실행

**변경 이유:**
1. Playwright는 Node.js/Python 런타임이 필요하여 Flutter(Dart)에서 직접 실행 불가
2. 자동화 코드의 보안 격리 — 백엔드에서 샌드박스 실행
3. LLM이 생성한 코드를 백엔드에서 검증 후 실행하는 것이 안전
4. 자동화 실행 상태 관리가 서버 사이드에서 더 용이

#### 변경 2: 구조화된 액션 명령 체계

**원안:** LLM이 코드를 생성하여 프론트엔드에서 실행  
**수정안:** LLM이 **구조화된 액션 명령**을 생성하고, 백엔드의 **Automation Engine**이 해석/실행

**변경 이유:**
1. LLM이 직접 실행 코드를 생성하면 보안 위험이 매우 높음
2. 사전 정의된 액션 세트를 통해 안전성과 예측 가능성 확보
3. 복잡한 작업은 액션 체인(Action Chain)으로 구성

---

## 5. 핵심 모듈 상세

### 5.1 STT (Speech-to-Text) 모듈

| 구성 요소 | 설명 |
|----------|------|
| Wake Word 감지 | 경량 모델로 상시 대기 (예: Porcupine, Snowboy, 또는 커스텀 모델) |
| 음성 인식 | Whisper (OpenAI) 또는 Faster-Whisper (로컬), Google Cloud STT (클라우드) |
| VAD (Voice Activity Detection) | Silero VAD 등으로 음성 구간 감지 |
| 한국어 최적화 | 한국어 전용 모델 또는 fine-tuning 검토 |

**동작 흐름:**
1. 시스템 트레이에서 Wake Word 감지 엔진 상시 실행 (예: "네비야", "도와줘")
2. Wake Word 감지 시 메인 UI 활성화 + STT 시작
3. 음성을 텍스트로 변환하여 LLM Agent로 전달

### 5.2 LLM Agent 모듈

#### Agent 아키텍처: Multi-Agent + Ontology

```
┌─────────────────────────────────────────────┐
│              Orchestrator Agent              │
│  (사용자 의도 분석 & 작업 분해 & 라우팅)        │
└──────────┬──────────┬──────────┬────────────┘
           │          │          │
    ┌──────▼──┐ ┌─────▼────┐ ┌──▼──────────┐
    │ Browser │ │  App     │ │  System     │
    │ Agent   │ │  Agent   │ │  Agent      │
    │         │ │          │ │             │
    │ 웹 탐색  │ │ 앱 실행   │ │ 시스템 설정  │
    │ 검색     │ │ 앱 조작   │ │ 파일 관리   │
    └─────────┘ └──────────┘ └─────────────┘
           │          │          │
    ┌──────▼──────────▼──────────▼────────────┐
    │          Ontology Knowledge Base         │
    │  (앱/웹사이트 구조, UI 요소, 조작 방법)     │
    └─────────────────────────────────────────┘
```

#### LLM 서비스 옵션

| 구분 | 서비스 | 장점 | 단점 |
|------|--------|------|------|
| 유료 | OpenAI GPT-4o | 높은 정확도, 풍부한 도구 지원 | 비용, 네트워크 의존 |
| 유료 | Google Gemini 2.5 | 멀티모달, 긴 컨텍스트 | 비용, 한국어 품질 변동 |
| 유료 | Anthropic Claude | 안전성, 긴 컨텍스트 | 비용, 도구 사용 제한적 |
| 무료 | Google Gemma 3 | 로컬 실행 가능, 무료 | 성능 제한, GPU 필요 |
| 무료 | Meta Llama 3.1 | 로컬 실행, 다양한 크기 | 한국어 성능 제한 |
| 무료 | Microsoft Phi-3 | 경량, 로컬 실행 | 복잡한 작업에 제한 |

#### 온톨로지 기법 적용

```yaml
# 예시: 유튜브 온톨로지
YouTube:
  type: WebApplication
  url: "https://www.youtube.com"
  actions:
    search:
      steps:
        - navigate_to: "https://www.youtube.com"
        - find_element: "input[name='search_query']"
        - type_text: "{query}"
        - click: "button#search-icon-legacy"
    play_first_result:
      steps:
        - wait_for: "ytd-video-renderer"
        - click: "ytd-video-renderer:first-child a#video-title"
    control_playback:
      play_pause: "button.ytp-play-button"
      volume: "input.ytp-volume-slider"
```

### 5.3 TTS (Text-to-Speech) 모듈

| 옵션 | 설명 | 추천 용도 |
|------|------|----------|
| Edge TTS | Microsoft Edge 음성, 무료, 고품질 한국어 | 기본 TTS |
| Google Cloud TTS | 자연스러운 음성, 유료 | 프리미엄 옵션 |
| Coqui TTS | 오픈소스, 로컬 실행 | 오프라인 모드 |
| Windows SAPI | Windows 내장, 저지연 | 시스템 안내 |

### 5.4 자동화 엔진 (Automation Engine)

| 도구 | 용도 |
|------|------|
| Playwright (Python) | 웹 브라우저 자동화 (Chromium/Firefox/WebKit) |
| PyAutoGUI | 범용 GUI 자동화 (마우스/키보드) |
| pywinauto | Windows 네이티브 앱 자동화 (Win32/UIA) |
| subprocess | 프로세스 실행/관리 |
| comtypes/pywin32 | Windows COM 자동화 (Excel, Word 등) |

#### 액션 명령 체계 (Action Schema)

```json
{
  "task_id": "uuid",
  "intent": "search_and_play_youtube_video",
  "actions": [
    {
      "type": "browser",
      "action": "navigate",
      "params": { "url": "https://www.youtube.com" }
    },
    {
      "type": "browser",
      "action": "type",
      "params": { "selector": "input[name='search_query']", "text": "고양이 춤" }
    },
    {
      "type": "browser",
      "action": "click",
      "params": { "selector": "button#search-icon-legacy" }
    },
    {
      "type": "browser",
      "action": "wait_and_click",
      "params": { "selector": "ytd-video-renderer:first-child a#video-title" }
    }
  ],
  "feedback": "유튜브에서 '고양이 춤' 영상을 검색하고 첫 번째 결과를 재생합니다."
}
```

---

## 6. Frontend (Flutter) 상세

### 6.1 UI/UX 설계 원칙

**접근성 최우선 원칙:**
- 모든 UI 요소에 `Semantics` 위젯 적용 (스크린리더 호환)
- 고대비 모드 기본 지원
- 대형 폰트 옵션
- 키보드 네비게이션 완전 지원
- 화면 확대/축소 지원

### 6.2 화면 구성

| 화면 | 설명 |
|------|------|
| 시스템 트레이 | 백그라운드 상태 표시, 설정 메뉴 |
| 메인 대화 화면 | 음성 입력 시각화, 대화 이력, 상태 표시 |
| 설정 화면 | LLM 선택, 음성 설정, 접근성 설정 |
| 작업 진행 화면 | 자동화 실행 상태, 단계별 진행 표시 |

### 6.3 핵심 패키지

| 패키지 | 용도 |
|--------|------|
| `system_tray` | 시스템 트레이 통합 |
| `window_manager` | 윈도우 관리 (숨기기/보이기) |
| `record` / `flutter_sound` | 마이크 음성 녹음 |
| `dio` / `web_socket_channel` | 백엔드 통신 |
| `flutter_riverpod` 또는 `flutter_bloc` | 상태 관리 |
| `just_audio` | TTS 오디오 재생 |

---

## 7. Backend (FastAPI) 상세

### 7.1 API 엔드포인트 설계

```
POST   /api/v1/stt/transcribe          # 음성 → 텍스트 변환
WS     /api/v1/stt/stream              # 실시간 스트리밍 STT

POST   /api/v1/agent/process           # 사용자 입력 처리 (텍스트)
WS     /api/v1/agent/stream             # 실시간 에이전트 응답 스트림

POST   /api/v1/tts/synthesize          # 텍스트 → 음성 변환
GET    /api/v1/tts/stream/{task_id}    # TTS 오디오 스트리밍

POST   /api/v1/automation/execute      # 자동화 액션 실행
GET    /api/v1/automation/status/{id}  # 실행 상태 조회
POST   /api/v1/automation/cancel/{id}  # 실행 취소

GET    /api/v1/settings                # 설정 조회
PUT    /api/v1/settings                # 설정 변경
```

### 7.2 디렉토리 구조

```
backend/
├── app/
│   ├── main.py                    # FastAPI 앱 진입점
│   ├── config.py                  # 설정 관리
│   ├── api/
│   │   ├── v1/
│   │   │   ├── stt.py             # STT 라우터
│   │   │   ├── agent.py           # Agent 라우터
│   │   │   ├── tts.py             # TTS 라우터
│   │   │   ├── automation.py      # Automation 라우터
│   │   │   └── settings.py        # Settings 라우터
│   ├── services/
│   │   ├── stt_service.py         # STT 비즈니스 로직
│   │   ├── llm_service.py         # LLM Agent 로직
│   │   ├── tts_service.py         # TTS 비즈니스 로직
│   │   └── automation_service.py  # 자동화 엔진
│   ├── agents/
│   │   ├── orchestrator.py        # 오케스트레이터 에이전트
│   │   ├── browser_agent.py       # 브라우저 자동화 에이전트
│   │   ├── app_agent.py           # 앱 자동화 에이전트
│   │   └── system_agent.py        # 시스템 제어 에이전트
│   ├── automation/
│   │   ├── browser_engine.py      # Playwright 래퍼
│   │   ├── app_engine.py          # pywinauto/PyAutoGUI 래퍼
│   │   ├── system_engine.py       # 시스템 명령 래퍼
│   │   └── action_executor.py     # 액션 실행기
│   ├── ontology/
│   │   ├── loader.py              # 온톨로지 로더
│   │   ├── schemas/               # 앱/사이트별 온톨로지 정의
│   │   │   ├── youtube.yaml
│   │   │   ├── naver_map.yaml
│   │   │   └── kakaotalk.yaml
│   │   └── registry.py            # 온톨로지 레지스트리
│   ├── models/
│   │   ├── schemas.py             # Pydantic 모델
│   │   └── actions.py             # 액션 모델
│   └── utils/
│       ├── audio.py               # 오디오 처리 유틸
│       └── security.py            # 보안 유틸
├── tests/
├── requirements.txt
└── Dockerfile
```

---

## 8. 보안 고려사항

**주의: LLM 생성 코드 실행 위험**
- LLM이 직접 Python 코드를 생성하여 실행하는 방식은 **보안 위험이 매우 높음**
- 악의적 프롬프트 주입(Prompt Injection)으로 시스템 명령 실행 가능
- **반드시** 사전 정의된 액션 세트 + 화이트리스트 방식으로 제한

### 보안 계층

| 계층 | 설명 |
|------|------|
| Action Whitelist | 허용된 액션 타입만 실행 가능 |
| Parameter Validation | 모든 파라미터 검증 (URL, 셀렉터 등) |
| Sandboxing | 자동화 엔진을 제한된 환경에서 실행 |
| Rate Limiting | API 호출 빈도 제한 |
| Audit Logging | 모든 자동화 실행 기록 |

---

## 9. 개발 로드맵

### Phase 1: Foundation (MVP) — 4~6주
- 프로젝트 셋업 (Flutter + FastAPI)
- STT 기본 연동 (Whisper)
- TTS 기본 연동 (Edge TTS)
- LLM 기본 연동 (GPT-4o)
- 단순 브라우저 자동화 (유튜브 검색/재생)

### Phase 2: Core Features — 4~6주
- Multi-Agent 아키텍처 구현
- 온톨로지 기반 웹사이트 지원 확대
- Windows 앱 자동화 (메모장, 카카오톡)
- 시스템 트레이 + Wake Word 구현
- 기본 접근성 UI

### Phase 3: Enhancement — 4~6주
- 네이버 지도 경로 탐색
- 엑셀, 동영상 플레이어 자동화
- 온톨로지 확장 및 자동 학습
- 로컬 LLM 지원 (Gemma, Llama)
- 고급 접근성 기능

### Phase 4: Polish & Release — 2~4주
- 통합 테스트 및 QA
- 성능 최적화
- 설치 패키지 생성 (MSIX/Inno Setup)
- 사용자 가이드 작성
- 베타 테스트

---

## 10. 기술적 도전 과제

| 과제 | 설명 | 대응 전략 |
|------|------|----------|
| 웹사이트 구조 변경 | 사이트 업데이트 시 셀렉터 변경 | 온톨로지 버전 관리 + AI 기반 셀렉터 탐색 |
| LLM 환각(Hallucination) | 잘못된 액션 생성 | 액션 검증 + 사용자 확인 단계 |
| 다양한 앱 지원 | 앱마다 UI 구조가 다름 | pywinauto UIA + 온톨로지 매핑 |
| 실시간 음성 처리 | 지연시간 최소화 | 스트리밍 STT + 로컬 VAD |
| 한국어 음성 인식 정확도 | 한국어 특화 모델 부족 | 다중 STT 엔진 비교 + fine-tuning |

---

## 11. 의존성 및 사전 조건

### 개발 환경
- Python 3.11+
- Flutter 3.x (Stable)
- Node.js 18+ (Playwright 브라우저 설치용)
- Windows 10/11

### API 키 (선택)
- OpenAI API Key (GPT-4o 사용 시)
- Google Cloud API Key (Gemini, Cloud TTS 사용 시)
- Anthropic API Key (Claude 사용 시)
