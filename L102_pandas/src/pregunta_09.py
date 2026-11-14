from pathlib import Path
import pandas as pd

DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "tbl0.tsv"


def pregunta_09():
    df = pd.read_csv(DATA_FILE, sep="\t")
    df["year"] = df["c3"].str.slice(0, 4)
    return df