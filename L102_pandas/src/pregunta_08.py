from pathlib import Path
import pandas as pd

DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "tbl0.tsv"


def pregunta_08():
    df = pd.read_csv(DATA_FILE, sep="\t")
    df["suma"] = df["c0"] + df["c2"]
    return df