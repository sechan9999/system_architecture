# api/server.py
"""
FastAPI REST API Server for Compound AI Fraud Detection System

엔드포인트:
- POST /analyze: 단일 청구 분석
- POST /batch-analyze: 배치 청구 분석
- GET /health: 헬스 체크
- GET /agents: 활성 Agent 목록
- GET /metrics: 시스템 메트릭
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import asyncio
import time
import uuid

# 기존 모듈 임포트
from models.schemas import Claim, AgentResult, FinalDecision, RiskLevel
from agents.statistical_agent import StatisticalAnomalyAgent
from agents.ml_agent import MLPatternAgent
from agents.rule_agent import RuleComplianceAgent
from orchestrator.llm_orchestrator import LLMOrchestrator

# ============================================================
# API 스키마 정의
# ============================================================

class ClaimRequest(BaseModel):
    """청구 분석 요청"""
    claim_id: str = Field(..., example="CLM001")
    provider_id: str = Field(..., example="PRV001")
    beneficiary_id: str = Field(..., example="BEN001")
    procedure_code: str = Field(..., example="99213")
    diagnosis_code: str = Field(..., example="J06.9")
    claim_amount: float = Field(..., example=500.0)
    service_date: datetime = Field(..., example="2024-11-15T00:00:00")
    provider_specialty: str = Field(..., example="General Practice")
    beneficiary_age: int = Field(..., example=45)
    beneficiary_state: str = Field(..., example="CA")

class BatchClaimRequest(BaseModel):
    """배치 청구 분석 요청"""
    claims: List[ClaimRequest]
    async_mode: bool = Field(default=False, description="비동기 처리 여부")

class AgentResultResponse(BaseModel):
    """Agent 분석 결과 응답"""
    agent_name: str
    risk_score: float
    confidence: float
    findings: List[str]
    evidence: Dict[str, Any]

class AnalysisResponse(BaseModel):
    """분석 결과 응답"""
    request_id: str
    claim_id: str
    overall_risk_score: float
    risk_level: str
    explanation: str
    key_findings: List[str]
    recommended_action: str
    agent_results: List[AgentResultResponse]
    processing_time_ms: float
    timestamp: datetime

class BatchAnalysisResponse(BaseModel):
    """배치 분석 결과 응답"""
    request_id: str
    total_claims: int
    completed: int
    results: List[AnalysisResponse]
    summary: Dict[str, Any]

class HealthResponse(BaseModel):
    """헬스 체크 응답"""
    status: str
    version: str
    agents_count: int
    uptime_seconds: float

class AgentInfo(BaseModel):
    """Agent 정보"""
    name: str
    weight: float
    status: str

# ============================================================
# FastAPI 앱 초기화
# ============================================================

app = FastAPI(
    title="Compound AI Fraud Detection API",
    description="Healthcare Fraud Detection System using Multi-Agent Architecture",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# 시스템 초기화
# ============================================================

class FraudDetectionService:
    """서비스 클래스: 싱글톤 패턴"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.start_time = time.time()
        self.agents = [
            StatisticalAnomalyAgent(),
            MLPatternAgent(),
            RuleComplianceAgent(),
        ]
        self.orchestrator = LLMOrchestrator(use_mock=True)
        self.request_count = 0
        self.total_processing_time = 0
        self._initialized = True
    
    async def analyze_claim(self, claim: Claim) -> FinalDecision:
        """단일 청구 분석"""
        self.request_count += 1
        
        # 모든 Agent 병렬 실행
        agent_tasks = [agent.analyze(claim) for agent in self.agents]
        agent_results = await asyncio.gather(*agent_tasks)
        
        # Orchestrator로 종합
        final_decision = await self.orchestrator.synthesize(claim, agent_results)
        
        return final_decision

# 서비스 인스턴스
service = FraudDetectionService()

# ============================================================
# API 엔드포인트
# ============================================================

@app.get("/", tags=["Root"])
async def root():
    """루트 엔드포인트"""
    return {
        "message": "Compound AI Fraud Detection API",
        "docs": "/docs",
        "version": "1.0.0"
    }

@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """시스템 헬스 체크"""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        agents_count=len(service.agents),
        uptime_seconds=round(time.time() - service.start_time, 2)
    )

@app.get("/agents", response_model=List[AgentInfo], tags=["System"])
async def get_agents():
    """활성 Agent 목록"""
    return [
        AgentInfo(
            name=agent.name,
            weight=agent.weight,
            status="active"
        )
        for agent in service.agents
    ]

