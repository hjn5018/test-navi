# 🧭 Test-Navi

**시각 장애인 및 저시력 사용자를 위한 AI 음성 기반 브라우저 및 Windows 자동화 어시스턴트**

## 소개

Test-Navi는 음성만으로 컴퓨터의 모든 기능을 활용할 수 있도록 돕는 AI 어시스턴트입니다.
STT(음성인식), LLM(대규모 언어 모델), TTS(음성 합성) 기술을 결합하여
웹 브라우저 탐색, 응용 프로그램 실행/조작, 시스템 설정 등을 자연어로 수행합니다.

## 기술 스택

| 영역 | 기술 |
|------|------|
| Frontend | Flutter (Windows Desktop) |
| Backend | FastAPI (Python) |
| STT | Whisper / Faster-Whisper |
| LLM | GPT-4o / Gemini / Claude / Gemma / Llama |
| TTS | Edge TTS / Google Cloud TTS |
| 브라우저 자동화 | Playwright |
| 앱 자동화 | pywinauto / PyAutoGUI |

## 프로젝트 구조

```
test-navi/
├── frontend/               # Flutter Windows 앱
│   ├── lib/
│   ├── windows/
│   └── pubspec.yaml
├── backend/                 # FastAPI 서버
│   ├── app/
│   │   ├── api/             # API 라우터
│   │   ├── services/        # 비즈니스 로직
│   │   ├── agents/          # LLM 에이전트
│   │   ├── automation/      # 자동화 엔진
│   │   ├── ontology/        # 온톨로지 정의
│   │   └── models/          # 데이터 모델
│   ├── tests/
│   └── requirements.txt
├── docs/                    # 문서
│   └── planning/
│       ├── project_overview.md
│       └── architecture.md
└── README.md
```

## 시작하기

### 사전 요구사항

- Python 3.11+
- Flutter 3.x (Stable)
- Windows 10/11
- (선택) NVIDIA GPU (로컬 STT/LLM 사용 시)

### Backend 설정

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend 설정

```bash
cd frontend
flutter pub get
flutter run -d windows
```

## 문서

- [프로젝트 기획서](docs/planning/project_overview.md)
- [아키텍처 상세](docs/planning/architecture.md)

## 라이선스

TBD
