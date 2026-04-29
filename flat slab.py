import streamlit as st
import math

st.title("🏗️ Post-Tensioned Flat Slab Calculator")
st.markdown("โปรแกรมคำนวณจำนวนเส้นลวด (Strands) และความหนาพื้นเบื้องต้น")

# --- Sidebar: Input ---
st.sidebar.header("📋 ข้อมูลการออกแบบ (PT)")
L = st.sidebar.number_input("ระยะช่วงเสาที่ยาวที่สุด (เมตร)", value=8.0, step=0.5)
width = st.sidebar.number_input("ความกว้างของแถบพื้นที่จะคำนวณ (เมตร)", value=1.0, help="ปกติคำนวณต่อความกว้าง 1 เมตร")
live_load = st.sidebar.number_input("น้ำหนักบรรทุกจร (kg/m²)", value=300)
f_ci = st.sidebar.number_input("กำลังอัดคอนกรีตขณะดึงลวด (kg/cm²)", value=240)

# --- ส่วนคำนวณ ---
# 1. ประมาณความหนาพื้น (PT slab มักจะบางกว่า RC)
# สูตรลัด: L / 40 ถึง L / 45
t_estimated = (L * 100) / 45 
t = st.number_input("ความหนาพื้น PT ที่เลือกใช้ (ซม.)", value=float(math.ceil(t_estimated)))

# 2. คำนวณน้ำหนัก
dead_load = (t/100) * 2400
total_load = dead_load + live_load

# 3. คำนวณแรงดึงลวดเบื้องต้น (Prestressing Force)
# ใช้หลักการ Balance Load (ชดเชยน้ำหนักบรรทุกประมาณ 60-80% ของ Dead Load)
w_bal = 0.75 * dead_load 
# สูตร Force (P) = (w_bal * L^2) / (8 * sag)
sag = (t/100) - 0.05 # ระยะโก่งของลวด (หักระยะหุ้มบน-ล่าง)
p_force = (w_bal * (L**2)) / (8 * sag)

# 4. จำนวนเส้นลวด (Strands)
# ลวด 1 เส้น (ขนาด 0.5 นิ้ว) รับแรงดึงปลอดภัยได้ประมาณ 14,000 - 15,000 kg
strand_capacity = 14500
num_strands = p_force / strand_capacity

# --- แสดงผล ---
st.header("📊 สรุปผลการออกแบบเบื้องต้น")
c1, c2, c3 = st.columns(3)
c1.metric("ความหนาพื้น", f"{t} ซม.")
c2.metric("น้ำหนักรวม", f"{total_load:.0f} kg/m²")
c3.metric("จำนวนลวดที่ใช้", f"{math.ceil(num_strands)} เส้น/เมตร")

st.write(f"**แรงดึงลวดที่ต้องการ (P):** {p_force:,.2f} kg ต่อความกว้าง 1 เมตร")

st.expander("📝 อธิบายเพิ่มเติมสำหรับมือใหม่").write("""
- **Prestressing Force (P):** คือแรงที่เราดึงลวดให้ตึงเพื่อให้มันไปบีบอัดคอนกรีต
- **Balance Load:** คือเทคนิคการทำให้ลวดรับน้ำหนักตัวมันเอง (Dead Load) ไว้ส่วนหนึ่ง ทำให้พื้นไม่แอ่น
- **Strands:** คือเส้นลวดเหล็กตีเกลียวที่อยู่ในท่อ (Duct) ก่อนจะเทคอนกรีต
""")
