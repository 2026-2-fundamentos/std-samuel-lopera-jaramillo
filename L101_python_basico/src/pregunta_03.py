import gzip
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "data.csv.gz"


def pregunta_03():
    totals = {}
    with gzip.open(DATA_FILE, "rt", encoding="utf-8") as file:
        for line in file:
            cols = line.strip().split("\t")
            letter = cols[0]
            value = int(cols[1])
            totals[letter] = totals.get(letter, 0) + value
    return sorted(totals.items())