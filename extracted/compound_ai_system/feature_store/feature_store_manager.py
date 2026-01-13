# feature_store/feature_store_manager.py
"""
Feature Store Manager

Feature Store 초기화, 데이터 적재, Feature 조회를 담당합니다.
실제 환경에서는 Databricks/Spark와 연동하여 대규모 데이터를 처리합니다.
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Feast imports
# from feast import FeatureStore
# from feast.repo_config import RepoConfig
FeatureStore = None  # Mock

class FeatureStoreManager:
    """Feature Store 관리 클래스"""
    
    def __init__(self, repo_path: str = None):
        if repo_path is None:
            # Use directory of this file as default
            repo_path = str(Path(__file__).parent)
            
        self.repo_path = Path(repo_path)
        self.data_path = self.repo_path / "data"
        self.data_path.mkdir(parents=True, exist_ok=True)
        self.store = None
    
    def generate_sample_data(self, n_providers: int = 100, n_beneficiaries: int = 500):
        """
        샘플 Feature 데이터 생성
        
        실제 환경에서는 이 데이터가 ETL 파이프라인에서 생성됩니다.
        - Bronze: Raw claims data
        - Silver: Cleaned & validated
        - Gold: Aggregated features (여기서 사용)
        """
        np.random.seed(42)
        
        # Provider Features 생성
        print("📊 Generating provider features...")
        provider_ids = [f"PRV{str(i).zfill(3)}" for i in range(1, n_providers + 1)]
        
        # 일부 Provider에 높은 위험 점수 부여 (사기 의심)
        high_risk_providers = np.random.choice(provider_ids, size=int(n_providers * 0.1), replace=False)
        
        provider_data = []
        for pid in provider_ids:
            is_high_risk = pid in high_risk_providers
            
            provider_data.append({
                "provider_id": pid,
                "event_timestamp": datetime.now() - timedelta(hours=1),
                "avg_claim_amount_30d": np.random.exponential(2000) if is_high_risk else np.random.exponential(500),
                "total_claims_30d": int(np.random.exponential(50)) if is_high_risk else int(np.random.exponential(15)),
                "denial_rate_90d": np.random.beta(5, 2) if is_high_risk else np.random.beta(1, 10),
                "unique_beneficiaries_30d": int(np.random.exponential(100)) if is_high_risk else int(np.random.exponential(20)),
                "specialty_risk_score": np.random.uniform(0.6, 0.9) if is_high_risk else np.random.uniform(0.1, 0.4),
                "sanctions_flag": 1 if pid in ["PRV999", "PRV888"] else 0,
            })
        
        provider_df = pd.DataFrame(provider_data)
        provider_df["event_timestamp"] = pd.to_datetime(provider_df["event_timestamp"])
        
        # Float32로 변환
        float_cols = ["avg_claim_amount_30d", "denial_rate_90d", "specialty_risk_score"]
        for col in float_cols:
            provider_df[col] = provider_df[col].astype("float32")
        
        int_cols = ["total_claims_30d", "unique_beneficiaries_30d", "sanctions_flag"]
        for col in int_cols:
            provider_df[col] = provider_df[col].astype("int64")
        
        # Beneficiary Features 생성
        print("📊 Generating beneficiary features...")
        beneficiary_ids = [f"BEN{str(i).zfill(4)}" for i in range(1, n_beneficiaries + 1)]
        
        beneficiary_data = []
        for bid in beneficiary_ids:
            beneficiary_data.append({
                "beneficiary_id": bid,
                "event_timestamp": datetime.now() - timedelta(hours=1),
                "total_claims_ytd": int(np.random.exponential(10)),
                "total_amount_ytd": float(np.random.exponential(5000)),
                "unique_providers_90d": int(np.random.poisson(3)),
                "er_visits_30d": int(np.random.poisson(0.5)),
                "chronic_condition_count": int(np.random.poisson(2)),
                "risk_adjustment_factor": float(np.random.uniform(0.5, 2.0)),
            })
        
        beneficiary_df = pd.DataFrame(beneficiary_data)
        beneficiary_df["event_timestamp"] = pd.to_datetime(beneficiary_df["event_timestamp"])
        
        # 타입 변환
        beneficiary_df["total_amount_ytd"] = beneficiary_df["total_amount_ytd"].astype("float32")
        beneficiary_df["risk_adjustment_factor"] = beneficiary_df["risk_adjustment_factor"].astype("float32")
        for col in ["total_claims_ytd", "unique_providers_90d", "er_visits_30d", "chronic_condition_count"]:
            beneficiary_df[col] = beneficiary_df[col].astype("int64")
        
        # Parquet 저장
        provider_path = self.data_path / "provider_features.parquet"
        beneficiary_path = self.data_path / "beneficiary_features.parquet"
        
        provider_df.to_parquet(provider_path, index=False)
        beneficiary_df.to_parquet(beneficiary_path, index=False)
        
        print(f"✅ Provider features saved: {provider_path}")
        print(f"   Shape: {provider_df.shape}")
        print(f"✅ Beneficiary features saved: {beneficiary_path}")
        print(f"   Shape: {beneficiary_df.shape}")
        
        return provider_df, beneficiary_df
    
    def initialize_store(self):
        """Feature Store 초기화 및 등록 (Mock)"""
        print("\n🔧 Initializing Feature Store (Mock)...")
        print("✅ Feature Store initialized")
        return self.store
    
    def materialize_features(self):
        """Online Store에 Feature 적재 (Mock)"""
        print("\n⬆️ Materializing features to online store (Mock)...")
        print("✅ Features materialized to online store")
    
    def get_online_features(self, provider_id: str = None, beneficiary_id: str = None) -> dict:
        """
        Online Store에서 실시간 Feature 조회 (Mock)
        """
        features_dict = {}
        
        if provider_id:
            # Mock logic based on ID
            is_risky = provider_id in ["PRV001", "PRV999", "PRV888"] 
            features_dict["provider"] = {
                "avg_claim_amount_30d": 2000.0 if is_risky else 500.0,
                "total_claims_30d": 50 if is_risky else 15,
                "denial_rate_90d": 0.8 if is_risky else 0.1,
                "unique_beneficiaries_30d": 100 if is_risky else 20,
                "specialty_risk_score": 0.8 if is_risky else 0.2,
                "sanctions_flag": 1 if provider_id in ["PRV999", "PRV888"] else 0,
            }
        
        if beneficiary_id:
            features_dict["beneficiary"] = {
                "total_claims_ytd": 10,
                "total_amount_ytd": 5000.0,
                "unique_providers_90d": 3,
                "er_visits_30d": 0,
                "chronic_condition_count": 2,
                "risk_adjustment_factor": 1.2,
            }
        
        return features_dict
        
        return features_dict
    
    def get_historical_features(
        self, 
        entity_df: pd.DataFrame,
        feature_refs: list
    ) -> pd.DataFrame:
        """
        Offline Store에서 학습용 Historical Feature 조회
        
        Point-in-Time Join을 수행하여 데이터 누수 방지.
        """
        if self.store is None:
            self.initialize_store()
        
        training_df = self.store.get_historical_features(
            entity_df=entity_df,
            features=feature_refs
        ).to_df()
        
        return training_df


# ============================================================
# 실행 예시
# ============================================================
def demo_feature_store():
    """Feature Store 데모"""
    print("=" * 60)
    print("🏪 FEATURE STORE DEMO")
    print("=" * 60)
    
    manager = FeatureStoreManager()
    
    # Step 1: 샘플 데이터 생성
    provider_df, beneficiary_df = manager.generate_sample_data(
        n_providers=100, 
        n_beneficiaries=500
    )
    
    # Step 2: Feature Store 초기화
    manager.initialize_store()
    
    # Step 3: 샘플 Feature 조회 (파일에서 직접)
    print("\n📖 Sample Provider Features:")
    print(provider_df.head(3).to_string())
    
    print("\n📖 Sample Beneficiary Features:")
    print(beneficiary_df.head(3).to_string())
    
    # Step 4: 특정 Provider Feature 조회 (시뮬레이션)
    print("\n🔍 Looking up features for PRV001...")
    prv_features = provider_df[provider_df["provider_id"] == "PRV001"].iloc[0].to_dict()
    print(f"   avg_claim_amount_30d: ${prv_features['avg_claim_amount_30d']:,.2f}")
    print(f"   denial_rate_90d: {prv_features['denial_rate_90d']*100:.1f}%")
    print(f"   sanctions_flag: {prv_features['sanctions_flag']}")
    
    return manager


if __name__ == "__main__":
    demo_feature_store()
