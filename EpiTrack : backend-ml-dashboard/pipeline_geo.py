import os
from datetime import datetime

import numpy as np
import pandas as pd

from sqlalchemy import create_engine

OUT_DIR = os.environ.get("OUT_DIR", "./outputs")
os.makedirs(OUT_DIR, exist_ok=True)

PG_URI = os.environ.get("PG_URI")

# Very simple country → lat/lon lookup.
# You can add more as needed.
COUNTRY_COORDS = {
    "Japan": (36.2048, 138.2529),
    "New Zealand": (-40.9006, 174.8860),
    "United States": (37.0902, -95.7129),
    "USA": (37.0902, -95.7129),
    "India": (20.5937, 78.9629),
    "United Kingdom": (55.3781, -3.4360),
    "UK": (55.3781, -3.4360),
    "Australia": (-25.2744, 133.7751),
    "Canada": (56.1304, -106.3468),
    # add more if you like
}

def main():
    if not PG_URI:
        print("❌ PG_URI not set; writing empty geo_points.csv.")
        write_empty()
        return

    engine = create_engine(PG_URI)
    df = pd.read_sql(
        """
        SELECT
            id,
            title,
            description,
            source,
            keywords,
            published_at,
            country,
            disease_mention_count,
            disease_breakdown
        FROM articles
        WHERE published_at IS NOT NULL
        ORDER BY published_at DESC
        """,
        engine,
    )

    if df.empty:
        print("⚠️ No rows returned from articles; writing empty geo_points.csv.")
        write_empty()
        return

    df["published_at"] = pd.to_datetime(df["published_at"], errors="coerce")
    df = df.dropna(subset=["published_at"])
    df["date"] = df["published_at"].dt.normalize()

    # parse disease names from disease_breakdown if present,
    # else fallback to disease_mention_count>0 and title/description.
    def extract_diseases(row):
        breakdown = row.get("disease_breakdown", None)
        if isinstance(breakdown, dict):
            return [k for k, v in breakdown.items() if (isinstance(v, (int, float)) and v > 0)]
        # fallback: you could reuse regex, but for simplicity:
        # if disease_mention_count > 0, just label as "Unknown"
        if isinstance(row.get("disease_mention_count", 0), (int, float)) and row["disease_mention_count"] > 0:
            return ["Unknown"]
        return []

    records = []
    for _, r in df.iterrows():
        date = r["date"]
        country = r.get("country", None)
        if country is None or str(country).strip() == "":
            # keep row but without coordinates; will still work for hotzones
            lat, lon = (None, None)
        else:
            c_norm = str(country).strip()
            lat, lon = COUNTRY_COORDS.get(c_norm, (None, None))

        diseases = extract_diseases(r)
        if not diseases:
            continue

        for dis in diseases:
            mention_count = r.get("disease_mention_count", 1)
            if not isinstance(mention_count, (int, float)):
                mention_count = 1
            if mention_count <= 0:
                mention_count = 1

            records.append({
                "date": date.normalize(),
                "disease_name": dis,
                "country": country,
                "lat": lat,
                "lon": lon,
                "mention_count": int(mention_count),
            })

    if not records:
        print("⚠️ No geo disease records derived; writing empty geo_points.csv.")
        write_empty()
        return

    geo = pd.DataFrame(records)
    geo.to_csv(os.path.join(OUT_DIR, "geo_points.csv"), index=False)
    print(f"✅ geo_points.csv written with {len(geo)} rows to {OUT_DIR}")


def write_empty():
    cols = ["date", "disease_name", "country", "lat", "lon", "mention_count"]
    pd.DataFrame(columns=cols).to_csv(
        os.path.join(OUT_DIR, "geo_points.csv"), index=False
    )
    print("✅ Empty geo_points.csv written.")


if __name__ == "__main__":
    main()
