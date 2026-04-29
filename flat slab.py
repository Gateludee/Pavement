import streamlit as st
import math

st.title("🏗️ PT Slab Checker & Finder")
st.markdown("กรอกรายละเอียดเพื่อเช็คความหนาที่เหมาะสมสำหรับอาคาร 4 ชั้น")

# --- แถบด้านข้าง: กรอกข้อมูล ---
st.sidebar.header("📋 ข้อมูลอาคาร")
L_long = st.sidebar.number_input("ระยะช่วงเสาด้านยาว (เมตร)", value=8.0)
L_short = st.sidebar.number_input("ระยะช่วงเสาด้านสั้น (เมตร)", value=6.0)

st.sidebar.divider()
ll = st.sidebar.number_input("น้ำหนักบรรทุกจร - LL (kg/m²)", value=300)
dl_mep = st.sidebar.number_input("น้ำหนักปูผิว + MEP (kg/m²)", value=150)

# --- ส่วนคำนวณหาค่าแนะนำ (Auto) ---
h_min_recommended = math.ceil((L_long * 100) / 45) # สูตร Span/45
if h_min_recommended < 15: h_min_recommended = 15

# --- ส่วนแสดงผลหน้าจอหลัก ---
st.info(f"💡 วิศวกรแนะนำ: สำหรับช่วงเสานี้ ความหนาที่เหมาะสมคือ **{h_min_recommended} ซม.**")

# ช่องให้คุณกรอกความหนาเอง (ที่คุณต้องการ)
t_input = st.number_input("👉 ระบุความหนาพื้นที่คุณต้องการทดสอบ (ซม.)", value=float(h_min_recommended))

# --- คำนวณความปลอดภัยจากตัวเลขที่คุณกรอก ---
# 1. น้ำหนักพื้นจากความหนาที่คุณเลือก
self_weight = (t_input / 100) * 2400
total_load = self_weight + dl_mep + ll

# 2. เช็คแรงเฉือนทะลุ (Punching Shear)
# สมมติเสา 30x30 cm, คอนกรีต f'c 320
d = t_input - 3.5 # ระยะใช้งานจริง (หักระยะหุ้ม)
b_o = 4 * (30 + d) # เส้นรอบรูปวิกฤต
v_u = total_load * (L_long * L_short) # แรงกดทั้งหมดลงเสา
v_c = 1.1 * math.sqrt(320) * b_o * d # กำลังที่คอนกรีตรับได้

# --- สรุปผล ---
st.divider()
st.subheader("📢 ผลการตรวจสอบ")

col1, col2 = st.columns(2)
with col1:
    st.metric("น้ำหนักรวม (Total Load)", f"{total_load:.0f} kg/m²")
    st.write(f"น้ำหนักคอนกรีต: {self_weight:.0f} kg/m²")

with col2:
    # เงื่อนไขการตัดสิน: ต้องหนาพอรับแรงเฉือนได้ และไม่บางกว่าค่าแนะนำมากเกินไป
    is_safe = (v_c > v_u) and (t_input >= (h_min_recommended - 2))
    
    if is_safe:
        st.success("✅ ผลลัพธ์: ใช้ได้ (Safe)")
        st.write("ความหนานี้เพียงพอต่อการรับน้ำหนักและปลอดภัยครับ")
    else:
        st.error("❌ ผลลัพธ์: ไม่ผ่าน (NG)")
        if v_c <= v_u:
            st.write("เหตุผล: **พื้นบางเกินไป** เสี่ยงต่อการเกิดแรงเฉือนทะลุ (Punching Shear)")
        else:
            st.write(f"เหตุผล: บางกว่าค่าแนะนำ ({h_min_recommended} ซม.) พื้นอาจจะสั่นหรือแอ่นตัวได้")

st.divider()
st.warning("⚠️ โปรดปรึกษาวิศวกรโครงสร้างเพื่อคำนวณการจัดวางลวด (Tendon Profile) อีกครั้งก่อนใช้งานจริง")
