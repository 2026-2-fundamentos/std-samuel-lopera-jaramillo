from pathlib import Path

import pandas as pd

ACTIVITY_DIR = Path(__file__).resolve().parents[1]
DATA_FILE = ACTIVITY_DIR / "data" / "flights_by_carrier_day_hour.csv.gz"
SUBMISSION_DIR = ACTIVITY_DIR / "submission"


def pregunta_01() -> tuple[pd.DataFrame, pd.DataFrame]:
    df = pd.read_csv(DATA_FILE)

    # 1. Tasa nacional de demora por hora programada de salida (0 a 23)
    hourly_delay_rates = (
        df.groupby("scheduled_departure_hour", as_index=False)
        .agg(
            operated_flights=("operated_flights", "sum"),
            delayed_departure_15_flights=("delayed_departure_15_flights", "sum"),
        )
        .sort_values("scheduled_departure_hour")
        .reset_index(drop=True)
    )
    hourly_delay_rates["operated_flights"] = hourly_delay_rates[
        "operated_flights"
    ].astype(int)
    hourly_delay_rates["delayed_departure_15_flights"] = hourly_delay_rates[
        "delayed_departure_15_flights"
    ].astype(int)
    hourly_delay_rates["delay_rate"] = (
        hourly_delay_rates["delayed_departure_15_flights"]
        / hourly_delay_rates["operated_flights"]
    )

    # 2. Demoras observadas vs. esperadas por aerolínea
    df_with_rate = df.merge(
        hourly_delay_rates[["scheduled_departure_hour", "delay_rate"]].rename(
            columns={"delay_rate": "national_delay_rate"}
        ),
        on="scheduled_departure_hour",
        how="left",
    )
    df_with_rate["expected_delayed_flights"] = (
        df_with_rate["operated_flights"] * df_with_rate["national_delay_rate"]
    )

    carrier_adjusted_delays = df_with_rate.groupby(
        "reporting_airline", as_index=False
    ).agg(
        operated_flights=("operated_flights", "sum"),
        delayed_departure_15_flights=("delayed_departure_15_flights", "sum"),
        expected_delayed_flights=("expected_delayed_flights", "sum"),
    )

    carrier_adjusted_delays = carrier_adjusted_delays[
        carrier_adjusted_delays["operated_flights"] >= 100_000
    ].copy()

    carrier_adjusted_delays["operated_flights"] = carrier_adjusted_delays[
        "operated_flights"
    ].astype(int)
    carrier_adjusted_delays["delayed_departure_15_flights"] = carrier_adjusted_delays[
        "delayed_departure_15_flights"
    ].astype(int)

    carrier_adjusted_delays["delay_rate"] = (
        carrier_adjusted_delays["delayed_departure_15_flights"]
        / carrier_adjusted_delays["operated_flights"]
    )
    carrier_adjusted_delays["observed_to_expected_ratio"] = (
        carrier_adjusted_delays["delayed_departure_15_flights"]
        / carrier_adjusted_delays["expected_delayed_flights"]
    )

    carrier_adjusted_delays["crude_rank"] = (
        carrier_adjusted_delays["delay_rate"]
        .rank(ascending=False, method="min")
        .astype(int)
    )
    carrier_adjusted_delays["adjusted_rank"] = (
        carrier_adjusted_delays["observed_to_expected_ratio"]
        .rank(ascending=False, method="min")
        .astype(int)
    )

    carrier_adjusted_delays = (
        carrier_adjusted_delays.sort_values("adjusted_rank")[
            [
                "reporting_airline",
                "operated_flights",
                "delayed_departure_15_flights",
                "delay_rate",
                "expected_delayed_flights",
                "observed_to_expected_ratio",
                "crude_rank",
                "adjusted_rank",
            ]
        ]
        .reset_index(drop=True)
    )

    # Guardar resultados
    SUBMISSION_DIR.mkdir(parents=True, exist_ok=True)
    hourly_delay_rates.to_csv(
        SUBMISSION_DIR / "hourly_delay_rates.csv", index=False
    )
    carrier_adjusted_delays.to_csv(
        SUBMISSION_DIR / "carrier_adjusted_delays.csv", index=False
    )

    return hourly_delay_rates, carrier_adjusted_delays