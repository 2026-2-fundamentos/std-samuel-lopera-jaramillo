import gzip
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "data.csv.gz"


def pregunta_09():
    counts = {}
    with gzip.open(DATA_FILE, "rt", encoding="utf-8") as file:
        for line in file:
            metrics = line.strip().split("\t")[4]
            for item in metrics.split(","):
                key = item.split(":")[0]
                counts[key] = counts.get(key, 0) + 1

    return dict(sorted(counts.items()))