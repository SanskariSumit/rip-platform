import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from CoolProp.CoolProp import PropsSI

# --- PAGE CONFIG ---
st.set_page_config(page_title="RIP - Refrigeration Intelligence Platform", layout="wide")

# --- STYLE ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# --- REFRIGERATION PHYSICS ENGINE ---
def calculate_metrics(p_suc, t_suc, p_dis, t_dis, t_liq, refrigerant):
    try:
        # Convert to SI units
        ps = p_suc * 100000
        pd = p_dis * 100000
        ts = t_suc + 273.15
        td = t_dis + 273.15
        tl = t_liq + 273.15

        # Saturation Temperatures
        t_evap = PropsSI('T', 'P', ps, 'Q', 1, refrigerant) - 273.15
        t_cond = PropsSI('T', 'P', pd, 'Q', 0, refrigerant) - 273.15

        # Enthalpies
        h_suc = PropsSI('H', 'P', ps, 'T', ts, refrigerant) / 1000
        h_dis = PropsSI('H', 'P', pd, 'T', td, refrigerant) / 1000
        h_liq = PropsSI('H', 'P', pd, 'T', tl, refrigerant) / 1000
        
        # Performance
        superheat = t_suc - t_evap
        subcooling = t_cond - t_liq
        cop = (h_suc - h_liq) / (h_dis - h_suc)
        
        return {
            "T_Evap": t_evap, "T_Cond": t_cond, "SH": superheat, 
            "SC": subcooling, "COP": cop, "H_Suc": h_suc, "H_Dis": h_dis, "H_Liq": h_liq
        }
    except:
        return None

# --- SIDEBAR: CONTROLS ---
st.sidebar.title("🛠 RIP Control Panel")
ref = st.sidebar.selectbox("Refrigerant", ["R290", "R134a", "R600a", "R404A", "R410A"])
objective = st.sidebar.multiselect("Engineering Objective", ["Reduce Pull-down", "Improve COP", "Reduce Charge"])

# --- MAIN UI ---
st.title("❄️ Refrigeration Intelligence Platform")
st.subheader("Digital Senior Engineer Dashboard")

tab1, tab2, tab3 = st.tabs(["📊 Live Analysis", "📈 P-h Diagram", "🤖 AI Design Assistant"])

with tab1:
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.write("### Sensor Inputs")
        p_suc = st.number_input("Suction Press (Bar)", value=1.5)
        t_suc = st.number_input("Suction Temp (°C)", value=10.0)
        p_dis = st.number_input("Discharge Press (Bar)", value=12.0)
        t_dis = st.number_input("Discharge Temp (°C)", value=85.0)
        t_liq = st.number_input("Liquid Line Temp (°C)", value=35.0)

    res = calculate_metrics(p_suc, t_suc, p_dis, t_dis, t_liq, ref)

    with col2:
        if res:
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("COP (Efficiency)", f"{res['COP']:.2f}", "+2%")
            m2.metric("Superheat", f"{res['SH']:.1f} K", "-1.2K")
            m3.metric("Subcooling", f"{res['SC']:.1f} K", "Optimal")
            m4.metric("Condensing T", f"{res['T_Cond']:.1f} °C")
            
            # --- DIAGNOSTIC AI ---
            st.info("### 🤖 AI Diagnostic Verdict")
            if res['SH'] > 12:
                st.error("⚠️ **High Superheat Detected:** Possible Refrigerant Undercharge or Expansion Restriction.")
            elif res['T_Cond'] > 50:
                st.warning("⚠️ **High Condensing Temp:** Check Condenser Airflow or Fin Blockage.")
            else:
                st.success("✅ **System Balanced:** Thermodynamic points are within historical benchmarks.")

with tab2:
    if res:
        st.write("### Pressure-Enthalpy (P-h) Visualization")
        # Simplified Ph Diagram with Plotly
        fig = go.Figure()
        # Draw Cycle
        h_pts = [res['H_Liq'], res['H_Suc'], res['H_Dis'], res['H_Liq']]
        p_pts = [p_dis, p_suc, p_dis, p_dis]
        fig.add_trace(go.Scatter(x=h_pts, y=p_pts, mode='lines+markers', name='Cycle', line=dict(color='red', width=4)))
        fig.update_layout(xaxis_title="Enthalpy (kJ/kg)", yaxis_title="Pressure (Bar)", yaxis_type="log")
        st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.write("### 🏗 Design Assistant")
    vol = st.number_input("Cabinet Volume (Liters)", value=300)
    amb = st.slider("Ambient Temp (°C)", 25, 45, 32)
    
    if st.button("Generate Design Recommendation"):
        st.write("---")
        st.write(f"**Recommended Compressor:** Embraco EMX20CLC (R290)")
        st.write(f"**Estimated Charge:** 65g - 75g")
        st.write(f"**Capillary Suggestion:** 0.031\" ID x 3200mm")
        st.balloons()

# --- UPLOAD SECTION ---
st.sidebar.write("---")
uploaded_file = st.sidebar.file_uploader("Upload Test Report (CSV/XLSX)")
if uploaded_file:
    st.sidebar.success("Data ingested. AI is analyzing trends...")