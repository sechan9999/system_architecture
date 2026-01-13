# agents/graph_agent.py
"""
Knowledge Graph Agent

Neo4j Knowledge Graph를 활용하여 네트워크 기반 사기 탐지를 수행합니다.
- Provider 네트워크 분석
- 사기 링 연관성 체크
- Beneficiary Doctor Shopping 탐지
"""
import sys
sys.path.insert(0, '/home/claude/compound_ai_system')

from models.schemas import Claim, AgentResult
from agents.base_agent import BaseAgent
from knowledge_graph.graph_manager import KnowledgeGraphManager

class KnowledgeGraphAgent(BaseAgent):
    """Knowledge Graph 기반 분석 Agent"""
    
    def __init__(self):
        super().__init__(name="KnowledgeGraphAgent", weight=0.35)
        self.graph_manager = KnowledgeGraphManager(use_neo4j=False)
        
        # 사기 링 사전 탐지
        self.fraud_rings = self.graph_manager.find_fraud_rings(min_size=3)
        self.fraud_ring_members = set()
        for ring in self.fraud_rings:
            self.fraud_ring_members.update(ring["members"])
    
    async def analyze(self, claim: Claim, context: dict = None) -> AgentResult:
        """Knowledge Graph 기반 분석 수행"""
        findings = []
        evidence = {}
        risk_scores = []
        
        provider_id = claim.provider_id
        beneficiary_id = claim.beneficiary_id
        
        # 1. Provider가 사기 링에 포함되어 있는지 체크
        if provider_id in self.fraud_ring_members:
            findings.append(f"Provider {provider_id}는 의심스러운 네트워크 그룹에 포함됨")
            risk_scores.append(0.8)
            evidence["in_fraud_ring"] = True
            
            # 어떤 링에 속해있는지 찾기
            for ring in self.fraud_rings:
                if provider_id in ring["members"]:
                    evidence["fraud_ring"] = {
                        "members": ring["members"],
                        "ring_risk_score": ring["risk_score"]
                    }
                    break
        else:
            evidence["in_fraud_ring"] = False
        
        # 2. Provider 네트워크 분석
        provider_network = self.graph_manager.get_provider_network(provider_id)
        
        if "error" not in provider_network:
            evidence["provider_network"] = {
                "referral_partners_count": len(provider_network["referral_partners"]),
                "total_beneficiaries": provider_network.get("total_beneficiaries", 0),
                "network_risk_score": provider_network["network_risk_score"]
            }
            
            # 많은 상호 의뢰 관계는 의심
            if len(provider_network["referral_partners"]) > 5:
                findings.append(f"Provider가 {len(provider_network['referral_partners'])}개의 상호 의뢰 관계 보유")
                risk_scores.append(0.6)
            
            # 네트워크 위험 점수
            if provider_network["network_risk_score"] > 0.5:
                findings.append(f"Provider 네트워크 위험 점수 높음: {provider_network['network_risk_score']}")
                risk_scores.append(provider_network["network_risk_score"])
        
        # 3. Beneficiary Doctor Shopping 분석
        beneficiary_journey = self.graph_manager.get_beneficiary_journey(beneficiary_id)
        
        if "error" not in beneficiary_journey:
            evidence["beneficiary_journey"] = {
                "unique_providers": beneficiary_journey["unique_providers"],
                "total_claims": beneficiary_journey["total_claims"],
                "doctor_shopping_score": beneficiary_journey["doctor_shopping_score"]
            }
            
            if beneficiary_journey["doctor_shopping_score"] > 0.5:
                findings.append(f"Beneficiary Doctor Shopping 의심: {beneficiary_journey['unique_providers']}명의 Provider 방문")
                risk_scores.append(beneficiary_journey["doctor_shopping_score"])
        
        # 4. Provider-Beneficiary 관계 분석
        claim_context = self.graph_manager.get_claim_context(provider_id, beneficiary_id)
        
        evidence["prior_claims_together"] = claim_context["prior_claims_together"]
        evidence["relationship_risk_score"] = claim_context["relationship_risk_score"]
        
        # 처음 관계인데 고액 청구는 의심
        if claim_context["prior_claims_together"] == 0 and claim.claim_amount > 1000:
            findings.append("첫 방문에 고액 청구 - 관계 이력 없음")
            risk_scores.append(0.5)
        
        # 최종 점수 계산
        if risk_scores:
            final_score = sum(risk_scores) / len(risk_scores)
        else:
            final_score = 0.15
            findings.append("Knowledge Graph 분석 결과 이상 없음")
        
        confidence = 0.85  # 그래프 분석은 신뢰도 높음
        
        return self._create_result(
            risk_score=min(final_score, 1.0),
            confidence=confidence,
            findings=findings,
            evidence=evidence
        )


# 테스트
async def test_graph_agent():
    """Knowledge Graph Agent 테스트"""
    from datetime import datetime
    
    agent = KnowledgeGraphAgent()
    
    # 사기 링에 포함된 Provider로 테스트
    test_claim = Claim(
        claim_id="TEST001",
        provider_id="PRV001",  # 사기 링 멤버
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
    
    print("\n🔗 Knowledge Graph Agent Test Result:")
    print(f"   Risk Score: {result.risk_score:.2f}")
    print(f"   Confidence: {result.confidence:.2f}")
    print(f"   Findings:")
    for f in result.findings:
        print(f"      • {f}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_graph_agent())
