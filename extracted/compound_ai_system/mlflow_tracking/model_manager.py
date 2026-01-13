# mlflow_tracking/model_manager.py
"""
MLflow Model Manager

Agent 모델의 전체 라이프사이클을 관리합니다:
- 모델 학습 로깅
- 실험 추적
- 모델 버전 관리
- 모델 배포 (Staging → Production)

Production 환경에서의 Best Practice:
1. 모든 실험은 MLflow에 기록
2. Model Registry로 버전 관리
3. A/B Testing을 통한 점진적 배포
"""
import mlflow
import mlflow.sklearn
from mlflow.tracking import MlflowClient
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_score, recall_score, f1_score, roc_auc_score
from datetime import datetime
import json
import os
import warnings
warnings.filterwarnings('ignore')

# MLflow 설정
# MLflow 설정
current_dir = os.path.dirname(os.path.abspath(__file__))
mlruns_dir = os.path.join(current_dir, "mlruns")
# Ensure correct URI format for Windows
TRACKING_URI = f"file:///{mlruns_dir.replace(os.path.sep, '/')}"
EXPERIMENT_NAME = "fraud_detection_agents"

class MLflowModelManager:
    """MLflow 기반 모델 관리 클래스"""
    
    def __init__(self):
        # MLflow 초기화
        mlflow.set_tracking_uri(TRACKING_URI)
        
        # 실험 생성 또는 가져오기
        try:
            self.experiment_id = mlflow.create_experiment(EXPERIMENT_NAME)
        except:
            self.experiment_id = mlflow.get_experiment_by_name(EXPERIMENT_NAME).experiment_id
        
        mlflow.set_experiment(EXPERIMENT_NAME)
        self.client = MlflowClient()
        
        print(f"✅ MLflow initialized")
        print(f"   Tracking URI: {TRACKING_URI}")
        print(f"   Experiment: {EXPERIMENT_NAME}")
    
    def generate_training_data(self, n_samples: int = 10000) -> tuple:
        """
        학습용 샘플 데이터 생성
        
        실제 환경에서는 Feature Store에서 가져옴
        """
        np.random.seed(42)
        
        # 정상 데이터 (90%)
        n_normal = int(n_samples * 0.9)
        normal_data = np.column_stack([
            np.random.exponential(500, n_normal),      # claim_amount
            np.random.randint(20, 85, n_normal),       # beneficiary_age
            np.random.beta(1, 10, n_normal),           # provider_denial_rate
            np.random.poisson(3, n_normal),            # unique_providers_90d
            np.random.exponential(15, n_normal),       # total_claims_30d
        ])
        normal_labels = np.zeros(n_normal)
        
        # 사기 데이터 (10%)
        n_fraud = n_samples - n_normal
        fraud_data = np.column_stack([
            np.random.exponential(2000, n_fraud),      # 높은 청구 금액
            np.random.randint(20, 85, n_fraud),
            np.random.beta(5, 2, n_fraud),             # 높은 거부율
            np.random.poisson(8, n_fraud),             # 많은 Provider
            np.random.exponential(50, n_fraud),        # 많은 청구
        ])
        fraud_labels = np.ones(n_fraud)
        
        X = np.vstack([normal_data, fraud_data])
        y = np.concatenate([normal_labels, fraud_labels])
        
        # 셔플
        idx = np.random.permutation(len(y))
        X, y = X[idx], y[idx]
        
        feature_names = [
            "claim_amount", "beneficiary_age", "provider_denial_rate",
            "unique_providers_90d", "total_claims_30d"
        ]
        
        return X, y, feature_names
    
    def train_isolation_forest(
        self, 
        X: np.ndarray, 
        y: np.ndarray,
        model_name: str = "fraud_isolation_forest",
        **params
    ) -> str:
        """
        Isolation Forest 모델 학습 및 MLflow 로깅
        
        Returns:
            run_id: MLflow run ID
        """
        # 기본 파라미터
        default_params = {
            "n_estimators": 100,
            "contamination": 0.1,
            "random_state": 42,
            "max_samples": "auto"
        }
        default_params.update(params)
        
        with mlflow.start_run(run_name=f"{model_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}") as run:
            # 파라미터 로깅
            mlflow.log_params(default_params)
            mlflow.log_param("model_type", "IsolationForest")
            mlflow.log_param("n_samples", len(y))
            mlflow.log_param("n_features", X.shape[1])
            
            # 모델 학습
            model = IsolationForest(**default_params)
            model.fit(X)
            
            # 예측 및 메트릭 계산
            # Isolation Forest는 -1(이상치), 1(정상) 반환
            predictions = model.predict(X)
            predictions_binary = (predictions == -1).astype(int)  # 이상치를 1로
            
            # 메트릭 계산
            precision = precision_score(y, predictions_binary, zero_division=0)
            recall = recall_score(y, predictions_binary, zero_division=0)
            f1 = f1_score(y, predictions_binary, zero_division=0)
            
            # 메트릭 로깅
            mlflow.log_metrics({
                "precision": precision,
                "recall": recall,
                "f1_score": f1,
                "fraud_detection_rate": recall,  # 사기 탐지율 = Recall
            })
            
            # 모델 저장
            mlflow.sklearn.log_model(
                model, 
                artifact_path="model",
                registered_model_name=model_name
            )
            
            # 추가 아티팩트 저장
            metrics_dict = {
                "precision": precision,
                "recall": recall,
                "f1_score": f1,
                "training_samples": len(y),
                "fraud_samples": int(y.sum()),
                "training_timestamp": datetime.now().isoformat()
            }
            
            metrics_path = os.path.join(os.environ.get('TEMP', '.'), 'metrics.json')
            with open(metrics_path, "w") as f:
                json.dump(metrics_dict, f, indent=2)
            mlflow.log_artifact(metrics_path)
            
            print(f"\n📊 Model Training Completed:")
            print(f"   Run ID: {run.info.run_id}")
            print(f"   Precision: {precision:.3f}")
            print(f"   Recall (Fraud Detection Rate): {recall:.3f}")
            print(f"   F1 Score: {f1:.3f}")
            
            return run.info.run_id
    
    def train_random_forest(
        self,
        X: np.ndarray,
        y: np.ndarray,
        model_name: str = "fraud_random_forest",
        **params
    ) -> str:
        """
        Random Forest 분류 모델 학습
        """
        # Train/Test 분할
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # 기본 파라미터
        default_params = {
            "n_estimators": 100,
            "max_depth": 10,
            "min_samples_split": 5,
            "random_state": 42,
            "class_weight": "balanced"
        }
        default_params.update(params)
        
        with mlflow.start_run(run_name=f"{model_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}") as run:
            # 파라미터 로깅
            mlflow.log_params(default_params)
            mlflow.log_param("model_type", "RandomForestClassifier")
            mlflow.log_param("train_samples", len(y_train))
            mlflow.log_param("test_samples", len(y_test))
            
            # 모델 학습
            model = RandomForestClassifier(**default_params)
            model.fit(X_train, y_train)
            
            # 예측
            y_pred = model.predict(X_test)
            y_pred_proba = model.predict_proba(X_test)[:, 1]
            
            # 메트릭 계산
            metrics = {
                "precision": precision_score(y_test, y_pred),
                "recall": recall_score(y_test, y_pred),
                "f1_score": f1_score(y_test, y_pred),
                "roc_auc": roc_auc_score(y_test, y_pred_proba),
            }
            
            mlflow.log_metrics(metrics)
            
            # Feature Importance 로깅
            feature_importance = dict(zip(
                [f"feature_{i}" for i in range(X.shape[1])],
                model.feature_importances_.tolist()
            ))
            mlflow.log_params({f"importance_{k}": round(v, 3) for k, v in feature_importance.items()})
            
            # 모델 저장
            mlflow.sklearn.log_model(
                model,
                artifact_path="model",
                registered_model_name=model_name
            )
            
            print(f"\n📊 Random Forest Training Completed:")
            print(f"   Run ID: {run.info.run_id}")
            print(f"   ROC-AUC: {metrics['roc_auc']:.3f}")
            print(f"   Precision: {metrics['precision']:.3f}")
            print(f"   Recall: {metrics['recall']:.3f}")
            
            return run.info.run_id
    
    def get_model_versions(self, model_name: str) -> list:
        """등록된 모델의 버전 목록 조회"""
        try:
            versions = self.client.search_model_versions(f"name='{model_name}'")
            return [
                {
                    "version": v.version,
                    "stage": v.current_stage,
                    "run_id": v.run_id,
                    "status": v.status
                }
                for v in versions
            ]
        except:
            return []
    
    def promote_model(self, model_name: str, version: int, stage: str = "Production"):
        """
        모델을 특정 스테이지로 승격
        
        Stages: None → Staging → Production → Archived
        """
        self.client.transition_model_version_stage(
            name=model_name,
            version=version,
            stage=stage
        )
        print(f"✅ Model {model_name} v{version} promoted to {stage}")
    
    def load_production_model(self, model_name: str):
        """Production 스테이지 모델 로드"""
        model_uri = f"models:/{model_name}/Production"
        try:
            model = mlflow.sklearn.load_model(model_uri)
            print(f"✅ Loaded {model_name} from Production")
            return model
        except Exception as e:
            print(f"⚠️ No Production model found: {e}")
            # Latest 버전 시도
            model_uri = f"models:/{model_name}/latest"
            return mlflow.sklearn.load_model(model_uri)
    
    def compare_experiments(self) -> pd.DataFrame:
        """실험 결과 비교"""
        runs = mlflow.search_runs(
            experiment_ids=[self.experiment_id],
            order_by=["metrics.f1_score DESC"]
        )
        
        if len(runs) == 0:
            return pd.DataFrame()
        
        # 주요 컬럼만 선택
        cols = [c for c in runs.columns if c.startswith(('metrics.', 'params.model_type', 'run_id'))]
        return runs[cols].head(10)


