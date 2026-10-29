import os
import pandas as pd
import numpy as np
import logging
from config.settings import RAW_DATA_DIR, RANDOM_SEED

logger = logging.getLogger(__name__)

class DataLoader:
    """Handles dataset acquisition, including UCIML repo fetch and synthetic generation."""
    
    def __init__(self, data_path=None):
        self.data_path = data_path or os.path.join(RAW_DATA_DIR, "student_data.csv")
        np.random.seed(RANDOM_SEED)

    def get_data(self) -> pd.DataFrame:
        """Main method to get the dataset."""
        if os.path.exists(self.data_path):
            logger.info(f"Loading existing dataset from {self.data_path}")
            return pd.read_csv(self.data_path)
            
        logger.info("Dataset not found locally. Attempting to fetch from UCI...")
        try:
            df = self._fetch_uci_data()
            logger.info("Successfully fetched and transformed UCI dataset.")
            self._save_data(df)
            return df
        except Exception as e:
            logger.warning(f"Failed to fetch UCI dataset: {e}. Falling back to synthetic DEMO data.")
            df = self._generate_synthetic_data()
            logger.info("Successfully generated synthetic DEMO dataset.")
            self._save_data(df)
            return df

    def _fetch_uci_data(self) -> pd.DataFrame:
        from ucimlrepo import fetch_ucirepo
        
        # Fetch Student Performance (ID 320)
        student_performance = fetch_ucirepo(id=320)
        
        X = student_performance.data.features
        y = student_performance.data.targets
        
        # Combine into one dataframe
        df = pd.concat([X, y], axis=1)
        
        # We need the 4 core methodology features:
        # 1. attendance_rate
        # 2. assignment_submission_frequency
        # 3. internal_test_score
        # 4. study_hours
        
        # UCI has: absences, studytime (1-4), G1, G2, G3.
        
        # 1. attendance_rate (approximate from absences, assuming 93 total classes per semester)
        # Cap at 0 to 100
        total_classes = 93
        df['attendance_rate'] = 100 * (1 - (df['absences'] / total_classes))
        df['attendance_rate'] = df['attendance_rate'].clip(lower=0, upper=100)
        
        # 2. study_hours (map 1-4 scale to hours)
        # 1: <2 hours, 2: 2-5 hours, 3: 5-10 hours, 4: >10 hours
        study_map = {1: 1.0, 2: 3.5, 3: 7.5, 4: 12.0}
        df['study_hours'] = df['studytime'].map(study_map)
        
        # 3. internal_test_score (average of G1 and G2, scale 0-20 to 0-100)
        df['internal_test_score'] = ((df['G1'] + df['G2']) / 2.0) * 5.0
        
        # 4. assignment_submission_frequency (Not in UCI, generate synthetically with correlation)
        # Higher study hours and test scores -> higher submission frequency
        noise = np.random.normal(0, 10, size=len(df))
        submission_freq = 40 + (df['study_hours'] * 2) + (df['internal_test_score'] * 0.4) + noise
        df['assignment_submission_frequency'] = submission_freq.clip(lower=0, upper=100)
        
        # Target: G3 (final grade). Let's define At-Risk (1) as G3 < 10, else 0.
        df['target_at_risk'] = (df['G3'] < 10).astype(int)
        
        # Retain some demographic/behavioral columns for dashboard filtering/context
        keep_cols = [
            'sex', 'age', 'address', 'famsize', 'Pstatus', 'Medu', 'Fedu', 
            'traveltime', 'failures', 'schoolsup', 'famsup', 'activities', 
            'internet', 'romantic', 'goout', 'Dalc', 'Walc', 'health', 
            'attendance_rate', 'study_hours', 'internal_test_score', 
            'assignment_submission_frequency', 'target_at_risk'
        ]
        
        return df[keep_cols]

    def _generate_synthetic_data(self, n_samples=500) -> pd.DataFrame:
        """Generates a purely synthetic DEMO dataset if UCI is unreachable."""
        # Risk factors (features)
        attendance_rate = np.random.normal(75, 15, n_samples).clip(0, 100)
        study_hours = np.random.normal(5, 3, n_samples).clip(0, 20)
        internal_test_score = np.random.normal(65, 18, n_samples).clip(0, 100)
        
        # assignment_submission_frequency correlated with attendance and study hours
        assignment_submission_frequency = (attendance_rate * 0.5 + study_hours * 2 + np.random.normal(10, 10, n_samples)).clip(0, 100)
        
        # Calculate a latent risk score
        latent_risk = (
            -0.4 * attendance_rate 
            -1.5 * study_hours 
            -0.3 * internal_test_score 
            -0.2 * assignment_submission_frequency 
            + np.random.normal(50, 10, n_samples)
        )
        
        # Threshold for At Risk (roughly top 30-40% of latent risk)
        threshold = np.percentile(latent_risk, 65)
        target_at_risk = (latent_risk > threshold).astype(int)
        
        df = pd.DataFrame({
            'attendance_rate': attendance_rate,
            'study_hours': study_hours,
            'internal_test_score': internal_test_score,
            'assignment_submission_frequency': assignment_submission_frequency,
            'failures': np.random.randint(0, 4, n_samples),
            'sex': np.random.choice(['F', 'M'], n_samples),
            'internet': np.random.choice(['yes', 'no'], n_samples, p=[0.8, 0.2]),
            'target_at_risk': target_at_risk,
            'is_synthetic_demo_data': True  # explicit label
        })
        return df

    def _save_data(self, df: pd.DataFrame):
        df.to_csv(self.data_path, index=False)
