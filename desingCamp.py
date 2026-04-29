import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# --- UI Config ---
st.set_page_config(page_title="Pile Foundation Expert", layout="wide")

st.markdown("""
    <style>
    .report-card { background-color: #ffffff; padding: 20px; border-radius: 10px; border: 1px solid #e1e4e8; margin-bottom: 20px; }
    .metric-box { text-align: center; padding: 10px; background: #f0f2f6; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏗️ โปรแกรมวิเคราะห์แรงในเสาเข็มแบบละเอียด")
st.write("คำนวณตั้งแต่หาจุดศูนย์ถ่วง ระยะเยื้องศูนย์ จนถึงแรงปฏิกิริยาในเสาเข็ม")

# --- Sidebar Inputs ---
with st.sidebar:
    st.header("1. ข้อมูลน้ำหนักบรรทุก")
    P_axial = st.number_input("แรงแนวแกน P [kN]", value=1200.0)
    Mx_app = st.number_input("Applied Moment Mx [kN-m]", value=100.0)
    My_app = st.number_input("Applied Moment My [kN-m]", value=80.0)
    
    st.header("2. ตำแหน่งเสาตอม่อ (Column)")
    col_x = st.number_input("พิกัดเสาตอม่อ X [m]", value=0.2)
    col_y = st.number_input("พิกัดเสาตอม่อ Y [m]", value=0.1)

    st.header("3. การจัดเรียงเสาเข็ม")
    nx = st.number_input("จำนวนเสาเข็มแถว X", min_value=1, value=3)
    ny = st.number_input("จำนวนเสาเข็มแถว Y", min_value=1, value=2)
    sx = st.number_input("ระยะห่างแนว X (sx) [m]", value=1.0)
    sy = st.number_input("ระยะห่างแนว Y (sy) [m]", value=1.0)
    q_safe = st.number_input("Capacity ต่อต้น [kN]", value=250.0)

# --- Process Calculation ---

# A. สร้างพิกัดเสาเข็มเบื้องต้น (Relative to 0,0)
x_raw = np.linspace(0, (nx-1)*sx, nx)
y_raw = np.linspace(0, (ny-1)*sy, ny)
xv, yv = np.meshgrid(x_raw, y_raw)
piles = pd.DataFrame({'x_raw': xv.flatten(), 'y_raw': yv.flatten()})

# B. หา x_bar, y_bar (Centroid)
x_bar = piles['x_raw'].mean()
y_bar = piles['y_raw'].mean()

# C. ปรับพิกัดให้เทียบกับจุดศูนย์ถ่วง (Local Coordinates)
piles['xi'] = piles['x_raw'] - x_bar
piles['yi'] = piles['y_raw'] - y_bar

# D. หา Eccentricity (ระยะเยื้องศูนย์)
ex = col_x - x_bar
ey = col_y - y_bar

# E. คำนวณ Total Moment
Mx_total = Mx_app + (P_axial * ey)
My_total = My_app + (P_axial * ex)

# F. คำนวณ Sum x^2 และ Sum y^2
sum_x2 = (piles['xi']**2).sum()
sum_y2 = (piles['yi']**2).sum()

# G. คำนวณ Pi (Force in each pile)
n = len(piles)
piles['Pi'] = (P_axial / n) + \
             (Mx_total * piles['yi'] / sum_y2 if sum_y2 != 0 else 0) + \
             (My_total * piles['xi'] / sum_x2 if sum_x2 != 0 else 0)

# --- Display Results ---
col1, col2 = st.columns([1, 2])

with col1:
    st.markdown('<div class="report-card">', unsafe_allow_html=True)
    st.subheader("📝 ผลการคำนวณพิกัด")
    st.write(f"**จุดศูนย์ถ่วงกลุ่มเข็ม ($\overline{{x}}, \overline{{y}}$):** ({x_bar:.2f}, {y_bar:.2f}) m")
    st.write(f"**ระยะเยื้องศูนย์ ($e_x, e_y$):** ({ex:.3f}, {ey:.3f}) m")
    st.divider()
    st.subheader("⚖️ โมเมนต์ที่ใช้เขียนแบบ")
    st.write(f"**Total $M_x$:** {Mx_total:.2f} kN-m")
    st.write(f"**Total $M_y$:** {My_total:.2f} kN-m")
    st.divider()
    
    max_pi = piles['Pi'].max()
    st.metric("Max Pile Load ($P_i$)", f"{max_pi:.2f} kN", 
              delta=f"{max_pi - q_safe:.2f}" if max_pi > q_safe else "Safe",
              delta_color="inverse")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    # --- Visualization ---
    fig = go.Figure()

    # วาดเข็ม
    fig.add_trace(go.Scatter(
        x=piles['xi'], y=piles['yi'],
        mode='markers+text',
        text=piles['Pi'].round(1),
        textposition="top center",
        marker=dict(
            size=30,
            color=piles['Pi'],
            colorscale='RdYlGn',
            reversescale=True,
            showscale=True,
            line=dict(width=2, color='DarkSlateGrey')
        ),
        name='Pile Force'
    ))

    # วาดจุดที่แรงลง (Column Position)
    fig.add_trace(go.Scatter(
        x=[ex], y=[ey],
        mode='markers',
        marker=dict(color='blue', size=15, symbol='x'),
        name='Point of Load (Column)'
    ))

    fig.update_layout(
        title="แผนผังแรงในเสาเข็ม (เทียบกับจุดศูนย์ถ่วงกลุ่มเข็ม)",
        xaxis_title="Distance from X-bar (m)",
        yaxis_title="Distance from Y-bar (m)",
        height=600,
        yaxis=dict(scaleanchor="x", scaleratio=1)
    )
    
    st.plotly_chart(fig, use_container_width=True)

# ตารางสรุป
st.subheader("📋 รายละเอียดเสาเข็มแต่ละต้น")
st.dataframe(piles[['xi', 'yi', 'Pi']].rename(columns={'xi':'x (local)', 'yi':'y (local)', 'Pi':'Force [kN]'}).style.background_gradient(cmap='YlOrRd'))
