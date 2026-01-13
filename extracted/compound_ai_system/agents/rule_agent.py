# agents/rule_agent.py
from datetime import datetime
import sys
sys.path.insert(0, '/home/claude/compound_ai_system')
from models.schemas import Claim, AgentResult
from agents.base_agent import BaseAgent

class RuleComplianceAgent(BaseAgent):
    """규칙 기반 컴플라이언스 검증 Agent"""
    
    def __init__(self):
        super().__init__(name="RuleComplianceAgent", weight=0.3)
        
        # CMS 규정 기반 규칙
        self.rules = {
            "max_claim_amounts": {
                "99213": 150,
                "99214": 200,
                "99215": 300,
                "93000": 50,
                "93306": 800,
            },
            "excluded_providers": ["PRV999", "PRV888"],
            "weekend_procedures": ["99281", "99282", "99283"],
        }
    
    async def analyze(self, claim: Claim, context: dict = None) -> AgentResult:
        findings = []
        evidence = {}
        violations = []
        
        # Rule 1: 청구 금액 상한 검증
        proc_code = claim.procedure_code[:5]
        if proc_code in self.rules["max_claim_amounts"]:
            max_amount = self.rules["max_claim_amounts"][proc_code]
            if claim.claim_amount > max_amount * 1.5:
                findings.append(f"청구 금액이 CMS 상한의 150% 초과: ${claim.claim_amount} > ${max_amount}")
                violations.append(("max_amount", 0.9))
                evidence["max_allowed"] = max_amount
                evidence["actual_amount"] = claim.claim_amount
        
        # Rule 2: 제재된 Provider 체크
        if claim.provider_id in self.rules["excluded_providers"]:
            findings.append(f"Provider {claim.provider_id}는 제재 목록에 있음")
            violations.append(("excluded_provider", 1.0))
            evidence["exclusion_status"] = "EXCLUDED"
        
        # Rule 3: 주말 비응급 시술 체크
        if claim.service_date.weekday() >= 5:
            if claim.procedure_code[:5] not in self.rules["weekend_procedures"]:
                findings.append(f"주말에 비응급 시술 청구: {claim.procedure_code}")
                violations.append(("weekend_non_emergency", 0.6))
                evidence["service_day"] = claim.service_date.strftime("%A")
        
        # Rule 4: 미래 날짜 청구 체크
        if claim.service_date > datetime.now():
            findings.append("서비스 날짜가 미래임 - 명백한 규정 위반")
            violations.append(("future_date", 1.0))
        
        # Rule 5: 나이 제한 시술 체크
        age_restricted = {
            "G0402": (65, 999),
            "G0438": (65, 999),
        }
        if claim.procedure_code in age_restricted:
            min_age, max_age = age_restricted[claim.procedure_code]
            if not (min_age <= claim.beneficiary_age <= max_age):
                findings.append(f"나이 제한 위반: {claim.procedure_code}는 {min_age}-{max_age}세만 가능")
                violations.append(("age_restriction", 0.8))
        
        # 점수 계산
        if violations:
            risk_score = max(v[1] for v in violations)
            confidence = 0.95
        else:
            risk_score = 0.05
            confidence = 0.95
            findings.append("모든 컴플라이언스 규칙 통과")
        
        evidence["violations_count"] = len(violations)
        evidence["rules_checked"] = 5
        
        return self._create_result(
            risk_score=risk_score,
            confidence=confidence,
            findings=findings,
            evidence=evidence
        )
