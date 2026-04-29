import streamlit as st
import math

st.set_page_config(page_title="PT Slab Checker", layout="wide")
st.title("🏗️ PT Flat Slab Design & Verification")

# --- ส่วนรับข้อมูล ---
with st.sidebar:
    st.header("📋 ข้อมูลการออกแบบ")
    L_long = st.sidebar.number_input("ระยะช่วงเสาด้านยาว (เมตร)", value=8.0)
    L_short = st.sidebar.number_input("ระยะช่วงเสาด้านสั้น (เมตร)", value=7.0)
    h_cm = st.sidebar.number_input("ความหนาพื้นที่ต้องการทดสอบ (ซม.)", value=20.0)
    live_load = st.sidebar.number_input("น้ำหนักบรรทุกจร (kg/m²)", value=300)
    sd_load = st.sidebar.number_input("น้ำหนักวัสดุปูผิว (kg/m²)", value=150)
    fc_prime = st.sidebar.number_input("กำลังอัดคอนกรีต f'c (kg/cm²)", value=320)

# --- ส่วนการคำนวณภายใน ---
self_weight = (h_cm / 100) * 2400
total_dead_load = self_weight + sd_load
# คำนวณแรงดึงลวด (Target Load Balancing 80% of Dead Load)
w_bal = 0.80 * self_weight
sag = (h_cm - 5) / 100 # สมมติระยะหุ้มรวม 5 ซม.
p_eff = (w_bal * (L_long**2)) / (8 * sag) # แรงดึงต่อความกว้าง 1 เมตร

# คำนวณแรงเค้นอัดเฉลี่ย (Average Prestress: P/A)
# ค่าที่เหมาะสมควรอยู่ในช่วง 8.5 ถึง 35 kg/cm² ตามมาตรฐาน ACI/EIT
area_concrete = 100 * h_cm # พื้นที่หน้าตัดกว้าง 1 เมตร (100 ซม.)
avg_prestress = p_eff / area_concrete

# จำนวนลวด
strand_cap = 14800
num_strands = math.ceil(p_eff / strand_cap)

# --- ส่วนสรุปผลการตรวจสอบ ---
st.header("📊 สรุปผลการตรวจสอบ (Design Summary)")

# สร้างกล่องสถานะ
if 8.5 <= avg_prestress <= 35:
    status_text = "✅ ผ่าน (OK): การออกแบบอยู่ในเกณฑ์มาตรฐาน"
    status_color = "green"
else:
    if avg_prestress < 8.5:
        status_text = "❌ ไม่ผ่าน (NG): แรงอัดน้อยไป พื้นอาจแตกร้าวได้ง่าย (เพิ่มลวดหรือลดความหนา)"
    else:
        status_text = "❌ ไม่ผ่าน (NG): แรงอัดมากเกินไป คอนกรีตอาจระเบิด (ลดลวดหรือเพิ่มความหนา)"
    status_color = "red"

st.subheader(f"สถานะ: :{status_color}[{status_text}]")

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("แรงกดอัดเฉลี่ย (P/A)", f"{avg_prestress:.2f} kg/cm²")
with col2:
    st.metric("จำนวนลวดที่ใช้", f"{num_strands} เส้น/เมตร")
with col3:
    st.metric("น้ำหนักคอนกรีต", f"{self_weight:.0f} kg/m²")

# คำแนะนำเพิ่มเติม
st.divider()
with st.expander("📝 เกณฑ์ที่ใช้วิจารณ์ผล (สำหรับผู้ไม่มีพื้นฐาน)"):
    st.write("""
    1. **Average Prestress (P/A):** คือการวัดว่าเราเอาลวดไป "บีบ" คอนกรีตแรงแค่ไหน 
       - ถ้าบีบน้อยกว่า **8.5 kg/cm²**: คอนกรีตจะไม่มีแรงพอไปสู้กับน้ำหนัก ทำให้พื้นร้าว
       - ถ้าบีบมากกว่า **35.0 kg/cm²**: คอนกรีตจะรับแรงบีบไม่ไหวจนแตกละเอียด (Crushing)
    2. **Load Balancing:** โปรแกรมนี้พยายามดึงลวดให้ช่วยแบกน้ำหนักตัวพื้นเองไว้ 80% เพื่อให้พื้นไม่อ่อนตัว
    """)
