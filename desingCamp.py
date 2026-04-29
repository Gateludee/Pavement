import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# --- UI Configuration ---
st.set_page_config(page_title="Geotech Pile Foundation Designer", layout="wide")

# Custom CSS เพื่อความสวยงาม
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #007bff; color: white; }
    .result-card { background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    </style>
    """, unsafe_allow_html=True)

st.title("🏗️ Eccentric Pile Foundation Analyzer")
st.subheader("การออกแบบฐานรากรับโมเมนต์และตรวจสอบแรงในเสาเข็ม")

# --- Sidebar Inputs ---
with st.sidebar:
    st.header("📥 Input Parameters")
    
    with st.expander("Loadings (Service Loads)", expanded=True):
        P = st.number_input("Vertical Load (P) [kN]", value=1000.0)
        Mx = st.number_input("Moment Mx [kN-m]", value=150.0)
        My = st.number_input("Moment My [kN-m]", value=100.0)
    
    with st.expander("Pile Configuration", expanded=True):
        col_count = st.number_input("Number of Columns", min_value=1, value=3)
        row_count = st.number_input("Number of Rows", min_value=1, value=3)
        spacing_x = st.number_input("Spacing X [m]", value=1.0)
        spacing_y = st.number_input("Spacing Y [m]", value=1.0)
        pile_capacity = st.number_input("Pile Safe Capacity [kN]", value=200.0)

# --- Calculation Logic ---
def calculate_pile_forces(P, Mx, My, nx, ny, sx, sy):
    # สร้าง Coordinates ของเสาเข็ม (Center x=0, y=0)
    x_coords = np.linspace(-(nx-1)*sx/2, (nx-1)*sx/2, nx)
    y_coords = np.linspace(-(ny-1)*sy/2, (ny-1)*sy/2, ny)
    xv, yv = np.meshgrid(x_coords, y_coords)
    
    piles = pd.DataFrame({
        'ID': range(1, nx*ny + 1),
        'X': xv.flatten(),
        'Y': yv.flatten()
    })
    
    n = len(piles)
    sum_x2 = (piles['X']**2).sum()
    sum_y2 = (piles['Y']**2).sum()
    
    # คำนวณ Force ต่อต้น
    # Qi = P/n + (Mx*y/sum_y2) + (My*x/sum_x2)
    piles['Force'] = (P/n) + (Mx * piles['Y'] / sum_y2 if sum_y2 != 0 else 0) + \
                     (My * piles['X'] / sum_x2 if sum_x2 != 0 else 0)
    
    return piles

piles_df = calculate_pile_forces(P, Mx, My, col_count, row_count, spacing_x, spacing_y)
max_force = piles_df['Force'].max()
min_force = piles_df['Force'].min()

# --- Main Display ---
col1, col2 = st.columns([1, 1.5])

with col1:
    st.markdown('<div class="result-card">', unsafe_allow_html=True)
    st.write("### 📊 Summary Results")
    st.metric("Max Pile Force", f"{max_force:.2f} kN", 
              delta=f"{max_force - pile_capacity:.2f}" if max_force > pile_capacity else "OK",
              delta_color="inverse")
    st.metric("Min Pile Force", f"{min_force:.2f} kN")
    
    # Check Status
    if max_force > pile_capacity:
        st.error("❌ OVER CAPACITY: แรงในเสาเข็มเกินค่าที่กำหนด")
    elif min_force < 0:
        st.warning("⚠️ TENSION DETECTED: พบแรงดึงในเสาเข็ม")
    else:
        st.success("✅ DESIGN PASS: ฐานรากปลอดภัย")
    
    st.dataframe(piles_df.style.highlight_max(axis=0, subset=['Force'], color='#ffcccc'))
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    # --- Visualization with Plotly ---
    fig = go.Figure()

    # วาดเข็ม
    fig.add_trace(go.Scatter(
        x=piles_df['X'], y=piles_df['Y'],
        mode='markers+text',
        text=piles_df['Force'].round(1),
        textposition="top center",
        marker=dict(
            size=piles_df['Force'].abs() / max_force * 40 + 10,
            color=piles_df['Force'],
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title="Force (kN)")
        ),
        name='Piles'
    ))

    # ตกแต่ง Layout
    fig.update_layout(
        title="Pile Force Distribution Map",
        xaxis_title="Distance X (m)",
        yaxis_title="Distance Y (m)",
        height=600,
        template="plotly_white"
    )
    
    st.plotly_chart(fig, use_container_width=True)

# --- Footer ---
st.divider()
st.caption("Developed by Geotechnical Engineer AI Collaborator | Python 3.11+ | Streamlit")
