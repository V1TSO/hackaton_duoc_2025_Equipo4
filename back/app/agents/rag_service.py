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
            
        termino_limpio = termino.lower().split('_')[0]
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

    # 4. Si no hay contenido, usar mínimo default
    if not contexto_json:
        if default_doc:
            # Truncar default para que quepa
            truncated_default = truncate_kb_entry(default_doc["doc"], max_tokens)
            contexto_json.append(truncated_default)
            citas.add(truncated_default.get("cita", "sin_cita"))
            tokens_used = count_tokens(json.dumps(truncated_default, ensure_ascii=False))
        else:
            logger.error("Contexto RAG está vacío. Ningún archivo .json coincidió.")
            return "[]", []

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