import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from CoolProp.CoolProp import PropsSI
import os

# --- IDENTITY ---
DEV_NAME = "Sumit Yadav"
DEV_CREDENTIALS = "B.Tech Mechanical Engineer"
PHOTO_PATH = "sumit.jpg"

# --- CONFIG ---
st.set_page_config(page_title=f"RIP v2.0 | {DEV_NAME}", layout="wide", page_icon="⚡")

# --- UI ENHANCEMENTS (ADVANCED CSS) ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');
    
    html, body, [class*="css"] {{
        font-family: 'JetBrains+Mono', monospace;
        background-color: #050505;
        color: #00f2ff;
    }}
    
    .stApp {{
        background: radial-gradient(circle at 50% 50%, #0d1117 0%, #050505 100%);
    }}

    /* Glassmorphism Cards */
    .glass-card {{
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 25px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.8);
    }}

    .metric-value {{
        font-size: 2.5rem;
        font-weight: bold;
        color: #00f2ff;
        text-shadow: 0 0 10px rgba(0, 242, 255, 0.5);
    }}

    /* Custom Sidebar */
    [data-testid="stSidebar"] {{
        background-color: rgba(10, 10, 10, 0.95);
        border-right: 1px solid #1f2937;
    }}

    .grade-a {{ color: #00ff88; text-shadow: 0 0 15px #00ff88; font-size: 4rem; }}
    .grade-f {{ color: #ff0044; text-shadow: 0 0 15px #ff0044; font-size: 4rem; }}
    </style>
    """, unsafe_allow_html=True)

# --- HELPER FUNCTIONS ---
def get_energy_grade(cop):
    if cop > 3.5: return "A+", "grade-a", "Exceptional Efficiency"
    if cop > 2.8: return "A", "grade-a", "High Efficiency"
    if cop > 2.2: return "B", "grade-a", "Standard Efficiency"
    if cop > 1.8: return "C", "style='color:yellow'", "Sub-optimal"
    return "F", "grade-f", "Critical Inefficiency"

def draw_ph_diagram(ref, p_suc, p_dis, h_pts):
    # Generate Saturation Dome
    t_crit = PropsSI('Tcrit', ref)
    t_min = PropsSI('Tmin', ref)
    temps = np.linspace(t_min, t_crit - 0.5, 50)
    
    h_l = [PropsSI('H', 'T', t, 'Q', 0, ref)/1000 for t in temps]
    h_v = [PropsSI('H', 'T', t, 'Q', 1, ref)/1000 for t in temps]
    p_sat = [PropsSI('P', 'T', t, 'Q', 0, ref)/1e5 for t in temps]

    fig = go.Figure()
    # Saturation Line
    fig.add_trace(go.Scatter(x=h_l + h_v[::-1], y=p_sat + p_sat[::-1], 
                             fill='toself', fillcolor='rgba(0, 242, 255, 0.05)',
                             line=dict(color='rgba(0, 242, 255, 0.3)'), name='Saturation Dome'))
    # Cycle
    p_pts = [p_dis, p_suc, p_dis, p_dis]
    fig.add_trace(go.Scatter(x=h_pts + [h_pts[0]], y=p_pts + [p_pts[0]], 
                             mode='lines+markers', line=dict(color='#00f2ff', width=4),
                             marker=dict(size=10), name='Active Cycle'))
    
    fig.update_layout(xaxis_title="Enthalpy (kJ/kg)", yaxis_title="Pressure (Bar)", 
                      yaxis_type="log", template="plotly_dark", height=500,
                      margin=dict(l=20, r=20, t=20, b=20))
    return fig

# --- SIDEBAR ---
with st.sidebar:
    st.markdown(f"""
    <div style="text-align: center; padding: 20px;">
        <img src="https://raw.githubusercontent.com/your-username/your-repo/main/sumit.jpg" style="border-radius: 50%; width: 150px; border: 3px solid #00f2ff;">
        <h2 style="margin-top: 10px;">{DEV_NAME}</h2>
        <p style="color: #666;">{DEV_CREDENTIALS}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.write("---")
    ref_choice = st.selectbox("⚡ Active Refrigerant", ["R290", "R134a", "R600a", "R404A", "R32", "R744"])
    st.write("---")
    st.markdown("### 🛠 Engineering Tools")
    tool = st.selectbox("Quick Convert", ["Pressure (Bar ↔ PSI)", "Temp (°C ↔ °F)"])
    if tool == "Pressure (Bar ↔ PSI)":
        b = st.number_input("Bar", value=1.0)
        st.caption(f"Result: {b * 14.5038:.2f} PSI")

# --- MAIN ENGINE ---
st.markdown("<h1 style='text-align: center; letter-spacing: 5px;'>REFRIGERATION INTELLIGENCE COMMAND</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; color: #555;'>Platform Architect: {DEV_NAME} | Vibe Coder Edition</p>", unsafe_allow_html=True)

# Data Input Row
col_in1, col_in2, col_in3, col_in4, col_in5 = st.columns(5)
ps = col_in1.number_input("P_Suction (Bar)", value=1.5)
ts = col_in2.number_input("T_Suction (°C)", value=10.0)
pd = col_in3.number_input("P_Discharge (Bar)", value=12.0)
td = col_in4.number_input("T_Discharge (°C)", value=85.0)
tl = col_in5.number_input("T_Liquid (°C)", value=35.0)

# Calculations
try:
    ref = "Propane" if ref_choice == "R290" else "Isobutane" if ref_choice == "R600a" else ref_choice
    h_s = PropsSI('H', 'P', ps*1e5, 'T', ts+273.15, ref)/1000
    h_d = PropsSI('H', 'P', pd*1e5, 'T', td+273.15, ref)/1000
    h_l = PropsSI('H', 'P', pd*1e5, 'T', tl+273.15, ref)/1000
    cop = (h_s - h_l) / (h_d - h_s)
    sh = ts - (PropsSI('T', 'P', ps*1e5, 'Q', 1, ref)-273.15)
    sc = (PropsSI('T', 'P', pd*1e5, 'Q', 0, ref)-273.15) - tl

    # UI LAYOUT
    col_left, col_right = st.columns([2, 1])

    with col_left:
        st.plotly_chart(draw_ph_diagram(ref, ps, pd, [h_l, h_s, h_d, h_l]), use_container_width=True)

    with col_right:
        grade, g_class, g_desc = get_energy_grade(cop)
        st.markdown(f"""
        <div class="glass-card" style="text-align: center;">
            <p style="margin-bottom: 0;">ENERGY GRADE</p>
            <h1 class="{g_class}">{grade}</h1>
            <p style="color: #888;">{g_desc}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="glass-card">
            <p style="color: #888; font-size: 0.8rem;">REAL-TIME COP</p>
            <p class="metric-value">{cop:.2f}</p>
        </div>
        """, unsafe_allow_html=True)

    # Simulator Sliders
    st.markdown("### 🕹️ Vibe Simulator (What-If Analysis)")
    sim_col1, sim_col2 = st.columns(2)
    ambient_inc = sim_col1.slider("Simulate Ambient Temp Increase (°C)", 0, 20, 0)
    airflow_dec = sim_col2.slider("Simulate Airflow Loss (%)", 0, 100, 0)
    
    if ambient_inc > 0 or airflow_dec > 0:
        sim_cop = cop * (1 - (ambient_inc * 0.02)) * (1 - (airflow_dec * 0.005))
        st.warning(f"Simulated Outcome: COP would drop to **{sim_cop:.2f}** under these conditions.")

except Exception as e:
    st.error(f"Waiting for stable sensor data... (Error: {e})")

st.markdown("---")
st.markdown(f"<div style='text-align: center; color: #444;'>RIP PLATFORM 2.0 | ENCRYPTED LINK | DESIGNED BY {DEV_NAME.upper()}</div>", unsafe_allow_html=True)
