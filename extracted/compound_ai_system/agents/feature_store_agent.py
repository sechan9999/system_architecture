# agents/feature_store_agent.py
"""
Feature Store 연동 Agent

Feature Store에서 실시간으로 Feature를 조회하여 분석에 활용합니다.
이를 통해 Training과 Serving에서 동일한 Feature를 사용할 수 있습니다.
"""
import pandas as pd
import numpy as np
from pathlib import Path
import sys
sys.path.insert(0, '/home/claude/compound_ai_system')

from models.schemas import Claim, AgentResult
from agents.base_agent import BaseAgent

class FeatureStoreAgent(BaseAgent):
    """Feature Store 기반 분석 Agent"""
    
    def __init__(self, data_path: str = "/home/claude/compound_ai_system/feature_store/data"):
        super().__init__(name="FeatureStoreAgent", weight=0.35)
        self.data_path = Path(data_path)
        
        # Feature 데이터 로드 (실제로는 Online Store에서 실시간 조회)
        self._load_features()
    
    def _load_features(self):
        """Feature 데이터 로드"""
        provider_path = self.data_path / "provider_features.parquet"
        beneficiary_path = self.data_path / "beneficiary_features.parquet"
        
        if provider_path.exists():
            self.provider_features = pd.read_parquet(provider_path)
            self.provider_features.set_index("provider_id", inplace=True)
        else:
            self.provider_features = pd.DataFrame()
        
        if beneficiary_path.exists():
            self.beneficiary_features = pd.read_parquet(beneficiary_path)
            self.beneficiary_features.set_index("beneficiary_id", inplace=True)
        else:
            self.beneficiary_features = pd.DataFrame()
    
    def _get_provider_features(self, provider_id: str) -> dict:
        """Provider Feature 조회"""
        if provider_id in self.provider_features.index:
            return self.provider_features.loc[provider_id].to_dict()
        return None
    
    def _get_beneficiary_features(self, beneficiary_id: str) -> dict:
        """Beneficiary Feature 조회"""
        if beneficiary_id in self.beneficiary_features.index:
            return self.beneficiary_features.loc[beneficiary_id].to_dict()
        return None
    
    async def analyze(self, claim: Claim, context: dict = None) -> AgentResult:
        """Feature Store 기반 분석 수행"""
        findings = []
        evidence = {}
        risk_scores = []
        
        # 1. Provider Features 분석
        provider_feats = self._get_provider_features(claim.provider_id)
        
        if provider_feats:
            evidence["provider_features"] = {
                "avg_claim_30d": round(provider_feats.get("avg_claim_amount_30d", 0), 2),
                "denial_rate_90d": round(provider_feats.get("denial_rate_90d", 0), 3),
                "sanctions_flag": int(provider_feats.get("sanctions_flag", 0))
            }
            
            # 제재 Provider 체크
            if provider_feats.get("sanctions_flag", 0) == 1:
                findings.append(f"Provider {claim.provider_id}는 제재 목록에 있음 (Feature Store)")
                risk_scores.append(1.0)
            
            # 높은 거부율 체크
            denial_rate = provider_feats.get("denial_rate_90d", 0)
            if denial_rate > 0.2:
                findings.append(f"Provider 90일 거부율이 높음: {denial_rate*100:.1f}%")
                risk_scores.append(0.7)
            
            # 청구 금액 대비 분석
            avg_claim = provider_feats.get("avg_claim_amount_30d", 0)
            if avg_claim > 0:
                ratio = claim.claim_amount / avg_claim
                evidence["claim_to_avg_ratio"] = round(ratio, 2)
                
                if ratio > 5:
                    findings.append(f"청구 금액이 Provider 평균의 {ratio:.1f}배")
                    risk_scores.append(0.8)
                elif ratio > 3:
                    findings.append(f"청구 금액이 Provider 평균의 {ratio:.1f}배")
                    risk_scores.append(0.5)
            
            # 전문 분야 위험 점수
            specialty_risk = provider_feats.get("specialty_risk_score", 0)
            if specialty_risk > 0.6:
                findings.append(f"Provider 전문 분야 기본 위험 점수 높음: {specialty_risk:.2f}")
                risk_scores.append(specialty_risk)
        else:
            findings.append(f"Provider {claim.provider_id} Feature 없음 - 신규 또는 알 수 없는 Provider")
            risk_scores.append(0.4)
            evidence["provider_features"] = None
        
        # 2. Beneficiary Features 분석
        beneficiary_feats = self._get_beneficiary_features(claim.beneficiary_id)
        
        if beneficiary_feats:
            evidence["beneficiary_features"] = {
                "total_claims_ytd": int(beneficiary_feats.get("total_claims_ytd", 0)),
                "unique_providers_90d": int(beneficiary_feats.get("unique_providers_90d", 0)),
                "chronic_conditions": int(beneficiary_feats.get("chronic_condition_count", 0))
            }
            
            # 많은 Provider 방문 체크 (Doctor Shopping 의심)
            unique_providers = beneficiary_feats.get("unique_providers_90d", 0)
            if unique_providers > 10:
                findings.append(f"Beneficiary가 90일간 {unique_providers}명의 Provider 방문 (Doctor Shopping 의심)")
                risk_scores.append(0.7)
            
            # 연간 청구 건수 체크
            total_claims = beneficiary_feats.get("total_claims_ytd", 0)
            if total_claims > 50:
                findings.append(f"Beneficiary 연간 청구 건수 과다: {total_claims}건")
                risk_scores.append(0.6)
        else:
            evidence["beneficiary_features"] = None
        
        # 최종 점수 계산
        if risk_scores:
            final_score = np.mean(risk_scores)
        else:
            final_score = 0.1
            findings.append("Feature Store 분석 결과 이상 없음")
        
        confidence = 0.9 if provider_feats else 0.5
        
        return self._create_result(
            risk_score=min(final_score, 1.0),
            confidence=confidence,
            findings=findings,
            evidence=evidence
        )


# 테스트
async def test_feature_store_agent():
    """Feature Store Agent 테스트"""
    from datetime import datetime
    
    # 먼저 Feature 데이터 생성
    sys.path.insert(0, '/home/claude/compound_ai_system/feature_store')
    from feature_store_manager import FeatureStoreManager
    
    manager = FeatureStoreManager()
    manager.generate_sample_data()
    
    # Agent 테스트
    agent = FeatureStoreAgent()
    
    test_claim = Claim(
        claim_id="TEST001",
        provider_id="PRV001",
        beneficiary_id="BEN0001",
        procedure_code="99213",
        diagnosis_code="J06.9",
        claim_amount=5000.0,
        service_date=datetime.now(),
        provider_specialty="General Practice",
        beneficiary_age=45,
        beneficiary_state="CA"
    )
    
    result = await agent.analyze(test_claim)
    
    print("\n🏪 Feature Store Agent Test Result:")
    print(f"   Risk Score: {result.risk_score:.2f}")
    print(f"   Confidence: {result.confidence:.2f}")
    print(f"   Findings: {result.findings}")
    print(f"   Evidence: {result.evidence}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_feature_store_agent())
