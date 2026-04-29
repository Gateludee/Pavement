import streamlit as st
import math

# ส่วนหัวข้อ App
st.title("🏗️ Flat Slab Design Helper")
st.markdown("โปรแกรมช่วยคำนวณความหนาพื้นและแรงเฉือนเบื้องต้นสำหรับอาคาร 4 ชั้น")

# --- Sidebar: รับค่า Input ---
st.sidebar.header("📋 พารามิเตอร์ที่ต้องระบุ")

# ระยะห่างเสา (Span)
l_x = st.sidebar.number_input("ระยะช่วงเสาด้านสั้น (เมตร)", value=5.0, step=0.5)
l_y = st.sidebar.number_input("ระยะช่วงเสาด้านยาว (เมตร)", value=6.0, step=0.5)

# น้ำหนักบรรทุก (Load)
live_load = st.sidebar.number_input("น้ำหนักบรรทุกจร (kg/m²)", value=200, help="อาคารพักอาศัยทั่วไปประมาณ 150-200 kg/m²")
superimposed_dead_load = st.sidebar.number_input("น้ำหนักวัสดุปูผิว/ผนัง (kg/m²)", value=150)

# วัสดุ (Materials)
fc_prime = st.sidebar.number_input("กำลังอัดคอนกรีต f'c (kg/cm²)", value=240)
fy = st.sidebar.number_input("กำลังรับแรงดึงเหล็กเสริม fy (kg/cm²)", value=4000)

# --- ส่วนคำนวณ ---
st.header("🔍 ผลการวิเคราะห์")

# 1. หาความหนาพื้นขั้นต่ำ (Minimum Thickness)
# สูตรประมาณการสำหรับ Flat Slab ทั่วไปคือ Span/30 ถึง Span/32
min_thickness = (max(l_x, l_y) * 100) / 32 
st.info(f"💡 ความหนาพื้นแนะนำเบื้องต้น: **{min_thickness:.2f} ซม.**")

t = st.number_input("ระบุความหนาพื้นที่คุณต้องการใช้ (ซม.)", value=float(math.ceil(min_thickness)))

# 2. คำนวณน้ำหนักรวม (Total Load Calculation)
concrete_density = 2400 # kg/m³
dead_load = (t/100) * concrete_density
total_load = dead_load + superimposed_dead_load + live_load

# 3. คำนวณแรงเฉือนที่เสา (Punching Shear Check - Simplified)
# พิจารณาเสาขนาด 30x30 ซม.
column_size = 30 
d = t - 3 # ระยะใช้งาน (หักระยะหุ้มเหล็กออก 3 ซม.)
perimeter = 4 * (column_size + d) # เส้นรอบรูปวิกฤต
v_u = total_load * (l_x * l_y) # แรงทั้งหมดที่ลงเสา 1 ต้น

# กำลังรับแรงเฉือนของคอนกรีต (สูตรเบื้องต้น)
# $V_c = 0.53 \times \sqrt{f'c} \times b_o \times d$ (หน่วย kg)
v_c = 0.53 * math.sqrt(fc_prime) * perimeter * d

# --- การแสดงผล ---
col1, col2 = st.columns(2)
with col1:
    st.metric("น้ำหนักรวม (kg/m²)", f"{total_load:.0f}")
with col2:
    status = "✅ ปลอดภัย" if v_c > v_u else "❌ หนาไม่พอ (พื้นอาจทะลุ)"
    st.metric("สถานะแรงเฉือนรอบเสา", status)

st.write(f"**แรงที่กระทำจริง ($V_u$):** {v_u:,.2f} kg")
st.write(f"**ความสามารถในการรับแรงของคอนกรีต ($V_c$):** {v_c:,.2f} kg")

# หมายเหตุ
st.warning("⚠️ โปรดทราบ: นี่เป็นการคำนวณเบื้องต้นเท่านั้น ในการก่อสร้างจริงต้องพิจารณาโมเมนต์ดัดและการจัดเหล็กเสริมโดยวิศวกรโยธาที่มีใบอนุญาต")
