import streamlit as st
import pandas as pd
import joblib
import numpy as np

# Set page config
st.set_page_config(
    page_title="Student Dropout Predictor",
    layout="centered",
    page_icon="🎓"
)

# Load model and feature names
@st.cache_resource
def load_model():
    model = joblib.load('model.joblib')
    feature_names = joblib.load('feature_names.joblib')
    return model, feature_names

model, feature_names = load_model()

# Header with logo
col1, col2 = st.columns([1, 3])

with col1:
    st.image("Logo_JayaJaya_Institut.png", width=180)

with col2:
    st.markdown(
        """
        <div style="display: flex; flex-direction: column; justify-content: center; height: 150px;">
            <h1 style="margin: 0; text-align: center;">Welcome to Jaya Jaya Institute</h1>
            <h3 style="margin: 5px 0 0 0; text-align: center;">Risk Prediction for Students</h3>
            <p style="margin: 5px 0 0 0; text-align: center;"><em>Early Warning System untuk Memantau Perkembangan Mahasiswa</em></p>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("---")

# Form input
with st.form("prediction_form"):
    st.markdown("### 📝 Masukkan Data Mahasiswa")

    col1, col2 = st.columns(2)

    with col1:
        age = st.number_input("Usia", min_value=16, max_value=70, value=20)
        gender = st.selectbox("Jenis Kelamin", ["Laki-laki", "Perempuan"])
        marital_status = st.selectbox("Status Pernikahan", ["Belum Menikah", "Menikah"])

    with col2:
        tuition_fees_up_to_date = st.selectbox("Biaya Kuliah Tepat Waktu?", ["Ya", "Tidak"])
        scholarship_holder = st.selectbox("Penerima Beasiswa?", ["Ya", "Tidak"])
        debtor = st.selectbox("Memiliki Hutang?", ["Ya", "Tidak"])

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        enrolled_1st = st.number_input("Jumlah Mata Kuliah Diambil (Semester 1)", min_value=0, max_value=20, value=6)
        approved_1st = st.number_input("Jumlah Mata Kuliah Lulus (Semester 1)", min_value=0, max_value=20, value=5)

    with col2:
        grade_1st = st.number_input("Rata-rata Nilai Semester 1", min_value=0.0, max_value=20.0, value=12.0, step=0.1)

    # Tombol submit
    submitted = st.form_submit_button("🔍 Prediksi Risiko Dropout")

if submitted:
    # Konversi tipe data
    age = int(age)
    enrolled_1st = int(enrolled_1st)
    approved_1st = int(approved_1st)
    grade_1st = float(grade_1st)

    # Encode input
    gender_encoded = 1 if gender == "Laki-laki" else 0
    marital_encoded = 1 if marital_status == "Menikah" else 0
    tuition_encoded = 1 if tuition_fees_up_to_date == "Ya" else 0
    scholarship_encoded = 1 if scholarship_holder == "Ya" else 0
    debtor_encoded = 1 if debtor == "Ya" else 0

    # Hitung approval rate
    approval_rate_1st = approved_1st / (enrolled_1st + 1e-5)

    # Buat DataFrame input
    input_data = pd.DataFrame([{
        'Age_at_enrollment': age,
        'Gender': gender_encoded,
        'Marital_status': marital_encoded,
        'Course': 9085,
        'Daytime_evening_attendance': 1,
        'Previous_qualification': 1,
        'Admission_grade': 120.0,
        'Tuition_fees_up_to_date': tuition_encoded,
        'Scholarship_holder': scholarship_encoded,
        'Debtor': debtor_encoded,
        'Curricular_units_1st_sem_enrolled': enrolled_1st,
        'Curricular_units_1st_sem_approved': approved_1st,
        'Curricular_units_1st_sem_grade': grade_1st,
        'approval_rate_1st': approval_rate_1st,
        
        # Fitur turunan
        'low_grade_1st': int(grade_1st <= 11.0),
        'inactive_1st': 0,
        'grade_change': -5.0,
        'sharp_decline': 0,
        'total_approved': approved_1st,
        'total_enrolled': enrolled_1st,
        'academic_efficiency': approved_1st / (enrolled_1st + 1e-5),
        'financial_risk': int((debtor_encoded == 1) or (tuition_encoded == 0)),
        'high_financial_risk': int((scholarship_encoded == 0) and (debtor_encoded == 1)),
        'low_grade_financial_risk': int((grade_1st <= 11.0) and ((debtor_encoded == 1) or (tuition_encoded == 0))),
        'no_scholarship_low_grade': int((scholarship_encoded == 0) and (grade_1st <= 11.0)),
        
        # Fitur lain (default)
        'Curricular_units_1st_sem_credited': 0,
        'Curricular_units_1st_sem_evaluations': approved_1st,
        'Curricular_units_1st_sem_without_evaluations': 0,
        'Curricular_units_2nd_sem_credited': 0,
        'Curricular_units_2nd_sem_enrolled': 0,
        'Curricular_units_2nd_sem_evaluations': 0,
        'Curricular_units_2nd_sem_approved': 0,
        'Curricular_units_2nd_sem_grade': 0.0,
        'Curricular_units_2nd_sem_without_evaluations': 0,
        'Unemployment_rate': 13.9,
        'Inflation_rate': -0.3,
        'GDP': 0.79
    }])

    # Pastikan urutan kolom sesuai model
    input_final = input_data.reindex(columns=feature_names, fill_value=0)

    # Prediksi probabilitas
    y_proba = model.predict_proba(input_final)[0][1]

    # Kategorisasi hasil risiko
    if y_proba <= 0.37:
        prediction = "Tidak Berisiko Dropout"
        color = "#006400"
        advice = "💡 Mahasiswa ini berada dalam jalur aman. Tetap pantau perkembangannya secara berkala."
        icon = "✅"
    elif y_proba >= 0.60:
        prediction = "Berisiko Tinggi Dropout"
        color = "#B22222"
        advice = "💡 Mahasiswa ini berisiko tinggi dropout. Rekomendasi: Segera lakukan intervensi intensif melalui konseling akademik, kegiatan tutor, penyesuaian beban, atau memberikan bantuan finansial."
        icon = "‼️"
    else:
        prediction = "Mulai Berisiko Dropout"
        color = "#DE9B0B"
        advice = "💡 Mahasiswa ini mulai berisiko dropout. Rekomendasi: Lakukan pengecekan akademik dan finansial. Beri dukungan motivasi belajar atau opsi cicilan pembayaran."
        icon = "⚠️"

    # Tampilkan hasil
    st.divider()
    st.subheader("📊 Hasil Prediksi")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            f"""
            <div style="font-size: 24px; font-weight: bold; color: {color};">
                {icon} {prediction}
            </div>
            """,
            unsafe_allow_html=True
        )
    with col2:
        st.metric("Probabilitas Dropout", f"{y_proba:.2%}")

    # Tampilkan saran
    if y_proba <= 0.37:
        st.success(advice)
    elif y_proba >= 0.60:
        st.error(advice)
    else:
        st.warning(advice)

    