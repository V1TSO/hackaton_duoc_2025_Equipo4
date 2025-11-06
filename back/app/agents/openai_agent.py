from openai import OpenAI
from app.core.config import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)

def generar_consejo_salud(riesgo: float) -> str:
    """
    Genera un consejo basado en el nivel de riesgo estimado.
    - No entrega diagnóstico médico.
    - Entrega recomendaciones generales de estilo de vida.
    """
    # Asegurar rango razonable
    try:
        r = float(riesgo)
    except (TypeError, ValueError):
        r = 0.5

    if r < 0:
        r = 0.0
    if r > 1:
        r = 1.0

    if r < 0.33:
        nivel = "bajo"
    elif r < 0.66:
        nivel = "moderado"
    else:
        nivel = "alto"

    prompt = f"""
    El modelo estima un riesgo {nivel} (valor: {r:.2f}) de presentar condiciones cardiometabólicas
    en base a hábitos y medidas generales de salud.

    1. Explica en lenguaje simple qué significa tener un riesgo {nivel} (sin alarmar).
    2. Entrega TRES recomendaciones concretas y realistas de estilo de vida (actividad física, alimentación, sueño, hábitos).
    3. Deja claro que esto NO es un diagnóstico médico y que debe consultar a un profesional de la salud,
       especialmente si presenta síntomas o si su riesgo es alto.

    Responde en tono amable, motivador y en no más de 6-7 líneas.
    """

    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Eres un coach de bienestar preventivo, empático y responsable. "
                        "No eres médico, no entregas diagnósticos ni tratamientos. "
                        "Te enfocas en hábitos saludables basados en evidencia general."
                        "Si te encuentras en situaciones donde el usuario atenta contra si mismo o alguien más, da telefonos de ayuda"
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
        )
        return completion.choices[0].message.content.strip()
    except Exception:
        # Fallback seguro si la API de OpenAI falla
        if nivel == "alto":
            extra = " Te recomiendo consultar con un profesional de la salud pronto."
        else:
            extra = ""
        return (
            f"Tu resultado sugiere un riesgo {nivel}. "
            f"Te puede ayudar mantener una alimentación equilibrada, moverte al menos 30 minutos al día, "
            f"dormir bien y evitar el tabaco.{extra} Esto no es un diagnóstico médico."
        )
