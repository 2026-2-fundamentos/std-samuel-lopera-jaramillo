import gzip
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "data.csv.gz"


def pregunta_12():
    totals = {}
    with gzip.open(DATA_FILE, "rt", encoding="utf-8") as file:
        for line in file:
            cols = line.strip().split("\t")
            letter = cols[0]
            metrics_sum = sum(
                int(item.split(":")[1]) for item in cols[4].split(",")
            )
            totals[letter] = totals.get(letter, 0) + metrics_sum

    return dict(sorted(totals.items()))