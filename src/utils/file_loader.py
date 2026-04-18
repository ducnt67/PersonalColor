import pandas as pd
import streamlit as st
import os

from src.config import PROFILES_DIR

@st.cache_data
def load_fashion_data():
    body_path = os.path.join(PROFILES_DIR, "body_shape_recommendations.csv")
    profile_path = os.path.join(PROFILES_DIR, "personal_color_profiles.csv")
    
    body_df = pd.read_csv(body_path) if os.path.exists(body_path) else pd.DataFrame()
    profile_df = pd.read_csv(profile_path) if os.path.exists(profile_path) else pd.DataFrame()
    
    return body_df, profile_df

def safe_get_unique(df, col_name, fallback_list):
    if df is not None and col_name in df.columns:
        return df[col_name].dropna().astype(str).unique().tolist()
    return fallback_list
