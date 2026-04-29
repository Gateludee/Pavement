import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# --- UI Config ---
st.set_page_config(page_title="Pile Design Pro", layout="wide")

# CSS เพื่อความสวยงามและอ่านง่าย
st.markdown("""
    <style>
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .main-box { background-color: #f8f9fa; padding: 25px; border-radius: 15px; border: 1px solid #dee2e6; }
    h3 { color: #1e3a8a; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏗️ วิเคราะห์ฐานรากเยื้องศูนย์และการกระจายแรง $P_i$")

# --- Sidebar Inputs ---
with st.sidebar:
    st.header("📥 ข้อมูลออกแบบ")
    with st.expander("น้ำหนักบรรทุกและเสาตอม่อ", expanded=True):
        P_axial = st.number_input("แรงแนวแกน P [kN]", value=1000.0)
        Mx_app = st.number_input("Applied Mx [kN-m]", value=50.0)
        My_app = st.number_input("Applied My [kN-m]", value=30.0)
        col_x = st.number_input("พิกัดเสาตอม่อ X [m]", value=0.15)
        col_y = st.number_input("พิกัดเสาตอม่อ Y [m]", value=0.10)
    
    with st.expander("การจัดเรียงเสาเข็ม", expanded=True):
        nx = st.number_input("จำนวนเข็มแถว X", min_value=1, value=3)
        ny = st.number_input("จำนวนเข็มแถว Y", min_value=1, value=2)
        sx = st.number_input("ระยะห่างแนว X (s) [m]", value=0.8)
        sy = st.number_input("ระยะห่างแนว Y (s) [m]", value=0.8)
        q_safe = st.number_input("น้ำหนักปลอดภัย [kN]", value=200.0)

# --- Calculation Logic ---
# 1. พิกัดเข็มเบื้องต้น
x_raw = np.linspace(0, (nx-1)*sx, nx)
y_raw = np.linspace(0, (ny-1)*sy, ny)
xv, yv = np.meshgrid(x_raw, y_raw)
piles = pd.DataFrame({'x_raw': xv.flatten(), 'y_raw': yv.flatten()})

# 2. Centroid (x_bar, y_bar)
x_bar, y_bar = piles['x_raw'].mean(), piles['y_raw'].mean()

# 3. Local Coordinates (xi, yi)
piles['xi'] = piles['x_raw'] - x_bar
piles['yi'] = piles['y_raw'] - y_bar

# 4. Eccentricity (ex, ey)
ex = col_x - x_bar
ey = col_y - y_bar

# 5. Total Moment & Forces
Mx_total = Mx_app + (P_axial * ey)
My_total = My_app + (P_axial * ex)
sum_x2, sum_y2 = (piles['xi']**2).sum(), (piles['yi']**2).sum()
n_piles = len(piles)

piles['Pi'] = (P_axial / n_piles) + \
             (Mx_total * piles['yi'] / sum_y2 if sum_y2 != 0 else 0) + \
             (My_total * piles['xi'] / sum_x2 if sum_x2 != 0 else 0)

# --- Visualization (รูปที่เข้าใจง่าย) ---
st.markdown('<div class="main-box">', unsafe_allow_html=True)
col_plot, col_stats = st.columns([2, 1])

with col_plot:
    fig = go.Figure()
    
    # วาดตัวฐานราก (Rectangular Footing)
    footing_x = [piles['xi'].min()-0.4, piles['xi'].max()+0.4, piles['xi'].max()+0.4, piles['xi'].min()-0.4, piles['xi'].min()-0.4]
    footing_y = [piles['yi'].min()-0.4, piles['yi'].min()-0.4, piles['yi'].max()+0.4, piles['yi'].max()+0.4, piles['yi'].min()-0.4]
    fig.add_trace(go.Scatter(x=footing_x, y=footing_y, fill="toself", fillcolor='rgba(200,200,200,0.2)', 
                             line=dict(color='gray', dash='dash'), name='ขอบเขตฐานราก'))

    # วาดเสาเข็ม
    colors = ['#ef4444' if p > q_safe else '#22c55e' for p in piles['Pi']]
    fig.add_trace(go.Scatter(
        x=piles['xi'], y=piles['yi'], mode='markers+text',
        text=piles['Pi'].apply(lambda x: f"{x:.1f} kN"),
        textposition="bottom center",
        marker=dict(size=piles['Pi']/piles['Pi'].max()*40 + 10, color=colors, line=dict(width=2, color='white')),
        name='แรงในเสาเข็ม'
    ))

    # จุด CG และจุดลงแรง (Column)
    fig.add_trace(go.Scatter(x=[0], y=[0], mode='markers', marker=dict(color='black', size=12, symbol='cross'), name='Centroid (CG)'))
    fig.add_trace(go.Scatter(x=[ex], y=[ey], mode='markers', marker=dict(color='blue', size=15, symbol='circle'), name='จุดลงแรง (Column)'))

    fig.update_layout(title="แผนผังการกระจายแรงในเสาเข็ม (Top View)", height=500, 
                      xaxis=dict(gridcolor='#e5e7eb'), yaxis=dict(gridcolor='#e5e7eb', scaleanchor="x", scaleratio=1))
    st.plotly_chart(fig, use_container_width=True)

with col_stats:
    st.subheader("📋 สรุปค่าวิกฤต")
    max_p = piles['Pi'].max()
    min_p = piles['Pi'].min()
    st.metric("Max Force ($P_i$)", f"{max_p:.2f} kN", delta=f"{max_p-q_safe:.1f} kN" if max_p > q_safe else "OK")
    st.metric("Min Force ($P_i$)", f"{min_p:.2f} kN")
    st.write(f"**$\overline{{x}}, \overline{{y}}$:** {x_bar:.2f}, {y_bar:.2f}")
    st.write(f"**$e_x, e_y$:** {ex:.3f}, {ey:.3f}")
    st.write(f"**$M_{{x,total}}$:** {Mx_total:.2f} kN-m")
    st.write(f"**$M_{{y,total}}$:** {My_total:.2f} kN-m")

st.markdown('</div>', unsafe_allow_html=True)

# --- ตารางรายละเอียดแบบเดิม ---
st.subheader("📝 ตารางรายละเอียดเสาเข็มรายต้น")
# ปรับแต่งตารางโดยไม่ใช้ background_gradient เพื่อเลี่ยงปัญหา matplotlib ในบางครั้ง
st.dataframe(piles[['xi', 'yi', 'Pi']].rename(columns={
    'xi': 'ระยะแนว X (จาก CG)', 
    'yi': 'ระยะแนว Y (จาก CG)', 
    'Pi': 'แรงในเสาเข็ม Pi (kN)'
}), use_container_width=True)
