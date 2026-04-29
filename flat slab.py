import streamlit as st
import math

# ตั้งค่าหน้าจอ
st.set_page_config(page_title="PT Slab Designer", layout="wide")

st.title("🏗️ Post-Tensioned Flat Slab Design Tool")
st.subheader("เครื่องมือคำนวณพื้นอัดแรงเบื้องต้น สำหรับอาคาร 4 ชั้น")

# --- ส่วนรับข้อมูล (Input) ---
with st.sidebar:
    st.header("📋 พารามิเตอร์การออกแบบ")
    
    # มิติของพื้น
    span_l = st.number_input("ระยะช่วงเสาด้านยาว (L) - เมตร", value=8.0, step=0.5)
    span_s = st.number_input("ระยะช่วงเสาด้านสั้น (S) - เมตร", value=7.0, step=0.5)
    
    # น้ำหนักบรรทุก
    live_load = st.number_input("น้ำหนักบรรทุกจร (kg/m²)", value=300, help="สำนักงาน=300, ที่พักอาศัย=200")
    sd_load = st.number_input("น้ำหนักวัสดุปูผิวและผนัง (kg/m²)", value=150)
    
    # วัสดุ
    fc_prime = st.number_input("กำลังอัดคอนกรีต f'c (kg/cm²)", value=320)
    strand_type = st.selectbox("ชนิดเส้นลวด", ["0.5 inch (Grade 270)"])

# --- ขั้นตอนการคำนวณ ---

# 1. ประมาณความหนาพื้น (Thickness - h)
# สำหรับ PT Slab มักใช้ Span/45 (ถ้า RC มักใช้ Span/32)
h_min = (span_l * 100) / 45
h_selected = st.slider("เลือกความหนาพื้นที่จะใช้ (ซม.)", 15, 30, int(math.ceil(h_min)))

# 2. คำนวณน้ำหนัก (Load Calculation)
self_weight = (h_selected / 100) * 2400 # คอนกรีตหนัก 2400 kg/m³
total_dead_load = self_weight + sd_load
total_load = total_dead_load + live_load

# 3. คำนวณหาจำนวนลวด (Tendons Selection)
# เราจะพยายามยก (Balance) น้ำหนักตัวเองของพื้น 80%
w_balance = 0.80 * self_weight

# ระยะดัดลวด (Sag) - สมมติระยะหุ้มคอนกรีต 2.5 ซม.
# ระยะจากจุดศูนย์กลางลวดถึงขอบคอนกรีต
cover = 2.5
d_eff = h_selected - (cover * 2) # ระยะที่ลวดสามารถ "แอ่น" ได้
sag = (d_eff / 100) 

# แรงดึงที่ต้องการ (Effective Prestress Force - P_e)
# สูตร: P = (w_bal * L^2) / (8 * sag)
p_effective = (w_balance * (span_l**2)) / (8 * sag)

# ความสามารถในการรับแรงของลวด 1 เส้น (0.5") ประมาณ 14,000 - 14,800 kg
strand_cap = 14800
num_strands = p_effective / strand_cap

# --- การแสดงผล (Output) ---
col1, col2 = st.columns(2)

with col1:
    st.write("### 📐 สรุปขนาดและน้ำหนัก")
    st.metric("ความหนาพื้น", f"{h_selected} ซม.")
    st.metric("น้ำหนักพื้นรวม (Total Load)", f"{total_load:.2f} kg/m²")
    st.write(f"- น้ำหนักพื้นเอง: {self_weight:.0f} kg/m²")
    st.write(f"- น้ำหนักบรรทุกอื่น: {sd_load + live_load:.0f} kg/m²")

with col2:
    st.write("### 🧶 ผลการคำนวณลวดอัดแรง (PT)")
    st.metric("จำนวนลวดที่แนะนำ", f"{math.ceil(num_strands)} เส้น/เมตร")
    st.write(f"แรงดึงที่ต้องการทั้งหมด: **{p_effective:,.2f} kg/m**")
    st.write(f"แรงต้านทานลวดต่อเส้น: {strand_cap} kg")

st.divider()
st.info("💡 **วิศวกรแนะนำ:** ระบบ PT สำหรับอาคาร 4 ชั้น ช่วยลดปริมาณคอนกรีตได้ถึง 20-30% เมื่อเทียบกับพื้นปกติ และช่วยให้งานระบบไฟฟ้า/ประปา เดินท่อได้ง่ายเพราะไม่มีคานขวาง")
