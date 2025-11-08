# back/app/agents/rag_service.py
import logging
import os
import json
from pathlib import Path
from app.utils.token_counter import count_tokens, truncate_to_budget
from app.core.config import settings

logger = logging.getLogger(__name__)

# La lógica para encontrar KB_PATH sigue igual
try:
    REPO_ROOT = Path(__file__).parent.parent.parent.parent
    KB_PATH = REPO_ROOT / "kb"
    if not KB_PATH.exists() or not KB_PATH.is_dir():
        logger.warning(f"La carpeta KB_PATH '{KB_PATH}' no existe.")
        KB_PATH = REPO_ROOT / "kb_mock_path" 
except Exception as e:
    logger.error(f"Error al calcular la ruta del repositorio: {e}")
    KB_PATH = Path("/tmp/kb")

logger.info(f"Ruta de la Base de Conocimiento (KB) configurada en: {KB_PATH}")

# Mapeo de nombres técnicos de features NHANES a nombres de archivos KB
FEATURE_TO_KB_MAP = {
    # Features de presión arterial
    'bpxsy1': 'default',  # Presión sistólica - usar default
    'bpxsy2': 'default',
    'bpxsy3': 'default',
    'bpxsy4': 'default',
    'bpxdi1': 'default',  # Presión diastólica
    'bpxdi2': 'default',
    'bpxdi3': 'default',
    'bpxdi4': 'default',
    'systolic_bp': 'default',
    'diastolic_bp': 'default',
    
    # Features de medidas corporales
    'bmxsad2': 'cintura',  # Sagittal Abdominal Diameter - relacionado con cintura
    'bmxwaist': 'cintura',
    'bmxbmi': 'imc',
    'bmxht': 'imc',  # Altura
    'bmxwt': 'imc',  # Peso
    'bmi': 'imc',
    'waist_height_ratio': 'cintura',
    'waist_cm': 'cintura',
    'circunferencia_cintura': 'cintura',
    'cintura_cm': 'cintura',
    'central_obesity': 'cintura',
    'high_waist_height_ratio': 'cintura',
    
    # Features de peso muestral (no relevantes para KB)
    'wtmec2yr': 'default',
    'wtint2yr': 'default',
    'wtmec4yr': 'default',
    'wtint4yr': 'default',
    
    # Features de estado/demografía
    'ridstatr': 'default',  # Estado de residencia
    'ridageyr': 'default',  # Edad
    'riagendr': 'default',  # Género
    
    # Features de sueño
    'sleep_hours': 'sueño',
    'poor_sleep': 'sueño',
    'slq': 'sueño',  # Sleep questionnaire
    
    # Features de tabaquismo
    'smq': 'tabaquismo',  # Smoking questionnaire
    'cigarettes_per_day': 'tabaquismo',
    'current_smoker': 'tabaquismo',
    'ever_smoker': 'tabaquismo',
    
    # Features de actividad física
    'paq': 'actividad_fisica',  # Physical activity questionnaire
    'total_active_days': 'actividad_fisica',
    'days_mvpa_week': 'actividad_fisica',
    'meets_activity_guidelines': 'actividad_fisica',
    'sedentary_flag': 'actividad_fisica',
    
    # Features de estilo de vida
    'lifestyle_risk_score': 'default',
    'high_risk_profile': 'default',
    
    # Features de interacción
    'bmi_age_interaction': 'imc',
    'waist_age_interaction': 'cintura',
    'age_squared': 'default',
    'age_poor_sleep': 'sueño',
}

def map_feature_to_kb(feature_name: str) -> str:
    """
    Mapea un nombre técnico de feature a un nombre de archivo KB.
    
    Args:
        feature_name: Nombre técnico de la feature (ej: 'BPXSY1', 'bmi', 'sleep_hours')
    
    Returns:
        Nombre del archivo KB correspondiente (sin extensión)
    """
    feature_lower = feature_name.lower()
    
    # Buscar coincidencia exacta
    if feature_lower in FEATURE_TO_KB_MAP:
        return FEATURE_TO_KB_MAP[feature_lower]
    
    # Buscar por prefijos comunes
    if feature_lower.startswith('bpx') or 'systolic' in feature_lower or 'diastolic' in feature_lower or 'bp' in feature_lower:
        return 'default'
    if feature_lower.startswith('bmx') or 'bmi' in feature_lower or 'weight' in feature_lower or 'height' in feature_lower:
        return 'imc'
    if 'waist' in feature_lower or 'cintura' in feature_lower or 'sad' in feature_lower:
        return 'cintura'
    if 'sleep' in feature_lower or 'sueño' in feature_lower or 'slq' in feature_lower:
        return 'sueño'
    if 'smoke' in feature_lower or 'cigarette' in feature_lower or 'smq' in feature_lower or 'tabaco' in feature_lower:
        return 'tabaquismo'
    if 'activity' in feature_lower or 'active' in feature_lower or 'paq' in feature_lower or 'mvpa' in feature_lower or 'sedentary' in feature_lower:
        return 'actividad_fisica'
    if feature_lower.startswith('wt') and ('mec' in feature_lower or 'int' in feature_lower):
        return 'default'  # Pesos muestrales - usar default
    
    # Por defecto
    return 'default'


def load_kb_content(termino_clave: str) -> dict | None:
    """
    Carga el contenido de un archivo .json de la KB.
    """
    # ¡Cambiamos la extensión!
    filename = f"{termino_clave}.json"
    filepath = KB_PATH / filename
    
    if not filepath.exists():
        logger.warning(f"No se encontró el archivo '{filename}' en la KB.")
        return None

    try:
        # ¡Leemos el archivo como JSON!
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Devolvemos el diccionario JSON completo
            return data
            
    except json.JSONDecodeError:
        logger.error(f"Error: El archivo '{filename}' no es un JSON válido.")
        return None
    except Exception as e:
        logger.error(f"Error al leer el archivo KB '{filepath}': {e}")
        return None


