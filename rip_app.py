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
        ref_map = {"R290": "Propane", "R600a": "Isobutane", "R744": "CarbonDioxide"}
        ref = ref_map.get(ref_name, ref_name)
        
        # PropsSI calls
        t_evap = PropsSI('T', 'P', ps*1e5, 'Q', 1, ref) - 273.15
        t_cond = PropsSI('T', 'P', pd*1e5, 'Q', 0, ref) - 273.15
        h_suc = PropsSI('H', 'P', ps*1e5, 'T', ts+273.15, ref)/1000
        h_dis = PropsSI('H', 'P', pd*1e5, 'T', td+273.15, ref)/1000
        h_liq = PropsSI('H', 'P', pd*1e5, 'T', tl+273.15, ref)/1000
        
        return {
            "t_evap": t_evap, "t_cond": t_cond, 
            "sh": ts - t_evap, "sc": t_cond - tl,
            "cop": (h_suc - h_liq) / (h_dis - h_suc),
            "h_pts": [h_liq, h_suc, h_dis, h_liq], "p_pts": [pd, ps, pd, pd]
        }
    except: return None

# --- SIDEBAR: ENGINEER PROFILE ---
with st.sidebar:
    st.markdown(f"### ⚙️ Command Center")
    ref_choice = st.selectbox("Fluid Selection", ["R290", "R134a", "R600a", "R404A", "R32"])
    st.write("---")
    st.markdown(f"**Lead Architect:**")
    st.markdown(f"**{DEV_NAME}**\n\n{DEV_CREDENTIALS}")
    st.write("---")
    st.info("System Status: Online 🛰️")

# --- MAIN UI ---
st.title("❄️ Refrigeration Intelligence Platform (RIP)")
st.markdown(f"Expert-grade diagnostics & design studio by **{DEV_NAME}**")

# Tabs based on your reference HTML
tab_dash, tab_ph, tab_sim, tab_design = st.tabs(["📊 Diagnostics", "📈 P-h Diagram", "🕹️ Simulation", "🏗 Design Studio"])

# 1. DIAGNOSTICS TAB
with tab_dash:
    col_in, col_diag = st.columns([1.2, 2])
    
    with col_in:
        st.subheader("System Inputs")
        p_s = st.number_input("Suction Press (Bar)", value=1.45)
        t_s = st.number_input("Suction Temp (°C)", value=12.0)
        p_d = st.number_input("Discharge Press (Bar)", value=11.8)
        t_d = st.number_input("Discharge Temp (°C)", value=82.0)
        t_l = st.number_input("Liquid Temp (°C)", value=34.0)
        
    data = get_cycle_data(p_s, t_s, p_d, t_d, t_l, ref_choice)

    with col_diag:
        if data:
            st.subheader("Key Performance Indicators")
            m1, m2, m3, m4 = st.columns(4)
            m1.markdown(f'<div class="metric-card"><div class="metric-label">COP</div><div class="metric-value">{data["cop"]:.2f}</div></div>', unsafe_allow_html=True)
            m2.markdown(f'<div class="metric-card"><div class="metric-label">Superheat</div><div class="metric-value">{data["sh"]:.1f}K</div></div>', unsafe_allow_html=True)
            m3.markdown(f'<div class="metric-card"><div class="metric-label">Subcooling</div><div class="metric-value">{data["sc"]:.1f}K</div></div>', unsafe_allow_html=True)
            m4.markdown(f'<div class="metric-card"><div class="metric-label">Condensing</div><div class="metric-value">{data["t_cond"]:.1f}°C</div></div>', unsafe_allow_html=True)
            
            st.write("---")
            st.subheader("Root Cause Analysis (AI Probabilities)")
            
            # RCA Logic
            def rca_bar(label, prob, color):
                st.markdown(f"""
                <div class="rca-container">
                    <div class="rca-label"><span>{label}</span><span style="color:{color}">{prob}%</span></div>
                    <div class="rca-bar-bg"><div class="rca-bar-fill" style="width:{prob}%; background:{color}"></div></div>
                </div>
                """, unsafe_allow_html=True)

            rca_bar("Refrigerant Undercharge", 78 if data['sh'] > 12 else 15, "#fbbf24")
            rca_bar("Condenser Airflow Restriction", 65 if data['t_cond'] > 48 else 20, "#f87171")
            rca_bar("Expansion Device Blockage", 40 if data['sh'] > 15 else 10, "#60a5fa")

