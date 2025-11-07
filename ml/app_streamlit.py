import streamlit as st
import requests
import pandas as pd
import altair as alt
from pdf_generator import generate_wellness_pdf
from datetime import datetime

# Configuración de página
st.set_page_config(
    page_title="Coach de Bienestar Preventivo",
    page_icon="🏥",
    layout="wide"
)

API_URL = "http://localhost:8000"

st.title("🏥 Coach de Bienestar Preventivo")
st.markdown(
    """
    Este sistema estima tu riesgo cardiometabólico y genera un plan personalizado.

    **⚠️ DISCLAIMER:** Este NO es un diagnóstico médico. Consulta con un profesional de salud.
    """
)

with st.sidebar:
    st.header("📋 Tu Perfil")

    st.subheader("Demográfico")
    age = st.number_input("Edad", min_value=18, max_value=85, value=45)
    sex = st.selectbox("Sexo", ["M", "F"], format_func=lambda x: "Masculino" if x == "M" else "Femenino")

    st.subheader("Antropometría")
    height_cm = st.number_input("Altura (cm)", min_value=120, max_value=220, value=170)
    weight_kg = st.number_input("Peso (kg)", min_value=30, max_value=220, value=75)
    waist_cm = st.number_input("Cintura (cm)", min_value=40, max_value=170, value=90)

    bmi = weight_kg / ((height_cm / 100) ** 2)
    st.info(f"IMC: {bmi:.1f}")

    st.subheader("Estilo de Vida")
    sleep_hours = st.slider("Horas de sueño/día", 3, 12, 7)
    smokes_cig_day = st.number_input("Cigarrillos/día", min_value=0, max_value=60, value=0)
    days_mvpa_week = st.slider("Días de ejercicio/semana", 0, 7, 3)
    fruit_veg_portions_day = st.slider("Porciones frutas/verduras/día", 0, 12, 5)

    evaluate_button = st.button("🔍 Evaluar Riesgo", type="primary")


def render_driver_table(drivers: pd.DataFrame):
    display_df = drivers[["description", "value", "shap_value", "impact"]].copy()
    display_df.columns = ["Factor", "Valor", "Impacto SHAP", "Efecto"]
    display_df["Valor"] = display_df["Valor"].round(3)
    display_df["Impacto SHAP"] = display_df["Impacto SHAP"].round(4)
    st.dataframe(display_df, use_container_width=True)


def render_driver_chart(drivers: pd.DataFrame):
    chart_df = drivers.copy()
    chart_df["Impacto"] = chart_df["shap_value"].apply(lambda v: "Mayor riesgo" if v > 0 else "Menor riesgo")
    chart = (
        alt.Chart(chart_df)
        .mark_bar()
        .encode(
            x=alt.X("shap_value", title="Impacto SHAP"),
            y=alt.Y("description", sort="-x", title="Factor"),
            color=alt.Color(
                "Impacto",
                scale=alt.Scale(
                    domain=["Mayor riesgo", "Menor riesgo"],
                    range=["#d62728", "#2ca02c"]
                )
            ),
            tooltip=["description", "value", "shap_value", "impact"]
        )
    )
    st.altair_chart(chart, use_container_width=True)


def render_driver_caption(drivers: pd.DataFrame):
    bullets = []
    for _, row in drivers.iterrows():
        direction = "⬆️ aumenta" if row["shap_value"] > 0 else "⬇️ reduce"
        bullets.append(f"{row['description']} ({direction} el riesgo)")
    if bullets:
        st.caption("; ".join(bullets))


if evaluate_button:
    payload = {
        "age": age,
        "sex": sex,
        "height_cm": height_cm,
        "weight_kg": weight_kg,
        "waist_cm": waist_cm,
        "sleep_hours": sleep_hours,
        "smokes_cig_day": smokes_cig_day,
        "days_mvpa_week": days_mvpa_week,
        "fruit_veg_portions_day": fruit_veg_portions_day
    }

    with st.spinner("Analizando tu perfil..."):
        try:
            response = requests.post(f"{API_URL}/predict", json=payload)
            response.raise_for_status()
            result = response.json()
        except Exception as exc:  # noqa: BLE001
            st.error(f"Error conectando con la API: {exc}")
            st.info("Asegúrate de que la API esté corriendo en http://localhost:8000")
        else:
            col1, col2, col3 = st.columns(3)

            with col1:
                risk_score = result["score"]
                st.metric("Puntaje de Riesgo", f"{risk_score:.1%}")

            with col2:
                st.metric("Nivel de Riesgo", result["risk_level"])

            with col3:
                indicator = "🟢"
                if risk_score >= 0.6:
                    indicator = "🔴"
                elif risk_score >= 0.3:
                    indicator = "🟡"
                st.metric("Indicador", indicator)

            st.info(f"📌 {result['recommendation']}")

            st.subheader("🎯 Factores que impulsan tu riesgo")
            drivers_df = pd.DataFrame(result.get("drivers", []))
            if not drivers_df.empty:
                render_driver_table(drivers_df)
                render_driver_chart(drivers_df)
                render_driver_caption(drivers_df)
            else:
                st.info("No se identificaron factores clave para este caso.")

            if st.button("📝 Generar Plan Personalizado"):
                with st.spinner("Creando tu plan..."):
                    coach_request = {
                        "user_profile": payload,
                        "risk_score": risk_score,
                        "top_drivers": [driver['feature'] for driver in result.get('drivers', [])[:3]]
                    }
                    coach_response = requests.post(f"{API_URL}/coach", json=coach_request)
                    if coach_response.status_code == 200:
                        plan_data = coach_response.json()
                        st.subheader("📋 Tu Plan de Bienestar Personalizado")
                        st.markdown(plan_data['plan'])
                        st.caption(f"📚 Fuentes: {', '.join(plan_data['sources'])}")
                        
                        # Generar y ofrecer descarga de PDF
                        try:
                            pdf_buffer = generate_wellness_pdf(
                                user_profile=payload,
                                risk_score=risk_score,
                                risk_level=result['risk_level'],
                                drivers=result.get('drivers', []),
                                plan_text=plan_data['plan'],
                                sources=plan_data['sources']
                            )
                            
                            st.download_button(
                                label="⬇️ Descargar Plan en PDF",
                                data=pdf_buffer.getvalue(),
                                file_name=f"plan_bienestar_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                                mime="application/pdf",
                                type="primary"
                            )
                        except Exception as pdf_error:
                            st.warning(f"No se pudo generar el PDF: {pdf_error}")
                            st.info("Puedes copiar el plan desde arriba")
                    else:
                        st.error(f"Error generando plan: {coach_response.status_code}")

st.markdown("---")
st.caption(
    """
    Desarrollado para Hackathon IA Duoc UC 2025 |
    Basado en datos NHANES |
    ⚠️ No sustituye atención médica profesional
    """
)