def buscar_en_kb(terminos_clave: list[str], max_tokens: int = None) -> tuple[str, list[str]]:
    """
    Busca en la /kb los archivos .json basados en los drivers.
    Construye el contexto (como un string JSON) y la lista de citas.
    
    Ahora con gestión de tokens:
    - Prioriza documentos de drivers específicos
    - Respeta el presupuesto de tokens
    - Trunca si es necesario
    
    Args:
        terminos_clave: Lista de términos clave (drivers) para buscar
        max_tokens: Máximo de tokens permitidos (por defecto usa TOKEN_BUDGET_RAG)
    
    Returns:
        Tupla de (contexto_json_string, lista_de_citas)
    """
    if max_tokens is None:
        max_tokens = settings.TOKEN_BUDGET_RAG
    
    logger.info(f"Iniciando búsqueda RAG (budget: {max_tokens} tokens) con drivers: {terminos_clave}")
    
    # Estructuras para priorización
    priority_docs = []  # Documentos de drivers específicos
    default_doc = None
    citas = set()

    if not terminos_clave:
        terminos_clave = ["default"]

    # 1. Cargar documentos de drivers (alta prioridad)
    for termino in terminos_clave:
        if termino.lower() == "default":
            continue
        
        # Mapear el nombre técnico de la feature a un nombre de archivo KB
        termino_limpio = map_feature_to_kb(termino)
        kb_entry = load_kb_content(termino_limpio)
        
        if kb_entry:
            doc_tokens = count_tokens(json.dumps(kb_entry, ensure_ascii=False))
            priority_docs.append({
                "doc": kb_entry,
                "tokens": doc_tokens,
                "term": termino_limpio
            })
            citas.add(kb_entry.get("cita", "sin_cita"))
            logger.info(f"Cargado documento '{termino_limpio}': {doc_tokens} tokens")

    # 2. Cargar documento default (baja prioridad)
    kb_entry_default = load_kb_content("default")
    if kb_entry_default:
        default_tokens = count_tokens(json.dumps(kb_entry_default, ensure_ascii=False))
        default_doc = {
            "doc": kb_entry_default,
            "tokens": default_tokens,
            "term": "default"
        }
        logger.info(f"Cargado documento 'default': {default_tokens} tokens")

    # 3. Construir contexto respetando el presupuesto de tokens
    contexto_json = []
    tokens_used = 0
    
    # Agregar documentos prioritarios primero
    for doc_info in priority_docs:
        if tokens_used + doc_info["tokens"] <= max_tokens:
            contexto_json.append(doc_info["doc"])
            tokens_used += doc_info["tokens"]
        else:
            logger.warning(f"Budget alcanzado, omitiendo documento '{doc_info['term']}'")
    
    # Intentar agregar default si hay espacio
    if default_doc and tokens_used + default_doc["tokens"] <= max_tokens:
        contexto_json.append(default_doc["doc"])
        citas.add(default_doc["doc"].get("cita", "sin_cita"))
        tokens_used += default_doc["tokens"]
    elif default_doc:
        logger.warning(f"No hay espacio para 'default' ({default_doc['tokens']} tokens)")

    # 4. Si no hay contenido, lanzar error
    if not contexto_json:
        if default_doc:
            # Truncar default para que quepa
            truncated_default = truncate_kb_entry(default_doc["doc"], max_tokens)
            contexto_json.append(truncated_default)
            citas.add(truncated_default.get("cita", "sin_cita"))
            tokens_used = count_tokens(json.dumps(truncated_default, ensure_ascii=False))
        else:
            logger.error("Contexto RAG está vacío. Ningún archivo .json coincidió.")
            raise Exception("No se encontró contenido en la base de conocimiento. Por favor, verifica que los archivos de la KB estén disponibles.")

    # 5. Generar string JSON final
    contexto_rag_string = json.dumps(contexto_json, indent=2, ensure_ascii=False)
    final_tokens = count_tokens(contexto_rag_string)

    logger.info(f"Contexto RAG generado: {len(contexto_json)} docs, {final_tokens} tokens (budget: {max_tokens})")
    logger.info(f"Citas incluidas: {list(citas)}")
    
    return contexto_rag_string, list(citas)


def truncate_kb_entry(kb_entry: dict, max_tokens: int) -> dict:
    """
    Trunca un documento KB para que quepa en el presupuesto de tokens.
    Mantiene la estructura JSON pero trunca el campo 'texto'.
    
    Args:
        kb_entry: Documento KB a truncar
        max_tokens: Máximo de tokens permitidos
    
    Returns:
        Documento KB truncado
    """
    # Calcular tokens del overhead (cita, termino_clave, estructura JSON)
    overhead = count_tokens(json.dumps({
        "cita": kb_entry.get("cita", ""),
        "termino_clave": kb_entry.get("termino_clave", "")
    }, ensure_ascii=False))
    
    # Tokens disponibles para el texto
    available_tokens = max_tokens - overhead - 50  # 50 tokens de margen
    
    if available_tokens < 100:
        logger.warning(f"Muy poco espacio para truncar ({available_tokens} tokens)")
        available_tokens = 100
    
    texto_original = kb_entry.get("texto", "")
    texto_truncado = truncate_to_budget(texto_original, available_tokens)
    
    return {
        "cita": kb_entry.get("cita", ""),
        "termino_clave": kb_entry.get("termino_clave", ""),
        "texto": texto_truncado
    }