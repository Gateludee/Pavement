import streamlit as st
import math

st.title("🏗️ PT Slab Thickness Finder")
st.markdown("คำนวณหาความหนาพื้นที่ 'เหมาะสมและปลอดภัย' สำหรับอาคาร 4 ชั้น")

# --- แถบด้านข้าง: กรอกข้อมูลที่คุณรู้ ---
st.sidebar.header("📋 ข้อมูลการออกแบบ")
L_long = st.sidebar.number_input("ระยะเสาด้านยาว (เมตร)", value=8.0)
L_short = st.sidebar.number_input("ระยะเสาด้านสั้น (เมตร)", value=6.0)

st.sidebar.divider()
live_load = st.sidebar.number_input("น้ำหนักบรรทุกจร - LL (kg/m²)", value=300)
dl_mep = st.sidebar.number_input("น้ำหนักพื้นผิว + MEP (kg/m²)", value=150)

# --- ขั้นตอนการหาความหนาที่เหมาะสม (Calculation Logic) ---

# 1. หาความหนาขั้นต่ำตามมาตรฐาน (L_long / 45) 
# เป็นค่าเริ่มต้นที่พื้น PT มักจะเริ่ม 'นิ่ง' และไม่สั่น
h_suggested = math.ceil((L_long * 100) / 45)
if h_suggested < 15: h_suggested = 15 # มาตรฐานขั้นต่ำมักไม่น้อยกว่า 15 ซม.

# 2. คำนวณน้ำหนักเพื่อเช็คความปลอดภัย
concrete_weight = (h_suggested / 100) * 2400
total_load = concrete_weight + dl_mep + live_load

# 3. เช็คแรงเฉือนทะลุพื้น (Punching Shear) - หัวใจความปลอดภัย
# สมมติเสาขนาด 30x30 ซม. และคอนกรีต f'c 320
d = h_suggested - 3 # ระยะใช้งานจริง
punching_area = 4 * (30 + d) * d
v_u = total_load * (L_long * L_short) # แรงกดทั้งหมด
v_c = 1.1 * math.sqrt(320) * punching_area # ความสามารถในการรับแรงของคอนกรีต

# --- การแสดงผลสรุป ---
st.header("📍 ความหนาที่แนะนำ")

# แสดงความหนาที่คำนวณได้เป็นตัวใหญ่ๆ
st.info(f"ความหนาพื้นที่เหมาะสมสำหรับโครงการของคุณคือ: **{h_suggested} เซนติเมตร**")

col1, col2 = st.columns(2)
with col1:
    st.metric("น้ำหนักรวม (Total Load)", f"{total_load:.0f} kg/m²")
    st.write(f"- จากคอนกรีต: {concrete_weight:.0f} kg/m²")
    st.write(f"- จาก LL+MEP: {live_load + dl_mep:.0f} kg/m²")

with col2:
    is_safe = v_c > v_u
    status = "✅ ปลอดภัย (Safe)" if is_safe else "❌ เสี่ยงทะลุ (Need Thickness)"
    st.metric("สถานะความปลอดภัย", status)

st.divider()

# --- บรรทัดสรุปส่งท้าย ---
if is_safe:
    st.success(f"สรุป: สำหรับระยะเสา {L_long}x{L_short} ม. แนะนำใช้พื้นหนา **{h_suggested} ซม.** โดยวางลวดประมาณ **{math.ceil(h_suggested*0.6)} เส้นต่อเมตร** จะได้พื้นที่มีประสิทธิภาพสูงสุดครับ")
else:
    st.error("คำเตือน: ระยะเสากว้างเกินไปสำหรับความหนานี้ แนะนำให้เพิ่มความหนาเป็นชั้นละ 2-3 ซม. จนกว่าสถานะจะเป็นสีเขียว")
