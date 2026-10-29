import streamlit as st
import pandas as pd
from ml.data_loader import DataLoader

def app():
    st.title("Data Import")
    st.markdown("Import a CSV file to update the local dataset.")
    
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.write("Preview:")
        st.dataframe(df.head())
        
        st.write(f"Total Rows: {df.shape[0]}, Total Columns: {df.shape[1]}")
        
        if st.button("Confirm and Save"):
            loader = DataLoader()
            df.to_csv(loader.data_path, index=False)
            st.success(f"Data saved to {loader.data_path}. You can now retrain the model.")
