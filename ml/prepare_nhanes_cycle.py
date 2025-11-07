#!/usr/bin/env python3
import argparse
from functools import reduce
from pathlib import Path
import pandas as pd

CYCLE_TO_LETTER = {
    "2007-2008": "E",
    "2009-2010": "F",
    "2011-2012": "G",
    "2013-2014": "H",
    "2015-2016": "I",
    "2017-2018": "J",
    "2019-2020": "K",
}

GROUP_DEFINITIONS = {
    "DEMO": ["DEMO"],
    "EXAM": ["BMX", "BPX"],
    "LAB": ["GHB", "GLU", "TRIGLY", "TCHOL", "HDL", "INS", "HSCRP"],
    "QUEST": ["SMQ", "PAQ", "SLQ", "ALQ"],
    "DIET": ["DR1TOT"],
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Agrupa y renombra archivos NHANES convertidos a CSV."
    )
    parser.add_argument(
        "--cycle",
        default="2017-2018",
        help="Ciclo NHANES a procesar (ej: 2017-2018).",
    )
    parser.add_argument(
        "--data-dir",
        default="./data",
        help="Directorio donde están los CSV convertidos.",
    )
    return parser.parse_args()


def cycle_to_letter(cycle: str) -> str:
    if cycle not in CYCLE_TO_LETTER:
        raise ValueError(f"Ciclo no soportado: {cycle}")
    return CYCLE_TO_LETTER[cycle]


def load_dataset(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"No se encontró el archivo requerido: {path}")
    return pd.read_csv(path)


def merge_dataframes(frames: list[pd.DataFrame]) -> pd.DataFrame:
    def merge_pair(left: pd.DataFrame, right: pd.DataFrame) -> pd.DataFrame:
        merged = left.merge(right, on="SEQN", how="outer", suffixes=("", "_dup"))
        duplicate_columns = [c for c in merged.columns if c.endswith("_dup")]
        if duplicate_columns:
            merged = merged.drop(columns=duplicate_columns)
        return merged

    if not frames:
        raise ValueError("No se entregaron DataFrames para combinar.")
    return reduce(merge_pair, frames)


def prepare_group(
    group_name: str,
    codes: list[str],
    data_dir: Path,
    cycle_letter: str,
    cycle_label: str,
) -> pd.DataFrame:
    frames = []
    for code in codes:
        file_name = f"{code}_{cycle_letter}.csv"
        csv_path = data_dir / file_name
        if not csv_path.exists():
            print(
                f"  ⚠️ Archivo faltante para el módulo {code}: {file_name}. "
                "Descárgalo y conviértelo a CSV para incluirlo en el merge."
            )
            continue
        frame = load_dataset(csv_path)
        if group_name == "LAB":
            renamed = {
                column: column if column == "SEQN" or column.startswith("LAB_") else f"LAB_{column}"
                for column in frame.columns
            }
            frame = frame.rename(columns=renamed)
        frames.append(frame)
    if not frames:
        raise FileNotFoundError(
            f"No se pudieron cargar archivos para el grupo {group_name} en el ciclo {cycle_label}."
        )
    combined = merge_dataframes(frames)
    combined.insert(1, "CYCLE", cycle_label)
    return combined


def main() -> None:
    args = parse_args()
    data_dir = Path(args.data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)

    cycle_letter = cycle_to_letter(args.cycle)
    cycle_label = args.cycle
    suffix = args.cycle.replace("-", "_")

    for group_name, dataset_codes in GROUP_DEFINITIONS.items():
        combined = prepare_group(
            group_name=group_name,
            codes=dataset_codes,
            data_dir=data_dir,
            cycle_letter=cycle_letter,
            cycle_label=cycle_label,
        )
        output_name = f"{group_name}_{suffix}.csv"
        output_path = data_dir / output_name
        combined.to_csv(output_path, index=False)
        print(f"✅ {output_name}: {len(combined):,} registros, {len(combined.columns)} columnas")


if __name__ == "__main__":
    main()