@app.get("/metrics", tags=["System"])
async def get_metrics():
    """시스템 메트릭"""
    return {
        "total_requests": service.request_count,
        "avg_processing_time_ms": (
            service.total_processing_time / service.request_count * 1000
            if service.request_count > 0 else 0
        ),
        "uptime_seconds": round(time.time() - service.start_time, 2),
        "agents": {
            agent.name: {"weight": agent.weight}
            for agent in service.agents
        }
    }

@app.post("/analyze", response_model=AnalysisResponse, tags=["Analysis"])
async def analyze_claim(request: ClaimRequest):
    """
    단일 청구 분석
    
    청구 데이터를 입력받아 사기 위험 점수와 권장 조치를 반환합니다.
    """
    request_id = str(uuid.uuid4())[:8]
    start_time = time.time()
    
    # ClaimRequest → Claim 변환
    claim = Claim(
        claim_id=request.claim_id,
        provider_id=request.provider_id,
        beneficiary_id=request.beneficiary_id,
        procedure_code=request.procedure_code,
        diagnosis_code=request.diagnosis_code,
        claim_amount=request.claim_amount,
        service_date=request.service_date,
        provider_specialty=request.provider_specialty,
        beneficiary_age=request.beneficiary_age,
        beneficiary_state=request.beneficiary_state
    )
    
    try:
        # 분석 수행
        decision = await service.analyze_claim(claim)
        
        processing_time = (time.time() - start_time) * 1000
        service.total_processing_time += processing_time / 1000
        
        # 응답 생성
        return AnalysisResponse(
            request_id=request_id,
            claim_id=decision.claim_id,
            overall_risk_score=decision.overall_risk_score,
            risk_level=decision.risk_level.value,
            explanation=decision.explanation,
            key_findings=decision.key_findings,
            recommended_action=decision.recommended_action,
            agent_results=[
                AgentResultResponse(
                    agent_name=ar.agent_name,
                    risk_score=ar.risk_score,
                    confidence=ar.confidence,
                    findings=ar.findings,
                    evidence=ar.evidence
                )
                for ar in decision.agent_contributions
            ],
            processing_time_ms=round(processing_time, 2),
            timestamp=datetime.now()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/batch-analyze", response_model=BatchAnalysisResponse, tags=["Analysis"])
async def batch_analyze_claims(request: BatchClaimRequest):
    """
    배치 청구 분석
    
    여러 청구를 동시에 분석합니다.
    """
    request_id = str(uuid.uuid4())[:8]
    results = []
    
    risk_distribution = {"low": 0, "medium": 0, "high": 0, "critical": 0}
    action_distribution = {}
    
    for claim_req in request.claims:
        # 각 청구 분석
        claim = Claim(
            claim_id=claim_req.claim_id,
            provider_id=claim_req.provider_id,
            beneficiary_id=claim_req.beneficiary_id,
            procedure_code=claim_req.procedure_code,
            diagnosis_code=claim_req.diagnosis_code,
            claim_amount=claim_req.claim_amount,
            service_date=claim_req.service_date,
            provider_specialty=claim_req.provider_specialty,
            beneficiary_age=claim_req.beneficiary_age,
            beneficiary_state=claim_req.beneficiary_state
        )
        
        start_time = time.time()
        decision = await service.analyze_claim(claim)
        processing_time = (time.time() - start_time) * 1000
        
        # 통계 업데이트
        risk_distribution[decision.risk_level.value] += 1
        action_distribution[decision.recommended_action] = \
            action_distribution.get(decision.recommended_action, 0) + 1
        
        results.append(AnalysisResponse(
            request_id=request_id,
            claim_id=decision.claim_id,
            overall_risk_score=decision.overall_risk_score,
            risk_level=decision.risk_level.value,
            explanation=decision.explanation,
            key_findings=decision.key_findings,
            recommended_action=decision.recommended_action,
            agent_results=[
                AgentResultResponse(
                    agent_name=ar.agent_name,
                    risk_score=ar.risk_score,
                    confidence=ar.confidence,
                    findings=ar.findings,
                    evidence=ar.evidence
                )
                for ar in decision.agent_contributions
            ],
            processing_time_ms=round(processing_time, 2),
            timestamp=datetime.now()
        ))
    
    return BatchAnalysisResponse(
        request_id=request_id,
        total_claims=len(request.claims),
        completed=len(results),
        results=results,
        summary={
            "risk_distribution": risk_distribution,
            "action_distribution": action_distribution,
            "avg_risk_score": sum(r.overall_risk_score for r in results) / len(results) if results else 0
        }
    )

# ============================================================
# 서버 실행
# ============================================================

def run_server(host: str = "0.0.0.0", port: int = 8000):
    """서버 실행"""
    import uvicorn
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    run_server()
