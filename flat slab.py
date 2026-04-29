import streamlit as st
import math

# ตั้งค่าหน้าจอ
st.set_page_config(page_title="PT Slab Design - Academic", layout="wide")
st.title("🏗️ PT Flat Slab Design (LL 500 kg/m² Edition)")
st.markdown("ระบบคำนวณพื้นอัดแรงสำหรับน้ำหนักบรรทุกหนักพิเศษ")

# --- แถบด้านข้าง: กรอกข้อมูล ---
st.sidebar.header("📋 พารามิเตอร์การออกแบบ")

# 1. ระยะช่วงเสา
l_long = st.sidebar.number_input("ระยะช่วงเสาด้านยาว (เมตร)", value=8.0, step=0.5)
l_short = st.sidebar.number_input("ระยะช่วงเสาด้านสั้น (เมตร)", value=7.0, step=0.5)

# 2. น้ำหนักบรรทุก (Loads) - หน่วยเป็น kg/m² 
# (หมายเหตุ: 500 kg/m² เทียบเท่ากับ LL ที่คุณระบุมา)
ll = st.sidebar.number_input("น้ำหนักบรรทุกจร (Live Load) - kg/m²", value=500)
dl_extra = st.sidebar.number_input("น้ำหนักวัสดุปูผิว (Dead Load) - kg/m²", value=100)
mep_load = st.sidebar.number_input("น้ำหนักงานระบบ (MEP) - kg/m²", value=150)

# 3. กำลังวัสดุ (Materials)
fc_prime = st.sidebar.number_input("กำลังอัดคอนกรีต f'c (kg/cm²)", value=320)
fy = st.sidebar.number_input("กำลังดึงเหล็กเสริม fy (kg/cm²)", value=4000)

# 4. ความหนาพื้นที่ระบุ (อาจารย์บอกขั้นต่ำ 30 ซม.)
t_input = st.sidebar.number_input("ระบุความหนาพื้นที่ต้องการทดสอบ (ซม.)", value=30.0)

# --- ขั้นตอนการคำนวณ ---
# น้ำหนักคอนกรีต (Self-weight)
sw = (t_input / 100) * 2400
total_load = sw + dl_extra + mep_load + ll

# เช็คแรงเฉือนทะลุ (Punching Shear)
d = t_input - 4  # ระยะใช้งาน
column_size = 40 # สำหรับโหลดหนัก เสาควรจะใหญ่ขึ้น (สมมติ 40x40 ซม.)
b_o = 4 * (column_size + d)
v_u = total_load * (l_long * l_short)
v_c = (0.27 * math.sqrt(fc_prime) + 0.3 * 15) * b_o * d # สูตรเบื้องต้น

# --- การแสดงผล ---
st.header("🔍 ผลการวิเคราะห์")

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("⚖️ น้ำหนักรวม")
    st.metric("Total Load", f"{total_load:.0f} kg/m²")
    st.write(f"- น้ำหนักพื้น (SW): {sw:.0f}")
    st.write(f"- น้ำหนัก DL+MEP: {dl_extra + mep_load:.0f}")
    st.write(f"- น้ำหนัก LL: {ll:.0f}")

with col2:
    st.subheader("🧱 วัสดุที่ใช้")
    st.metric("f'c (Concrete)", f"{fc_prime} ksc")
    st.metric("fy (Steel)", f"{fy} ksc")

with col3:
    st.subheader("🛡️ ความปลอดภัย")
    is_safe_punching = v_c > v_u
    status = "✅ ผ่าน" if is_safe_punching else "❌ ไม่ผ่าน"
    st.metric("สถานะแรงเฉือน", status)
    st.write(f"แรงกดลงเสา: {v_u:,.0f} kg")
    st.write(f"ขีดจำกัดที่รับได้: {v_c:,.0f} kg")

st.divider()

# --- ส่วนสรุปผลตามเงื่อนไขอาจารย์ ---
st.subheader("📢 บทสรุปและการตรวจสอบ")

# เงื่อนไขจากอาจารย์ (Thickness >= 30 cm)
prof_rule = t_input >= 30

if is_safe_punching and prof_rule:
    st.success(f"✅ **ใช้ได้:** ความหนา {t_input} ซม. เป็นไปตามที่อาจารย์กำหนด และปลอดภัยต่อแรงเฉือน")
else:
    error_msg = ""
    if not prof_rule:
        error_msg += f"- **ความหนาไม่พอ:** อาจารย์กำหนดขั้นต่ำ 30 ซม. (ปัจจุบันเลือก {t_input} ซม.) \n"
    if not is_safe_punching:
        error_msg += "- **อันตราย:** แรงกดจากน้ำหนัก LL {ll} kg/m² มากเกินไป พื้นเสี่ยงจะทะลุหัวเสา \n"
    st.error(f"❌ **ต้องแก้ไข:** \n {error_msg}")

st.info("💡 **Tips:** สำหรับ LL 500 kg/m² พื้นจะรับน้ำหนักมากเป็นพิเศษ การใช้ความหนา 30 ซม. จะช่วยลดการสั่นสะเทือนและการแอ่นตัวได้ดีมากตามที่อาจารย์แนะนำครับ")
