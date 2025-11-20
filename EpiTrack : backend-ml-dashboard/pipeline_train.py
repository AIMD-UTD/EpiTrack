import os
import re
import time
import argparse
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

# Forecasting lib (optional but recommended)
try:
    from statsmodels.tsa.holtwinters import ExponentialSmoothing
    HAS_SM = True
except Exception:
    HAS_SM = False

# SQLAlchemy for Neon
try:
    from sqlalchemy import create_engine
    HAS_SQLA = True
except Exception:
    HAS_SQLA = False


# =====================================================
# CONFIG & DATA LOADING
# =====================================================

OUT_DIR = os.environ.get("OUT_DIR", "./outputs")
os.makedirs(OUT_DIR, exist_ok=True)

PG_URI = os.environ.get("PG_URI")
CSV_FALLBACK = os.environ.get("ARTICLES_CSV", "./articles.csv")

def load_articles() -> pd.DataFrame:
    """
    Load articles either from Neon (PG_URI) or from a local CSV.
    Only uses columns that actually exist in your schema.
    """
    if PG_URI and HAS_SQLA:
        print("🔌 Using Neon database as input...")
        engine = create_engine(PG_URI)
        query = """
        SELECT
            id,
            title,
            description,
            source,
            keywords,
            published_at,
            fetched_at,
            country,
            disease_mention_count,
            disease_breakdown,
            confidence_score,
            created_at
        FROM articles
        ORDER BY published_at DESC
        """
        df = pd.read_sql(query, engine)
    else:
        print("📄 Using local CSV as input…")
        if not os.path.exists(CSV_FALLBACK):
            raise FileNotFoundError(
                f"CSV fallback {CSV_FALLBACK} not found and PG_URI not set."
            )
        df = pd.read_csv(CSV_FALLBACK)

    return df


df = load_articles()

DATE_CANDIDATES = [
    "published_at", "publishedAt", "published_date",
    "date", "created_at", "fetched_at"
]
date_col = next((c for c in DATE_CANDIDATES if c in df.columns), None)
if not date_col:
    raise ValueError(
        f"No date column found. Looked for {DATE_CANDIDATES}. Got {list(df.columns)}"
    )

df[date_col] = pd.to_datetime(df[date_col], errors="coerce", utc=True)
df[date_col] = df[date_col].dt.tz_convert(None)
df = df.dropna(subset=[date_col])

# Ensure text fields exist
for col in ["title", "description", "source"]:
    if col not in df.columns:
        df[col] = ""

# keywords column may be jsonb/list/str/null
if "keywords" not in df.columns:
    df["keywords"] = None

# Build text for regex detection (title + description only)
df["full_text"] = (
    df["title"].astype(str) + " " +
    df["description"].astype(str)
)

print(f"✅ Using date column: {date_col} | rows: {len(df)}")


# =====================================================
# DISEASE PATTERNS
# =====================================================

PATTERNS = {
    r"\bcovid[-\s]?19\b|\bcoronavirus\b|\bsars[-\s]?cov[-\s]?2\b": "COVID-19",
    r"\bdengue\b": "Dengue",
    r"\bmalaria\b": "Malaria",
    r"\bflu\b|\binfluenza\b": "Influenza",
    r"\bmeasles\b": "Measles",
    r"\bebola\b": "Ebola",
    r"\bzika\b": "Zika",
    r"\btuberculosis\b|\btb\b": "Tuberculosis",
    r"\bmeningitis\b": "Meningitis",
}
COMPILED = [(re.compile(p, re.I), name) for p, name in PATTERNS.items()]
KEYWORD_MAP = {name.lower(): name for name in set(PATTERNS.values())}


# =====================================================
# EXTRACT MENTIONS
# =====================================================

rows = []

