import streamlit as st
import math

# ส่วนหัวโปรแกรม
st.title("🏗️ โปรแกรมคำนวณพื้น PT แบบง่าย")
st.markdown("สำหรับอาคาร 4 ชั้น (คำนวณต่อความกว้างพื้น 1 เมตร)")

# --- แถบด้านข้าง: กรอกตัวเลข (เหมือนโค้ดแรก) ---
st.sidebar.header("📋 ใส่ตัวเลขที่นี่")
L = st.sidebar.number_input("ระยะห่างระหว่างเสา (เมตร)", value=8.0)
live_load = st.sidebar.number_input("น้ำหนักคน/สิ่งของ (kg/m²)", value=300)
sd_load = st.sidebar.number_input("น้ำหนักกระเบื้อง/ผนัง (kg/m²)", value=150)
t_cm = st.sidebar.number_input("ความหนาพื้นที่จะใช้ (ซม.)", value=20.0)

# --- ส่วนคำนวณ (สูตรลับวิศวกร) ---
# 1. น้ำหนักพื้น (คอนกรีตหนัก 2400 kg ต่อลูกบาศก์เมตร)
self_weight = (t_cm / 100) * 2400
total_load = self_weight + sd_load + live_load

# 2. คำนวณแรงดึงลวด (P) เพื่อยกน้ำหนักพื้น 80%
# สูตร: P = (weight * L^2) / (8 * ระยะดัดลวด)
w_bal = 0.80 * self_weight
sag = (t_cm - 5) / 100  # ระยะดัดลวดในเนื้อคอนกรีต
p_force = (w_bal * (L**2)) / (8 * sag)

# 3. จำนวนเส้นลวด (ลวด 1 เส้นรับแรงได้ 14,800 kg)
num_strands = math.ceil(p_force / 14800)

# 4. เช็คความปลอดภัย (P/A Stress)
# คือการดูว่าแรงบีบเหมาะสมไหม (ต้องอยู่ระหว่าง 8.5 - 35)
p_over_a = p_force / (100 * t_cm)

# --- ส่วนแสดงผลหน้าจอหลัก ---
st.header("🔍 ผลการคำนวณ")

col1, col2 = st.columns(2)
with col1:
    st.metric("น้ำหนักรวมที่พื้นต้องรับ", f"{total_load:.0f} kg/m²")
    st.write(f"แยกเป็นน้ำหนักพื้นเอง: {self_weight:.0f} kg/m²")

with col2:
    st.metric("จำนวนเส้นลวดที่ต้องใช้", f"{num_strands} เส้น")
    st.write(f"แรงดึงลวดทั้งหมด: {p_force:,.0f} kg")

st.divider()

# --- บรรทัดสรุปผล (ตามที่ขอ) ---
st.subheader("📢 สรุปผลการออกแบบ")

if 8.5 <= p_over_a <= 35:
    st.success(f"✅ ใช้ได้: ความหนา {t_cm} ซม. และลวด {num_strands} เส้น เหมาะสมตามมาตรฐาน")
else:
    if p_over_a < 8.5:
        st.error(f"❌ ใช้ไม่ได้: แรงบีบน้อยไป (P/A = {p_over_a:.2f}) พื้นจะร้าว ให้ลดความหนาพื้น หรือเพิ่มจำนวนลวด")
    else:
        st.error(f"❌ ใช้ไม่ได้: แรงบีบมากไป (P/A = {p_over_a:.2f}) คอนกรีตจะแตก ให้เพิ่มความหนาพื้น")

st.warning("⚠️ หมายเหตุ: ใช้สำหรับการประมาณการเบื้องต้นเท่านั้น ต้องให้วิศวกรวิชาชีพเซ็นรับรองแบบก่อนสร้างจริง")
