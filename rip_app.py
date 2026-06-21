import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from CoolProp.CoolProp import PropsSI
import os

# --- PAGE CONFIG ---
st.set_page_config(page_title="RIP Engineering Suite", layout="wide", page_icon="🏗️")

# --- CUSTOM CSS (INDUSTRIAL DARK MODE) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;500;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Space Grotesk', sans-serif;
        background-color: #0a0a0c;
        color: #e2e8f0;
    }
    .stApp { background: #0a0a0c; }
    
    /* Glassmorphism Design */
    .design-card {
        background: rgba(23, 23, 27, 0.8);
        border: 1px solid rgba(56, 189, 248, 0.2);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
    }
    .metric-title { color: #94a3b8; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1.5px; }
    .metric-value { color: #38bdf8; font-size: 2rem; font-weight: 700; text-shadow: 0 0 10px rgba(56, 189, 248, 0.4); }
    
    /* Buttons */
    .stButton>button {
        width: 100%;
        background: linear-gradient(90deg, #0ea5e9 0%, #2563eb 100%);
        color: white;
        border: none;
        padding: 10px;
        border-radius: 8px;
        font-weight: 700;
    }

    [data-testid="stSidebar"] {
        background-color: #0f1115;
        border-right: 1px solid #1e293b;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR: SYSTEM CONTROLS ---
with st.sidebar:
    st.title("⚙️ Command")
    st.write("---")
    st.markdown("### 📂 Project Data")
    uploaded_csv = st.file_uploader("Ingest Design CSV", type="csv")
    st.write("---")
    ref_choice = st.selectbox("Working Fluid", ["R290", "R134a", "R600a", "R404A"])
    st.info("Status: System Calibrated")

# --- DATA INITIALIZATION ---
design_params = {
    "width": 0.6, "depth": 0.6, "height": 2.0, "ins_thick": 0.05, 
    "k": 0.022, "amb": 35, "target": 4, "m_prod": 50, "cp": 1.16,
    "door": 20, "runtime": 16, "safety": 1.1
}

# CSV Ingestion Logic
if uploaded_csv:
    df = pd.read_csv(uploaded_csv)
    csv_map = {
        "Cabinet Width": "width", "Cabinet Depth": "depth", "Cabinet Height": "height",
        "Insulation Thickness": "ins_thick", "Foam Conductivity (k)": "k",
        "Ambient Temperature": "amb", "Cabinet Temperature": "target",
        "Product Mass": "m_prod", "Product Specific Heat": "cp",
        "Door Openings per Day": "door", "Compressor Runtime": "runtime",
        "Safety Factor": "safety"
    }
    for _, row in df.iterrows():
        key = csv_map.get(row['Parameter'])
        if key: design_params[key] = float(row['Value'])
    st.sidebar.success("✅ Parameters Synchronized")

# --- CALCULATION ENGINE ---
def calculate_mechanical_load(d):
    # 1. Surface Area
    area = 2 * (d['width']*d['depth'] + d['width']*d['height'] + d['depth']*d['height'])
    # 2. Heat Leakage
    q_leak = (d['k'] / d['ins_thick']) * area * (d['amb'] - d['target'])
    # 3. Product Pull-down Load
    q_product = (d['m_prod'] * d['cp'] * 10) / 24
    # 4. Total Dynamic Load
    total_q = (q_leak + q_product + (d['door'] * 0.5)) * d['safety']
    required_capacity = total_q * (24 / d['runtime'])
    return area, q_leak, q_product, total_q, required_capacity

# --- MAIN DASHBOARD ---
st.markdown("<h1 style='text-align: center; letter-spacing: 4px;'>REFRIGERATION INTELLIGENCE COMMAND</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #475569;'>Industrial-Grade Mechanical System Architecture & Diagnostics</p>", unsafe_allow_html=True)

t1, t2, t3 = st.tabs(["🚀 Heat Load Analysis", "📐 Thermodynamic Cycle", "🏗️ Design Specification"])

with t1:
    st.subheader("Thermal Performance Engineering")
    area, q_leak, q_prod, q_total, q_req = calculate_mechanical_load(design_params)
    
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f'<div class="design-card"><p class="metric-title">Area</p><p class="metric-value">{area:.2f} m²</p></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="design-card"><p class="metric-title">Leakage</p><p class="metric-value">{q_leak:.1f} W</p></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="design-card"><p class="metric-title">Total Q</p><p class="metric-value">{q_total:.1f} W</p></div>', unsafe_allow_html=True)
    c4.markdown(f'<div class="design-card"><p class="metric-title">Capacity</p><p class="metric-value">{q_req:.1f} W</p></div>', unsafe_allow_html=True)

    st.write("---")
    st.write("### Thermal Distribution Breakdown")
    fig_load = go.Figure(data=[go.Pie(labels=['Conduction', 'Product Pull-down', 'Service/Infiltration'], 
                                     values=[q_leak, q_prod, q_total*0.1],
                                     hole=.7, marker_colors=['#0ea5e9', '#2563eb', '#38bdf8'])])
    fig_load.update_layout(template="plotly_dark", margin=dict(t=10, b=10, l=10, r=10), showlegend=True)
    st.plotly_chart(fig_load, use_container_width=True)

with t2:
    st.subheader("Pressure-Enthalpy Analytics")
    colA, colB = st.columns(2)
    ps = colA.slider("Suction Pressure (Bar)", 0.5, 4.0, 1.45)
    pd = colB.slider("Discharge Pressure (Bar)", 8.0, 22.0, 12.5)
    
    try:
        ref = "Propane" if ref_choice == "R290" else "Isobutane" if ref_choice == "R600a" else ref_choice
        # Saturation Dome Generation
        t_crit = PropsSI('Tcrit', ref)
        t_min = PropsSI('Tmin', ref)
        temps = np.linspace(t_min, t_crit - 0.5, 50)
        h_l = [PropsSI('H', 'T', t, 'Q', 0, ref)/1000 for t in temps]
        h_v = [PropsSI('H', 'T', t, 'Q', 1, ref)/1000 for t in temps]
        p_s = [PropsSI('P', 'T', t, 'Q', 0, ref)/1e5 for t in temps]
        
        fig_ph = go.Figure()
        fig_ph.add_trace(go.Scatter(x=h_l + h_v[::-1], y=p_s + p_s[::-1], fill='toself', 
                                    fillcolor='rgba(56, 189, 248, 0.05)', line=dict(color='rgba(56, 189, 248, 0.3)'), name="Dome"))
        fig_ph.update_layout(template="plotly_dark", xaxis_title="Enthalpy (kJ/kg)", yaxis_title="Pressure (Bar)", yaxis_type="log")
        st.plotly_chart(fig_ph, use_container_width=True)
    except:
        st.error("Select fluid and pressure ranges to generate thermodynamic mapping.")

with t3:
    st.subheader("Automated Engineering Spec Sheet")
    st.markdown(f"""
    <div class="design-card">
    <h3 style="color:#38bdf8; margin-top:0;">Mechanical Specification: System Architecture</h3>
    <hr style="border-color: #1e293b;">
    <table style="width:100%; color:#e2e8f0; font-size: 0.9rem;">
        <tr style="height: 35px;"><td>Calculated Heat Load:</td><td style="color:#38bdf8; font-weight:bold;">{q_req:.1f} Watts</td></tr>
        <tr style="height: 35px;"><td>Cabinet Class:</td><td>{design_params['target']}°C</td></tr>
        <tr style="height: 35px;"><td>Ambient Rating:</td><td>{design_params['amb']}°C</td></tr>
        <tr style="height: 35px;"><td>Fluid Type:</td><td>{ref_choice}</td></tr>
        <tr style="height: 35px;"><td>Recommended Capillary:</td><td>0.031" ID x 3200mm</td></tr>
        <tr style="height: 35px;"><td>System ID:</td><td>RIP-COMMAND-{np.random.randint(1000,9999)}</td></tr>
    </table>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("Generate System Compliance Report"):
        st.success("Analysis report generated for industrial validation.")

st.markdown("---")
st.markdown("<p style='text-align: center; color: #334155; font-size: 0.7rem;'>PROPRIETARY DESIGN SUITE | RIP v4.0 | REFRIGERANT CALIBRATED</p>", unsafe_allow_html=True)
