import gzip
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "data.csv.gz"


def pregunta_06():
    values_by_key = {}
    with gzip.open(DATA_FILE, "rt", encoding="utf-8") as file:
        for line in file:
            metrics = line.strip().split("\t")[4]
            for item in metrics.split(","):
                key, val = item.split(":")
                values_by_key.setdefault(key, []).append(int(val))

    return [
        (key, min(vals), max(vals))
        for key, vals in sorted(values_by_key.items())
    ]