import streamlit as st
import pandas as pd
from ml.data_loader import DataLoader
from ml.train import ModelTrainer
import os
from config.settings import RAW_DATA_DIR

def app():
    st.title("Model Training")
    st.markdown("Train the machine learning pipeline using local or UCI data.")

    data_loader = DataLoader()
    
    st.subheader("1. Dataset Status")
    if os.path.exists(data_loader.data_path):
        st.success(f"Dataset found: {data_loader.data_path}")
        df = pd.read_csv(data_loader.data_path)
        st.write(f"**Records:** {df.shape[0]}")
        st.write(f"**Features:** {df.shape[1]}")
        
        if 'target_at_risk' in df.columns:
            st.write("**Class Distribution:**")
            st.bar_chart(df['target_at_risk'].value_counts())
    else:
        st.warning("No dataset found. Click below to fetch or generate data.")

    if st.button("Fetch / Generate Dataset"):
        with st.spinner("Fetching data..."):
            df = data_loader.get_data()
            st.success("Dataset loaded successfully.")
            st.rerun()

    st.markdown("---")
    st.subheader("2. Train / Retrain Model")
    st.markdown("""
    This process will:
    1. Preprocess data (missing values, scaling, encoding)
    2. Apply SMOTE to training folds
    3. Train 4 models via Stratified K-Fold CV & GridSearch
    4. Select the best model automatically
    """)
    
    if st.button("Start Training Pipeline", type="primary"):
        if not os.path.exists(data_loader.data_path):
            st.error("Please fetch the dataset first.")
            return
            
        with st.spinner("Training models (this may take a few minutes)..."):
            df = pd.read_csv(data_loader.data_path)
            trainer = ModelTrainer(df)
            result = trainer.run_training_pipeline()
            
            st.success(f"Training complete! Selected Model: **{result['selected_model']}**")
            st.info(f"Reason: {result['selection_reason']}")
            
            st.write("### Cross-Validation Results")
            results_df = []
            for name, res in result['results'].items():
                results_df.append({
                    "Model": name,
                    "CV F1 (Macro)": res['cv_best_score'],
                    "Test Accuracy": res['metrics']['Accuracy'],
                    "Test High-Risk Recall": res['metrics']['Recall (High-Risk)'],
                    "Train Time (s)": res['train_time']
                })
            
            st.dataframe(pd.DataFrame(results_df))
