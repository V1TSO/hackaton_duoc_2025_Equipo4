# Datos NHANES 2017-2018

## Resumen
- Ciclo procesado: 2017-2018 (`J`)
- Fecha de generación: 2025-11-06
- Herramientas utilizadas:
  - `python descargar_nhanes.py --cycle 2017-2018 --bundle full-model`
  - `python convertir_nhanes.py`
  - `python prepare_nhanes_cycle.py --cycle 2017-2018`

## Archivos disponibles
| Tipo | Archivo | Registros | Columnas | Tamaño |
|------|---------|-----------|----------|--------|
| Demografía | `DEMO_2017_2018.csv` | 9,254 | 47 | 2.1 MB |
| Examen (BMX+BPX) | `EXAM_2017_2018.csv` | 8,704 | 42 | 1.1 MB |
| Laboratorio | `LAB_2017_2018.csv` | 8,366 | 23 | 0.9 MB |
| Cuestionarios | `QUEST_2017_2018.csv` | 6,734 | 73 | 1.6 MB |
| Dieta 24h | `DIET_2017_2018.csv` | 8,704 | 169 | 6.7 MB |
| Raw DEMO | `DEMO_J.csv` | 9,254 | 46 | 2.1 MB |
| Raw BMX | `BMX_J.csv` | 8,704 | 21 | 0.5 MB |
| Raw BPX | `BPX_J.csv` | 8,704 | 21 | 0.6 MB |
| Raw GHB | `GHB_J.csv` | 6,401 | 2 | 0.1 MB |
| Raw GLU | `GLU_J.csv` | 3,036 | 4 | 0.1 MB |
| Raw TRIGLY | `TRIGLY_J.csv` | 3,036 | 10 | 0.2 MB |
| Raw TCHOL | `TCHOL_J.csv` | 7,435 | 3 | 0.1 MB |
| Raw HDL | `HDL_J.csv` | 7,435 | 3 | 0.1 MB |
| Raw INS | `INS_J.csv` | 3,036 | 5 | 0.2 MB |
| Raw HSCRP | `HSCRP_J.csv` | 8,366 | 3 | 0.3 MB |
| Raw SMQ | `SMQ_J.csv` | 6,724 | 37 | 0.5 MB |
| Raw PAQ | `PAQ_J.csv` | 5,856 | 17 | 0.3 MB |
| Raw SLQ | `SLQ_J.csv` | 6,161 | 11 | 0.5 MB |
| Raw ALQ | `ALQ_J.csv` | 5,533 | 10 | 0.3 MB |
| Raw DR1TOT | `DR1TOT_J.csv` | 8,704 | 168 | 7.2 MB |

> Todos los archivos mantienen la clave `SEQN`. Los datasets combinados (`*_2017_2018.csv`) incluyen la columna `CYCLE` como etiqueta temporal.

## Validaciones
- `python test_datos.py` ejecutado sin errores. Los avisos sobre ciclos anteriores son esperados (aún no disponibles en `data/`).
- Tamaños verificados con `ls -lh data`.

## Reglas anti-fuga
- Las columnas de laboratorio se renombraron con prefijo `LAB_` durante la combinación para recordar que solo se usan como etiquetas o variables objetivo (ver `Desafio_Salud_NHANES_2025_duoc.txt`).
- Al generar features, omitir cualquier campo `LAB_*` si la etiqueta se construye con analitos de laboratorio.

## Próximos pasos sugeridos
- Integrar `DEMO_2017_2018.csv`, `EXAM_2017_2018.csv`, `QUEST_2017_2018.csv` y `DIET_2017_2018.csv` como features.
- Usar `LAB_2017_2018.csv` únicamente para derivar la etiqueta de riesgo (ej. HbA1c, glucosa).
- Repetir el flujo para ciclos 2007-2016 si se requiere el set de entrenamiento completo del hackathon.




