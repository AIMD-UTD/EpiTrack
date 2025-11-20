import os
import time
import subprocess
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from datetime import timedelta

# ------------------- PAGE CONFIG -------------------
st.set_page_config(page_title="Disease Mention Forecast Dashboard", layout="wide")

# ------------------- PATHS -------------------
OUT_DIR = os.environ.get(
    "OUT_DIR",
    "/Users/shauryadas/Desktop/All Files/EpiTrack/DiseaseForecast/outputs"
)
CLEAN_PATH = os.path.join(OUT_DIR, "clean_timeseries.csv")
SUMMARY_PATH = os.path.join(OUT_DIR, "rising_diseases.csv")
FORECAST_PATH = os.path.join(OUT_DIR, "forecasts.csv")

# ------------------- SIDEBAR -------------------
st.sidebar.header("⚙️ Forecast Settings")

forecast_days = st.sidebar.selectbox(
    "Forecast horizon (days):",
    [7, 14, 30, 60],
    index=0
)

recent_window = st.sidebar.selectbox(
    "Recent stats window:",
    [7, 14, 30, 60],
    index=0
)

# ------------------- HELPER FUNCTIONS -------------------
def wait_for_update(path, old_mtime, timeout=15):
    start = time.time()
    while time.time() - start < timeout:
        if os.path.exists(path) and os.path.getmtime(path) > old_mtime:
            return True
        time.sleep(0.3)
    return False

# ------------------- RUN MODEL -------------------
if st.sidebar.button("🔁 Update Forecast"):
    st.info(f"Running pipeline for next {forecast_days} days...")
    old_times = {
        p: os.path.getmtime(p) if os.path.exists(p) else 0
        for p in [CLEAN_PATH, SUMMARY_PATH, FORECAST_PATH]
    }
    try:
        subprocess.run(["python", "pipeline_train.py", "--days", str(forecast_days)], check=True)
        ok = any(wait_for_update(p, old_times[p]) for p in old_times)
        if ok:
            st.success(f"✅ Forecast updated for {forecast_days} days.")
            st.balloons()
        else:
            st.warning("Files didn't update. Try re-running or check console.")
    except Exception as e:
        st.error(f"Error running pipeline: {e}")
    st.cache_data.clear()
    st.rerun()

# ------------------- LOAD DATA -------------------
if not os.path.exists(CLEAN_PATH) or not os.path.exists(SUMMARY_PATH):
    st.warning("⚠️ Run the training script first to generate outputs.")
    st.stop()

st.cache_data.clear()
clean = pd.read_csv(CLEAN_PATH, parse_dates=["date"])
summary = pd.read_csv(SUMMARY_PATH)
forecasts = (
    pd.read_csv(FORECAST_PATH, parse_dates=["date"])
    if os.path.exists(FORECAST_PATH)
    else pd.DataFrame()
)

# ------------------- MAIN LAYOUT -------------------
st.title("🦠 Disease Mention Trends & Forecasts")

left, right = st.columns([2.5, 1])

# ------------------- RIGHT PANEL -------------------
with right:
    st.subheader(f"📈 Rising Diseases (Next {forecast_days} Days)")
    if "disease_name" in summary.columns:
        st.dataframe(summary)
    else:
        st.info("Summary file missing expected columns.")

# ------------------- LEFT PANEL -------------------
with left:
    diseases = sorted(clean["disease_name"].unique())
    pick = st.selectbox("Select a Disease", diseases)

    sub = clean[clean["disease_name"] == pick].sort_values("date")

    if len(sub) > 0:
        last_date = sub["date"].max()
        recent_start = last_date - timedelta(days=recent_window)
        recent_data = sub[sub["date"] >= recent_start]

        # ------------------- PLOT -------------------
        fig, ax = plt.subplots(figsize=(9, 4))
        ax.plot(sub["date"], sub["mention_count"], marker="o", linewidth=2, label="Actual Mentions")

        # Overlay forecast
        if not forecasts.empty:
            fsub = forecasts[forecasts["disease_name"] == pick].sort_values("date")
            if len(fsub):
                ax.plot(
                    fsub["date"],
                    fsub["forecast"],
                    linestyle="--",
                    linewidth=2,
                    color="tab:orange",
                    label=f"Forecast (+{forecast_days} days)"
                )

        ax.set_title(f"{pick} — Daily Mentions & Forecast")
        ax.set_xlabel("Date")
        ax.set_ylabel("Mentions")
        ax.legend()
        ax.grid(alpha=0.3)
        st.pyplot(fig)

        # ------------------- RECENT STATS -------------------
        st.markdown("### 📊 Recent Stats Summary")

        if len(recent_data) > 0:
            start = recent_data["date"].min().strftime("%Y-%m-%d")
            end = recent_data["date"].max().strftime("%Y-%m-%d")
            count = recent_data["date"].nunique()

            st.info(f"🗓 Date range: **{start} → {end}**  | 🧮 Days covered: **{count}**")

            st.dataframe(
                recent_data[["date", "mention_count", "sentiment_score", "source_reliability"]]
                .describe(include="all")
            )
        else:
            st.warning("Not enough data available for this window.")
    else:
        st.warning("No data found for this disease.")

# ------------------- TREND STATUS -------------------
st.markdown("---")
st.subheader("🚨 Trend Status Overview")

def trend_label(row):
    if row.get("is_rising"):
        return "🟢 Rising"
    elif row.get("pct_change_vs_recent", 0) < -0.1:
        return "🔴 Declining"
    else:
        return "🟡 Stable"

if "disease_name" in summary.columns:
    summary["Trend"] = summary.apply(trend_label, axis=1)
    st.dataframe(summary[["disease_name", "model_used", "pct_change_vs_recent", "Trend"]])
else:
    st.info("Trend columns missing in summary file.")
