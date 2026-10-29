import time
import json
import joblib
import pandas as pd
import numpy as np
import os
from sklearn.model_selection import train_test_split, StratifiedKFold, GridSearchCV
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
from imblearn.pipeline import Pipeline as ImbPipeline
from imblearn.over_sampling import SMOTE
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier

from src.preprocessing import get_preprocessor

class ModelTrainer:
    def __init__(self, df: pd.DataFrame):
        self.df = df
        # Ensure target is present
        assert 'target_at_risk' in df.columns, "target_at_risk column missing"
        
        self.X = self.df.drop(columns=['target_at_risk', 'is_synthetic_demo_data'], errors='ignore')
        self.y = self.df['target_at_risk']
        
        self.preprocessor = get_preprocessor()
        
        # 4 requested classical models
        self.models = {
            "Decision Tree": (DecisionTreeClassifier(random_state=42), {
                'classifier__max_depth': [3, 5, 7, None],
                'classifier__min_samples_split': [2, 5]
            }),
            "SVC": (SVC(probability=True, random_state=42), {
                'classifier__C': [0.1, 1, 10],
                'classifier__kernel': ['linear', 'rbf']
            }),
            "Logistic Regression": (LogisticRegression(max_iter=1000, random_state=42), {
                'classifier__C': [0.1, 1, 10],
            }),
            "Random Forest": (RandomForestClassifier(random_state=42), {
                'classifier__n_estimators': [50, 100],
                'classifier__max_depth': [5, 10, None]
            })
        }
        
        self.results = {}

    def run_training_pipeline(self):
        print("Starting training pipeline...")
        # 1. Train / Test Split
        X_train, X_test, y_train, y_test = train_test_split(
            self.X, self.y, test_size=0.2, stratify=self.y, random_state=42
        )
        
        # Calculate safe k_neighbors for SMOTE
        min_class_count = min(y_train.value_counts())
        k_neighbors = min(5, min_class_count - 1) if min_class_count > 1 else 1
        print(f"SMOTE k_neighbors dynamically set to {k_neighbors} based on minority class size {min_class_count}")
        
        # 2. Iterate through Models
        for name, (model, params) in self.models.items():
            print(f"Training {name}...")
            start_train_time = time.time()
            
            # Use imblearn Pipeline to prevent leakage (SMOTE only applied to training folds in CV)
            pipeline = ImbPipeline([
                ('preprocessor', self.preprocessor),
                ('smote', SMOTE(random_state=42, k_neighbors=k_neighbors)),
                ('classifier', model)
            ])
            
            # CV
            cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
            
            # GridSearchCV prioritizing Macro F1
            grid = GridSearchCV(
                pipeline, 
                param_grid=params, 
                cv=cv, 
                scoring='f1_macro', 
                n_jobs=-1
            )
            
            grid.fit(X_train, y_train)
            train_time = time.time() - start_train_time
            
            # Inference measurement
            best_model = grid.best_estimator_
            start_infer_time = time.time()
            y_pred = best_model.predict(X_test)
            infer_time = (time.time() - start_infer_time) / len(X_test) # time per sample
            
            # Metrics
            acc = accuracy_score(y_test, y_pred)
            prec = precision_score(y_test, y_pred, zero_division=0)
            rec = recall_score(y_test, y_pred, zero_division=0) # High-Risk recall
            f1 = f1_score(y_test, y_pred, zero_division=0)
            f1_mac = f1_score(y_test, y_pred, average='macro', zero_division=0)
            
            self.results[name] = {
                "Model": name,
                "CV Macro F1": grid.best_score_,
                "Test Accuracy": acc,
                "Test Precision": prec,
                "Test Recall": rec,
                "Test F1": f1,
                "Test Macro F1": f1_mac,
                "Training Time (s)": train_time,
                "Inference Time (ms)": infer_time * 1000,
                "best_estimator": best_model
            }
            
        # 3. Model Selection
        selected_model_name, selection_reason = self._select_best_model()
        print(f"Selected Model: {selected_model_name}")
        print(f"Reason: {selection_reason}")
        
        # 4. Save Artifacts and Metrics
        self._save_results(selected_model_name, selection_reason)
        
        return {
            "selected_model": selected_model_name,
            "selection_reason": selection_reason,
            "results": self.results
        }
        
    def _select_best_model(self):
        """
        Dynamically selects best model prioritizing:
        1. Macro F1
        2. High-Risk Recall
        3. Interpretability (Tree/Linear over SVC/RBF)
        """
        best_name = None
        best_score = -1
        reason = ""
        
        for name, metrics in self.results.items():
            # Composite score: heavily weights Macro F1, adds bonus for High-Risk Recall
            score = (metrics["Test Macro F1"] * 0.7) + (metrics["Test Recall"] * 0.3)
            
            # Apply slight interpretability penalty to SVC if others are competitive
            if name == "SVC":
                score -= 0.01
                
            if score > best_score:
                best_score = score
                best_name = name
                reason = f"Highest composite score (Test Macro F1: {metrics['Test Macro F1']:.3f}, Test High-Risk Recall: {metrics['Test Recall']:.3f})"
                
        return best_name, reason

    def _save_results(self, selected_model_name, selection_reason):
        # Save CSV and JSON comparisons
        os.makedirs('results', exist_ok=True)
        os.makedirs('models/artifacts', exist_ok=True)
        
        comparison_df = pd.DataFrame([{k: v for k, v in res.items() if k != 'best_estimator'} for res in self.results.values()])
        comparison_df.to_csv('results/model_comparison.csv', index=False)
        
        # Save JSON
        with open('results/model_comparison.json', 'w') as f:
            json.dump({
                "selected_model": selected_model_name,
                "selection_reason": selection_reason,
                "metrics": comparison_df.to_dict(orient='records')
            }, f, indent=4)
            
        # Serialize the best pipeline
        best_pipeline = self.results[selected_model_name]['best_estimator']
        
        # Measure size on disk
        artifact_path = 'models/artifacts/best_model.pkl'
        joblib.dump(best_pipeline, artifact_path)
        
        size_kb = os.path.getsize(artifact_path) / 1024
        
        with open('results/runtime_metrics.json', 'w') as f:
            json.dump({
                "Training Time (s)": self.results[selected_model_name]['Training Time (s)'],
                "Inference Time (ms/sample)": self.results[selected_model_name]['Inference Time (ms)'],
                "Model Size (KB)": size_kb
            }, f, indent=4)
            
if __name__ == "__main__":
    from src.data_loader import DataLoader
    loader = DataLoader()
    df = loader.load_data()
    trainer = ModelTrainer(df)
    trainer.run_training_pipeline()
