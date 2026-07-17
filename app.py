import streamlit as st
import pandas as pd
import numpy as np
import joblib

# ตั้งค่าหน้าเว็บ
st.set_page_config(
    page_title="ระบบทำนายการอนุมัติสินเชื่อ",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #555;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
        font-size: 1.1rem;
        font-weight: bold;
        border-radius: 8px;
        padding: 0.5rem;
    }
    .stButton>button:hover {
        background-color: #155a8a;
    }
    .result-box {
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        font-size: 1.5rem;
        font-weight: bold;
        margin-top: 1rem;
    }
    .approved {
        background-color: #d4edda;
        color: #155724;
        border: 2px solid #c3e6cb;
    }
    .rejected {
        background-color: #f8d7da;
        color: #721c24;
        border: 2px solid #f5c6cb;
    }
</style>
""", unsafe_allow_html=True)

# โหลดโมเดล
@st.cache_resource
def load_model():
    return joblib.load('loan_model.pkl')

try:
    model = load_model()
except FileNotFoundError:
    st.error("❌ ไม่พบไฟล์ `loan_model.pkl` กรุณาอัปโหลดไฟล์โมเดลไว้ในโฟลเดอร์เดียวกัน")
    st.stop()

# ส่วนหัว
st.markdown('<div class="main-header">🏦 ระบบทำนายการอนุมัติสินเชื่อ</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">กรอกข้อมูลด้านล่างเพื่อประเมินโอกาสในการได้รับอนุมัติสินเชื่อ</div>', unsafe_allow_html=True)

st.divider()

# Sidebar
st.sidebar.header("📝 กรอกข้อมูลผู้กู้")

person_age = st.sidebar.number_input("อายุ (ปี)", min_value=18, max_value=100, value=25)
person_gender = st.sidebar.selectbox("เพศ", ["male", "female"])
person_education = st.sidebar.selectbox("ระดับการศึกษา", ["High School", "Associate", "Bachelor", "Master", "Doctorate"])
person_income = st.sidebar.number_input("รายได้ต่อปี (บาท)", min_value=0, value=50000, step=1000)
person_emp_exp = st.sidebar.number_input("ประสบการณ์ทำงาน (ปี)", min_value=0, max_value=50, value=2)
person_home_ownership = st.sidebar.selectbox("สถานะที่อยู่อาศัย", ["RENT", "OWN", "MORTGAGE", "OTHER"])
loan_amnt = st.sidebar.number_input("จำนวนเงินที่ขอกู้ (บาท)", min_value=1000, value=10000, step=1000)
loan_intent = st.sidebar.selectbox("วัตถุประสงค์การกู้", ["PERSONAL", "MEDICAL", "EDUCATION", "VENTURE", "HOMEIMPROVEMENT", "DEBTCONSOLIDATION"])
loan_int_rate = st.sidebar.number_input("อัตราดอกเบี้ย (%)", min_value=0.0, max_value=30.0, value=10.0, step=0.1)
loan_percent_income = st.sidebar.number_input("สัดส่วนเงินกู้ต่อรายได้ (0.0 - 1.0)", min_value=0.0, max_value=1.0, value=0.2, step=0.01)
cb_person_cred_hist_length = st.sidebar.number_input("ความยาวประวัติเครดิต (ปี)", min_value=0, max_value=50, value=3)
credit_score = st.sidebar.number_input("คะแนนเครดิต", min_value=300, max_value=850, value=650)
previous_loan_defaults_on_file = st.sidebar.selectbox("เคยผิดนัดชำระหนี้ในอดีตหรือไม่", ["No", "Yes"])

# แปลงค่า
gender_map = {"male": 1, "female": 0}
default_map = {"Yes": 1, "No": 0}

# ปุ่มทำนาย
st.markdown("<br>", unsafe_allow_html=True)
if st.button("🔍 ทำนายผลการอนุมัติ"):
    with st.spinner("กำลังประมวลผล..."):
        input_data = pd.DataFrame({
            'person_age': [person_age],
            'person_gender': [gender_map[person_gender]],
            'person_education': [person_education],
            'person_income': [person_income],
            'person_emp_exp': [person_emp_exp],
            'person_home_ownership': [person_home_ownership],
            'loan_amnt': [loan_amnt],
            'loan_intent': [loan_intent],
            'loan_int_rate': [loan_int_rate],
            'loan_percent_income': [loan_percent_income],
            'cb_person_cred_hist_length': [cb_person_cred_hist_length],
            'credit_score': [credit_score],
            'previous_loan_defaults_on_file': [default_map[previous_loan_defaults_on_file]]
        })
        
        prediction = model.predict(input_data)[0]
        probability = model.predict_proba(input_data)[0]
        
        st.divider()
        if prediction == 0:
            st.markdown(f"""
                <div class="result-box approved">
                    ✅ อนุมัติสินเชื่อ!<br>
                    <span style="font-size: 1rem; font-weight: normal;">
                        โอกาสอนุมัติ: {probability[0]*100:.1f}%
                    </span>
                </div>
            """, unsafe_allow_html=True)
            st.success("ยินดีด้วย! โปรไฟล์ของคุณมีแนวโน้มสูงที่จะได้รับการอนุมัติสินเชื่อ")
        else:
            st.markdown(f"""
                <div class="result-box rejected">
                    ❌ ไม่อนุมัติสินเชื่อ<br>
                    <span style="font-size: 1rem; font-weight: normal;">
                        โอกาสไม่อนุมัติ: {probability[1]*100:.1f}%
                    </span>
                </div>
            """, unsafe_allow_html=True)
            st.warning("ขออภัย โปรไฟล์ของคุณมีความเสี่ยงสูง อาจไม่ได้รับการอนุมัติในขณะนี้")

# Footer
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown(
    "<div style='text-align: center; color: #888; font-size: 0.9rem;'>"
    "© 2024 Loan Prediction System | Powered by Streamlit & Scikit-Learn"
    "</div>", 
    unsafe_allow_html=True
)