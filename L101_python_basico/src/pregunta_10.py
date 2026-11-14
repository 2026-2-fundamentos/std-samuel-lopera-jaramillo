import gzip
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "data.csv.gz"


def pregunta_10():
    result = []
    with gzip.open(DATA_FILE, "rt", encoding="utf-8") as file:
        for line in file:
            cols = line.strip().split("\t")
            letter = cols[0]
            codes_count = len(cols[3].split(","))
            metrics_count = len(cols[4].split(","))
            result.append((letter, codes_count, metrics_count))

    return result