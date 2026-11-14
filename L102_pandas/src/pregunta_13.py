from pathlib import Path
import pandas as pd

DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def pregunta_13():
    tbl0 = pd.read_csv(DATA_DIR / "tbl0.tsv", sep="\t")
    tbl2 = pd.read_csv(DATA_DIR / "tbl2.tsv", sep="\t")
    merged = pd.merge(tbl0, tbl2, on="c0")
    return merged.groupby("c1")["c5b"].sum()