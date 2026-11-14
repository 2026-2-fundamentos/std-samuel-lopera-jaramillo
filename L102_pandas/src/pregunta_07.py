from pathlib import Path
import pandas as pd

DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "tbl0.tsv"


def pregunta_07():
    df = pd.read_csv(DATA_FILE, sep="\t")
    return df.groupby("c1")["c2"].sum()