import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# --- UI Configuration ---
st.set_page_config(page_title="Pro Pile Analyzer - Centralized", layout="wide")

st.markdown("""
    <style>
    .report-card { background-color: #ffffff; padding: 20px; border-radius: 12px; border: 1px solid #e2e8f0; }
    .status-pass { color: #15803d; background-color: #f0fdf4; padding: 10px; border-radius: 8px; border: 1px solid #bbf7d0; font-weight: bold; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏗️ Pile Foundation System (Auto-Centering)")

# --- Sidebar Inputs ---
with st.sidebar:
    st.header("1. ข้อมูลการจัดเรียงเข็ม (Pile)")
    nx = st.number_input("จำนวนแถว X", min_value=1, value=3)
    ny = st.number_input("จำนวนแถว Y", min_value=1, value=2)
    sx = st.number_input("ระยะห่าง S-X [m]", value=0.90)
    sy = st.number_input("ระยะห่าง S-Y [m]", value=0.90)
    q_safe = st.number_input("กำลังรับน้ำหนักปลอดภัย [kN/ต้น]", value=300.0)

    st.header("2. ข้อมูลน้ำหนักบรรทุก (Load)")
    P = st.number_input("แรงในแนวแกน (P) [kN]", value=1200.0)
    Mx_app = st.number_input("โมเมนต์ดัด Mx [kN-m]", value=50.0)
    My_app = st.number_input("โมเมนต์ดัด My [kN-m]", value=30.0)
    
    st.header("3. ตำแหน่งเสาตอม่อ (Column)")
    auto_center = st.checkbox("จัดวางเสาตรงกลางฐานรากอัตโนมัติ", value=True)
    
    if not auto_center:
        col_x_input = st.number_input("ตำแหน่งเสา X [m]", value=0.9)
        col_y_input = st.number_input("ตำแหน่งเสา Y [m]", value=0.45)

# --- Calculation Engine ---
# สร้างพิกัดเข็ม
x_raw = np.linspace(0, (nx-1)*sx, nx) if nx > 1 else np.array([0.0])
y_raw = np.linspace(0, (ny-1)*sy, ny) if ny > 1 else np.array([0.0])
xv, yv = np.meshgrid(x_raw, y_raw)
piles = pd.DataFrame({'x_raw': xv.flatten(), 'y_raw': yv.flatten()})

# หาจุดศูนย์ถ่วง (Centroid)
xb, yb = piles['x_raw'].mean(), piles['y_raw'].mean()

# กำหนดตำแหน่งเสา (Column Location)
if auto_center:
    col_x, col_y = xb, yb
else:
    col_x, col_y = col_x_input, col_y_input

# พิกัด Local เทียบกับ CG
piles['xi'] = piles['x_raw'] - xb
piles['yi'] = piles['y_raw'] - yb

# หาความเยื้องศูนย์ (Eccentricity)
ex = col_x - xb
ey = col_y - yb

# คำนวณโมเมนต์สุทธิ (คิดรวมผลจากระยะเยื้องศูนย์)
Mx_total = Mx_app + (P * ey)
My_total = My_app + (P * ex)

# คำนวณ Inertia ของกลุ่มเข็ม
sum_x2 = (piles['xi']**2).sum()
sum_y2 = (piles['yi']**2).sum()

# คำนวณแรง Pi ทุกต้น
n = len(piles)
piles['Pi'] = (P / n) + \
             (Mx_total * piles['yi'] / sum_y2 if sum_y2 != 0 else 0) + \
             (My_total * piles['xi'] / sum_x2 if sum_x2 != 0 else 0)

# --- Display ---
col_ui, col_viz = st.columns([1, 1.5])

with col_ui:
    st.subheader("🚩 สถานะการออกแบบ")
    max_p = piles['Pi'].max()
    if max_p <= q_safe:
        st.markdown(f'<div class="status-pass">✅ ผ่าน (Max: {max_p:.1f} kN)</div>', unsafe_allow_html=True)
    else:
        st.error(f"❌ เกินพิกัด! (Max: {max_p:.1f} kN)")

    with st.expander("รายละเอียดพิกัดทางวิศวกรรม", expanded=True):
        st.write(f"**จุดกึ่งกลาง (CG):** ({xb:.2f}, {yb:.2f}) m")
        st.write(f"**ตำแหน่งเสาจริง:** ({col_x:.2f}, {col_y:.2f}) m")
        st.write(f"**ระยะเยื้องศูนย์ ($e$):** {np.sqrt(ex**2 + ey**2):.3f} m")
        st.info("เมื่อเสาอยู่ตรงกลางพอดี ex และ ey จะเป็น 0 ทำให้โมเมนต์ที่เกิดจากแรงแนวแกนหายไป")

with col_viz:
    fig = go.Figure()
    # ขอบเขตฐานราก
    off = 0.5
    fig.add_trace(go.Scatter(x=[piles.xi.min()-off, piles.xi.max()+off, piles.xi.max()+off, piles.xi.min()-off, piles.xi.min()-off],
                             y=[piles.yi.min()-off, piles.yi.min()-off, piles.yi.max()+off, piles.yi.max()+off, piles.yi.min()-off],
                             fill="toself", fillcolor='rgba(236, 240, 241, 0.5)', line=dict(color='#bdc3c7'), name='Footing'))
    # เสาเข็ม
    fig.add_trace(go.Scatter(x=piles['xi'], y=piles['yi'], mode='markers+text',
                             text=piles['Pi'].apply(lambda x: f"{x:.1f}"),
                             marker=dict(size=30, color=piles['Pi'], colorscale='Greens', showscale=True),
                             name='แรง Pi (kN)'))
    # เสาตอม่อ (Blue dot)
    fig.add_trace(go.Scatter(x=[ex], y=[ey], mode='markers', marker=dict(color='blue', size=15, symbol='square'), name='เสาตอม่อ'))
    
    fig.update_layout(yaxis=dict(scaleanchor="x", scaleratio=1), height=500)
    st.plotly_chart(fig, use_container_width=True)

st.subheader("📋 ตารางพิกัดและแรงปฏิกิริยารายต้น")
st.dataframe(piles[['xi', 'yi', 'Pi']].rename(columns={'xi':'x local (m)', 'yi':'y local (m)', 'Pi':'Force Pi (kN)'}))
