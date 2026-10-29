import streamlit as st
import os
from config.settings import RANDOM_SEED, APP_NAME, APP_VERSION

def app():
    st.title("Settings")
    
    st.subheader("Application Configuration")
    st.write(f"**App Name:** {APP_NAME}")
    st.write(f"**Version:** {APP_VERSION}")
    st.write(f"**Random Seed:** {RANDOM_SEED}")
    
    st.subheader("Database")
    db_path = os.path.join(os.getcwd(), "edurisk.db")
    st.write(f"**SQLite Database Path:** {db_path}")
    st.write(f"**Size:** {os.path.getsize(db_path) / 1024:.2f} KB" if os.path.exists(db_path) else "Not found.")
    
    st.markdown("---")
    st.write("Edit `.env` or `config/settings.py` for advanced configuration.")
