import json
from pathlib import Path

import pandas as pd

ACTIVITY_DIR = Path(__file__).resolve().parents[1]
DATA_FILE = ACTIVITY_DIR / "data" / "insurance.csv.gz"
SUBMISSION_DIR = ACTIVITY_DIR / "submission"
REPORT_FILE = SUBMISSION_DIR / "privacy_report.json"
PUBLISHED_FILE = SUBMISSION_DIR / "insurance_published.csv"


def pregunta_01():
    df = pd.read_csv(DATA_FILE)

    original_qis = ["age", "sex", "bmi", "children", "region"]
    orig_sizes = df.groupby(original_qis).size()
    original_k = int(orig_sizes.min())
    original_unique_records = int((orig_sizes == 1).sum())

    df["age_group"] = pd.cut(
        df["age"],
        bins=[17, 29, 39, 49, 64],
        labels=["18-29", "30-39", "40-49", "50-64"],
    ).astype(str)

    df["bmi_group"] = pd.cut(
        df["bmi"],
        bins=[-float("inf"), 18.5, 25, 30, float("inf")],
        right=False,
        labels=["bajo peso", "normal", "sobrepeso", "obesidad"],
    ).astype(str)

    df["children_group"] = pd.cut(
        df["children"],
        bins=[-1, 0, 2, float("inf")],
        labels=["0", "1-2", "3+"],
    ).astype(str)

    schemes_config = {
        "with_children": [
            "age_group",
            "sex",
            "bmi_group",
            "children_group",
            "region",
        ],
        "without_children": [
            "age_group",
            "sex",
            "bmi_group",
            "region",
        ],
    }

    schemes_report = {}
    published_dfs = {}

    for name, qis in schemes_config.items():
        grouped = df.groupby(qis)
        class_sizes = grouped.size()
        row_class_sizes = grouped["smoker"].transform("count")

        pub_df = df[row_class_sizes >= 5].copy()
        published_dfs[name] = pub_df

        pub_grouped = pub_df.groupby(qis)
        pub_class_sizes = pub_grouped.size()
        smoker_nunique = pub_grouped["smoker"].nunique()
        no_div_mask = smoker_nunique == 1

        schemes_report[name] = {
            "quasi_identifiers": qis,
            "equivalence_classes": int(len(class_sizes)),
            "k_before_suppression": int(class_sizes.min()),
            "suppressed_records": int((row_class_sizes < 5).sum()),
            "published_records": int(len(pub_df)),
            "published_classes": int(len(pub_class_sizes)),
            "classes_without_smoker_diversity": int(no_div_mask.sum()),
            "records_without_smoker_diversity": int(pub_class_sizes[no_div_mask].sum()),
        }

    selected_scheme = min(
        schemes_report,
        key=lambda s: schemes_report[s]["suppressed_records"],
    )
    selected_qis = schemes_config[selected_scheme]
    selected_df = published_dfs[selected_scheme][
        selected_qis + ["smoker", "charges"]
    ]

    report = {
        "original_k": original_k,
        "original_unique_records": original_unique_records,
        "schemes": schemes_report,
        "selected_scheme": selected_scheme,
        "mean_charges_original": float(df["charges"].mean()),
        "mean_charges_published": float(selected_df["charges"].mean()),
        "smoker_rate_original": float((df["smoker"] == "yes").mean()),
        "smoker_rate_published": float((selected_df["smoker"] == "yes").mean()),
    }

    SUBMISSION_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_FILE.write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    selected_df.to_csv(PUBLISHED_FILE, index=False)

    return report