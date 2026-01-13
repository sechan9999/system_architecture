# models/schemas.py
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime
from enum import Enum

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class Claim(BaseModel):
    """청구 데이터 스키마"""
    claim_id: str
    provider_id: str
    beneficiary_id: str
    procedure_code: str
    diagnosis_code: str
    claim_amount: float
    service_date: datetime
    provider_specialty: str
    beneficiary_age: int
    beneficiary_state: str

class AgentResult(BaseModel):
    """개별 Agent 분석 결과"""
    agent_name: str
    risk_score: float = Field(ge=0.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0)
    findings: List[str]
    evidence: dict
    
class FinalDecision(BaseModel):
    """최종 판단 결과"""
    claim_id: str
    overall_risk_score: float = Field(ge=0.0, le=1.0)
    risk_level: RiskLevel
    explanation: str
    key_findings: List[str]
    recommended_action: Literal["auto_approve", "manual_review", "flag_for_investigation", "auto_deny"]
    agent_contributions: List[AgentResult]
    processing_timestamp: datetime
