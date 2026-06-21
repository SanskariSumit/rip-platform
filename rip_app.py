import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from CoolProp.CoolProp import PropsSI
import io

# --- IDENTITY ---
DEV_NAME = "Sumit Yadav"
DEV_CREDENTIALS = "B.Tech Mechanical Engineer"
DEV_TITLE = "Mechanical System Architect & Vibe Coder"

# --- PAGE CONFIG ---
st.set_page_config(page_title=f"RIP v4.0 | {DEV_NAME}", layout="wide", page_icon="🏗️")

# --- CUSTOM CSS (INDUSTRIAL DARK MODE) ---
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;500;700&display=swap');
    
    html, body, [class*="css"] {{
        font-family: 'Space Grotesk', sans-serif;
        background-color: #0a0a0c;
        color: #e2e8f0;
    }}
    .stApp {{ background: #0a0a0c; }}
    
    /* Glassmorphism Design */
    .design-card {{
        background: rgba(23, 23, 27, 0.8);
        border: 1px solid rgba(56, 189, 248, 0.2);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
    }}
    .metric-title {{ color: #94a3b8; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 1.5px; }}
    .metric-value {{ color: #38bdf8; font-size: 2rem; font-weight: 700; text-shadow: 0 0 10px rgba(56, 189, 248, 0.4); }}
    
    /* Buttons */
    .stButton>button {{
        width: 100%;
        background: linear-gradient(90deg, #0ea5e9 0%, #2563eb 100%);
        color: white;
        border: none;
        padding: 10px;
        border-radius: 8px;
        font-weight: 700;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR: ENGINEER PROFILE ---
with st.sidebar:
    st.image("sumit.jpg", use_container_width=True)
    st.markdown(f"### {DEV_NAME}")
    st.caption(DEV_CREDENTIALS)
    st.write("---")
    st.title("📂 Project Assets")
    uploaded_csv = st.file_uploader("Upload Design CSV", type="csv")
    st.write("---")
    ref_choice = st.selectbox("Fluid", ["R290", "R134a", "R600a", "R404A"])

# --- LOAD DATA FROM CSV ---
design_params = {
    "width": 0.6, "depth": 0.6, "height": 2.0, "ins_thick": 0.05, 
    "k": 0.022, "amb": 35, "target": 4, "m_prod": 50, "cp": 1.16,
    "door": 20, "runtime": 16, "safety": 1.1
}

if uploaded_csv:
    df = pd.read_csv(uploaded_csv)
    # Mapping CSV parameters to our design_params
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
    st.sidebar.success("✅ Mechanical Design Specs Ingested")

# --- MECHANICAL CALCULATION ENGINE ---
def calculate_mechanical_load(d):
    # 1. Surface Area (m2)
    area = 2 * (d['width']*d['depth'] + d['width']*d['height'] + d['depth']*d['height'])
    # 2. Conduction Leakage (W)
    q_leak = (d['k'] / d['ins_thick']) * area * (d['amb'] - d['target'])
    # 3. Product Load (Wh -> W)
    # Assumes product needs to cool 10C over 24 hours
    q_product = (d['m_prod'] * d['cp'] * 10) / 24
    # 4. Service Load (Heuristic for door openings)
    q_service = (d['door'] * 0.5) # Watts per opening factor
    
    total_q = (q_leak + q_product + q_service) * d['safety']
    required_capacity = total_q * (24 / d['runtime'])
    
    return area, q_leak, q_product, total_q, required_capacity

# --- MAIN DASHBOARD ---
st.title("❄️ Refrigeration Intelligence Command (RIP v4.0)")
st.markdown(f"**Lead Mechanical Architect:** {DEV_NAME} | **Engine:** B.Tech Mech High-Precision")

t1, t2, t3 = st.tabs(["🚀 Mechanical Load Analysis", "📐 Cycle Analytics", "🏗️ Spec Generator"])

with t1:
    st.subheader("Thermal Load Engineering")
    area, q_leak, q_prod, q_total, q_req = calculate_mechanical_load(design_params)
    
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(f'<div class="design-card"><p class="metric-title">Surf. Area</p><p class="metric-value">{area:.2f} m²</p></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="design-card"><p class="metric-title">Heat Leak</p><p class="metric-value">{q_leak:.1f} W</p></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="design-card"><p class="metric-title">Total Load</p><p class="metric-value">{q_total:.1f} W</p></div>', unsafe_allow_html=True)
    c4.markdown(f'<div class="design-card"><p class="metric-title">Req. Capacity</p><p class="metric-value">{q_req:.1f} W</p></div>', unsafe_allow_html=True)

    # Break down chart
    st.write("### Heat Load Distribution")
    fig_load = go.Figure(data=[go.Pie(labels=['Leakage', 'Product', 'Service'], 
                                     values=[q_leak, q_prod, q_total*0.1],
                                     hole=.6, marker_colors=['#0ea5e9', '#2563eb', '#38bdf8'])])
    fig_load.update_layout(template="plotly_dark", margin=dict(t=0, b=0, l=0, r=0))
    st.plotly_chart(fig_load, use_container_width=True)

with t2:
    st.subheader("Thermodynamic Cycle Pulses")
    # Simulation based on Design Load
    p_suc, p_dis = st.columns(2)
    ps = p_suc.slider("Suction (Bar)", 0.5, 4.0, 1.4)
    pd = p_dis.slider("Discharge (Bar)", 8.0, 20.0, 12.0)
    
    # Calculate Cycle Points
    try:
        ref = "Propane" if ref_choice == "R290" else "Isobutane" if ref_choice == "R600a" else ref_choice
        t_evap = PropsSI('T', 'P', ps*1e5, 'Q', 1, ref) - 273.15
        t_cond = PropsSI('T', 'P', pd*1e5, 'Q', 0, ref) - 273.15
        
        # P-h Plotting
        st.write("#### Dynamic P-h Diagram")
        t_crit = PropsSI('Tcrit', ref)
        temps = np.linspace(PropsSI('Tmin', ref), t_crit - 0.5, 50)
        h_l = [PropsSI('H', 'T', t, 'Q', 0, ref)/1000 for t in temps]
        h_v = [PropsSI('H', 'T', t, 'Q', 1, ref)/1000 for t in temps]
        p_s = [PropsSI('P', 'T', t, 'Q', 0, ref)/1e5 for t in temps]
        
        fig_ph = go.Figure()
        fig_ph.add_trace(go.Scatter(x=h_l + h_v[::-1], y=p_s + p_s[::-1], fill='toself', 
                                    fillcolor='rgba(56, 189, 248, 0.1)', line=dict(color='#38bdf8')))
        fig_ph.update_layout(template="plotly_dark", xaxis_title="Enthalpy (kJ/kg)", yaxis_title="Pressure (Bar)", yaxis_type="log")
        st.plotly_chart(fig_ph, use_container_width=True)
    except:
        st.error("Select a valid refrigerant for current pressures.")

with t3:
    st.subheader("Mechanical Specification Sheet")
    st.markdown(f"""
    <div class="design-card">
    <h3>System Architecture Summary</h3>
    <p><b>Engineer:</b> {DEV_NAME} ({DEV_CREDENTIALS})</p>
    <hr>
    <table style="width:100%; border-collapse: collapse;">
        <tr><td>Required Capacity:</td><td style="color:#38bdf8">{q_req:.1f} Watts</td></tr>
        <tr><td>Target Cabinet Temp:</td><td>{design_params['target']}°C</td></tr>
        <tr><td>Ambient Condition:</td><td>{design_params['amb']}°C (Tropical)</td></tr>
        <tr><td>Refrigerant:</td><td>{ref_choice}</td></tr>
        <tr><td>Recommended Capillary:</td><td>0.031" ID x 3.2m</td></tr>
    </table>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("Generate Final Engineering Report"):
        st.balloons()
        st.success("Report Compiled for Cabinet ID: RIP-SYS-2024")

st.markdown("---")
st.markdown(f"<p style='text-align: center; color: #475569;'>RIP v4.0 | BUILT BY {DEV_NAME.upper()} | MECHANICAL LOAD ENGINE ENABLED</p>", unsafe_allow_html=True)
