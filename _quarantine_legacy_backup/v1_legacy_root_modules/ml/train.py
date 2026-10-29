import time
import logging
import pickle
import os
from datetime import datetime
import pandas as pd
import numpy as np

from sklearn.model_selection import StratifiedKFold, GridSearchCV, train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report, roc_auc_score

from imblearn.pipeline import Pipeline as ImbPipeline
from imblearn.over_sampling import SMOTE

from ml.preprocessing import get_preprocessor
from config.settings import RANDOM_SEED, CURRENT_MODEL_DIR, MODEL_VERSIONS_DIR

logger = logging.getLogger(__name__)

class ModelTrainer:
    def __init__(self, data: pd.DataFrame):
        self.data = data
        self.random_seed = RANDOM_SEED
        self.models = {
            'Decision Tree': DecisionTreeClassifier(random_state=self.random_seed),
            'SVC': SVC(probability=True, random_state=self.random_seed),
            'Logistic Regression': LogisticRegression(random_state=self.random_seed, max_iter=1000),
            'Random Forest': RandomForestClassifier(random_state=self.random_seed)
        }
        self.param_grids = {
            'Decision Tree': {
                'classifier__max_depth': [3, 5, 7, None],
                'classifier__min_samples_split': [2, 5, 10],
                'classifier__criterion': ['gini', 'entropy']
            },
            'SVC': {
                'classifier__C': [0.1, 1, 10],
                'classifier__kernel': ['linear', 'rbf']
            },
            'Logistic Regression': {
                'classifier__C': [0.1, 1, 10],
                'classifier__penalty': ['l2']
            },
            'Random Forest': {
                'classifier__n_estimators': [50, 100],
                'classifier__max_depth': [5, 10, None],
                'classifier__min_samples_split': [2, 5]
            }
        }
        self.results = {}

    def run_training_pipeline(self):
        """Executes the full training, evaluation, and selection pipeline."""
        logger.info("Starting training pipeline...")
        
        # 1. Prepare data
        exclude_cols = ['target_at_risk', 'is_synthetic_demo_data']
        feature_cols = [c for c in self.data.columns if c not in exclude_cols]
        X = self.data[feature_cols]
        y = self.data['target_at_risk']
        
        # Train-Test Split (Independent Evaluation Set)
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, stratify=y, random_state=self.random_seed
        )
        
        logger.info(f"Train set: {X_train.shape[0]} samples. Test set: {X_test.shape[0]} samples.")
        
        # Preprocessor
        preprocessor = get_preprocessor(X_train)
        
        # Calculate optimal CV folds based on minority class count
        minority_class_count = y_train.value_counts().min()
        n_splits = min(5, max(2, minority_class_count // 5)) 
        # Determine SMOTE k_neighbors safely
        k_neighbors = min(5, minority_class_count - 1)
        
        if k_neighbors < 1:
            logger.warning("Dataset too small/imbalanced for SMOTE. Disabling SMOTE.")
            use_smote = False
        else:
            use_smote = True
        
        cv = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=self.random_seed)
        
        # 2. Train and Evaluate each model
        for name, classifier in self.models.items():
            logger.info(f"Training {name}...")
            
            # Construct leakage-safe pipeline
            steps = [('preprocessor', preprocessor)]
            if use_smote:
                steps.append(('smote', SMOTE(random_state=self.random_seed, k_neighbors=k_neighbors)))
            steps.append(('classifier', classifier))
            
            pipeline = ImbPipeline(steps=steps)
            param_grid = self.param_grids[name]
            
            # GridSearchCV
            grid_search = GridSearchCV(
                pipeline, param_grid, cv=cv, scoring='f1_macro', n_jobs=-1
            )
            
            start_train = time.time()
            grid_search.fit(X_train, y_train)
            train_time = time.time() - start_train
            
            best_model = grid_search.best_estimator_
            
            # 3. Final Test Evaluation
            start_infer = time.time()
            y_pred = best_model.predict(X_test)
            y_prob = best_model.predict_proba(X_test)[:, 1] if hasattr(best_model, "predict_proba") else None
            infer_time = time.time() - start_infer
            
            # Metrics
            acc = accuracy_score(y_test, y_pred)
            prec = precision_score(y_test, y_pred, zero_division=0)
            rec = recall_score(y_test, y_pred, zero_division=0) # High-risk recall
            f1 = f1_score(y_test, y_pred, zero_division=0)
            f1_macro = f1_score(y_test, y_pred, average='macro', zero_division=0)
            roc_auc = roc_auc_score(y_test, y_prob) if y_prob is not None else None
            cm = confusion_matrix(y_test, y_pred)
            
            self.results[name] = {
                'model': best_model,
                'cv_best_score': grid_search.best_score_,
                'best_params': grid_search.best_params_,
                'metrics': {
                    'Accuracy': acc,
                    'Precision': prec,
                    'Recall (High-Risk)': rec,
                    'F1': f1,
                    'Macro F1': f1_macro,
                    'ROC AUC': roc_auc,
                    'Confusion Matrix': cm.tolist()
                },
                'train_time': train_time,
                'inference_time': infer_time / len(X_test) # Time per sample
            }
            logger.info(f"{name} trained. Macro F1: {f1_macro:.4f}, High-Risk Recall: {rec:.4f}")

        # 4. Model Selection
        selected_model_name, selection_reason = self._select_best_model()
        
        # 5. Save Artifacts
        version = self._save_model_artifacts(selected_model_name, X_train.columns.tolist())
        
        return {
            'results': self.results,
            'selected_model': selected_model_name,
            'selection_reason': selection_reason,
            'version': version,
            'train_size': len(X_train),
            'test_size': len(X_test)
        }

    def _select_best_model(self):
        """
        Selects the best model based on High-risk recall + Macro F1 + Accuracy,
        preferring lighter/interpretable models if performance is similar.
        """
        best_name = None
        best_score = -1
        reason = ""
        
        # Interpretability hierarchy (lighter = better tie-breaker)
        interpretability_score = {
            'Decision Tree': 4,
            'Logistic Regression': 3,
            'Random Forest': 2,
            'SVC': 1
        }
        
        for name, data in self.results.items():
            m = data['metrics']
            # Composite score heavily weighting recall of at-risk students
            # weight: Recall(0.5) + Macro F1(0.3) + Accuracy(0.2)
            composite_score = (m['Recall (High-Risk)'] * 0.5) + (m['Macro F1'] * 0.3) + (m['Accuracy'] * 0.2)
            
            # Incorporate tie-breaker logic (small boost for interpretability)
            composite_score += (interpretability_score[name] * 0.01)
            
            if composite_score > best_score:
                best_score = composite_score
                best_name = name
                reason = f"Highest composite score ({composite_score:.3f}) driven by High-Risk Recall ({m['Recall (High-Risk)']:.3f}) and Macro F1 ({m['Macro F1']:.3f})."

        return best_name, reason

    def _save_model_artifacts(self, selected_model_name, feature_names):
        """Saves the selected model and its metadata."""
        selected_model = self.results[selected_model_name]['model']
        
        # Versioning based on timestamp
        version = datetime.now().strftime("v%Y%m%d_%H%M%S")
        
        artifact = {
            'model': selected_model,
            'model_name': selected_model_name,
            'version': version,
            'feature_names': feature_names,
            'metrics': self.results[selected_model_name]['metrics'],
            'timestamp': datetime.now().isoformat(),
            'random_seed': self.random_seed
        }
        
        # Save to current
        current_path = os.path.join(CURRENT_MODEL_DIR, "model.pkl")
        with open(current_path, 'wb') as f:
            pickle.dump(artifact, f)
            
        # Save to versions
        version_path = os.path.join(MODEL_VERSIONS_DIR, f"model_{version}.pkl")
        with open(version_path, 'wb') as f:
            pickle.dump(artifact, f)
            
        return version

def load_current_model():
    """Loads the current model artifact."""
    current_path = os.path.join(CURRENT_MODEL_DIR, "model.pkl")
    if os.path.exists(current_path):
        with open(current_path, 'rb') as f:
            return pickle.load(f)
    return None
