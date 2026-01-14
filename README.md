# System Architecture - Healthcare Fraud Detection

A comprehensive healthcare fraud detection system combining a sophisticated multi-agent AI backend with an interactive React dashboard for visualization and monitoring.

## 📋 Project Overview

This repository contains two main components:

1. **Compound AI Fraud Detection System** - A Python-based multi-agent system leveraging LLMs, machine learning, and knowledge graphs for healthcare fraud detection
2. **Interactive Dashboard** - A React-based web dashboard for visualizing fraud detection results and system metrics

## 🏗️ Repository Structure

```
system_architecture/
├── extracted/
│   └── compound_ai_system/     # Backend fraud detection system
│       ├── agents/              # 5 specialized AI agents
│       ├── api/                 # FastAPI REST API server
│       ├── feature_store/       # Feast feature management
│       ├── knowledge_graph/     # Neo4j/NetworkX graph analysis
│       ├── mlflow_tracking/     # Model versioning & experiments
│       └── orchestrator/        # LLM-based decision orchestrator
│
├── dashboard-app/               # Frontend React dashboard
│   ├── src/                     # React components & logic
│   └── public/                  # Static assets
│
└── .github/workflows/           # CI/CD for GitHub Pages deployment
```

## 🚀 Getting Started

### Backend: Compound AI Fraud Detection System

The fraud detection system uses 5 specialized agents working together to detect healthcare fraud:

- **Statistical Anomaly Agent** - Z-score and Benford's Law analysis
- **ML Pattern Agent** - Isolation Forest for pattern detection
- **Rule Compliance Agent** - CMS regulation validation
- **Feature Store Agent** - Real-time feature-based analysis
- **Knowledge Graph Agent** - Network relationship analysis

**Quick Start:**
```bash
cd extracted/compound_ai_system

# Run basic demo
python main.py

# Run integrated system (all 5 agents)
python main_integrated.py --mode demo

# Start API server
python main_integrated.py --mode api
# or
uvicorn api.server:app --reload --port 8000
```

**Full Documentation:** [extracted/compound_ai_system/README.md](extracted/compound_ai_system/README.md)

### Frontend: Interactive Dashboard

A modern React dashboard built with Vite and Tailwind CSS for monitoring fraud detection in real-time.

**Features:**
- Real-time fraud detection monitoring
- Interactive charts and visualizations
- Risk scoring and analysis
- Agent performance metrics

**Quick Start:**
```bash
cd dashboard-app

# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build
```

**Live Demo:** The dashboard is automatically deployed to GitHub Pages via GitHub Actions.

## 🔧 Technology Stack

### Backend
- **Python 3.12**
- **FastAPI** - REST API framework
- **Feast** - Feature Store
- **Neo4j/NetworkX** - Knowledge Graph
- **MLflow** - Experiment tracking & model management
- **scikit-learn** - Machine learning models
- **Pydantic** - Data validation

### Frontend
- **React 19** - UI framework
- **Vite 7** - Build tool
- **Tailwind CSS 4** - Styling
- **Recharts** - Data visualization
- **Framer Motion** - Animations
- **Lucide React** - Icons

## 🌐 Deployment

The dashboard is configured for automatic deployment to GitHub Pages:

- **Workflow:** `.github/workflows/deploy.yml`
- **Trigger:** Pushes to `main` branch
- **Build:** Vite production build
- **Deploy:** GitHub Pages

The backend API can be deployed to any Python-compatible hosting service that supports FastAPI (e.g., AWS Lambda, Google Cloud Run, Heroku).

## 📊 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    FRONTEND (React Dashboard)               │
│                    - Risk Visualization                     │
│                    - Real-time Monitoring                   │
│                    - Agent Performance Metrics              │
└────────────────────────┬────────────────────────────────────┘
                         │ REST API
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    BACKEND (FastAPI)                        │
│                    - /analyze                               │
│                    - /batch-analyze                         │
│                    - /health, /metrics                      │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              LLM ORCHESTRATOR (Claude API)                  │
│              - Multi-agent coordination                     │
│              - Explainable AI decisions                     │
└────────────────────────┬────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ Statistical  │ │  ML Pattern  │ │    Rule      │
│   Anomaly    │ │    Agent     │ │  Compliance  │
│    Agent     │ │              │ │    Agent     │
└──────────────┘ └──────────────┘ └──────────────┘
        │                │                │
        └────────────────┼────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│Feature Store │ │  Knowledge   │ │    MLflow    │
│   (Feast)    │ │ Graph (Neo4j)│ │   Registry   │
└──────────────┘ └──────────────┘ └──────────────┘
```

## 🔍 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | System health check |
| GET | `/agents` | List active agents |
| GET | `/metrics` | System performance metrics |
| POST | `/analyze` | Analyze single claim |
| POST | `/batch-analyze` | Analyze multiple claims |

## 📝 Example Usage

**Analyze a Healthcare Claim:**
```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "claim_id": "CLM12345",
    "provider_id": "PRV001",
    "beneficiary_id": "BEN001",
    "procedure_code": "93306",
    "diagnosis_code": "I50.9",
    "claim_amount": 15000.0,
    "service_date": "2024-01-15"
  }'
```

**Response:**
```json
{
  "risk_level": "HIGH",
  "risk_score": 0.777,
  "action": "FLAG_FOR_INVESTIGATION",
  "findings": [
    "Provider in suspicious network group",
    "Claim amount 19.2x provider average",
    "Unusual procedure-diagnosis combination"
  ]
}
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'Add some feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

## 📄 License

MIT License

## 📧 Contact

For questions or support, please open an issue in this repository.

---

**Built with ❤️ using Claude AI, React, and Python**
