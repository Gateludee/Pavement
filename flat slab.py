import streamlit as st
import math

# ตั้งค่าหน้าจอ
st.set_page_config(page_title="PT Slab Professional", layout="wide")
st.title("🏗️ PT Flat Slab Design Tool (Full Version)")
st.markdown("สำหรับอาคาร 4 ชั้น - วิเคราะห์ความหนาและความปลอดภัย")

# --- แถบด้านข้าง: กรอกข้อมูล (เรียงตามที่คุณต้องการ) ---
st.sidebar.header("📋 ข้อมูลการออกแบบ")

# 1. ระยะช่วงเสา
L_long = st.sidebar.number_input("ระยะช่วงเสาด้านยาว (เมตร)", value=8.0)
L_short = st.sidebar.number_input("ระยะช่วงเสาด้านสั้น (เมตร)", value=7.0)

# 2. น้ำหนักบรรทุก (Loads)
ll = st.sidebar.number_input("น้ำหนักบรรทุกจร - LL (kg/m²)", value=300)
dl_extra = st.sidebar.number_input("น้ำหนักบรรทุกคงที่เพิ่มเติม - DL (kg/m²)", value=100)
mep_load = st.sidebar.number_input("น้ำหนักงานระบบ - MEP (kg/m²)", value=50)

# 3. กำลังวัสดุ (Materials)
fc_prime = st.sidebar.number_input("กำลังอัดคอนกรีต f'c (kg/cm²)", value=320)
fy = st.sidebar.number_input("กำลังดึงเหล็กเสริม fy (kg/cm²)", value=4000)

# 4. ใส่ความหนาเอง
t_input = st.sidebar.number_input("ระบุความหนาพื้นที่คุณต้องการ (ซม.)", value=20.0)

# --- ขั้นตอนการคำนวณ ---

# น้ำหนักพื้น (Self-weight)
sw = (t_input / 100) * 2400
total_dead_load = sw + dl_extra + mep_load
total_load = total_dead_load + ll

# การตรวจสอบแรงเฉือนทะลุ (Punching Shear)
d = t_input - 4  # ระยะใช้งานจริง (หักระยะหุ้ม)
column_size = 30 # สมมติเสา 30x30 ซม.
b_o = 4 * (column_size + d) # เส้นรอบรูปวิกฤต
v_u = total_load * (L_long * L_short) # แรงกดลงหัวเสา
# สูตรกำลังรับแรงเฉือน PT เบื้องต้น
v_c = (0.27 * math.sqrt(fc_prime) + 0.3 * 15) * b_o * d  # 15 คือแรงกดอัดสมมติ

# --- ส่วนแสดงผลหน้าจอหลัก ---
st.header("🔍 รายงานการวิเคราะห์")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("⚖️ น้ำหนักที่กระทำ")
    st.write(f"- น้ำหนักพื้น (SW): {sw:.0f} kg/m²")
    st.write(f"- น้ำหนัก DL เพิ่มเติม: {dl_extra:.0f} kg/m²")
    st.write(f"- น้ำหนัก MEP: {mep_load:.0f} kg/m²")
    st.metric("น้ำหนักรวม (Total)", f"{total_load:.0f} kg/m²")

with col2:
    st.subheader("🧱 ข้อมูลวัสดุ")
    st.metric("กำลังคอนกรีต (f'c)", f"{fc_prime} ksc")
    st.metric("กำลังเหล็กเสริม (fy)", f"{fy} ksc")

with col3:
    st.subheader("🛡️ การตรวจสอบความปลอดภัย")
    punching_status = v_c > v_u
    if punching_status:
        st.success("แรงเฉือน: ✅ ผ่าน")
    else:
        st.error("แรงเฉือน: ❌ ไม่ผ่าน")
    
    st.write(f"แรงกดลงเสา: {v_u:,.0f} kg")
    st.write(f"ความสามารถที่รับได้: {v_c:,.0f} kg")

st.divider()

# --- บรรทัดสรุปผลตัวโตๆ ---
st.subheader("📢 บทสรุปวิศวกร")

h_min_code = (L_long * 100) / 45 # เกณฑ์ความหนาขั้นต่ำตามมาตรฐาน

if punching_status and t_input >= h_min_code:
    st.balloons()
    st.success(f"**ใช้ได้!** ความหนา {t_input} ซม. ปลอดภัยต่อการรับน้ำหนัก และไม่บางจนเกินไปสำหรับช่วงเสา {L_long} เมตร")
else:
    error_msg = ""
    if v_u > v_c: error_msg += "- พื้นเสี่ยงจะทะลุที่หัวเสา (Punching Shear Failure) \n"
    if t_input < h_min_code: error_msg += f"- พื้นบางกว่าเกณฑ์แนะนำ ({h_min_recommended:.1f} ซม.) อาจมีปัญหาการสั่นหรือแอ่นตัว \n"
    st.error(f"**ต้องปรับปรุง!** \n {error_msg}")

st.info(f"💡 คำแนะนำเพิ่มเติม: สำหรับเหล็กเสริม fy {fy} ksc ควรใส่เหล็กเสริมกันร้าวที่ผิวบนและล่างตามมาตรฐานเพื่อช่วยลวด PT อีกแรงครับ")
