import os, re, time, argparse
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Try statsmodels; fall back gracefully
try:
    from statsmodels.tsa.holtwinters import ExponentialSmoothing
    HAS_SM = True
except Exception:
    HAS_SM = False

# ------------------ I/O ------------------
INPUT = os.environ.get("ARTICLES_CSV", "./articles.csv")
OUT_DIR = os.environ.get("OUT_DIR", "./outputs")
os.makedirs(OUT_DIR, exist_ok=True)

# ------------------ Read & normalize ------------------
df = pd.read_csv(INPUT)

DATE_CANDIDATES = [
    "published_at", "publishedAt", "published_date",
    "date", "created_at", "fetched_at"
]
date_col = next((c for c in DATE_CANDIDATES if c in df.columns), None)
if not date_col:
    raise ValueError(f"No date column found. Looked for {DATE_CANDIDATES}. Got {list(df.columns)}")

df[date_col] = pd.to_datetime(df[date_col], errors="coerce", utc=True)
df[date_col] = df[date_col].dt.tz_convert(None)
df = df.dropna(subset=[date_col])

# ensure text columns exist
for col in ["title", "description", "content", "source", "keywords"]:
    if col not in df.columns:
        df[col] = ""

df["full_text"] = (
    df["title"].astype(str) + " " +
    df["description"].astype(str) + " " +
    df["content"].astype(str)
)

print(f"✅ Using date column: {date_col} | rows: {len(df)}")

# ------------------ Disease patterns ------------------
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
# map for keyword fallback
KEYWORD_MAP = {n.lower(): n for n in set(PATTERNS.values())}

# ------------------ Extract mentions ------------------
rows = []
for i, r in df.iterrows():
    txt = str(r["full_text"])
    # regex hits
    hit = False
    for rgx, name in COMPILED:
        m = rgx.findall(txt)
        if m:
            rows.append({
                "article_id": i,
                "date": pd.to_datetime(r[date_col]).normalize(),
                "disease_name": name,
                "mention_count": len(m),
                "source": r["source"],
            })
            hit = True

    # fallback via keywords column (comma/pipe/space separated)
    if not hit and pd.notna(r["keywords"]) and str(r["keywords"]).strip():
        toks = re.split(r"[,\|;/\s]+", str(r["keywords"]).lower())
        seen = {}
        for t in toks:
            n = KEYWORD_MAP.get(t.strip())
            if n:
                seen[n] = seen.get(n, 0) + 1
        for name, cnt in seen.items():
            rows.append({
                "article_id": i,
                "date": pd.to_datetime(r[date_col]).normalize(),
                "disease_name": name,
                "mention_count": int(cnt),
                "source": r["source"],
            })

mentions = pd.DataFrame(rows)
if mentions.empty:
    print("⚠️ No disease mentions found from text/keywords.")
    # Write empty but well-formed files so the app stays consistent
    pd.DataFrame(columns=["date","disease_name","mention_count","sentiment_score","source_reliability"]).to_csv(
        os.path.join(OUT_DIR, "clean_timeseries.csv"), index=False)
    pd.DataFrame(columns=["disease_name","model_used","recent_actual_mean","forecast_next_mean",
                          "pct_change_vs_recent","is_rising"]).to_csv(
        os.path.join(OUT_DIR, "rising_diseases.csv"), index=False)
    pd.DataFrame(columns=["date","disease_name","forecast"]).to_csv(
        os.path.join(OUT_DIR, "forecasts.csv"), index=False)
    raise SystemExit(0)

# ------------------ Aggregate to daily ------------------
agg = mentions.groupby(["date","disease_name"], as_index=False)["mention_count"].sum()

def fill_daily(g: pd.DataFrame) -> pd.DataFrame:
    g = g.set_index("date").sort_index()
    rng = pd.date_range(g.index.min(), g.index.max(), freq="D")
    g = g.reindex(rng).fillna(0.0)
    g.index.name = "date"
    g["mention_count"] = g["mention_count"].astype(float)
    return g.reset_index()

