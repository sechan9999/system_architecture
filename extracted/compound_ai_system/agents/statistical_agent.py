# agents/statistical_agent.py
import numpy as np
import sys
sys.path.insert(0, '/home/claude/compound_ai_system')
from models.schemas import Claim, AgentResult
from agents.base_agent import BaseAgent

class StatisticalAnomalyAgent(BaseAgent):
    """통계 기반 이상 탐지 Agent"""
    
    def __init__(self):
        super().__init__(name="StatisticalAnomalyAgent", weight=0.3)
        
        # 실제로는 DB에서 로드 - 여기선 시뮬레이션
        self.benchmarks = {
            "avg_claim_by_specialty": {
                "Cardiology": 1500,
                "Orthopedics": 2000,
                "General Practice": 200,
                "Oncology": 5000,
            },
            "std_claim_by_specialty": {
                "Cardiology": 500,
                "Orthopedics": 700,
                "General Practice": 100,
                "Oncology": 2000,
            },
            "procedure_frequency": {
                "99213": 0.15,  # Office visit
                "99214": 0.12,
                "99215": 0.05,  # High complexity - 드묾
            }
        }
    
    async def analyze(self, claim: Claim, context: dict = None) -> AgentResult:
        findings = []
        evidence = {}
        risk_scores = []
        
        # 1. 청구 금액 Z-score 분석
        specialty = claim.provider_specialty
        if specialty in self.benchmarks["avg_claim_by_specialty"]:
            avg = self.benchmarks["avg_claim_by_specialty"][specialty]
            std = self.benchmarks["std_claim_by_specialty"][specialty]
            
            z_score = (claim.claim_amount - avg) / std if std > 0 else 0
            evidence["z_score"] = round(z_score, 2)
            evidence["specialty_avg"] = avg
            
            if abs(z_score) > 3:
                findings.append(f"청구 금액이 전문 분야 평균 대비 극단적 이상치 (Z={z_score:.1f})")
                risk_scores.append(0.9)
            elif abs(z_score) > 2:
                findings.append(f"청구 금액이 전문 분야 평균 대비 높음 (Z={z_score:.1f})")
                risk_scores.append(0.6)
            else:
                risk_scores.append(0.1)
        
        # 2. 청구 금액 Benford's Law 검증 (첫 자릿수 분포)
        first_digit = int(str(int(claim.claim_amount))[0])
        
        # 9로 시작하는 금액은 의심 (자연 발생 확률 4.6%)
        if first_digit == 9:
            findings.append("청구 금액이 9로 시작 - Benford's Law 위반 가능성")
            risk_scores.append(0.5)
            evidence["benford_anomaly"] = True
        
        # 3. 연령-시술 적합성 검사
        if claim.beneficiary_age < 40 and claim.procedure_code in ["93000", "93306"]:
            findings.append(f"40세 미만 환자에게 심장 시술 청구")
            risk_scores.append(0.4)
            evidence["age_procedure_mismatch"] = True
        
        # 최종 점수 계산
        final_score = np.mean(risk_scores) if risk_scores else 0.1
        confidence = 0.85 if len(risk_scores) >= 2 else 0.6
        
        if not findings:
            findings.append("통계적 이상 징후 없음")
        
        return self._create_result(
            risk_score=min(final_score, 1.0),
            confidence=confidence,
            findings=findings,
            evidence=evidence
        )
