import gzip
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "data.csv.gz"


def pregunta_02():
    counts = {}
    with gzip.open(DATA_FILE, "rt", encoding="utf-8") as file:
        for line in file:
            letter = line.strip().split("\t")[0]
            counts[letter] = counts.get(letter, 0) + 1
    return sorted(counts.items())