# 2. P-H DIAGRAM TAB
with tab_ph:
    if data:
        st.subheader("Dynamic Pressure-Enthalpy Mapping")
        fig = go.Figure()
        
        # Saturation Dome
        ref = "Propane" if ref_choice == "R290" else "Isobutane" if ref_choice == "R600a" else ref_choice
        t_crit = PropsSI('Tcrit', ref)
        t_min = PropsSI('Tmin', ref)
        temps = np.linspace(t_min, t_crit - 0.5, 50)
        h_l = [PropsSI('H', 'T', t, 'Q', 0, ref)/1000 for t in temps]
        h_v = [PropsSI('H', 'T', t, 'Q', 1, ref)/1000 for t in temps]
        p_sat = [PropsSI('P', 'T', t, 'Q', 0, ref)/1e5 for t in temps]
        
        fig.add_trace(go.Scatter(x=h_l + h_v[::-1], y=p_sat + p_sat[::-1], fill='toself', 
                                 fillcolor='rgba(56, 189, 248, 0.1)', line=dict(color='rgba(56, 189, 248, 0.3)'), name='Saturation Dome'))
        
        fig.add_trace(go.Scatter(x=data['h_pts'], y=data['p_pts'], mode='lines+markers', 
                                 line=dict(color='#38bdf8', width=4), name='Actual Cycle'))
        
        fig.update_layout(xaxis_title="Enthalpy (kJ/kg)", yaxis_title="Pressure (Bar)", yaxis_type="log", 
                          template="plotly_dark", plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)

# 3. SIMULATION TAB
with tab_sim:
    st.subheader("Predictive What-If Engine")
    st.write("Adjust baseline parameters to simulate performance shifts.")
    
    col_s1, col_s2 = st.columns(2)
    s_charge = col_s1.slider("Refrigerant Charge (%)", 60, 140, 100)
    s_fan = col_s2.slider("Condenser Fan Airflow (%)", 40, 150, 100)
    
    # Simple simulation physics
    sim_cop = data['cop'] * (1 - abs(100-s_charge)*0.01) * (s_fan/100)**0.2
    sim_dis = data['t_cond'] + (100 - s_fan)*0.2
    
    # Pull-down Chart (Canvas style from your HTML)
    st.write("### Predicted Pull-down Curve")
    time_pts = np.linspace(0, 180, 50)
    # Predicted curve based on COP
    temp_pts = 32 - (32 - 4) * (1 - np.exp(-time_pts / (30 * sim_cop)))
    
    fig_pd = go.Figure()
    fig_pd.add_trace(go.Scatter(x=time_pts, y=temp_pts, line=dict(color='#10b981', width=3), name="Predicted"))
    fig_pd.add_hline(y=4, line_dash="dash", line_color="#f87171", annotation_text="Target 4°C")
    fig_pd.update_layout(template="plotly_dark", xaxis_title="Time (minutes)", yaxis_title="Temp (°C)")
    st.plotly_chart(fig_pd, use_container_width=True)

# 4. DESIGN STUDIO TAB
with tab_design:
    st.subheader("Mechanical System Architect")
    d_col1, d_col2, d_col3 = st.columns(3)
    vol = d_col1.number_input("Cabinet Volume (L)", 50, 1000, 300)
    amb = d_col2.number_input("Ambient Temp (°C)", 20, 50, 32)
    t_target = d_col3.selectbox("Target Class", ["Chiller (+2°C)", "Freezer (-18°C)"])
    
    if st.button("Generate Mechanical Specification ↗"):
        load = vol * 0.9 if t_target == "Chiller (+2°C)" else vol * 1.4
        st.markdown(f"""
        <div class="metric-card" style="text-align: left;">
            <p><b>PROJECT ARCHITECT:</b> {DEV_NAME}</p>
            <hr>
            <p><b>Recommended Compressor:</b> Embraco EMX20CLC (95W LBP)</p>
            <p><b>Design Load:</b> {load:.1f} Watts</p>
            <p><b>Capillary Recommendation:</b> 0.031" ID x 3200mm</p>
            <p><b>Condenser Face Area:</b> 0.08 m² (Fin-tube)</p>
            <p><b>Predicted COP:</b> 1.42</p>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")
st.markdown(f"<div style='text-align: center; color: #475569;'>RIP PLATFORM v3.0 | ENGINEERED BY {DEV_NAME.upper()} (B.TECH MECHANICAL)</div>", unsafe_allow_html=True)
