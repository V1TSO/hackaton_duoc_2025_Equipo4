# back/app/agents/rag_service.py
import logging
import os
import json # ¡Importante!
from pathlib import Path

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


def buscar_en_kb(terminos_clave: list[str]) -> tuple[str, list[str]]:
    """
    Busca en la /kb los archivos .json basados en los drivers.
    Construye el contexto (como un string JSON) y la lista de citas.
    """
    logger.info(f"Iniciando búsqueda RAG en /kb con los drivers: {terminos_clave}")
    
    contexto_json = []
    citas = set()

    if not terminos_clave:
        terminos_clave = ["default"]

    for termino in terminos_clave:
        termino_limpio = termino.lower().split('_')[0]
        kb_entry = load_kb_content(termino_limpio)
        
        if kb_entry:
            contexto_json.append(kb_entry)
            citas.add(kb_entry.get("cita", "sin_cita"))

    # 2. Asegurarnos de incluir siempre el "default"
    if "default" not in terminos_clave:
        kb_entry_default = load_kb_content("default")
        if kb_entry_default:
            contexto_json.append(kb_entry_default)
            citas.add(kb_entry_default.get("cita", "sin_cita"))

    if not contexto_json:
        logger.error("Contexto RAG está vacío. Ningún archivo .json coincidió.")
        return "[]", []

    contexto_rag_string = json.dumps(contexto_json, indent=2, ensure_ascii=False)

    logger.info(f"Contexto RAG (JSON) generado. Citas: {list(citas)}")
    return contexto_rag_string, list(citas)