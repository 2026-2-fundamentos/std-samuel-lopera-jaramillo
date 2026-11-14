from pathlib import Path

import numpy as np
import pandas as pd

ACTIVITY_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ACTIVITY_DIR / "data"
SUBMISSION_DIR = ACTIVITY_DIR / "submission"

DAYS_ORDER = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]


def pregunta_01() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    letter = pd.read_csv(DATA_DIR / "historical_requests_letter.csv.gz").drop_duplicates()
    letter["channel"] = "letter"

    web = pd.read_csv(DATA_DIR / "historical_requests_web.csv.gz").drop_duplicates()
    web["channel"] = "web"

    df = pd.concat([letter, web], ignore_index=True)

    df["in_date"] = pd.to_datetime(df["in_date"])
    df["out_date"] = pd.to_datetime(df["out_date"])
    df["is_answered"] = df["out_date"].notna()
    df["is_pending"] = df["out_date"].isna()
    df["year"] = df["in_date"].dt.year

    # Días calendario y días hábiles en (in_date, out_date] para respondidas
    df["calendar_days"] = (df["out_date"] - df["in_date"]).dt.days
    df["business_days"] = np.nan

    answered_mask = df["is_answered"]
    start_next = (
        df.loc[answered_mask, "in_date"].values.astype("datetime64[D]")
        + np.timedelta64(1, "D")
    )
    end_next = (
        df.loc[answered_mask, "out_date"].values.astype("datetime64[D]")
        + np.timedelta64(1, "D")
    )
    df.loc[answered_mask, "business_days"] = np.busday_count(start_next, end_next)

    df["on_time"] = answered_mask & (df["business_days"] <= 15)

    # 1. Resumen por canal
    channel_summary = (
        df.groupby("channel", as_index=False)
        .agg(
            requests=("in_date", "count"),
            answered=("is_answered", "sum"),
            pending=("is_pending", "sum"),
            median_business_days=("business_days", "median"),
            on_time_rate=("on_time", "mean"),
        )
        .sort_values("channel")
        .reset_index(drop=True)
    )
    channel_summary["answered"] = channel_summary["answered"].astype(int)
    channel_summary["pending"] = channel_summary["pending"].astype(int)

    # 2. Resumen por año y canal
    yearly_summary = (
        df.groupby(["year", "channel"], as_index=False)
        .agg(
            requests=("in_date", "count"),
            pending=("is_pending", "sum"),
            on_time_rate=("on_time", "mean"),
        )
        .sort_values(["year", "channel"])
        .reset_index(drop=True)
    )
    yearly_summary["pending"] = yearly_summary["pending"].astype(int)

    # 3. Resumen por día de la semana de entrada
    df["day_name"] = pd.Categorical(
        df["day_name"], categories=DAYS_ORDER, ordered=True
    )
    entry_day_summary = (
        df.groupby("day_name", observed=False, as_index=False)
        .agg(
            requests=("in_date", "count"),
            median_calendar_days=("calendar_days", "median"),
            median_business_days=("business_days", "median"),
        )
        .sort_values("day_name")
        .reset_index(drop=True)
    )

    # Guardar archivos
    SUBMISSION_DIR.mkdir(parents=True, exist_ok=True)
    channel_summary.to_csv(SUBMISSION_DIR / "channel_summary.csv", index=False)
    yearly_summary.to_csv(SUBMISSION_DIR / "yearly_summary.csv", index=False)
    entry_day_summary.to_csv(SUBMISSION_DIR / "entry_day_summary.csv", index=False)

    return channel_summary, yearly_summary, entry_day_summary