filled = []
for dis, g in agg.groupby("disease_name"):
    d = fill_daily(g)
    d["disease_name"] = dis
    filled.append(d)
clean = pd.concat(filled, ignore_index=True)

# basic placeholders (can be replaced later)
clean["sentiment_score"] = 0.0
clean["source_reliability"] = 0.5

# ------------------ Forecasting ------------------
ap = argparse.ArgumentParser()
ap.add_argument("--days", type=int, default=7, help="Forecast horizon: 7/14/30/60")
args = ap.parse_args()
H = int(args.days)

results = []
forecast_frames = []

for dis, g in clean.groupby("disease_name"):
    g = g.sort_values("date")
    y = g["mention_count"].astype(float)
    # guard: if all zeros, keep zeros forward
    if (y > 0).sum() == 0:
        fc = pd.Series([0.0]*H, index=range(H))
        model_used = "Zero"
    else:
        # prefer Holt-Winters if enough history
        fc = None
        model_used = None
        if HAS_SM and len(y) >= 10:
            try:
                seasonal = 7 if len(y) >= 21 else None
                m = ExponentialSmoothing(
                    y, trend="add",
                    seasonal=("add" if seasonal else None),
                    seasonal_periods=seasonal,
                    initialization_method="estimated"
                ).fit(optimized=True, use_brute=True)
                fc = m.forecast(H)
                model_used = "Holt-Winters"
            except Exception:
                fc = None
        if fc is None:
            # fallback: 7-day moving average
            ma = y.rolling(7, min_periods=1).mean().iloc[-1]
            fc = pd.Series([float(ma)]*H)
            model_used = "MovingAverage"

    # clip negatives (sometimes HW can dip < 0)
    fc = np.clip(fc.values, 0.0, None)

    future_dates = pd.date_range(g["date"].max() + timedelta(days=1), periods=H, freq="D")
    forecast_frames.append(pd.DataFrame({
        "date": future_dates,
        "disease_name": dis,
        "forecast": fc
    }))

    recent_mean = float(y.tail(7).mean()) if len(y) else 0.0
    next_mean = float(np.mean(fc))
    pct = (next_mean - recent_mean)/recent_mean if recent_mean > 0 else (1.0 if next_mean > 0 else 0.0)
    results.append({
        "disease_name": dis,
        "model_used": model_used,
        "recent_actual_mean": round(recent_mean, 3),
        "forecast_next_mean": round(next_mean, 3),
        "pct_change_vs_recent": round(pct, 3),
        "is_rising": bool(pct > 0.15)
    })

# ------------------ Save outputs (consistent schema) ------------------
summary = pd.DataFrame(results).sort_values("pct_change_vs_recent", ascending=False)
forecasts = pd.concat(forecast_frames, ignore_index=True)

# Always write “latest” files the Streamlit app reads
clean[["date","disease_name","mention_count","sentiment_score","source_reliability"]].to_csv(
    os.path.join(OUT_DIR, "clean_timeseries.csv"), index=False)
summary[["disease_name","model_used","recent_actual_mean","forecast_next_mean",
         "pct_change_vs_recent","is_rising"]].to_csv(
    os.path.join(OUT_DIR, "rising_diseases.csv"), index=False)
forecasts[["date","disease_name","forecast"]].to_csv(
    os.path.join(OUT_DIR, "forecasts.csv"), index=False)

# Also save versioned snapshots
stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
clean.to_csv(os.path.join(OUT_DIR, f"clean_timeseries_{stamp}.csv"), index=False)
summary.to_csv(os.path.join(OUT_DIR, f"rising_diseases_{H}d_{stamp}.csv"), index=False)
forecasts.to_csv(os.path.join(OUT_DIR, f"forecasts_{H}d_{stamp}.csv"), index=False)

print(f"✅ Model completed ({H} days). Files updated in {OUT_DIR}")
# small delay so the app can see new mtime on slower disks
time.sleep(0.5)
