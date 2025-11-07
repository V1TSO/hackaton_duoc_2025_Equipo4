#!/usr/bin/env python
"""
Script para preparar dataset consolidado NHANES desde archivos CSV.

Carga datos de múltiples ciclos, aplica preprocesamiento básico y
guarda un archivo consolidado listo para entrenamiento.

Uso:
    python prepare_dataset.py [--output nhanes_processed.csv]
"""
import pandas as pd
import numpy as np
from pathlib import Path
import argparse
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_cycle_data(cycle: str, data_path: Path) -> pd.DataFrame:
    """
    Carga datos de un ciclo NHANES específico.
    
    Args:
        cycle: String del ciclo (ej: '2015-2016')
        data_path: Directorio con archivos CSV
    
    Returns:
        DataFrame consolidado del ciclo
    """
    logger.info(f"Cargando ciclo {cycle}...")
    
    # Convertir guiones a guiones bajos para nombres de archivo
    cycle_filename = cycle.replace('-', '_')
    
    # Archivos base que necesitamos
    base_files = {
        'demo': f'DEMO_{cycle_filename}.csv',
        'exam': f'EXAM_{cycle_filename}.csv',
        'quest': f'QUEST_{cycle_filename}.csv',
        'lab': f'LAB_{cycle_filename}.csv'
    }
    
    # Verificar qué archivos existen
    available = {}
    for key, filename in base_files.items():
        filepath = data_path / filename
        if filepath.exists():
            available[key] = filepath
        else:
            logger.warning(f"   Archivo no encontrado: {filename}")
    
    if 'demo' not in available:
        raise FileNotFoundError(f"Archivo DEMO_{cycle}.csv es obligatorio")
    
    # Cargar DEMO (base)
    df = pd.read_csv(available['demo'])
    df['cycle'] = cycle
    logger.info(f"   DEMO: {len(df):,} registros, {len(df.columns)} columnas")
    
    # Merge con otros archivos disponibles
    for key in ['exam', 'quest']:
        if key in available:
            temp = pd.read_csv(available[key])
            if 'SEQN' in temp.columns:
                df = df.merge(temp, on='SEQN', how='left', suffixes=('', '_dup'))
                # Eliminar columnas duplicadas
                dup_cols = [c for c in df.columns if c.endswith('_dup')]
                if dup_cols:
                    df = df.drop(columns=dup_cols)
                logger.info(f"   {key.upper()}: merged {len(temp.columns)} columnas")
    
    # Lab (renombrar con prefijo LAB_)
    if 'lab' in available:
        lab = pd.read_csv(available['lab'])
        if 'SEQN' in lab.columns:
            # Renombrar columnas (excepto SEQN)
            lab_renamed = {
                c: f'LAB_{c}' if c != 'SEQN' else c
                for c in lab.columns
            }
            lab = lab.rename(columns=lab_renamed)
            df = df.merge(lab, on='SEQN', how='left')
            logger.info(f"   LAB: merged {len(lab.columns)} columnas (con prefijo LAB_)")
    
    logger.info(f"   ✓ Total: {len(df):,} registros, {len(df.columns)} columnas")
    
    return df


def create_target_variable(df: pd.DataFrame, 
                          a1c_col: str = 'LAB_LBXGH',
                          glucose_col: str = 'LAB_LBXGLU') -> pd.DataFrame:
    """
    Crea variable target de riesgo cardiometabólico.
    
    Definición:
    - Prediabetes/Diabetes: A1c >= 5.7% OR Glucosa >= 100 mg/dL
    
    Args:
        df: DataFrame con datos
        a1c_col: Nombre de columna A1c
        glucose_col: Nombre de columna glucosa
    
    Returns:
        DataFrame con columna 'target' añadida
    """
    logger.info("Creando variable target...")
    
    df = df.copy()
    
    # Buscar columnas con posibles variantes de nombres
    # (puede tener doble prefijo LAB_LAB_ o solo LAB_)
    a1c_col_variants = [a1c_col, f'LAB_{a1c_col}', 'LAB_LAB_LBXGH', 'LBXGH']
    glucose_col_variants = [glucose_col, f'LAB_{glucose_col}', 'LAB_LAB_LBXGLU', 'LBXGLU']
    
    # Encontrar la columna correcta
    a1c_found = None
    for variant in a1c_col_variants:
        if variant in df.columns:
            a1c_found = variant
            break
    
    glucose_found = None
    for variant in glucose_col_variants:
        if variant in df.columns:
            glucose_found = variant
            break
    
    # Verificar que existan las columnas
    has_a1c = a1c_found is not None
    has_glucose = glucose_found is not None
    
    if not has_a1c and not has_glucose:
        logger.warning("⚠️  No se encontraron columnas de lab para crear target")
        logger.warning(f"   Buscando: {a1c_col}, {glucose_col}")
        # Crear target dummy (50% prevalencia)
        df['target'] = np.random.binomial(1, 0.5, size=len(df))
        logger.warning(f"   Usando target aleatorio (50% prevalencia)")
        return df
    
    # Condiciones de riesgo
    conditions = []
    
    if has_a1c:
        conditions.append(df[a1c_found] >= 5.7)
        logger.info(f"   Usando {a1c_found} >= 5.7%")
    
    if has_glucose:
        conditions.append(df[glucose_found] >= 100)
        logger.info(f"   Usando {glucose_found} >= 100 mg/dL")
    
    # Target = cualquier condición se cumple
    if len(conditions) == 1:
        df['target'] = conditions[0].astype(int)
    else:
        df['target'] = (conditions[0] | conditions[1]).astype(int)
    
    # Manejar NaNs (mantener como NaN para filtrar después)
    prevalence = df['target'].sum() / df['target'].notna().sum()
    n_target = df['target'].notna().sum()
    n_positive = df['target'].sum()
    
    logger.info(f"   ✓ Target creado:")
    logger.info(f"      Con datos: {n_target:,}")
    logger.info(f"      Positivos: {n_positive:,}")
    logger.info(f"      Prevalencia: {prevalence:.2%}")
    
    return df


