import gzip
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "data.csv.gz"


def pregunta_04():
    counts = {}
    with gzip.open(DATA_FILE, "rt", encoding="utf-8") as file:
        for line in file:
            date = line.strip().split("\t")[2]
            month = date.split("-")[1]
            counts[month] = counts.get(month, 0) + 1
    return sorted(counts.items())