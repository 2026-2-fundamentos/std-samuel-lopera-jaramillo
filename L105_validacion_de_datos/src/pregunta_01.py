import json
import re
from pathlib import Path

import pandas as pd

ACTIVITY_DIR = Path(__file__).resolve().parents[1]
DATA_FILE = ACTIVITY_DIR / "data" / "ventas.csv.gz"
REPORT_FILE = ACTIVITY_DIR / "submission" / "data_quality_report.json"

REQUIRED_COLUMNS = [
    "supplier_id",
    "supplier",
    "country",
    "city",
    "purchase_date",
    "amount",
    "discount",
    "weight",
    "units",
    "unit_price",
    "contact_email",
]


def main():
    df = pd.read_csv(
        DATA_FILE,
        dtype=str,
        keep_default_na=False,
        encoding="utf-8-sig",
    )

    df.columns = [
        re.sub(r"\s+", "_", col.lstrip("\ufeff").strip().lower())
        for col in df.columns
    ]

    actual_columns = set(df.columns)
    required_set = set(REQUIRED_COLUMNS)

    missing_required_columns = sorted(required_set - actual_columns)
    unexpected_columns = sorted(actual_columns - required_set)

    missing_value_count_by_column = {
        col: int(df[col].str.strip().isin(["", "N/A"]).sum())
        for col in df.columns
    }

    email_pattern = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    invalid_email_count = int(
        (~df["contact_email"].str.match(email_pattern)).sum()
    )

    invalid_unit_count = 0
    for val in df["units"]:
        cleaned = val.strip()
        if cleaned in ("", "N/A"):
            continue
        try:
            num = float(cleaned)
        except ValueError:
            continue
        if num <= 0 or not num.is_integer():
            invalid_unit_count += 1

    report = {
        "row_count": int(len(df)),
        "column_count": int(len(df.columns)),
        "missing_required_columns": missing_required_columns,
        "unexpected_columns": unexpected_columns,
        "duplicate_row_count": int(df.duplicated().sum()),
        "duplicate_supplier_id_row_count": int(
            df["supplier_id"].duplicated(keep=False).sum()
        ),
        "missing_value_count_by_column": missing_value_count_by_column,
        "invalid_email_count": invalid_email_count,
        "invalid_unit_count": int(invalid_unit_count),
        "country_values": sorted(df["country"].unique().tolist()),
    }

    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    REPORT_FILE.write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    return report