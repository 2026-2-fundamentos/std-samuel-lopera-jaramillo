import gzip
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "data.csv.gz"


def pregunta_05():
    values_by_letter = {}
    with gzip.open(DATA_FILE, "rt", encoding="utf-8") as file:
        for line in file:
            cols = line.strip().split("\t")
            letter = cols[0]
            value = int(cols[1])
            values_by_letter.setdefault(letter, []).append(value)

    return [
        (letter, max(vals), min(vals))
        for letter, vals in sorted(values_by_letter.items())
    ]