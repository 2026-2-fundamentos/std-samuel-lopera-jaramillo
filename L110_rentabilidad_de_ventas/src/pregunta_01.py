from pathlib import Path

import pandas as pd

ACTIVITY_DIR = Path(__file__).resolve().parents[1]
DATA_FILE = ACTIVITY_DIR / "data" / "superstore_orders.csv.gz"
SUBMISSION_DIR = ACTIVITY_DIR / "submission"


def pregunta_01() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    df = pd.read_csv(DATA_FILE, sep=";", decimal=",")

    df["is_loss"] = df["Profit"] < 0
    df["loss_amount"] = (-df["Profit"]).where(df["is_loss"], 0.0)

    # 1. Resumen general de rentabilidad
    lines = int(len(df))
    orders = int(df["Order ID"].nunique())
    sales = float(df["Sales"].sum())
    profit = float(df["Profit"].sum())
    loss_lines = int(df["is_loss"].sum())
    lost_profit = float(df["loss_amount"].sum())

    profitability_summary = pd.DataFrame(
        [
            {
                "lines": lines,
                "orders": orders,
                "sales": sales,
                "profit": profit,
                "profit_margin": profit / sales,
                "loss_lines": loss_lines,
                "loss_line_rate": loss_lines / lines,
                "lost_profit": lost_profit,
            }
        ]
    )

    # 2. Resumen por rango de descuento
    bands = ["0%", "1%-5%", "6%-10%", "más de 10%"]
    df["discount_band"] = pd.cut(
        df["Discount"],
        bins=[-float("inf"), 0.0, 0.05, 0.10, float("inf")],
        labels=bands,
    )

    discount_summary = (
        df.groupby("discount_band", observed=False, as_index=False)
        .agg(
            lines=("Profit", "count"),
            sales=("Sales", "sum"),
            profit=("Profit", "sum"),
            loss_line_rate=("is_loss", "mean"),
            lost_profit=("loss_amount", "sum"),
        )
    )
    discount_summary["profit_margin"] = (
        discount_summary["profit"] / discount_summary["sales"]
    )
    discount_summary = discount_summary[
        [
            "discount_band",
            "lines",
            "sales",
            "profit",
            "profit_margin",
            "loss_line_rate",
            "lost_profit",
        ]
    ]

    # 3. Top 5 segmentos prioritarios (>= 100 líneas, mayor pérdida)
    priority_segments = (
        df.groupby(["Customer Segment", "Product Category"], as_index=False)
        .agg(
            lines=("Profit", "count"),
            sales=("Sales", "sum"),
            profit=("Profit", "sum"),
            lost_profit=("loss_amount", "sum"),
        )
    )
    priority_segments = priority_segments[priority_segments["lines"] >= 100].copy()
    priority_segments["profit_margin"] = (
        priority_segments["profit"] / priority_segments["sales"]
    )
    priority_segments = (
        priority_segments.sort_values("lost_profit", ascending=False)
        .head(5)[
            [
                "Customer Segment",
                "Product Category",
                "lines",
                "sales",
                "profit",
                "profit_margin",
                "lost_profit",
            ]
        ]
        .reset_index(drop=True)
    )

    # Guardar archivos
    SUBMISSION_DIR.mkdir(parents=True, exist_ok=True)
    profitability_summary.to_csv(
        SUBMISSION_DIR / "profitability_summary.csv", index=False
    )
    discount_summary.to_csv(SUBMISSION_DIR / "discount_summary.csv", index=False)
    priority_segments.to_csv(SUBMISSION_DIR / "priority_segments.csv", index=False)

    return profitability_summary, discount_summary, priority_segments