# 🏥 Compound AI Fraud Detection System

LLM 기반 Multi-Agent 아키텍처를 활용한 헬스케어 사기 탐지 시스템

## 📐 시스템 아키텍처

```
┌────────────────────────────────────────────────────────────────────────┐
│                    COMPOUND AI FRAUD DETECTION SYSTEM                  │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│  ┌──────────────────────────────────────────────────────────────────┐ │
│  │                    DATA FOUNDATION LAYER                          │ │
│  │  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐             │ │
│  │  │Feature Store│   │Knowledge    │   │MLflow Model │             │ │
│  │  │   (Feast)   │   │Graph (Neo4j)│   │  Registry   │             │ │
│  │  └─────────────┘   └─────────────┘   └─────────────┘             │ │
│  └──────────────────────────────────────────────────────────────────┘ │
│                                                                        │
│  ┌──────────────────────────────────────────────────────────────────┐ │
│  │                    AGENT LAYER (5 Specialized Agents)             │ │
│  │                                                                   │ │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐│ │
│  │  │Statistical│ │   ML    │ │  Rule    │ │ Feature  │ │Knowledge ││ │
│  │  │ Anomaly  │ │ Pattern │ │Compliance│ │  Store   │ │  Graph   ││ │
│  │  │  Agent   │ │  Agent  │ │  Agent   │ │  Agent   │ │  Agent   ││ │
│  │  └────┬─────┘ └────┬────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘│ │
│  │       │            │           │            │            │       │ │
│  │       └────────────┴───────────┼────────────┴────────────┘       │ │
│  │                                ▼                                 │ │
│  │              ┌─────────────────────────────────┐                 │ │
│  │              │      LLM ORCHESTRATOR           │                 │ │
│  │              │      (Claude API / Mock)        │                 │ │
│  │              │  - 결과 종합 및 판단            │                 │ │
│  │              │  - 설명 가능한 AI               │                 │ │
│  │              └─────────────────────────────────┘                 │ │
│  └──────────────────────────────────────────────────────────────────┘ │
│                                                                        │
│  ┌──────────────────────────────────────────────────────────────────┐ │
│  │                    SERVING LAYER (FastAPI)                        │ │
│  │                                                                   │ │
│  │  POST /analyze      - 단일 청구 분석                              │ │
│  │  POST /batch-analyze - 배치 청구 분석                             │ │
│  │  GET  /health       - 시스템 상태 확인                            │ │
│  │  GET  /agents       - 활성 Agent 목록                             │ │
│  │  GET  /metrics      - 시스템 메트릭                               │ │
│  └──────────────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────────┘
```

## 📁 프로젝트 구조

```
compound_ai_system/
├── models/
│   └── schemas.py              # Pydantic 데이터 스키마
├── agents/
│   ├── base_agent.py           # Agent 추상 베이스 클래스
│   ├── statistical_agent.py    # 통계 기반 이상 탐지
│   ├── ml_agent.py             # ML 모델 패턴 분석
│   ├── rule_agent.py           # 규칙 기반 컴플라이언스
│   ├── feature_store_agent.py  # Feature Store 연동
│   └── graph_agent.py          # Knowledge Graph 분석
├── orchestrator/
│   └── llm_orchestrator.py     # LLM 기반 결과 종합
├── feature_store/
│   ├── feature_store.yaml      # Feast 설정
│   ├── features.py             # Feature 정의
│   ├── feature_store_manager.py# Feature Store 관리
│   └── data/                   # Parquet 데이터
├── knowledge_graph/
│   └── graph_manager.py        # Neo4j/NetworkX 그래프
├── mlflow_tracking/
│   ├── model_manager.py        # MLflow 모델 관리
│   └── mlruns/                 # 실험 기록
├── api/
│   ├── server.py               # FastAPI 서버
│   └── test_client.py          # API 테스트
├── main.py                     # 기본 실행
└── main_integrated.py          # 통합 실행
```

## 🚀 실행 방법

### 1. 기본 데모 실행
```bash
python main.py
```

### 2. 통합 시스템 데모 (5개 Agent)
```bash
python main_integrated.py --mode demo
```

### 3. API 서버 실행
```bash
python main_integrated.py --mode api
# 또는
uvicorn api.server:app --reload --port 8000
```

### 4. API 테스트
```bash
python api/test_client.py
```

## 🔧 핵심 컴포넌트

### 1. Feature Store (Feast)
- Provider/Beneficiary Feature 관리
- Online/Offline Feature Serving
- Point-in-Time Join으로 데이터 누수 방지

### 2. Knowledge Graph (Neo4j/NetworkX)
- Provider 네트워크 분석
- 사기 링 탐지 (커뮤니티 탐지)
- Doctor Shopping 패턴 분석

### 3. MLflow
- 모델 학습 실험 추적
- Model Registry로 버전 관리
- Production 배포 관리

### 4. FastAPI
- RESTful API 서빙
- 비동기 처리
- 자동 문서화 (Swagger/ReDoc)

## 📊 Agent 설명

| Agent | 역할 | 가중치 |
|-------|------|--------|
| StatisticalAnomaly | Z-score, Benford's Law 분석 | 0.30 |
| MLPattern | Isolation Forest, 패턴 탐지 | 0.40 |
| RuleCompliance | CMS 규정 검증 | 0.30 |
| FeatureStore | 실시간 Feature 기반 분석 | 0.35 |
| KnowledgeGraph | 네트워크 관계 분석 | 0.35 |

## 📈 결과 예시

```
Risk Level: 🟠 HIGH
Risk Score: 0.777
Action: 👉 FLAG_FOR_INVESTIGATION

Key Findings:
• Provider PRV001는 의심스러운 네트워크 그룹에 포함됨
• 청구 금액이 Provider 평균의 19.2배
• 40세 미만 환자에게 심장 시술 청구
• 의심스러운 시술-진단 조합: 93306-M54
```

## 🔗 API 엔드포인트

| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/health` | 시스템 상태 확인 |
| GET | `/agents` | 활성 Agent 목록 |
| GET | `/metrics` | 시스템 메트릭 |
| POST | `/analyze` | 단일 청구 분석 |
| POST | `/batch-analyze` | 배치 청구 분석 |

## 🛠 기술 스택

- **Python 3.12**
- **FastAPI** - REST API
- **Pydantic** - 데이터 검증
- **Feast** - Feature Store
- **Neo4j/NetworkX** - Knowledge Graph
- **MLflow** - 실험 추적 및 모델 관리
- **scikit-learn** - ML 모델
- **NumPy/Pandas** - 데이터 처리

## 📝 License

MIT License
