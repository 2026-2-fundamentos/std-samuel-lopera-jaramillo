from pathlib import Path
import pandas as pd

DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "tbl1.tsv"


def pregunta_11():
    df = pd.read_csv(DATA_FILE, sep="\t")
    return df.groupby("c0", as_index=False)["c4"].agg(
        lambda s: ",".join(sorted(s))
    )