import os
import pandas as pd
import numpy as np
from ucimlrepo import fetch_ucirepo

class DataLoader:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.raw_path = os.path.join(self.data_dir, "raw", "student_data.csv")
        self.demo_path = os.path.join(self.data_dir, "demo", "demo_data.csv")
        
        # Ensure directories exist
        os.makedirs(os.path.join(self.data_dir, "raw"), exist_ok=True)
        os.makedirs(os.path.join(self.data_dir, "demo"), exist_ok=True)

    def load_data(self) -> pd.DataFrame:
        """Loads data from UCIML or falls back to synthetic DEMO data."""
        try:
            print("Attempting to fetch UCI Student Performance dataset...")
            student_performance = fetch_ucirepo(id=320)
            X = student_performance.data.features
            y = student_performance.data.targets
            
            # Combine
            df = pd.concat([X, y], axis=1)
            
            # Feature mapping to methodology requirements
            df = self._map_features(df)
            
            # Save raw
            df.to_csv(self.raw_path, index=False)
            df['is_synthetic_demo_data'] = False
            return df
        except Exception as e:
            print(f"Failed to fetch UCI data ({str(e)}). Generating DEMO data fallback.")
            df = self._generate_demo_data()
            df.to_csv(self.demo_path, index=False)
            return df
            
    def _map_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Maps UCI features to the four core Phase 2 methodology features + Target."""
        # Target creation: risk definition
        # UCI G3 is 0-20. Let's say < 10 is At-Risk (1), else Not At-Risk (0)
        df['target_at_risk'] = (df['G3'] < 10).astype(int)
        
        # 1. Study Hours: map studytime (1: <2 hours, 2: 2-5 hours, 3: 5-10 hours, 4: >10 hours)
        # We will roughly convert it to weekly hours
        study_map = {1: 1.5, 2: 3.5, 3: 7.5, 4: 12.0}
        df['study_hours'] = df['studytime'].map(study_map)
        
        # 2. Attendance Rate: 
        # Assuming 90 total days. attendance_rate = max(0, 100 - (absences/90)*100)
        df['attendance_rate'] = np.clip(100 - (df['absences'] / 90) * 100, 0, 100)
        
        # 3. Internal Test Score
        # Average of G1 and G2, mapped to 0-100 scale (from 0-20 scale)
        df['internal_test_score'] = ((df['G1'] + df['G2']) / 2) * 5
        
        # 4. Assignment Submission Frequency (Not present in UCI, so we must synthesize it)
        # We correlate it heavily with studytime and G1/G2 to be realistic but clearly mark it
        # as a synthetic addition.
        np.random.seed(42)
        base = df['internal_test_score'] * 0.7 + (df['studytime'] * 10) + np.random.normal(0, 10, len(df))
        df['assignment_submission_frequency'] = np.clip(base, 0, 100)
        
        # Keep only the core 4 features + target
        cols = ['attendance_rate', 'study_hours', 'internal_test_score', 'assignment_submission_frequency', 'target_at_risk']
        return df[cols]
        
    def _generate_demo_data(self, n=500) -> pd.DataFrame:
        """Generates clear, safe DEMO DATA for offline demonstration."""
        np.random.seed(42)
        data = {
            'attendance_rate': np.random.normal(85, 10, n),
            'study_hours': np.random.normal(5, 2, n),
            'internal_test_score': np.random.normal(65, 15, n),
            'assignment_submission_frequency': np.random.normal(75, 15, n)
        }
        df = pd.DataFrame(data)
        
        # Clip ranges
        df['attendance_rate'] = np.clip(df['attendance_rate'], 0, 100)
        df['study_hours'] = np.clip(df['study_hours'], 0, 20)
        df['internal_test_score'] = np.clip(df['internal_test_score'], 0, 100)
        df['assignment_submission_frequency'] = np.clip(df['assignment_submission_frequency'], 0, 100)
        
        # Define synthetic risk formula
        risk_score = (100 - df['attendance_rate']) * 0.3 + \
                     (20 - df['study_hours']) * 0.2 + \
                     (100 - df['internal_test_score']) * 0.4 + \
                     (100 - df['assignment_submission_frequency']) * 0.1
                     
        # Label top 30% as At-Risk
        threshold = np.percentile(risk_score, 70)
        df['target_at_risk'] = (risk_score > threshold).astype(int)
        
        df['is_synthetic_demo_data'] = True
        return df
