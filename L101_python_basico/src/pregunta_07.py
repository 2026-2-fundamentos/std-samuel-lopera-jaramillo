import gzip
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "data.csv.gz"


def pregunta_07():
    letters_by_value = {}
    with gzip.open(DATA_FILE, "rt", encoding="utf-8") as file:
        for line in file:
            cols = line.strip().split("\t")
            letter = cols[0]
            value = int(cols[1])
            letters_by_value.setdefault(value, []).append(letter)

    return sorted(letters_by_value.items())