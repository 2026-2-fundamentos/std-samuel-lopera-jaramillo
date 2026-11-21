import csv
import sqlite3
from pathlib import Path

ACTIVITY_DIR = Path(__file__).resolve().parents[1]
INPUT_FILE = ACTIVITY_DIR / "data" / "ventas.csv"
OUTPUT_FILE = ACTIVITY_DIR / "submission" / "ventas.csv"

QUERY = """
WITH raw_clean AS (
    SELECT
        supplier_id,
        TRIM(
            REPLACE(
                REPLACE(
                    REPLACE(
                        REPLACE(
                            REPLACE(
                                REPLACE(
                                    REPLACE(supplier, CHAR(160), ' '),
                                    CHAR(9), ' '
                                ),
                                CHAR(10), ' '
                            ),
                            CHAR(13), ' '
                        ),
                        '  ', ' '
                    ),
                    '  ', ' '
                ),
                '  ', ' '
            )
        ) AS supplier_norm,
        TRIM(city) AS city_norm,
        NULLIF(NULLIF(TRIM(purchase_date), ''), 'N/A') AS date_raw,
        TRIM(
            REPLACE(
                REPLACE(
                    NULLIF(NULLIF(TRIM(amount), ''), 'N/A'),
                    'COP', ''
                ),
                '$', ''
            )
        ) AS amount_raw,
        NULLIF(NULLIF(TRIM(discount), ''), 'N/A') AS discount_raw,
        LOWER(NULLIF(NULLIF(TRIM(weight), ''), 'N/A')) AS weight_raw,
        units,
        TRIM(
            REPLACE(
                REPLACE(
                    NULLIF(NULLIF(TRIM(unit_price), ''), 'N/A'),
                    '$', ''
                ),
                ',', ''
            )
        ) AS price_raw,
        TRIM(contact_email) AS contact_email
    FROM ventas
),
text_and_price AS (
    SELECT
        *,
        REPLACE(
            REPLACE(
                REPLACE(
                    REPLACE(
                        REPLACE(
                            REPLACE(
                                REPLACE(LOWER(supplier_norm), 'Á', 'á'),
                                'É', 'é'
                            ),
                            'Í', 'í'
                        ),
                        'Ó', 'ó'
                    ),
                    'Ú', 'ú'
                ),
                'Ü', 'ü'
            ),
            'Ñ', 'ñ'
        ) AS supplier_key,
        REPLACE(
            REPLACE(
                REPLACE(
                    REPLACE(
                        REPLACE(
                            REPLACE(
                                REPLACE(LOWER(city_norm), 'Á', 'á'),
                                'É', 'é'
                            ),
                            'Í', 'í'
                        ),
                        'Ó', 'ó'
                    ),
                    'Ú', 'ú'
                ),
                'Ü', 'ü'
            ),
            'Ñ', 'ñ'
        ) AS city_key,
        CASE
            WHEN price_raw IS NULL THEN NULL
            WHEN LENGTH(price_raw) - LENGTH(REPLACE(price_raw, '.', '')) > 1
                THEN SUBSTR(price_raw, 1, INSTR(price_raw, '.') - 1)
                     || SUBSTR(price_raw, INSTR(price_raw, '.') + 1)
            ELSE price_raw
        END AS price_step1,
        CASE
            WHEN date_raw IS NULL THEN NULL
            WHEN INSTR(date_raw, '-') > 0 THEN '-'
            WHEN INSTR(date_raw, '.') > 0 THEN '.'
            ELSE '/'
        END AS sep
    FROM raw_clean
),
date_split_1 AS (
    SELECT
        *,
        CASE
            WHEN price_step1 IS NULL THEN NULL
            WHEN LENGTH(price_step1) - LENGTH(REPLACE(price_step1, '.', '')) > 1
                THEN SUBSTR(price_step1, 1, INSTR(price_step1, '.') - 1)
                     || SUBSTR(price_step1, INSTR(price_step1, '.') + 1)
            ELSE price_step1
        END AS price_step2,
        CASE
            WHEN date_raw IS NOT NULL
                THEN SUBSTR(date_raw, 1, INSTR(date_raw, sep) - 1)
        END AS p1,
        CASE
            WHEN date_raw IS NOT NULL
                THEN SUBSTR(date_raw, INSTR(date_raw, sep) + 1)
        END AS rest
    FROM text_and_price
),
date_split_2 AS (
    SELECT
        *,
        CAST(p1 AS INTEGER) AS n1,
        CAST(SUBSTR(rest, 1, INSTR(rest, sep) - 1) AS INTEGER) AS n2,
        SUBSTR(rest, INSTR(rest, sep) + 1) AS p3_str,
        CAST(SUBSTR(rest, INSTR(rest, sep) + 1) AS INTEGER) AS n3
    FROM date_split_1
)
SELECT
    CAST(TRIM(supplier_id) AS INTEGER) AS supplier_id,
    CASE supplier_key
        WHEN 'amazon web services colombia' THEN 'Amazon Web Services Colombia'
        WHEN 'bancolombia s.a.' THEN 'Bancolombia S.A.'
        WHEN 'cementos argos sa' THEN 'Cementos Argos S.A.'
        WHEN 'cementos argos s.a.' THEN 'Cementos Argos S.A.'
        WHEN 'corona sas' THEN 'Corona S.A.S.'
        WHEN 'ecopetrol s.a.' THEN 'Ecopetrol S.A.'
        WHEN 'google colombia ltda.' THEN 'Google Colombia Ltda.'
        WHEN 'grupo éxito s.a.' THEN 'Grupo Éxito S.A.'
        WHEN 'ibm colombia sas.' THEN 'IBM Colombia S.A.S.'
        WHEN 'ibm colombia s.a.s.' THEN 'IBM Colombia S.A.S.'
        WHEN 'microsoft colombia inc.' THEN 'Microsoft Colombia Inc.'
        WHEN 'nutresa sa' THEN 'Nutresa S.A.'
        WHEN 'nutresa s.a.' THEN 'Nutresa S.A.'
        WHEN 'oracle colombia ltda.' THEN 'Oracle Colombia Ltda.'
        WHEN 'postobón s.a.' THEN 'Postobon S.A.'
        WHEN 'sap colombia sas' THEN 'SAP Colombia S.A.S.'
        WHEN 'schneider electric' THEN 'Schneider Electric'
        WHEN 'siemens s.a.s.' THEN 'Siemens S.A.S.'
        WHEN 'sura s.a.' THEN 'Sura S.A.'
        WHEN 'telefónica colombia' THEN 'Telefónica Colombia'
        ELSE supplier_norm
    END AS supplier,
    'COL' AS country,
    CASE city_key
        WHEN 'bogotá' THEN 'Bogotá'
        WHEN 'medellin' THEN 'Medellín'
        WHEN 'medellín' THEN 'Medellín'
        WHEN 'sopó' THEN 'Sopó'
        WHEN 'tenjo' THEN 'Tenjo'
        ELSE city_norm
    END AS city,
    CASE
        WHEN date_raw IS NULL THEN NULL
        WHEN n1 > 1000 THEN PRINTF('%04d-%02d-%02d', n1, n2, n3)
        WHEN sep = '-' AND LENGTH(p3_str) = 2 THEN PRINTF('%04d-%02d-%02d', 2000 + n3, n2, n1)
        WHEN sep = '.' THEN PRINTF('%04d-%02d-%02d', n3, n2, n1)
        WHEN n1 > 12 THEN PRINTF('%04d-%02d-%02d', n3, n2, n1)
        WHEN n2 > 12 THEN PRINTF('%04d-%02d-%02d', n3, n1, n2)
        ELSE PRINTF('%04d-%02d-%02d', n3, n2, n1)
    END AS purchase_date,
    CASE
        WHEN amount_raw IS NULL THEN NULL
        WHEN UPPER(amount_raw) LIKE '%K'
            THEN CAST(ROUND(CAST(TRIM(REPLACE(UPPER(amount_raw), 'K', '')) AS REAL) * 1000) AS INTEGER)
        ELSE CAST(REPLACE(REPLACE(amount_raw, ',', ''), '.', '') AS INTEGER)
    END AS amount,
    CASE
        WHEN discount_raw IS NULL THEN NULL
        WHEN SUBSTR(discount_raw, -1) = '%'
            THEN CAST(TRIM(REPLACE(discount_raw, '%', '')) AS REAL) / 100.0
        WHEN CAST(discount_raw AS REAL) > 1 AND CAST(discount_raw AS REAL) <= 100
            THEN CAST(discount_raw AS REAL) / 100.0
        ELSE CAST(discount_raw AS REAL)
    END AS discount,
    CASE
        WHEN weight_raw IS NULL THEN NULL
        WHEN weight_raw LIKE '%ton'
            THEN CAST(TRIM(REPLACE(weight_raw, 'ton', '')) AS REAL) * 1000.0
        WHEN weight_raw LIKE '%kg'
            THEN CAST(REPLACE(TRIM(REPLACE(weight_raw, 'kg', '')), ',', '.') AS REAL)
        WHEN weight_raw LIKE '%g'
            THEN CAST(TRIM(REPLACE(weight_raw, 'g', '')) AS REAL) / 1000.0
        ELSE CAST(REPLACE(weight_raw, ',', '.') AS REAL)
    END AS weight,
    CAST(TRIM(units) AS INTEGER) AS units,
    CAST(price_step2 AS REAL) AS unit_price,
    contact_email
FROM date_split_2;
"""


def main():
    conn = sqlite3.connect(":memory:")
    cur = conn.cursor()

    with open(INPUT_FILE, encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        headers = [
            h.lstrip("\ufeff").strip().lower().replace(" ", "_")
            for h in next(reader)
        ]
        cols_def = ", ".join(f"{col} TEXT" for col in headers)
        cur.execute(f"CREATE TABLE ventas ({cols_def})")
        placeholders = ", ".join("?" for _ in headers)
        data_rows = [row for row in reader if row]
        cur.executemany(f"INSERT INTO ventas VALUES ({placeholders})", data_rows)

    rows = cur.execute(QUERY).fetchall()
    out_cols = [desc[0] for desc in cur.description]
    conn.close()

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(out_cols)
        writer.writerows(rows)


if __name__ == "__main__":
    main()