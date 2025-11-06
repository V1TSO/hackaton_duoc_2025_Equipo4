"""
NHANES Data Converter - Script para descargar y convertir datos NHANES
=======================================================================

Este script ayuda a descargar y convertir datos de NHANES desde formato .XPT a CSV.

IMPORTANTE: Los datos de NHANES se distribuyen en formato SAS Transport File (.XPT)
y NO vienen directamente en CSV. Este script automatiza la conversión.

Referencias:
- NHANES Website: https://wwwn.cdc.gov/nchs/nhanes/
- NHANES Data Access: https://wwwn.cdc.gov/nchs/nhanes/Default.aspx
"""

import pandas as pd
from pathlib import Path
import urllib.request
import warnings

warnings.filterwarnings('ignore')

# URLs base de NHANES
NHANES_BASE_URL = "https://wwwn.cdc.gov/nchs/nhanes/"

# Ciclos disponibles en NHANES
NHANES_CYCLES = {
    '2007-2008': '2007-2008',
    '2009-2010': '2009-2010',
    '2011-2012': '2011-2012',
    '2013-2014': '2013-2014',
    '2015-2016': '2015-2016',
    '2017-2018': '2017-2018'
}

# Módulos disponibles (pueden variar por ciclo)
MODULES = {
    'DEMO': 'Demographics',
    'EXAM': 'Examination',
    'LAB': 'Laboratory',
    'QUEST': 'Questionnaire',
    'DIET': 'Dietary'
}


def download_nhanes_file(cycle, module, output_dir='./data'):
    """
    Descarga un archivo .XPT de NHANES y lo convierte a CSV.
    
    Args:
        cycle: Ciclo de NHANES (ej: '2007-2008')
        module: Módulo a descargar (ej: 'DEMO', 'EXAM', 'LAB')
        output_dir: Directorio donde guardar los archivos
    
    Returns:
        str: Ruta del archivo CSV creado
    """
    # Crear directorio si no existe
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Construir nombre del archivo
    cycle_underscore = cycle.replace('-', '_')
    filename_xpt = f"{module}_{cycle_underscore}.XPT"
    filename_csv = f"{module}_{cycle_underscore}.csv"
    
    filepath_xpt = Path(output_dir) / filename_xpt
    filepath_csv = Path(output_dir) / filename_csv
    
    # Si ya existe el CSV, no descargar de nuevo
    if filepath_csv.exists():
        print(f"✓ {filename_csv} ya existe, omitiendo descarga")
        return str(filepath_csv)
    
    # URL del archivo (estructura típica de NHANES)
    # NOTA: La URL exacta depende de cómo esté organizado el sitio
    # Esta es una estructura aproximada
    url = f"{NHANES_BASE_URL}{cycle}/{filename_xpt}"
    
    try:
        print(f"📥 Descargando {filename_xpt}...")
        print(f"   URL: {url}")
        
        # Descargar archivo
        urllib.request.urlretrieve(url, filepath_xpt)
        print(f"   ✓ Descargado: {filepath_xpt}")
        
    except Exception as e:
        print(f"   ⚠️ ERROR descargando: {e}")
        print(f"   💡 NOTA: Es posible que necesites descargar manualmente desde:")
        print(f"      https://wwwn.cdc.gov/nchs/nhanes/Default.aspx")
        print(f"      Busca el ciclo {cycle} y el módulo {MODULES.get(module, module)}")
        return None
    
    # Convertir .XPT a CSV
    try:
        print(f"🔄 Convirtiendo {filename_xpt} a CSV...")
        df = pd.read_sas(filepath_xpt, encoding='utf-8')
        df.to_csv(filepath_csv, index=False)
        print(f"   ✓ Convertido: {filepath_csv}")
        print(f"   📊 Registros: {len(df):,}, Columnas: {len(df.columns)}")
        
        # Eliminar archivo .XPT si se desea (opcional)
        # os.remove(filepath_xpt)
        
        return str(filepath_csv)
        
    except Exception as e:
        print(f"   ⚠️ ERROR convirtiendo: {e}")
        return None