def clean_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpia códigos de missing values de NHANES.
    
    Args:
        df: DataFrame con datos raw
    
    Returns:
        DataFrame con missing codes convertidos a NaN
    """
    logger.info("Limpiando missing values...")
    
    # Códigos de missing en NHANES
    missing_codes = [7, 9, 77, 99, 777, 999, 7777, 9999]
    
    # Aplicar solo a columnas numéricas
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    
    for col in numeric_cols:
        # Reemplazar códigos missing con NaN
        df[col] = df[col].replace(missing_codes, np.nan)
    
    logger.info(f"   ✓ Missing values limpiados en {len(numeric_cols)} columnas numéricas")
    
    return df


def filter_adults(df: pd.DataFrame, age_col: str = 'RIDAGEYR', min_age: int = 18) -> pd.DataFrame:
    """
    Filtra solo adultos (edad >= min_age).
    
    Args:
        df: DataFrame
        age_col: Nombre de columna de edad
        min_age: Edad mínima
    
    Returns:
        DataFrame filtrado
    """
    logger.info(f"Filtrando adultos (>= {min_age} años)...")
    
    if age_col not in df.columns:
        logger.warning(f"   Columna {age_col} no encontrada, saltando filtro")
        return df
    
    n_before = len(df)
    df = df[df[age_col] >= min_age].copy()
    n_after = len(df)
    
    logger.info(f"   ✓ Filtrados: {n_before:,} → {n_after:,} ({n_after/n_before:.1%})")
    
    return df


def main():
    """Función principal."""
    
    parser = argparse.ArgumentParser(description='Preparar dataset NHANES consolidado')
    parser.add_argument('--data-dir', type=str, default='data', help='Directorio con CSVs')
    parser.add_argument('--output', type=str, default='data/nhanes_processed.csv', 
                       help='Archivo de salida')
    parser.add_argument('--train-cycles', nargs='+', default=['2015-2016'],
                       help='Ciclos de entrenamiento')
    parser.add_argument('--test-cycles', nargs='+', default=['2017-2018'],
                       help='Ciclos de test')
    args = parser.parse_args()
    
    data_path = Path(args.data_dir)
    
    logger.info("="*70)
    logger.info(" PREPARACIÓN DE DATASET NHANES ")
    logger.info("="*70)
    logger.info(f"Data directory: {data_path}")
    logger.info(f"Train cycles: {args.train_cycles}")
    logger.info(f"Test cycles: {args.test_cycles}")
    logger.info("="*70)
    
    try:
        # Cargar todos los ciclos
        all_cycles = args.train_cycles + args.test_cycles
        datasets = []
        
        for cycle in all_cycles:
            try:
                df_cycle = load_cycle_data(cycle, data_path)
                datasets.append(df_cycle)
            except FileNotFoundError as e:
                logger.error(f"   ❌ Error en ciclo {cycle}: {e}")
                continue
        
        if not datasets:
            raise RuntimeError("No se pudieron cargar datos de ningún ciclo")
        
        # Concatenar todos los ciclos
        logger.info(f"\nConsolidando {len(datasets)} ciclos...")
        df = pd.concat(datasets, ignore_index=True)
        logger.info(f"   ✓ Total consolidado: {len(df):,} registros")
        
        # Limpiar missing values
        df = clean_missing_values(df)
        
        # Filtrar adultos
        df = filter_adults(df)
        
        # Crear target
        df = create_target_variable(df)
        
        # Eliminar registros sin target
        n_before = len(df)
        df = df.dropna(subset=['target'])
        n_after = len(df)
        logger.info(f"\nRegistros con target válido: {n_after:,} ({n_after/n_before:.1%})")
        
        # Guardar
        output_path = Path(args.output)
        output_path.parent.mkdir(exist_ok=True)
        df.to_csv(output_path, index=False)
        
        logger.info(f"\n✅ Dataset guardado: {output_path}")
        logger.info(f"   Shape: {df.shape}")
        logger.info(f"   Columnas: {len(df.columns)}")
        logger.info(f"   Registros por ciclo:")
        for cycle in df['cycle'].unique():
            n = len(df[df['cycle'] == cycle])
            logger.info(f"      {cycle}: {n:,}")
        
        # Resumen de target
        logger.info(f"\n   Target distribution:")
        logger.info(f"      Negativos (0): {(df['target']==0).sum():,}")
        logger.info(f"      Positivos (1): {(df['target']==1).sum():,}")
        logger.info(f"      Prevalencia: {df['target'].mean():.2%}")
        
        return 0
        
    except Exception as e:
        logger.error(f"\n❌ Error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())

