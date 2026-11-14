from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ACTIVITY_DIR = Path(__file__).resolve().parents[1]
DATA_FILE = ACTIVITY_DIR / "data" / "sales.csv.gz"
SUBMISSION_DIR = ACTIVITY_DIR / "submission"
CSV_FILE = SUBMISSION_DIR / "cohort_retention.csv"
PNG_FILE = SUBMISSION_DIR / "cohort_retention_heatmap.png"


def build_cohort_analysis() -> pd.DataFrame:
    df = pd.read_csv(DATA_FILE)

    order_period = pd.to_datetime(df["OrderDate"]).dt.to_period("M")
    df["order_period"] = order_period
    df["cohort_period"] = df.groupby("CustomerID")["order_period"].transform("min")

    df["cohort_month"] = df["cohort_period"].astype(str)
    df["period_index"] = (
        (df["order_period"].dt.year - df["cohort_period"].dt.year) * 12
        + (df["order_period"].dt.month - df["cohort_period"].dt.month)
    )

    retention = (
        df.groupby(["cohort_month", "period_index"], as_index=False)
        .agg(active_customers=("CustomerID", "nunique"))
        .sort_values(["cohort_month", "period_index"])
        .reset_index(drop=True)
    )

    cohort_sizes = (
        retention[retention["period_index"] == 0]
        .set_index("cohort_month")["active_customers"]
    )
    retention["cohort_size"] = retention["cohort_month"].map(cohort_sizes)
    retention["retention_rate"] = (
        retention["active_customers"] / retention["cohort_size"]
    )

    retention = retention[
        [
            "cohort_month",
            "period_index",
            "active_customers",
            "cohort_size",
            "retention_rate",
        ]
    ]

    SUBMISSION_DIR.mkdir(parents=True, exist_ok=True)
    retention.to_csv(CSV_FILE, index=False)

    # Mapa de calor de retención (%)
    pivot = retention.pivot(
        index="cohort_month",
        columns="period_index",
        values="retention_rate",
    )
    pct_matrix = pivot.to_numpy(dtype=float) * 100.0

    fig, ax = plt.subplots(figsize=(10, 6))
    cmap = plt.get_cmap("YlGnBu").copy()
    cmap.set_bad(color="white")

    im = ax.imshow(pct_matrix, aspect="auto", cmap=cmap, vmin=0, vmax=100)
    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label("Tasa de retención (%)")

    ax.set_xticks(np.arange(len(pivot.columns)))
    ax.set_xticklabels(pivot.columns)
    ax.set_yticks(np.arange(len(pivot.index)))
    ax.set_yticklabels(pivot.index)
    ax.set_xlabel("Período (meses desde primera compra)")
    ax.set_ylabel("Cohorte (mes de primera compra)")
    ax.set_title("Retención de clientes por cohorte (%)")

    for i in range(pct_matrix.shape[0]):
        for j in range(pct_matrix.shape[1]):
            val = pct_matrix[i, j]
            if not np.isnan(val):
                text_color = "white" if val > 55 else "black"
                ax.text(
                    j,
                    i,
                    f"{val:.1f}%",
                    ha="center",
                    va="center",
                    color=text_color,
                    fontsize=9,
                )

    fig.tight_layout()
    fig.savefig(PNG_FILE, dpi=150)
    plt.close(fig)

    return retention