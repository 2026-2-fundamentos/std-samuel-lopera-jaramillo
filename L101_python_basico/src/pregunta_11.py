import gzip
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "data.csv.gz"


def pregunta_11():
    totals = {}
    with gzip.open(DATA_FILE, "rt", encoding="utf-8") as file:
        for line in file:
            cols = line.strip().split("\t")
            value = int(cols[1])
            for code in cols[3].split(","):
                totals[code] = totals.get(code, 0) + value

    return dict(sorted(totals.items()))