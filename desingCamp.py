import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# --- UI Config ---
st.set_page_config(page_title="Pile Design Pro", layout="wide")

st.markdown("""
    <style>
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .main-box { background-color: #f8f9fa; padding: 25px; border-radius: 15px; border: 1px solid #dee2e6; }
    h3 { color: #1e3a8a; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏗️ วิเคราะห์ฐานรากและแรงในเสาเข็ม $P_i$")

# --- Sidebar Inputs ---
with st.sidebar:
    st.header("📥 ข้อมูลออกแบบ")
    with st.expander("น้ำหนักบรรทุกและเสาตอม่อ", expanded=True):
        P_axial = st.number_input("แรงแนวแกน P [kN]", value=1000.0)
        Mx_app = st.number_input("Applied Mx [kN-m]", value=50.0)
        My_app = st.number_input("Applied My [kN-m]", value=30.0)
        col_x = st.number_input("พิกัดเสาตอม่อ X [m] (เทียบมุมซ้ายล่าง)", value=0.15)
        col_y = st.number_input("พิกัดเสาตอม่อ Y [m] (เทียบมุมซ้ายล่าง)", value=0.10)
    
    with st.expander("การจัดเรียงเสาเข็ม", expanded=True):
        nx = st.number_input("จำนวนเข็มแถว X", min_value=1, value=3)
        ny = st.number_input("จำนวนเข็มแถว Y", min_value=1, value=2)
        sx = st.number_input("ระยะห่างแนว X (s) [m]", value=0.8)
        sy = st.number_input("ระยะห่างแนว Y (s) [m]", value=0.8)
        q_safe = st.number_input("น้ำหนักปลอดภัย [kN]", value=200.0)

# --- Calculation Logic ---
# 1. สร้างพิกัดเข็ม (เริ่มจาก 0,0 ที่มุมซ้ายล่าง)
x_raw = np.linspace(0, (nx-1)*sx, nx) if nx > 1 else np.array([0.0])
y_raw = np.linspace(0, (ny-1)*sy, ny) if ny > 1 else np.array([0.0])
xv, yv = np.meshgrid(x_raw, y_raw)
piles = pd.DataFrame({'x_raw': xv.flatten(), 'y_raw': yv.flatten()})

# 2. หาจุดศูนย์ถ่วง (X-bar, Y-bar)
x_bar, y_bar = piles['x_raw'].mean(), piles['y_raw'].mean()

# 3. พิกัดสัมพัทธ์เทียบกับ CG (xi, yi)
piles['xi'] = piles['x_raw'] - x_bar
piles['yi'] = piles['y_raw'] - y_bar

# 4. หา Eccentricity (ระยะเยื้องศูนย์)
ex = col_x - x_bar
ey = col_y - y_bar

# 5. คำนวณ Total Moment และแรง Pi
Mx_total = Mx_app + (P_axial * ey)
My_total = My_app + (P_axial * ex)
sum_x2, sum_y2 = (piles['xi']**2).sum(), (piles['yi']**2).sum()
n_piles = len(piles)

# สูตรคำนวณแรงในเสาเข็ม Pi
piles['Pi'] = (P_axial / n_piles) + \
             (Mx_total * piles['yi'] / sum_y2 if sum_y2 != 0 else 0) + \
             (My_total * piles['xi'] / sum_x2 if sum_x2 != 0 else 0)

# --- Visualization ---
st.markdown('<div class="main-box">', unsafe_allow_html=True)
col_plot, col_stats = st.columns([2, 1])

with col_plot:
    fig = go.Figure()
    
    # วาดขอบเขตฐานราก (Offset ออกจากเข็มเล็กน้อย)
    offset = 0.4
    f_x = [piles['xi'].min()-offset, piles['xi'].max()+offset, piles['xi'].max()+offset, piles['xi'].min()-offset, piles['xi'].min()-offset]
    f_y = [piles['yi'].min()-offset, piles['yi'].min()-offset, piles['yi'].max()+offset, piles['yi'].max()+offset, piles['yi'].min()-offset]
    fig.add_trace(go.Scatter(x=f_x, y=f_y, fill="toself", fillcolor='rgba(236, 240, 241, 0.5)', 
                             line=dict(color='#bdc3c7', width=2, dash='dash'), name='Footing Cap'))

    # คำนวณขนาดจุด (Size) ป้องกันค่าติดลบที่ทำให้เกิด Error
    # ใช้ค่าสัมบูรณ์และกำหนดค่าขั้นต่ำที่ 15
    max_val = abs(piles['Pi']).max() if abs(piles['Pi']).max() != 0 else 1
    piles['marker_size'] = (abs(piles['Pi']) / max_val * 40).clip(15)

    # กำหนดสีตามเงื่อนไข
    node_colors = []
    for val in piles['Pi']:
        if val > q_safe: node_colors.append('#e74c3c') # แดง (เกิน)
        elif val < 0: node_colors.append('#f39c12')    # ส้ม (แรงดึง)
        else: node_colors.append('#2ecc71')             # เขียว (ปกติ)

    # วาดเสาเข็ม
    fig.add_trace(go.Scatter(
        x=piles['xi'], y=piles['yi'], mode='markers+text',
        text=piles['Pi'].apply(lambda x: f"{x:.1f}"),
        textposition="top center",
        marker=dict(size=piles['marker_size'], color=node_colors, line=dict(width=2, color='white')),
        name='แรงในเข็ม (kN)'
    ))

    # จุด CG และจุดลงแรงเสา
    fig.add_trace(go.Scatter(x=[0], y=[0], mode='markers', marker=dict(color='black', size=12, symbol='cross'), name='Centroid (CG)'))
    fig.add_trace(go.Scatter(x=[ex], y=[ey], mode='markers', marker=dict(color='#3498db', size=15, symbol='circle-dot'), name='ตำแหน่งเสา (Column)'))

    fig.update_layout(
        title="Top View: Pile Force Distribution",
        xaxis=dict(title="X-distance (m)", zeroline=True, zerolinewidth=1, zerolinecolor='black'),
        yaxis=dict(title="Y-distance (m)", scaleanchor="x", scaleratio=1, zeroline=True, zerolinewidth=1, zerolinecolor='black'),
        height=550, margin=dict(l=20, r=20, t=50, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig, use_container_width=True)

with col_stats:
    st.subheader("📊 สรุปผล")
    max_p = piles['Pi'].max()
    min_p = piles['Pi'].min()
    
    st.metric("Max Load", f"{max_p:.2f} kN", delta=f"{max_p-q_safe:.1f} kN" if max_p > q_safe else "Safe")
    st.metric("Min Load", f"{min_p:.2f} kN", delta="Tension" if min_p < 0 else None, delta_color="inverse")
    
    with st.expander("รายละเอียดพิกัดและโมเมนต์", expanded=True):
        st.write(f"**$\overline{{x}}$:** {x_bar:.2f} m, **$\overline{{y}}$:** {y_bar:.2f} m")
        st.write(f"**$e_x$:** {ex:.3f} m, **$e_y$:** {ey:.3f} m")
        st.write(f"**$M_x (Total)$:** {Mx_total:.2f} kN-m")
        st.write(f"**$M_y (Total)$:** {My_total:.2f} kN-m")

st.markdown('</div>', unsafe_allow_html=True)

# --- ตารางรายละเอียดเดิม ---
st.subheader("📋 ตารางข้อมูลเสาเข็มรายต้น")
st.dataframe(piles[['xi', 'yi', 'Pi']].rename(columns={
    'xi': 'x (local)', 
    'yi': 'y (local)', 
    'Pi': 'Force (kN)'
}), use_container_width=True)
