import streamlit as st
import numpy as np
import math

# ตั้งค่าหน้าเว็บ
st.set_page_config(
    page_title="AASHTO 1993 Pavement Design Calculator",
    page_icon="🛣️",
    layout="wide"
)

# หัวข้อหลัก
st.title("🛣️ AASHTO 1993 Structure Number Calculator")
st.markdown("### การคำนวณ Structure Number สำหรับผิวทางลาดยาง")
st.markdown("---")

# ฟังก์ชันคำนวณ AASHTO 1993
def calculate_sn_aashto_1993(W18, ZR, So, delta_PSI, Mr, func_type='solve'):
    """
    คำนวณ Structure Number (SN) ตาม AASHTO 1993
    
    Parameters:
    - W18: Predicted number of 18-kip ESAL applications
    - ZR: Standard normal deviate (reliability)
    - So: Combined standard error
    - delta_PSI: PSI loss (pi - pt)
    - Mr: Resilient modulus (psi)
    - func_type: 'solve' for solving SN, 'check' for checking W18
    """
    
    def aashto_equation(SN):
        """AASHTO 1993 Design Equation"""
        log_W18 = (ZR * So + 9.36 * math.log10(SN + 1) - 0.20 + 
                   math.log10(delta_PSI / (4.2 - 1.5)) / 
                   (0.40 + 1094 / ((SN + 1) ** 5.19)) + 
                   2.32 * math.log10(Mr) - 8.07)
        return log_W18
    
    def newton_raphson_solve(target_log_W18, initial_guess=5.0, max_iter=100, tolerance=1e-6):
        """
        ใช้ Newton-Raphson method แก้สมการหา SN
        """
        SN = initial_guess
        
        for i in range(max_iter):
            # คำนวณ f(SN) = aashto_equation(SN) - target_log_W18
            f_SN = aashto_equation(SN) - target_log_W18
            
            # คำนวณ f'(SN) โดยใช้ numerical derivative
            h = 0.0001
            f_SN_plus_h = aashto_equation(SN + h) - target_log_W18
            f_prime = (f_SN_plus_h - f_SN) / h
            
            # ป้องกันการหารด้วย 0
            if abs(f_prime) < 1e-10:
                break
            
            # Newton-Raphson update
            SN_new = SN - f_SN / f_prime
            
            # ตรวจสอบ convergence
            if abs(SN_new - SN) < tolerance:
                return max(0, SN_new)
            
            SN = SN_new
            
            # ป้องกัน SN ติดลบมากเกินไป
            if SN < -1:
                SN = 0.1
        
        return max(0, SN)
    
    if func_type == 'solve':
        # แก้สมการหา SN
        try:
            target_log_W18 = math.log10(W18)
            SN_solution = newton_raphson_solve(target_log_W18)
            return SN_solution if SN_solution > 0 else None
        except:
            return None
    else:
        # คำนวณ W18 จาก SN
        return 10 ** aashto_equation(func_type)

def get_reliability_z(reliability_percent):
    """แปลง Reliability (%) เป็น Standard Normal Deviate (ZR)"""
    reliability_table = {
        50: 0.000,
        60: -0.253,
        70: -0.524,
        75: -0.674,
        80: -0.841,
        85: -1.037,
        90: -1.282,
        91: -1.340,
        92: -1.405,
        93: -1.476,
        94: -1.555,
        95: -1.645,
        96: -1.751,
        97: -1.881,
        98: -2.054,
        99: -2.327,
        99.9: -3.090
    }
    return reliability_table.get(reliability_percent, -1.645)

# Sidebar - Input Parameters
st.sidebar.header("📊 ข้อมูลนำเข้า (Input Parameters)")

# 1. Traffic Data
st.sidebar.subheader("1. ข้อมูลจราจร (Traffic)")
w18_input = st.sidebar.number_input(
    "ESAL (18-kip) - W₁₈",
    min_value=1000.0,
    max_value=100000000.0,
    value=5000000.0,
    step=100000.0,
    format="%.0f",
    help="Predicted number of 18-kip equivalent single axle load applications"
)

# 2. Reliability
st.sidebar.subheader("2. ความน่าเชื่อถือ (Reliability)")
reliability_options = [50, 60, 70, 75, 80, 85, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 99.9]
reliability = st.sidebar.selectbox(
    "Reliability (%)",
    options=reliability_options,
    index=reliability_options.index(95),
    help="Design reliability level"
)
ZR = get_reliability_z(reliability)
st.sidebar.info(f"ZR = {ZR:.3f}")