for i, r in df.iterrows():
    text = str(r["full_text"])
    date_val = pd.to_datetime(r[date_col]).normalize()

    hit = False

    # 1) Regex-based disease detection in text
    for rgx, name in COMPILED:
        matches = rgx.findall(text)
        if matches:
            rows.append({
                "article_id": int(r.get("id", i)),
                "date": date_val,
                "disease_name": name,
                "mention_count": len(matches),
                "source": r["source"],
            })
            hit = True

    # 2) Fallback via keywords (jsonb/list/str)
    kw = r.get("keywords", None)

    # Normalize keywords into a flat list of lowercase tokens
    toks = []
    if not hit and kw is not None:
        # list from jsonb
        if isinstance(kw, list):
            toks = [str(x).lower().strip() for x in kw if x]
        # dict (rare) -> keys
        elif isinstance(kw, dict):
            toks = [str(k).lower().strip() for k in kw.keys()]
        # string -> split by punctuation/whitespace
        elif isinstance(kw, str):
            toks = re.split(r"[,\|;/\s]+", kw.lower())
        # else: ignore

    if not hit and toks:
        seen = {}
        for t in toks:
            mapped = KEYWORD_MAP.get(t)
            if mapped:
                seen[mapped] = seen.get(mapped, 0) + 1

        for name, cnt in seen.items():
            rows.append({
                "article_id": int(r.get("id", i)),
                "date": date_val,
                "disease_name": name,
                "mention_count": int(cnt),
                "source": r["source"],
            })

mentions = pd.DataFrame(rows)

if mentions.empty:
    print("⚠️ No disease mentions found from text/keywords.")
    # Write empty but well-formed files so Streamlit doesn't crash
    pd.DataFrame(
        columns=["date", "disease_name", "mention_count",
                 "sentiment_score", "source_reliability"]
    ).to_csv(os.path.join(OUT_DIR, "clean_timeseries.csv"), index=False)

    pd.DataFrame(
        columns=[
            "disease_name", "model_used", "recent_actual_mean",
            "forecast_next_mean", "forecast_lower_95", "forecast_upper_95",
            "pct_change_vs_recent", "is_rising"
        ]
    ).to_csv(os.path.join(OUT_DIR, "rising_diseases.csv"), index=False)

    pd.DataFrame(
        columns=["date", "disease_name", "forecast",
                 "lower_95", "upper_95"]
    ).to_csv(os.path.join(OUT_DIR, "forecasts.csv"), index=False)

    print("✅ Empty outputs written (no diseases detected).")
    raise SystemExit(0)


# =====================================================
# AGGREGATE TO DAILY TIME SERIES
# =====================================================

agg = mentions.groupby(["date", "disease_name"], as_index=False)["mention_count"].sum()

def fill_daily(group: pd.DataFrame) -> pd.DataFrame:
    group = group.set_index("date").sort_index()
    idx = pd.date_range(group.index.min(), group.index.max(), freq="D")
    group = group.reindex(idx).fillna(0.0)
    group.index.name = "date"
    group["mention_count"] = group["mention_count"].astype(float)
    return group.reset_index()

filled = []
for dis, g in agg.groupby("disease_name"):
    d = fill_daily(g)
    d["disease_name"] = dis
    filled.append(d)

clean = pd.concat(filled, ignore_index=True)

# Placeholders (upgrade later if you want)
clean["sentiment_score"] = 0.0
clean["source_reliability"] = 0.5


# =====================================================
# FORECASTING + CONFIDENCE INTERVALS
# =====================================================

ap = argparse.ArgumentParser()
ap.add_argument("--days", type=int, default=7, help="Forecast horizon (7/14/30/60)")
args = ap.parse_args()
H = int(args.days)

results = []
forecast_frames = []