# ============================================================
# MLflow Agent Wrapper
# ============================================================
class MLflowAgentWrapper:
    """
    MLflow로 관리되는 모델을 Agent에서 사용하는 래퍼
    
    Production 환경에서:
    1. Model Registry에서 Production 모델 로드
    2. 추론 수행
    3. 예측 결과 로깅 (선택적)
    """
    
    def __init__(self, model_name: str):
        self.model_name = model_name
        mlflow.set_tracking_uri(TRACKING_URI)
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """모델 로드"""
        try:
            # Production 모델 시도
            model_uri = f"models:/{self.model_name}/Production"
            self.model = mlflow.sklearn.load_model(model_uri)
            self.model_stage = "Production"
        except:
            try:
                # Latest 버전 시도
                model_uri = f"models:/{self.model_name}/None"
                self.model = mlflow.sklearn.load_model(model_uri)
                self.model_stage = "None (Latest)"
            except Exception as e:
                print(f"⚠️ Could not load model {self.model_name}: {e}")
                self.model = None
                self.model_stage = None
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """예측 수행"""
        if self.model is None:
            raise ValueError("Model not loaded")
        return self.model.predict(X)
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """확률 예측 (지원되는 경우)"""
        if self.model is None:
            raise ValueError("Model not loaded")
        if hasattr(self.model, 'predict_proba'):
            return self.model.predict_proba(X)
        else:
            # Isolation Forest의 경우 score 사용
            scores = -self.model.score_samples(X)
            return scores


