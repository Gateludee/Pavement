import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# --- UI Configuration ---
st.set_page_config(page_title="Pile Design - New Centroid Coordinates", layout="wide")

st.markdown("""
    <style>
    .main-box { background-color: #ffffff; padding: 20px; border-radius: 12px; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
    .highlight-box { background-color: #f0f9ff; padding: 15px; border-radius: 10px; border-left: 5px solid #0ea5e9; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏗️ คำนวณพิกัดเสาเข็มใหม่ตามตำแหน่ง Centroid ของตอม่อ")

# --- Sidebar Inputs ---
with st.sidebar:
    st.header("1. ตำแหน่งเสาตอม่อ (Target Centroid)")
    col_x_final = st.number_input("พิกัดเสาตอม่อ X [m]", value=5.00, help="ต้องการให้ Centroid ของกลุ่มเข็มมาอยู่ที่พิกัดนี้")
    col_y_final = st.number_input("พิกัดเสาตอม่อ Y [m]", value=5.00, help="ต้องการให้ Centroid ของกลุ่มเข็มมาอยู่ที่พิกัดนี้")

    st.header("2. การจัดเรียงเข็ม (Layout)")
    nx = st.number_input("จำนวนเข็มแถว X", min_value=1, value=3)
    ny = st.number_input("จำนวนเข็มแถว Y", min_value=1, value=2)
    sx = st.number_input("ระยะห่าง S-X [m]", value=0.90)
    sy = st.number_input("ระยะห่าง S-Y [m]", value=0.90)
    
    st.header("3. น้ำหนักบรรทุก (Load)")
    P = st.number_input("แรงในแนวแกน P [kN]", value=1200.0)
    Mx_app = st.number_input("Mx จากโครงสร้าง [kN-m]", value=50.0)
    My_app = st.number_input("My จากโครงสร้าง [kN-m]", value=30.0)
    q_safe = st.number_input("Capacity [kN/ต้น]", value=300.0)

# --- Calculation Logic ---

# 1. สร้างพิกัดสัมพัทธ์ (Relative to its own center)
x_rel = np.linspace(-(nx-1)*sx/2, (nx-1)*sx/2, nx) if nx > 1 else np.array([0.0])
y_rel = np.linspace(-(ny-1)*sy/2, (ny-1)*sy/2, ny) if ny > 1 else np.array([0.0])
xv, yv = np.meshgrid(x_rel, y_rel)
piles = pd.DataFrame({'xi': xv.flatten(), 'yi': yv.flatten()})

# 2. คำนวณพิกัดใหม่ในระบบ Global (ขยับ Centroid ไปที่พิกัดเสาตอม่อ)
piles['X_Global'] = col_x_final + piles['xi']
piles['Y_Global'] = col_y_final + piles['yi']

# 3. คำนวณแรงในเสาเข็ม (เมื่อ e = 0 เพราะจัดวาง Centroid ตรงกับเสาแล้ว)
# แรงจะเกิดจาก P/n และโมเมนต์ Mx, My ที่มาจากโครงสร้างเท่านั้น
sum_x2 = (piles['xi']**2).sum()
sum_y2 = (piles['yi']**2).sum()
n = len(piles)

piles['Pi'] = (P / n) + \
             (Mx_app * piles['yi'] / sum_y2 if sum_y2 != 0 else 0) + \
             (My_app * piles['xi'] / sum_x2 if sum_x2 != 0 else 0)

# --- Results Display ---
col_res, col_plt = st.columns([1, 1.5])

with col_res:
    st.markdown('<div class="highlight-box">', unsafe_allow_html=True)
    st.subheader("📍 สรุปการจัดวางพิกัด")
    st.write(f"**ตำแหน่งเป้าหมาย (Centroid):** ({col_x_final:.2f}, {col_y_final:.2f})")
    st.write(f"**จำนวนเสาเข็มทั้งหมด:** {n} ต้น")
    st.write(f"**โมเมนต์ที่ใช้คำนวณ:** Mx={Mx_app:.1f}, My={My_app:.1f} kNm")
    st.markdown('</div>', unsafe_allow_html=True)

    max_p = piles['Pi'].max()
    if max_p <= q_safe:
        st.success(f"✅ ปลอดภัย: แรงสูงสุด {max_p:.1f} kN")
    else:
        st.error(f"❌ เกินพิกัด: แรงสูงสุด {max_p:.1f} kN")
    
    st.info("💡 พิกัด Global ในตารางด้านล่าง สามารถนำไปใช้ในแบบแปลนก่อสร้าง (Survey Layout) ได้ทันที")

with col_plt:
    # Visualization
    fig = go.Figure()
    
    # วาดเข็มในพิกัด Global
    fig.add_trace(go.Scatter(
        x=piles['X_Global'], y=piles['Y_Global'], mode='markers+text',
        text=piles['Pi'].apply(lambda x: f"{x:.1f} kN"),
        textposition="top center",
        marker=dict(size=25, color=piles['Pi'], colorscale='Blues', line=dict(width=1, color='DarkSlateGrey')),
        name='เสาเข็ม'
    ))
    
    # จุดตอม่อ (New Centroid)
    fig.add_trace(go.Scatter(
        x=[col_x_final], y=[col_y_final], mode='markers',
        marker=dict(color='red', size=12, symbol='star'),
        name='เสาตอม่อ (Centroid)'
    ))

    fig.update_layout(
        title="Survey Layout (Global Coordinates)",
        xaxis_title="Global X [m]", yaxis_title="Global Y [m]",
        yaxis=dict(scaleanchor="x", scaleratio=1),
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)

# --- ตารางแสดงพิกัดที่ใช้หน้างานจริง ---
st.subheader("📋 ตารางพิกัดเสาเข็มสำหรับงานสำรวจ (Survey Table)")
survey_table = piles[['X_Global', 'Y_Global', 'Pi']].copy()
survey_table.columns = ['พิกัด X (Global)', 'พิกัด Y (Global)', 'แรงปฏิกิริยา Pi (kN)']
st.dataframe(survey_table.style.format("{:.3f}"), use_container_width=True)
