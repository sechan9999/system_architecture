# agents/base_agent.py
from abc import ABC, abstractmethod
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from models.schemas import Claim, AgentResult

class BaseAgent(ABC):
    """모든 Agent의 베이스 클래스"""
    
    def __init__(self, name: str, weight: float = 1.0):
        self.name = name
        self.weight = weight  # Orchestrator에서 가중치 적용
    
    @abstractmethod
    async def analyze(self, claim: Claim, context: dict = None) -> AgentResult:
        """청구 분석 수행 - 각 Agent가 구현"""
        pass
    
    def _create_result(
        self, 
        risk_score: float, 
        confidence: float,
        findings: list,
        evidence: dict
    ) -> AgentResult:
        """표준화된 결과 생성"""
        return AgentResult(
            agent_name=self.name,
            risk_score=risk_score,
            confidence=confidence,
            findings=findings,
            evidence=evidence
        )
