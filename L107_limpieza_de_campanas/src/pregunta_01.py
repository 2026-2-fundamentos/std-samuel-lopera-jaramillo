from pathlib import Path

import pandas as pd

ACTIVITY_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ACTIVITY_DIR / "data"
SUBMISSION_DIR = ACTIVITY_DIR / "submission"

MONTH_MAP = {
    "jan": "01",
    "feb": "02",
    "mar": "03",
    "apr": "04",
    "may": "05",
    "jun": "06",
    "jul": "07",
    "aug": "08",
    "sep": "09",
    "oct": "10",
    "nov": "11",
    "dec": "12",
}


def clean_campaign_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    files = sorted(DATA_DIR.glob("*.csv.gz"))
    df = pd.concat((pd.read_csv(f, index_col=0) for f in files), ignore_index=True)

    # 1. Tabla client
    client = df[
        [
            "client_id",
            "age",
            "job",
            "marital",
            "education",
            "credit_default",
            "mortgage",
        ]
    ].copy()
    client["job"] = (
        client["job"]
        .str.replace(".", "", regex=False)
        .str.replace("-", "_", regex=False)
    )
    client["education"] = (
        client["education"]
        .str.replace(".", "_", regex=False)
        .replace("unknown", pd.NA)
    )
    client["credit_default"] = (client["credit_default"] == "yes").astype(int)
    client["mortgage"] = (client["mortgage"] == "yes").astype(int)

    # 2. Tabla campaign
    campaign = df[
        [
            "client_id",
            "number_contacts",
            "contact_duration",
            "previous_campaign_contacts",
            "previous_outcome",
            "campaign_outcome",
        ]
    ].copy()
    campaign["previous_outcome"] = (campaign["previous_outcome"] == "success").astype(int)
    campaign["campaign_outcome"] = (campaign["campaign_outcome"] == "yes").astype(int)
    month_num = df["month"].str.lower().map(MONTH_MAP)
    day_num = df["day"].astype(int).astype(str).str.zfill(2)
    campaign["last_contact_date"] = "2022-" + month_num + "-" + day_num

    # 3. Tabla economics
    economics = df[["client_id", "cons_price_idx", "euribor_three_months"]].copy()

    # Guardar resultados
    SUBMISSION_DIR.mkdir(parents=True, exist_ok=True)
    client.to_csv(SUBMISSION_DIR / "client.csv", index=False)
    campaign.to_csv(SUBMISSION_DIR / "campaign.csv", index=False)
    economics.to_csv(SUBMISSION_DIR / "economics.csv", index=False)

    return client, campaign, economics