import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from CoolProp.CoolProp import PropsSI
import os

# --- DEVELOPER IDENTITY ---
DEV_NAME = "Sumit Yadav"
DEV_CREDENTIALS = "B.Tech Mechanical Engineer"
PHOTO_PATH = "sumit.jpg"

# --- CONFIG ---
st.set_page_config(page_title=f"RIP v3.0 | {DEV_NAME}", layout="wide", page_icon="❄️")

# --- CUSTOM PREMIUM CSS (Glassmorphism + Industrial Blue) ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif;
        background-color: #0f172a;
        color: #f1f5f9;
    }}
    
    .stApp {{
        background: radial-gradient(circle at top right, #1e293b, #0f172a);
    }}

    /* Professional Metric Cards */
    .metric-card {{
        background: rgba(30, 41, 59, 0.7);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
        transition: transform 0.3s ease;
    }}
    .metric-card:hover {{ transform: translateY(-5px); border-color: #38bdf8; }}
    
    .metric-label {{ color: #94a3b8; font-size: 0.8rem; margin-bottom: 5px; }}
    .metric-value {{ font-size: 1.8rem; font-weight: 700; color: #38bdf8; }}

    /* Probabilistic RCA Bars */
    .rca-container {{ margin-bottom: 10px; }}
    .rca-label {{ display: flex; justify-content: space-between; font-size: 0.85rem; margin-bottom: 4px; }}
    .rca-bar-bg {{ background: #334155; height: 8px; border-radius: 4px; }}
    .rca-bar-fill {{ height: 100%; border-radius: 4px; transition: width 1s ease-in-out; }}

    /* Sidebar Fixes */
    [data-testid="stSidebar"] {{ background-color: #0f172a; border-right: 1px solid #1e293b; }}
    </style>
    """, unsafe_allow_html=True)

# --- THERMODYNAMIC CORE ENGINE ---
def get_cycle_data(ps, ts, pd, td, tl, ref_name):
    try:
        ref_map = {"R29