# 3. Standard Error
st.sidebar.subheader("3. ค่าคลาดเคลื่อน (Standard Error)")
So = st.sidebar.slider(
    "Overall Standard Deviation (So)",
    min_value=0.30,
    max_value=0.50,
    value=0.45,
    step=0.01,
    help="Combined standard error of traffic prediction and performance prediction"
)

# 4. Serviceability
st.sidebar.subheader("4. ค่า Serviceability")
col1, col2 = st.sidebar.columns(2)
with col1:
    pi = st.number_input(
        "Initial PSI (pi)",
        min_value=3.0,
        max_value=5.0,
        value=4.5,
        step=0.1
    )
with col2:
    pt = st.number_input(
        "Terminal PSI (pt)",
        min_value=1.5,
        max_value=3.5,
        value=2.5,
        step=0.1
    )
delta_PSI = pi - pt

if delta_PSI <= 0:
    st.sidebar.error("⚠️ pi ต้องมากกว่า pt")

# 5. Subgrade
st.sidebar.subheader("5. ชั้นดินเดิม (Subgrade)")
Mr = st.sidebar.number_input(
    "Resilient Modulus, Mr (psi)",
    min_value=1000,
    max_value=50000,
    value=8000,
    step=500,
    help="Roadbed soil resilient modulus"
)

# Main Content
col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("📝 สรุปข้อมูลนำเข้า")
    
    summary_data = {
        "Parameter": [
            "ESAL (W₁₈)",
            "Reliability (%)",
            "Standard Normal Deviate (ZR)",
            "Overall Standard Deviation (So)",
            "Initial PSI (pi)",
            "Terminal PSI (pt)",
            "ΔPSI (pi - pt)",
            "Resilient Modulus (Mr)"
        ],
        "Value": [
            f"{w18_input:,.0f}",
            f"{reliability}%",
            f"{ZR:.3f}",
            f"{So:.2f}",
            f"{pi:.1f}",
            f"{pt:.1f}",
            f"{delta_PSI:.1f}",
            f"{Mr:,} psi"
        ]
    }
    
    st.table(summary_data)

with col_right:
    st.subheader("🎯 ผลการคำนวณ Structure Number")
    
    if delta_PSI > 0:
        # คำนวณ SN
        SN_result = calculate_sn_aashto_1993(w18_input, ZR, So, delta_PSI, Mr, func_type='solve')
        
        if SN_result is not None and SN_result > 0:
            st.success(f"### **SN = {SN_result:.2f}**")
            st.info(f"**SN rounded = {math.ceil(SN_result * 2) / 2:.1f}**")
            
            # แสดงสมการ AASHTO
            st.markdown("---")
            st.markdown("#### 📐 AASHTO 1993 Design Equation:")
            st.latex(r"\log_{10}(W_{18}) = Z_R \cdot S_o + 9.36\log_{10}(SN+1) - 0.20")
            st.latex(r"+ \frac{\log_{10}\left[\frac{\Delta PSI}{4.2-1.5}\right]}{0.40 + \frac{1094}{(SN+1)^{5.19}}} + 2.32\log_{10}(M_R) - 8.07")
        else:
            st.error("❌ ไม่สามารถคำนวณ SN ได้ กรุณาตรวจสอบข้อมูลนำเข้า")
    else:
        st.warning("⚠️ กรุณาตรวจสอบค่า PSI (pi ต้องมากกว่า pt)")

# Layer Coefficient Section
st.markdown("---")
st.header("🏗️ การออกแบบชั้นทาง (Pavement Layer Design)")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("ชั้นผิวทาง (Surface)")
    a1 = st.number_input(
        "Layer Coefficient (a₁)",
        min_value=0.20,
        max_value=0.60,
        value=0.44,
        step=0.01,
        help="Asphalt concrete layer coefficient"
    )
    D1 = st.number_input(
        "Thickness D₁ (inches)",
        min_value=0.0,
        max_value=20.0,
        value=3.0,
        step=0.5
    )
    m1 = st.number_input(
        "Drainage Coefficient (m₁)",
        min_value=0.80,
        max_value=1.20,
        value=1.00,
        step=0.05
    )