def convert_xpt_to_csv(xpt_file, output_dir=None):
    """
    Convierte un archivo .XPT a CSV.
    
    Args:
        xpt_file: Ruta al archivo .XPT
        output_dir: Directorio de salida (opcional, usa el mismo del .XPT)
    
    Returns:
        str: Ruta del archivo CSV creado
    """
    xpt_path = Path(xpt_file)
    
    if not xpt_path.exists():
        print(f"⚠️ ERROR: Archivo no encontrado: {xpt_file}")
        return None
    
    if output_dir is None:
        output_dir = xpt_path.parent
    else:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
    
    csv_file = output_dir / f"{xpt_path.stem}.csv"
    
    try:
        print(f"🔄 Convirtiendo {xpt_path.name} a CSV...")
        df = pd.read_sas(xpt_path, encoding='utf-8')
        df.to_csv(csv_file, index=False)
        print(f"   ✓ Convertido: {csv_file}")
        print(f"   📊 Registros: {len(df):,}, Columnas: {len(df.columns)}")
        return str(csv_file)
        
    except Exception as e:
        print(f"   ⚠️ ERROR: {e}")
        print(f"   Asegúrate de que pandas tenga soporte para archivos SAS")
        return None


def download_full_cycle(cycle, modules=['DEMO', 'EXAM', 'LAB', 'QUEST'], output_dir='./data'):
    """
    Descarga todos los módulos de un ciclo de NHANES.
    
    Args:
        cycle: Ciclo de NHANES (ej: '2007-2008')
        modules: Lista de módulos a descargar
        output_dir: Directorio donde guardar los archivos
    """
    print(f"\n{'='*70}")
    print(f"📦 Descargando ciclo {cycle}")
    print(f"{'='*70}")
    
    results = {}
    
    for module in modules:
        print(f"\n📁 Módulo: {module} ({MODULES.get(module, module)})")
        csv_file = download_nhanes_file(cycle, module, output_dir)
        results[module] = csv_file
    
    print(f"\n{'='*70}")
    print(f"✅ Resumen del ciclo {cycle}:")
    print(f"{'='*70}")
    
    for module, csv_file in results.items():
        if csv_file:
            print(f"  ✓ {module}: {Path(csv_file).name}")
        else:
            print(f"  ✗ {module}: No descargado")
    
    return results


if __name__ == "__main__":
    """
    Ejemplo de uso:
    
    1. Descargar datos de un ciclo completo:
       python nhanes_data_converter.py
    
    2. O usar en Python:
       from nhanes_data_converter import download_full_cycle
       download_full_cycle('2007-2008')
    """
    
    print("="*70)
    print("NHANES Data Converter")
    print("="*70)
    print("\nEste script ayuda a descargar y convertir datos de NHANES.")
    print("\nIMPORTANTE:")
    print("1. Los datos vienen en formato .XPT (SAS Transport File)")
    print("2. Este script los convierte a CSV")
    print("3. Puede que necesites descargar manualmente desde:")
    print("   https://wwwn.cdc.gov/nchs/nhanes/Default.aspx")
    print("\n" + "="*70)
    
    # Ejemplo: Descargar ciclo 2007-2008
    cycle = '2007-2008'
    print(f"\n📥 Ejemplo: Descargando ciclo {cycle}")
    print("   (Puedes modificar el ciclo en el código)")
    
    # Descomentar para ejecutar:
    # download_full_cycle(cycle)
    
    print("\n" + "="*70)
    print("💡 INSTRUCCIONES:")
    print("="*70)
    print("""
1. OPCIÓN A - Descarga Manual (Recomendado):
   a) Ve a: https://wwwn.cdc.gov/nchs/nhanes/Default.aspx
   b) Selecciona el ciclo (ej: 2007-2008)
   c) Descarga los archivos .XPT que necesites:
      - Demographics (DEMO)
      - Examination (EXAM)
      - Laboratory (LAB)
      - Questionnaire (QUEST)
   d) Coloca los archivos .XPT en la carpeta ./data/
   e) Ejecuta este script para convertirlos a CSV

2. OPCIÓN B - Conversión de archivos ya descargados:
   from nhanes_data_converter import convert_xpt_to_csv
   convert_xpt_to_csv('./data/DEMO_2007_2008.XPT')

3. OPCIÓN C - Descarga automática (puede fallar si cambian URLs):
   from nhanes_data_converter import download_full_cycle
   download_full_cycle('2007-2008')
""")
    
    print("\n" + "="*70)