for dis, g in clean.groupby("disease_name"):
    g = g.sort_values("date")
    y = g["mention_count"].astype(float)

    fc = None
    lower_ci = None
    upper_ci = None
    model_used = None

    # Case 1: all-zero history
    if (y > 0).sum() == 0:
        fc = np.zeros(H)
        lower_ci = np.zeros(H)
        upper_ci = np.zeros(H)
        model_used = "Zero"

    else:
        # Case 2: Holt–Winters if enough history + statsmodels available
        if HAS_SM and len(y) >= 10:
            try:
                seasonal = 7 if len(y) >= 21 else None
                hw = ExponentialSmoothing(
                    y,
                    trend="add",
                    seasonal=("add" if seasonal else None),
                    seasonal_periods=seasonal,
                    initialization_method="estimated",
                ).fit(optimized=True, use_brute=True)

                fc = hw.forecast(H).values
                model_used = "Holt-Winters"

                resid = y - hw.fittedvalues
                resid_std = float(np.nanstd(resid, ddof=1))
                if not np.isfinite(resid_std):
                    resid_std = 0.0
                z = 1.96  # 95% CI
                lower_ci = fc - z * resid_std
                upper_ci = fc + z * resid_std
            except Exception:
                fc = None
                lower_ci = None
                upper_ci = None

        # Case 3: fallback to Moving Average + CI
        if fc is None:
            ma_series = y.rolling(7, min_periods=1).mean()
            ma_last = float(ma_series.iloc[-1])
            fc = np.full(H, ma_last)
            model_used = "MovingAverage"

            resid = y - ma_series
            resid_std = float(np.nanstd(resid, ddof=1))
            if not np.isfinite(resid_std):
                resid_std = 0.0
            z = 1.96
            lower_ci = fc - z * resid_std
            upper_ci = fc + z * resid_std

    # Safety: if CI still None, pin to forecast
    if lower_ci is None or upper_ci is None:
        lower_ci = fc.copy()
        upper_ci = fc.copy()

    # No negative counts
    fc = np.clip(fc, 0.0, None)
    lower_ci = np.clip(lower_ci, 0.0, None)
    upper_ci = np.clip(upper_ci, 0.0, None)

    # Build forecast frame for this disease
    future_dates = pd.date_range(
        g["date"].max() + timedelta(days=1),
        periods=H,
        freq="D"
    )
    forecast_frames.append(pd.DataFrame({
        "date": future_dates,
        "disease_name": dis,
        "forecast": fc,
        "lower_95": lower_ci,
        "upper_95": upper_ci,
    }))

    # Summary stats for rising_diseases table
    recent_mean = float(y.tail(7).mean()) if len(y) else 0.0
    next_mean = float(fc.mean())
    next_lower_mean = float(lower_ci.mean())
    next_upper_mean = float(upper_ci.mean())

    if recent_mean > 0:
        pct = (next_mean - recent_mean) / recent_mean
    else:
        pct = 1.0 if next_mean > 0 else 0.0

    results.append({
        "disease_name": dis,
        "model_used": model_used,
        "recent_actual_mean": round(recent_mean, 3),
        "forecast_next_mean": round(next_mean, 3),
        "forecast_lower_95": round(next_lower_mean, 3),
        "forecast_upper_95": round(next_upper_mean, 3),
        "pct_change_vs_recent": round(pct, 3),
        "is_rising": bool(pct > 0.15),
    })


# =====================================================
# SAVE OUTPUTS
# =====================================================

summary = pd.DataFrame(results).sort_values(
    "pct_change_vs_recent", ascending=False
)
forecasts = pd.concat(forecast_frames, ignore_index=True)

# Latest versions used by Streamlit
clean[["date", "disease_name", "mention_count",
       "sentiment_score", "source_reliability"]].to_csv(
    os.path.join(OUT_DIR, "clean_timeseries.csv"), index=False
)

summary[[
    "disease_name", "model_used", "recent_actual_mean",
    "forecast_next_mean", "forecast_lower_95", "forecast_upper_95",
    "pct_change_vs_recent", "is_rising"
]].to_csv(
    os.path.join(OUT_DIR, "rising_diseases.csv"), index=False
)

forecasts[["date", "disease_name", "forecast",
           "lower_95", "upper_95"]].to_csv(
    os.path.join(OUT_DIR, "forecasts.csv"), index=False
)

# Versioned snapshots
stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
clean.to_csv(os.path.join(OUT_DIR, f"clean_timeseries_{stamp}.csv"), index=False)
summary.to_csv(os.path.join(OUT_DIR, f"rising_diseases_{H}d_{stamp}.csv"), index=False)
forecasts.to_csv(os.path.join(OUT_DIR, f"forecasts_{H}d_{stamp}.csv"), index=False)

print(f"✅ Model completed ({H} days). Files updated in {OUT_DIR}")
time.sleep(0.5)
