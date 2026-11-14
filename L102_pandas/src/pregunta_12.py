from pathlib import Path
import pandas as pd

DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "tbl2.tsv"


def pregunta_12():
    df = pd.read_csv(DATA_FILE, sep="\t")
    df["c5"] = df["c5a"] + ":" + df["c5b"].astype(str)
    return df.groupby("c0", as_index=False)["c5"].agg(
        lambda s: ",".join(sorted(s))
    )