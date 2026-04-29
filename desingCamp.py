
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# --- Config หน้าจอ ---
st.set_page_config(
    page_title="Geotech Foundation Designer",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- CSS ที่ปรับปรุงใหม่ (Modern look & feel) ---
st.markdown("""
    <style>
    /* พื้นหลังหลัก */
    .main { background-color: #f8fafc; }
    
    /* สไตล์ Sidebar */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e2e8f0;
    }
    
    /* สไตล์ Input */
    div.stNumberInput > div > div > input {
        background-color: white;
        border-radius: 8px;
        border: 1px solid #cbd5e1;
    }

    /* สไตล์ปุ่มคำนวณ */
    div.stButton > button:first-child {
        background-color: #2563eb;
        color: white;
        font-weight: bold;
        border-radius: 8px;
        border: none;
        padding: 10px 20px;
        width: 100%;
        transition: all 0.3s ease;
    }
    div.stButton > button:first-child:hover {
        background-color: #1d4ed8;
        box-shadow: 0 4px 6px rgba(37, 99, 235, 0.2);
    }

    /* Container ของผลลัพธ์ */
    .result-container {
        background-color: white;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        margin-bottom: 1.5rem;
    }

    /* ตกแต่ง Metric Card ของ Streamlit */
    [data-testid="stMetricValue"] {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1e293b;
    }
    [data-testid="stMetricLabel"] {
        font-size: 1rem;
        color: #64748b;
    }

    </style>
    """, unsafe_allow_html=True)

# --- หัวข้อหลัก ---
st.markdown("<h1 style='text-align: center; color: #1e293b;'>🏗️ การออกแบบฐานรากรับโมเมนต์แบบเยื้องศูนย์</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #64748b; font-size: 1.2rem; margin-bottom: 2rem;'>โปรแกรมตรวจสอบแรงในเสาเข็มและวิเคราะห์ความปลอดภัยของฐานราก</p>", unsafe_allow_html=True)

# --- Sidebar Inputs ---
with st.sidebar:
    st.markdown("<h2 style='color: #2563eb; font-size: 1.5rem; margin-bottom: 1rem;'>📥 ข้อมูลนำเข้า</h2>", unsafe_allow_html=True)
    
    with st.expander("น้ำหนักบรรทุก (Service Loads)", expanded=True):
        P = st.number_input("แรงในแนวแกน (P) [kN]", value=1000.0, step=10.0, format="%.2f")
        Mx = st.number_input("โมเมนต์ รอบแกน X (Mx) [kN-m]", value=150.0, step=5.0, format="%.2f")
        My = st.number_input("โมเมนต์ รอบแกน Y (My) [kN-m]", value=100.0, step=5.0, format="%.2f")
        st.caption("หมายเหตุ: แกน X/Y อยู่กลางกลุ่มเสาเข็ม")
    
    with st.expander("การจัดเรียงเสาเข็ม", expanded=True):
        nx = st.number_input("จำนวนเสาเข็มในแนว X", min_value=1, value=3, step=1)
        ny = st.number_input("จำนวนเสาเข็มในแนว Y", min_value=1, value=3, step=1)
        sx = st.number_input("ระยะห่างเสาเข็มแนว X (sx) [m]", value=1.0, step=0.1, format="%.1f")
        sy = st.number_input("ระยะห่างเสาเข็มแนว Y (sy) [m]", value=1.0, step=0.1, format="%.1f")
        q_safe = st.number_input("น้ำหนักบรรทุกปลอดภัยต่อต้น [kN]", value=200.0, step=10.0, format="%.2f")

# --- การคำนวณ ---
def calculate_pile_data(P, Mx, My, nx, ny, sx, sy, q_safe):
    total_piles = nx * ny
    
    # สร้าง Coordinates
    if nx > 1:
        x_coords = np.linspace(-(nx-1)*sx/2, (nx-1)*sx/2, nx)
    else:
        x_coords = np.array([0.0])
        
    if ny > 1:
        y_coords = np.linspace(-(ny-1)*sy/2, (ny-1)*sy/2, ny)
    else:
        y_coords = np.array([0.0])
        
    xv, yv = np.meshgrid(x_coords, y_coords)
    piles_df = pd.DataFrame({
        'X': xv.flatten(),
        'Y': yv.flatten()
    })
    
    # คำนวณ Inertia
    sum_x2 = (piles_df['X']**2).sum()
    sum_y2 = (piles_df['Y']**2).sum()
    
    # คำนวณ Force ต่อต้น
    # Qi = P/n + (Mx*y/Iyy) + (My*x/Ixx)  => การแทนที่สมการอาจสลับตามการนิยามแกน 
    # ในที่นี้ใช้: Qi = P/n + (Mx*y/sum_y2) + (My*x/sum_x2) เพื่อให้สอดคล้องกับทั่วไป
    piles_df['Force'] = (P/total_piles) + \
                     (Mx * piles_df['Y'] / sum_y2 if sum_y2 != 0 else 0) + \
                     (My * piles_df['X'] / sum_x2 if sum_x2 != 0 else 0)
    
    piles_df['Status'] = np.where(piles_df['Force'] > q_safe, 'Over', 'Pass')
    piles_df['Status'] = np.where(piles_df['Force'] < 0, 'Tension', piles_df['Status'])
    
    # คำนวณ Eccentricity
    ex = My / P if P > 0 else 0
    ey = Mx / P if P > 0 else 0
    
    return piles_df, ex, ey

piles_data, ex, ey = calculate_pile_data(P, Mx, My, nx, ny, sx, sy, q_safe)
max_q = piles_data['Force'].max()
min_q = piles_data['Force'].min()
total_piles = len(piles_data)

# --- การแสดงผลลัพธ์ ---
col_result, col_plot = st.columns([1, 1.2], gap="large")

with col_result:
    st.markdown('<div class="result-container">', unsafe_allow_html=True)
    st.markdown("<h3 style='color: #1e293b; margin-top: 0;'>📊 ผลการวิเคราะห์</h3>", unsafe_allow_html=True)
    
    # แสดงสถานะความปลอดภัย
    if max_q > q_safe:
        st.error(f"❌ **ไม่ผ่าน:** แรงในเสาเข็มสูงสุด ({max_q:.2f} kN) เกินค่าที่กำหนด ({q_safe:.2f} kN)")
    elif min_q < 0:
        st.warning(f"⚠️ **แจ้งเตือน:** พบแรงดึงในเสาเข็ม ({min_q:.2f} kN) ตรวจสอบเหล็กเสริมแรงดึงในเสาเข็ม")
    else:
        st.success(f"✅ **ผ่าน:** ฐานรากสามารถรับน้ำหนักได้ปลอดภัย")

    st.divider()
    
    # สรุปข้อมูลสำคัญ
    st.metric("จำนวนเสาเข็ม", f"{total_piles} ต้น", f"{nx} x {ny}")
    st.metric("แรงกดสูงสุดในเสาเข็ม (Max Q)", f"{max_q:.2f} kN", delta=f"{max_q - q_safe:.2f}" if max_q > q_safe else None, delta_color="inverse")
    st.metric("แรงกดต่ำสุดในเสาเข็ม (Min Q)", f"{min_q:.2f} kN")
    
    with st.expander("รายละเอียดเพิ่มเติม (ระยะเยื้องศูนย์)"):
        st.metric("Ex", f"{ex:.3f} m")
        st.metric("Ey", f"{ey:.3f} m")

    st.markdown('</div>', unsafe_allow_html=True)

with col_plot:
    st.markdown('<div class="result-container">', unsafe_allow_html=True)
    st.markdown("<h3 style='color: #1e293b; margin-top: 0; text-align: center;'>🗺️ แผนผังฐานรากและแรงในเสาเข็ม</h3>", unsafe_allow_html=True)

    # --- สร้างกราฟฐานรากด้วย Plotly ---
    fig = go.Figure()

    # วาดตัวฐานราก (Rectangular Cap)
    if total_piles > 1:
        cap_x = [(piles_data['X'].min() - 0.5*sx), (piles_data['X'].max() + 0.5*sx), (piles_data['X'].max() + 0.5*sx), (piles_data['X'].min() - 0.5*sx), (piles_data['X'].min() - 0.5*sx)]
        cap_y = [(piles_data['Y'].min() - 0.5*sy), (piles_data['Y'].min() - 0.5*sy), (piles_data['Y'].max() + 0.5*sy), (piles_data['Y'].max() + 0.5*sy), (piles_data['Y'].min() - 0.5*sy)]
        
        fig.add_trace(go.Scatter(
            x=cap_x, y=cap_y,
            fill="toself",
            fillcolor='rgba(189, 195, 199, 0.3)',
            line=dict(color='rgba(149, 165, 166, 1)', width=1),
            name='ฐานราก',
            hoverinfo='skip'
        ))

    # กำหนดสีและสถานะเสาเข็ม
    def get_pile_color(force, q_safe):
        if force > q_safe:
            return '#ef4444' # สีแดง
        elif force < 0:
            return '#f59e0b' # สีส้ม
        else:
            return '#22c55e' # สีเขียว

    colors = [get_pile_color(f, q_safe) for f in piles_data['Force']]

    # วาดเสาเข็มและแสดงค่าที่คำนวณได้
    fig.add_trace(go.Scatter(
        x=piles_data['X'], y=piles_data['Y'],
        mode='markers+text',
        # ป้ายกำกับ: แรงในเสาเข็ม (kN) - ทำให้อ่านง่าย
        text=[f"Q = {f:.1f}" for f in piles_data['Force']],
        textposition="top center",
        textfont=dict(
            family="Sarabun, sans-serif",
            size=14,
            color="#1e293b"
        ),
        marker=dict(
            size=piles_data['Force'].apply(lambda x: abs(x)/max_q*30 if max_q > 0 else 10).clip(15, 30),
            color=colors,
            line=dict(width=2, color='white')
        ),
        name='เสาเข็ม',
        hovertemplate='<b>ตำแหน่ง:</b> (%{x:.2f}, %{y:.2f}) m<br><b>แรงในเสาเข็ม:</b> %{text} kN<extra></extra>'
    ))

    # กราฟิกเสริม: แกนศูนย์ถ่วง (CG) และระยะเยื้องศูนย์
    fig.add_hline(y=0, line=dict(color='black', width=1, dash='dash'))
    fig.add_vline(x=0, line=dict(color='black', width=1, dash='dash'))
    
    # จุด CG
    fig.add_trace(go.Scatter(x=[0], y=[0], mode='markers', marker=dict(color='black', size=10, symbol='cross'), name='CG', hoverinfo='skip'))
    
    # จุด Eccentricity (P)
    fig.add_trace(go.Scatter(x=[ex], y=[ey], mode='markers', marker=dict(color='#2563eb', size=12, symbol='circle'), name='จุดลงแรง', hoverinfo='skip'))

    # ตกแต่ง Layout ให้ดูง่าย
    fig.update_layout(
        xaxis=dict(
            title="ระยะทางแนว X (m)",
            zeroline=False,
            showgrid=True,
            gridcolor='#e2e8f0'
        ),
        yaxis=dict(
            title="ระยะทางแนว Y (m)",
            zeroline=False,
            showgrid=True,
            gridcolor='#e2e8f0',
            scaleanchor="x",
            scaleratio=1 # ทำให้ x และ y มีมาตราส่วนเดียวกัน (Aspect Ratio 1:1)
        ),
        plot_bgcolor='rgba(255, 255, 255, 1)',
        margin=dict(l=40, r=40, t=10, b=40),
        height=550,
        showlegend=True,
        legend=dict(yanchor="bottom", y=0.01, xanchor="left", x=0.01),
        font=dict(family="Sarabun, sans-serif")
    )
    
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- ส่วนท้าย ---
st.markdown("<p style='text-align: center; color: #94a3b8; font-size: 0.9rem;'>พัฒนาโดย Geotechnical Engineer AI Collaborator | สำหรับใช้ตรวจสอบเบื้องต้นเท่านั้น</p>", unsafe_allow_html=True)
