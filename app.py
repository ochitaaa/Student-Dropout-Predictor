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
    imputer = joblib.load('imputer.joblib')
    feature_names = joblib.load('feature_names.joblib')
    return model, imputer, feature_names

model, imputer, feature_names = load_model()

# Feature engineering function
def feature_engineering(X):
    X = X.copy()
    X['approval_rate_1st'] = (
        X['Curricular_units_1st_sem_approved'] /
        (X['Curricular_units_1st_sem_enrolled'] + 1e-5)
    )
    X['low_grade_1st'] = (X['Curricular_units_1st_sem_grade'] < 10).astype(int)
    X['inactive_1st'] = (X['Curricular_units_1st_sem_without_evaluations'] > 0).astype(int)
    X['financial_risk'] = ((X['Debtor'] == 1) | (X['Tuition_fees_up_to_date'] == 0)).astype(int)
    X['low_grade_financial_risk'] = ((X['low_grade_1st'] == 1) & (X['financial_risk'] == 1)).astype(int)
    return X

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
        tuition = st.selectbox("Biaya Kuliah Tepat Waktu?", ["Ya", "Tidak"])
        scholarship = st.selectbox("Penerima Beasiswa?", ["Ya", "Tidak"])
        debtor = st.selectbox("Memiliki Tunggakan?", ["Ya", "Tidak"])

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        enrolled_1st = st.number_input("Jumlah Mata Kuliah Diambil (Semester 1)", 0, 20, 6)
        approved_1st = st.number_input("Jumlah Mata Kuliah Lulus (Semester 1)", 0, 20, 5)

    with col2:
        grade_1st = st.number_input("Rata-rata Nilai Semester 1", 0.0, 20.0, 12.0, step=0.1)
        without_eval = st.number_input("Mata Kuliah Tanpa Evaluasi", 0, 20, 0)

    submitted = st.form_submit_button("🔍 Prediksi Risiko Dropout")

if submitted:
    input_df = pd.DataFrame([{
        "Age_at_enrollment": age,
        "Gender": 1 if gender == "Laki-laki" else 0,
        "Marital_status": 1 if marital_status == "Menikah" else 0,
        "Debtor": 1 if debtor == "Ya" else 0,
        "Tuition_fees_up_to_date": 1 if tuition == "Ya" else 0,
        "Scholarship_holder": 1 if scholarship == "Ya" else 0,
        "Curricular_units_1st_sem_enrolled": enrolled_1st,
        "Curricular_units_1st_sem_approved": approved_1st,
        "Curricular_units_1st_sem_grade": grade_1st,
        "Curricular_units_1st_sem_without_evaluations": without_eval
    }])

    # preprocessing
    X_fe = feature_engineering(input_df)

    dtype_dict = {
        'Age_at_enrollment': 'int64',
        'Gender': 'int64',
        'Marital_status': 'int64',
        'Debtor': 'int64',
        'Tuition_fees_up_to_date': 'int64',
        'Scholarship_holder': 'int64',
        'Curricular_units_1st_sem_enrolled': 'int64',
        'Curricular_units_1st_sem_approved': 'int64',
        'Curricular_units_1st_sem_grade': 'float64',
        'Curricular_units_1st_sem_without_evaluations': 'int64',
        'approval_rate_1st': 'float64',
        'low_grade_1st': 'int64',
        'inactive_1st': 'int64',
        'financial_risk': 'int64',
        'low_grade_financial_risk': 'int64'
    }

    for col, dtype in dtype_dict.items():
        if col in X_fe.columns:
            X_fe[col] = X_fe[col].astype(dtype)

    # Urutkan kolom sesuai training
    X_fe = X_fe[feature_names]
    
    # Imputasi
    X_imputed = imputer.transform(X_fe)

    # prediksi
    y_proba = model.predict_proba(X_imputed)[0, 1]

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

    