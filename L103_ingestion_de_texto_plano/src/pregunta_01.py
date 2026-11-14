import re
from pathlib import Path

import pandas as pd

DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "clusters_report.txt"


def pregunta_01():
    rows = []
    current = None
    header_pattern = re.compile(r"^(\d+)\s+(\d+)\s+(\d+,\d+)\s*%\s+(.*)$")

    with open(DATA_FILE, encoding="utf-8") as file:
        for line in file.readlines()[4:]:
            line = line.strip()
            if not line:
                continue

            match = header_pattern.match(line)
            if match:
                if current is not None:
                    rows.append(current)

                cluster, count, pct, keywords = match.groups()
                current = {
                    "cluster": int(cluster),
                    "cantidad_de_palabras_clave": int(count),
                    "porcentaje_de_palabras_clave": float(pct.replace(",", ".")),
                    "principales_palabras_clave": [keywords],
                }
            elif current is not None:
                current["principales_palabras_clave"].append(line)

    if current is not None:
        rows.append(current)

    for row in rows:
        text = " ".join(row["principales_palabras_clave"])
        text = re.sub(r"\s+", " ", text).strip().rstrip(".")
        text = re.sub(r",\s*", ", ", text)
        row["principales_palabras_clave"] = text

    return pd.DataFrame(rows)