with col2:
    st.subheader("ชั้นหินคลุก (Base)")
    a2 = st.number_input(
        "Layer Coefficient (a₂)",
        min_value=0.05,
        max_value=0.20,
        value=0.14,
        step=0.01,
        help="Base layer coefficient"
    )
    D2 = st.number_input(
        "Thickness D₂ (inches)",
        min_value=0.0,
        max_value=30.0,
        value=6.0,
        step=0.5
    )
    m2 = st.number_input(
        "Drainage Coefficient (m₂)",
        min_value=0.80,
        max_value=1.20,
        value=1.00,
        step=0.05
    )

with col3:
    st.subheader("ชั้นดินถม (Subbase)")
    a3 = st.number_input(
        "Layer Coefficient (a₃)",
        min_value=0.05,
        max_value=0.15,
        value=0.11,
        step=0.01,
        help="Subbase layer coefficient"
    )
    D3 = st.number_input(
        "Thickness D₃ (inches)",
        min_value=0.0,
        max_value=30.0,
        value=6.0,
        step=0.5
    )
    m3 = st.number_input(
        "Drainage Coefficient (m₃)",
        min_value=0.80,
        max_value=1.20,
        value=1.00,
        step=0.05
    )

# คำนวณ SN จากชั้นทาง
SN_provided = a1 * D1 * m1 + a2 * D2 * m2 + a3 * D3 * m3

st.markdown("---")
col_check1, col_check2 = st.columns(2)

with col_check1:
    st.subheader("📊 Structure Number ที่ได้จากการออกแบบชั้นทาง")
    st.metric(
        label="SN (Provided)",
        value=f"{SN_provided:.2f}",
        delta=None
    )
    
    # แสดงรายละเอียดการคำนวณ
    st.markdown("**รายละเอียดการคำนวณ:**")
    st.write(f"- Surface: {a1} × {D1} × {m1} = {a1*D1*m1:.2f}")
    st.write(f"- Base: {a2} × {D2} × {m2} = {a2*D2*m2:.2f}")
    st.write(f"- Subbase: {a3} × {D3} × {m3} = {a3*D3*m3:.2f}")
    st.write(f"- **Total SN = {SN_provided:.2f}**")

with col_check2:
    st.subheader("✅ การตรวจสอบการออกแบบ")
    
    if delta_PSI > 0 and SN_result is not None:
        SN_required = SN_result
        
        if SN_provided >= SN_required:
            st.success(f"✅ **ผ่านการตรวจสอบ!**")
            st.success(f"SN (Provided) = {SN_provided:.2f} ≥ SN (Required) = {SN_required:.2f}")
            surplus = SN_provided - SN_required
            st.info(f"มี SN เกิน: {surplus:.2f}")
        else:
            st.error(f"❌ **ไม่ผ่านการตรวจสอบ!**")
            st.error(f"SN (Provided) = {SN_provided:.2f} < SN (Required) = {SN_required:.2f}")
            deficit = SN_required - SN_provided
            st.warning(f"SN ขาด: {deficit:.2f}")
            st.warning("กรุณาเพิ่มความหนาของชั้นทาง")
    else:
        st.warning("กรุณาตรวจสอบข้อมูลนำเข้าด้านบน")

# คำแนะนำ
st.markdown("---")
with st.expander("ℹ️ คำอธิบายและคำแนะนำ"):
    st.markdown("""
    ### Structure Number (SN)
    Structure Number คือตัวเลขที่แสดงถึงความแข็งแรงโครงสร้างของผิวทางลาดยาง
    
    **สมการคำนวณ:**
    
    SN = a₁ × D₁ × m₁ + a₂ × D₂ × m₂ + a₃ × D₃ × m₃
    
    โดยที่:
    - **aᵢ** = Layer coefficient ของชั้นที่ i
    - **Dᵢ** = ความหนาของชั้นที่ i (นิ้ว)
    - **mᵢ** = Drainage coefficient ของชั้นที่ i
    
    ### Layer Coefficient (a) แนะนำ:
    - **Asphalt Concrete**: 0.40 - 0.44
    - **Crushed Stone Base**: 0.13 - 0.14
    - **Subbase**: 0.10 - 0.11
    
    ### Drainage Coefficient (m):
    - **Excellent**: 1.20 - 1.35
    - **Good**: 1.00 - 1.20
    - **Fair**: 0.90 - 1.00
    - **Poor**: 0.80 - 0.90
    
    ### Reliability:
    - ทางหลวงหลัก: 85-99.9%
    - ทางหลวงรอง: 80-95%
    - ทางในเมือง: 50-80%
    """)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center'>"
    "<p>🛣️ AASHTO 1993 Pavement Design Calculator | Developed for Pavement Engineering</p>"
    "</div>", 
    unsafe_allow_html=True
)