# ============================================================
# 데모 실행
# ============================================================
def demo_mlflow():
    """MLflow 데모"""
    print("=" * 60)
    print("📈 MLFLOW MODEL MANAGEMENT DEMO")
    print("=" * 60)
    
    manager = MLflowModelManager()
    
    # 1. 학습 데이터 생성
    print("\n📊 Generating training data...")
    X, y, feature_names = manager.generate_training_data(n_samples=5000)
    print(f"   Samples: {len(y)}, Features: {len(feature_names)}")
    print(f"   Fraud ratio: {y.mean()*100:.1f}%")
    
    # 2. Isolation Forest 학습
    print("\n🌲 Training Isolation Forest...")
    run_id_if = manager.train_isolation_forest(
        X, y, 
        model_name="fraud_isolation_forest",
        n_estimators=50,
        contamination=0.1
    )
    
    # 3. Random Forest 학습
    print("\n🌳 Training Random Forest...")
    run_id_rf = manager.train_random_forest(
        X, y,
        model_name="fraud_random_forest",
        n_estimators=50,
        max_depth=8
    )
    
    # 4. 모델 버전 확인
    print("\n📋 Model Versions:")
    for model_name in ["fraud_isolation_forest", "fraud_random_forest"]:
        versions = manager.get_model_versions(model_name)
        print(f"\n   {model_name}:")
        for v in versions[:3]:
            print(f"      v{v['version']}: {v['stage']}")
    
    # 5. 실험 비교
    print("\n📊 Experiment Comparison:")
    comparison = manager.compare_experiments()
    if len(comparison) > 0:
        print(comparison.to_string())
    
    return manager


if __name__ == "__main__":
    demo_mlflow()
