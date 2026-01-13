# agents/ml_agent.py
import numpy as np
from sklearn.ensemble import IsolationForest
import sys
sys.path.insert(0, '/home/claude/compound_ai_system')
from models.schemas import Claim, AgentResult
from agents.base_agent import BaseAgent

class MLPatternAgent(BaseAgent):
    """ML 모델 기반 패턴 분석 Agent"""
    
    def __init__(self):
        super().__init__(name="MLPatternAgent", weight=0.4)
        
        # Isolation Forest 모델 초기화
        self.isolation_forest = IsolationForest(
            contamination=0.1,
            random_state=42,
            n_estimators=100
        )
        self._train_model()
        
        # Provider 과거 이력 시뮬레이션
        self.provider_history = {
            "PRV001": {"avg_claims_per_day": 15, "denial_rate": 0.05},
            "PRV002": {"avg_claims_per_day": 50, "denial_rate": 0.25},  # 의심
            "PRV003": {"avg_claims_per_day": 8, "denial_rate": 0.02},
        }
    
    def _train_model(self):
        """시뮬레이션용 모델 학습"""
        np.random.seed(42)
        normal_data = np.random.randn(1000, 4) * [500, 10, 50, 5] + [1000, 30, 100, 10]
        self.isolation_forest.fit(normal_data)
    
    def _extract_features(self, claim: Claim) -> np.ndarray:
        """청구에서 특징 추출"""
        return np.array([[
            claim.claim_amount,
            claim.beneficiary_age,
            len(claim.diagnosis_code),
            len(claim.procedure_code)
        ]])
    
    async def analyze(self, claim: Claim, context: dict = None) -> AgentResult:
        findings = []
        evidence = {}
        risk_scores = []
        
        # 1. Isolation Forest 이상 탐지
        features = self._extract_features(claim)
        anomaly_score = -self.isolation_forest.score_samples(features)[0]
        
        normalized_score = min(max((anomaly_score + 0.5) / 1.0, 0), 1)
        evidence["isolation_forest_score"] = round(anomaly_score, 3)
        
        if normalized_score > 0.7:
            findings.append(f"ML 모델이 이상 패턴 감지 (anomaly_score={anomaly_score:.2f})")
            risk_scores.append(normalized_score)
        else:
            risk_scores.append(0.2)
        
        # 2. Provider 이력 기반 분석
        provider_id = claim.provider_id
        if provider_id in self.provider_history:
            history = self.provider_history[provider_id]
            evidence["provider_denial_rate"] = history["denial_rate"]
            
            if history["denial_rate"] > 0.15:
                findings.append(f"Provider의 과거 청구 거부율이 높음 ({history['denial_rate']*100:.0f}%)")
                risk_scores.append(0.7)
            
            if history["avg_claims_per_day"] > 40:
                findings.append(f"Provider의 일평균 청구 건수가 비정상적으로 높음 ({history['avg_claims_per_day']}건)")
                risk_scores.append(0.6)
        
        # 3. 시술-진단 코드 조합 분석
        suspicious_combos = [
            ("99215", "Z00"),
            ("93306", "M54"),
        ]
        
        for proc, diag in suspicious_combos:
            if claim.procedure_code.startswith(proc) and claim.diagnosis_code.startswith(diag):
                findings.append(f"의심스러운 시술-진단 조합: {proc}-{diag}")
                risk_scores.append(0.8)
                evidence["suspicious_combo"] = f"{proc}-{diag}"
        
        final_score = np.mean(risk_scores) if risk_scores else 0.15
        confidence = 0.75
        
        if not findings:
            findings.append("ML 패턴 분석 결과 이상 없음")
        
        return self._create_result(
            risk_score=min(final_score, 1.0),
            confidence=confidence,
            findings=findings,
            evidence=evidence
        )
