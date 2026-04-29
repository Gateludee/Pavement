import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# --- UI Configuration ---
st.set_page_config(page_title="Pro Pile Analyzer", layout="wide")

st.markdown("""
    <style>
    .report-card { background-color: #ffffff; padding: 20px; border-radius: 12px; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }
    .status-pass { color: #15803d; background-color: #f0fdf4; padding: 10px; border-radius: 8px; border: 1px solid #bbf7d0; font-weight: bold; }
    .status-fail { color: #b91c1c; background-color: #fef2f2; padding: 10px; border-radius: 8px; border: 1px solid #fecaca; font-weight: bold; }
    .status-warn { color: #a16207; background-color: #fffbeb; padding: 10px; border-radius: 8px; border: 1px solid #fef3c7; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏗️ Pile Foundation Expert System")

# --- Sidebar Inputs ---
with st.sidebar:
    st.header("1. ข้อมูลน้ำหนักบรรทุก (Load)")
    P = st.number_input("แรงในแนวแกน (P) [kN]", value=1200.0)
    Mx_app = st.number_input("โมเมนต์ดัด Mx [kN-m]", value=80.0)
    My_app = st.number_input("โมเมนต์ดัด My [kN-m]", value=60.0)
    
    st.header("2. พิกัดเสาตอม่อ (Column)")
    col_x = st.number_input("ตำแหน่งเสา X [m]", value=0.10)
    col_y = st.number_input("ตำแหน่งเสา Y [m]", value=0.10)

    st.header("3. การจัดเรียงเข็ม (Pile)")
    nx = st.number_input("จำนวนแถว X", min_value=1, value=3)
    ny = st.number_input("จำนวนแถว Y", min_value=1, value=2)
    sx = st.number_input("ระยะห่าง S-X [m]", value=0.90)
    sy = st.number_input("ระยะห่าง S-Y [m]", value=0.90)
    q_safe = st.number_input("กำลังรับน้ำหนักปลอดภัย [kN/ต้น]", value=300.0)

# --- Calculation Engine ---
# สร้างพิกัดเข็ม
x_raw = np.linspace(0, (nx-1)*sx, nx) if nx > 1 else np.array([0.0])
y_raw = np.linspace(0, (ny-1)*sy, ny) if ny > 1 else np.array([0.0])
xv, yv = np.meshgrid(x_raw, y_raw)
piles = pd.DataFrame({'x_raw': xv.flatten(), 'y_raw': yv.flatten()})

# หาจุดศูนย์ถ่วง (Centroid)
xb, yb = piles['x_raw'].mean(), piles['y_raw'].mean()

# พิกัด Local เทียบกับ CG
piles['xi'] = piles['x_raw'] - xb
piles['yi'] = piles['y_raw'] - yb

# หาความเยื้องศูนย์ (Eccentricity)
ex = col_x - xb
ey = col_y - yb

# คำนวณโมเมนต์สุทธิ
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

max_p = piles['Pi'].max()
min_p = piles['Pi'].min()

# --- Dashboard Display ---
col_ui, col_viz = st.columns([1, 1.5])

with col_ui:
    st.subheader("🚩 การตรวจสอบความปลอดภัย")
    
    # Logic ตรวจสอบสถานะ
    status_checks = []
    
    if max_p > q_safe:
        st.markdown(f'<div class="status-fail">❌ OVER CAPACITY: แรงสูงสุด {max_p:.1f} kN เกินกว่า {q_safe} kN</div>', unsafe_allow_html=True)
        status_checks.append("แก้ไข: เพิ่มจำนวนเสาเข็ม หรือ ขยายระยะห่างเสาเข็ม")
    elif max_p > q_safe * 0.9:
        st.markdown(f'<div class="status-warn">⚠️ MARGINAL: แรง {max_p:.1f} kN ใกล้ขีดจำกัดแล้ว</div>', unsafe_allow_html=True)
        status_checks.append("ระวัง: ตรวจสอบความถูกต้องของน้ำหนักบรรทุกอีกครั้ง")
    else:
        st.markdown(f'<div class="status-pass">✅ SAFE: แรงสูงสุด {max_p:.1f} kN อยู่ในเกณฑ์ปลอดภัย</div>', unsafe_allow_html=True)
    
    if min_p < 0:
        st.markdown(f'<div class="status-warn">⚠️ TENSION: พบแรงดึงในเข็ม {min_p:.1f} kN</div>', unsafe_allow_html=True)
        status_checks.append("แก้ไข: เสริมเหล็กรับแรงดึงในเข็ม หรือขยับตำแหน่งเสาตอม่อเข้าหาจุดศูนย์กลาง")

    if not status_checks:
        st.info("การออกแบบเบื้องต้นมีความสมดุลดี")
    else:
        for suggestion in status_checks:
            st.warning(suggestion)

    st.divider()
    st.write(f"**$\overline{{x}}, \overline{{y}}$ (Centroid):** {xb:.2f}, {yb:.2f} m")
    st.write(f"**$e_x, e_y$ (Eccentricity):** {ex:.3f}, {ey:.3f} m")
    st.write(f"**Total Moment:** Mx={Mx_total:.1f}, My={My_total:.1f} kNm")

with col_viz:
    # Plotly Visual
    fig = go.Figure()
    
    # ขอบเขตฐานราก
    off = 0.4
    fig.add_trace(go.Scatter(x=[piles.xi.min()-off, piles.xi.max()+off, piles.xi.max()+off, piles.xi.min()-off, piles.xi.min()-off],
                             y=[piles.yi.min()-off, piles.yi.min()-off, piles.yi.max()+off, piles.yi.max()+off, piles.yi.min()-off],
                             fill="toself", fillcolor='rgba(241, 245, 249, 0.7)', line=dict(color='#94a3b8'), name='Footing'))

    # เสาเข็ม
    colors = ['#dc2626' if p > q_safe else '#f59e0b' if p < 0 else '#16a34a' for p in piles['Pi']]
    fig.add_trace(go.Scatter(x=piles['xi'], y=piles['yi'], mode='markers+text',
                             text=piles['Pi'].apply(lambda x: f"{x:.1f}"),
                             textposition="top center",
                             marker=dict(size=np.abs(piles['Pi'])/max_p*40 + 10, color=colors, line=dict(width=1, color='white')),
                             name='แรง Pi (kN)'))
    
    # จุด Column
    fig.add_trace(go.Scatter(x=[ex], y=[ey], mode='markers', marker=dict(color='#2563eb', size=15, symbol='circle-dot'), name='Column Position'))

    fig.update_layout(height=500, margin=dict(l=0,r=0,t=30,b=0), yaxis=dict(scaleanchor="x", scaleratio=1), plot_bgcolor='white')
    st.plotly_chart(fig, use_container_width=True)

# --- ตารางรายละเอียดเดิม ---
st.subheader("📋 ตารางพิกัดและแรงปฏิกิริยารายต้น")
st.dataframe(piles[['xi', 'yi', 'Pi']].rename(columns={'xi':'x local (m)', 'yi':'y local (m)', 'Pi':'Force Pi (kN)'}), use_container_width=True)
