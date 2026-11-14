from pathlib import Path

import pandas as pd

ACTIVITY_DIR = Path(__file__).resolve().parents[1]
DATA_FILE = ACTIVITY_DIR / "data" / "solicitudes_de_credito.csv.gz"
SUBMISSION_FILE = ACTIVITY_DIR / "submission" / "solicitudes_de_credito.csv"

TEXT_COLUMNS = [
    "sexo",
    "tipo_de_emprendimiento",
    "idea_negocio",
    "barrio",
    "línea_credito",
]


def _parse_dates(values):
    dates = pd.to_datetime(values, format="%d/%m/%Y", errors="coerce")
    for date_format in ("%Y-%m-%d", "%Y/%m/%d"):
        dates = dates.fillna(
            pd.to_datetime(values, format=date_format, errors="coerce")
        )
    return dates


def pregunta_01():
    df = pd.read_csv(DATA_FILE, sep=";", index_col=0)

    required_cols = [c for c in df.columns if c != "comuna_ciudadano"]
    df = df.dropna(subset=required_cols).copy()

    for col in TEXT_COLUMNS:
        df[col] = (
            df[col]
            .str.lower()
            .str.replace("-", " ", regex=False)
            .str.replace("_", " ", regex=False)
            .str.replace(r"\s+", " ", regex=True)
            .str.strip()
        )

    df["estrato"] = df["estrato"].astype(int)
    df["comuna_ciudadano"] = pd.to_numeric(
        df["comuna_ciudadano"], errors="coerce"
    ).astype("Int64")

    df["fecha_de_beneficio"] = _parse_dates(
        df["fecha_de_beneficio"].astype(str).str.strip()
    ).dt.strftime("%Y-%m-%d")

    df["monto_del_credito"] = (
        df["monto_del_credito"]
        .astype(str)
        .str.replace("$", "", regex=False)
        .str.replace(",", "", regex=False)
        .str.strip()
        .pipe(pd.to_numeric)
        .astype(int)
    )

    df = df.drop_duplicates()

    SUBMISSION_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(SUBMISSION_FILE, sep=";", index=False)