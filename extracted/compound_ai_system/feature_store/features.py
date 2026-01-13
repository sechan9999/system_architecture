# feature_store/features.py
"""
Feast Feature Definitions for Healthcare Fraud Detection

이 파일은 Provider와 Beneficiary에 대한 Feature를 정의합니다.
Feature Store를 통해 Training과 Serving에서 동일한 Feature를 사용합니다.
"""
from datetime import timedelta
from feast import Entity, Feature, FeatureView, Field, FileSource
from feast.types import Float32, Int64, String

# ============================================================
# ENTITIES (Feature의 Primary Key)
# ============================================================

# Provider Entity - 의료 제공자
provider_entity = Entity(
    name="provider",
    join_keys=["provider_id"],
    description="Healthcare provider entity"
)

# Beneficiary Entity - 환자/수혜자
beneficiary_entity = Entity(
    name="beneficiary", 
    join_keys=["beneficiary_id"],
    description="Medicare beneficiary entity"
)

# ============================================================
# DATA SOURCES (Feature 원본 데이터)
# ============================================================

# Provider Features Source (Parquet 파일)
provider_source = FileSource(
    name="provider_features_source",
    path="/home/claude/compound_ai_system/feature_store/data/provider_features.parquet",
    timestamp_field="event_timestamp",
)

# Beneficiary Features Source
beneficiary_source = FileSource(
    name="beneficiary_features_source",
    path="/home/claude/compound_ai_system/feature_store/data/beneficiary_features.parquet",
    timestamp_field="event_timestamp",
)

# ============================================================
# FEATURE VIEWS (Feature 그룹 정의)
# ============================================================

# Provider Feature View
provider_features = FeatureView(
    name="provider_features",
    entities=[provider_entity],
    ttl=timedelta(days=365),
    schema=[
        Field(name="avg_claim_amount_30d", dtype=Float32, description="30일 평균 청구 금액"),
        Field(name="total_claims_30d", dtype=Int64, description="30일 총 청구 건수"),
        Field(name="denial_rate_90d", dtype=Float32, description="90일 거부율"),
        Field(name="unique_beneficiaries_30d", dtype=Int64, description="30일 고유 환자 수"),
        Field(name="specialty_risk_score", dtype=Float32, description="전문 분야별 기본 위험 점수"),
        Field(name="sanctions_flag", dtype=Int64, description="제재 플래그 (0/1)"),
    ],
    source=provider_source,
    online=True,  # Online serving 활성화
    tags={"team": "fraud_detection", "version": "v1"}
)

# Beneficiary Feature View
beneficiary_features = FeatureView(
    name="beneficiary_features",
    entities=[beneficiary_entity],
    ttl=timedelta(days=365),
    schema=[
        Field(name="total_claims_ytd", dtype=Int64, description="연간 총 청구 건수"),
        Field(name="total_amount_ytd", dtype=Float32, description="연간 총 청구 금액"),
        Field(name="unique_providers_90d", dtype=Int64, description="90일 고유 Provider 수"),
        Field(name="er_visits_30d", dtype=Int64, description="30일 응급실 방문 횟수"),
        Field(name="chronic_condition_count", dtype=Int64, description="만성 질환 수"),
        Field(name="risk_adjustment_factor", dtype=Float32, description="위험 조정 계수"),
    ],
    source=beneficiary_source,
    online=True,
    tags={"team": "fraud_detection", "version": "v1"}
)
