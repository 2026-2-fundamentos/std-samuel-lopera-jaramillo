from pathlib import Path
import pandas as pd

DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "tbl1.tsv"


def pregunta_06():
    df = pd.read_csv(DATA_FILE, sep="\t")
    return sorted(df["c4"].str.upper().unique().tolist())