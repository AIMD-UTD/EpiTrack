import os
import time
import subprocess

import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
from streamlit_autorefresh import st_autorefresh
import pydeck as pdk

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(page_title="Disease Mention Trends", layout="wide")

OUT_DIR = os.environ.get("OUT_DIR", "./outputs")
CLEAN_PATH = os.path.join(OUT_DIR, "clean_timeseries.csv")
SUMMARY_PATH = os.path.join(OUT_DIR, "rising_diseases.csv")
FORECASTS_PATH = os.path.join(OUT_DIR, "forecasts.csv")
GEO_POINTS_PATH = os.path.join(OUT_DIR, "geo_points.csv")


# -------------------------------------------------
# NEW: FUNCTION TO CHECK GEO FILE TIMESTAMP
# -------------------------------------------------
def geo_last_modified() -> float:
    """Return last modified timestamp of geo_points.csv or 0 if missing."""
    if not os.path.exists(GEO_POINTS_PATH):
        return 0.0
    return os.path.getmtime(GEO_POINTS_PATH)


# -------------------------------------------------
# LOAD DATA HELPERS (NO CACHE)
# -------------------------------------------------
def load_base_data():
    clean = pd.read_csv(CLEAN_PATH, parse_dates=["date"])
    summary = pd.read_csv(SUMMARY_PATH)
    forecasts = pd.read_csv(FORECASTS_PATH, parse_dates=["date"])
    return clean, summary, forecasts


def load_geo_points():
    if not os.path.exists(GEO_POINTS_PATH):
        return None
    geo = pd.read_csv(GEO_POINTS_PATH, parse_dates=["date"])
    return geo


def compute_country_hotzones(geo: pd.DataFrame, country: str) -> pd.DataFrame:
    """
    For a given country, compute a simple 'hotzone' signal:
    last 7 days vs previous 7 days per disease.
    """
    if geo is None:
        return pd.DataFrame()

    dfc = geo.copy()
    dfc = dfc[dfc["country"] == country]
    if dfc.empty:
        return pd.DataFrame()

    ts = (
        dfc.groupby(["date", "disease_name"], as_index=False)["mention_count"]
        .sum()
        .sort_values("date")
    )

    if ts["date"].nunique() < 10:
        return pd.DataFrame()

    max_date = ts["date"].max()
    last7_start = max_date - pd.Timedelta(days=6)
    prev7_end = last7_start - pd.Timedelta(days=1)
    prev7_start = prev7_end - pd.Timedelta(days=6)

    results = []
    for dis, g in ts.groupby("disease_name"):
        g = g.sort_values("date")

        last7 = g[(g["date"] >= last7_start) & (g["date"] <= max_date)]
        prev7 = g[(g["date"] >= prev7_start) & (g["date"] <= prev7_end)]

        if last7.empty or prev7.empty:
            continue

        last_mean = last7["mention_count"].mean()
        prev_mean = prev7["mention_count"].mean()

        if prev_mean > 0:
            pct = (last_mean - prev_mean) / prev_mean
        else:
            pct = 1.0 if last_mean > 0 else 0.0

        results.append(
            {
                "disease_name": dis,
                "prev7_mean": round(prev_mean, 3),
                "last7_mean": round(last_mean, 3),
                "pct_change": round(pct, 3),
                "is_hot": bool(pct > 0.30),
            }
        )

    if not results:
        return pd.DataFrame()

    return pd.DataFrame(results).sort_values("pct_change", ascending=False)


# -------------------------------------------------
# SIDEBAR (Smart Refresh)
# -------------------------------------------------
st.sidebar.header("⚙️ Forecast & View Settings")

forecast_days = st.sidebar.selectbox(
    "Forecast horizon (model training):",
    [7, 14, 30, 60],
    index=0,
    help="After changing this, click 'Run / Update Forecast' to regenerate the model outputs.",
)

# -------------------------
# SMART REFRESH LOGIC (ONLY WHEN GEO CHANGES)
# -------------------------
current_geo_ts = geo_last_modified()
previous_geo_ts = st.session_state.get("geo_ts", None)

st.sidebar.caption("🔄 Auto-refresh triggers ONLY when geo_points.csv is updated.")

# If we've seen a previous timestamp and it changed, trigger a quick auto-refresh
if previous_geo_ts is not None and previous_geo_ts != current_geo_ts:
    st.sidebar.success("geo_points.csv updated — refreshing dashboard…")
    st.session_state["geo_ts"] = current_geo_ts
    # tiny interval → one quick re-run, then it stops
    st_autorefresh(interval=500, key="geo_refresh")
else:
    # First load or no change: just store current timestamp
    st.session_state["geo_ts"] = current_geo_ts
# -------------------------


geo_points = load_geo_points()
country_pick = "All Countries"
if geo_points is not None and not geo_points.empty:
    countries = sorted(
        [c for c in geo_points["country"].dropna().unique() if str(c).strip()]
    )
    if countries:
        country_pick = st.sidebar.selectbox(
            "Filter map & hotzones by country:",
            ["All Countries"] + countries,
        )

if st.sidebar.button("🔁 Run / Update Forecast"):
    start = time.time()
    with st.spinner(f"Running pipeline_train.py for next {forecast_days} days..."):
        try:
            subprocess.run(
                ["python3", "pipeline_train.py", "--days", str(forecast_days)],
                check=True,
            )
            # If you ALSO want geo_points refreshed from the same data each time,
            # you can uncomment this:
            # subprocess.run(["python3", "pipeline_geo.py"], check=True)
            time.sleep(1.0)
            st.success(f"✅ Model updated for {forecast_days}-day horizon.")
            st.balloons()
        except Exception as e:
            st.error(f"⚠️ Error running pipeline: {e}")
    st.sidebar.write(f"⏱️ Completed in {round(time.time() - start, 1)} sec.")
    st.rerun()


# -------------------------------------------------
# SAFETY CHECK
# -------------------------------------------------
missing = [
    p for p in [CLEAN_PATH, SUMMARY_PATH, FORECASTS_PATH] if not os.path.exists(p)
]
if missing:
    st.warning(
        "⚠️ Output files not found.\n\n"
        "From terminal in your venv:\n"
        "```bash\n"
        "python3 pipeline_train.py --days 7\n"
        "python3 pipeline_geo.py\n"
        "```\n"
        "Then refresh this app."
    )
    st.stop()


# -------------------------------------------------
# LOAD BASE DATA
# -------------------------------------------------
clean, summary, forecasts = load_base_data()

st.title("🦠 Disease Mention Trends & Forecasts (Global + Regional)")

if os.path.exists(SUMMARY_PATH):
    st.caption(f"🕒 Last model update: {time.ctime(os.path.getmtime(SUMMARY_PATH))}")


# -------------------------------------------------
# TOP SUMMARY PANEL
# -------------------------------------------------
top_left, top_right = st.columns([2.5, 1.5])

with top_left:
    st.subheader("📊 Dataset Overview (Global Time Series)")

    st.markdown(
        f"""
    **Date range:** {clean['date'].min().date()} → {clean['date'].max().date()}  
    **Unique days:** {clean['date'].nunique()}  
    **Diseases tracked:** {clean['disease_name'].nunique()}  
    **Total daily data points:** {len(clean)}  
    """
    )

    if "is_rising" in summary.columns:
        rising = (summary["is_rising"] == True).sum()
        st.markdown(f"**Currently flagged as rising (global):** {rising} diseases")

with top_right:
    st.subheader(f"📈 Rising Diseases (Global, next {forecast_days} days)")

    if not summary.empty:
        sorted_sum = summary.sort_values("pct_change_vs_recent", ascending=False)
        st.dataframe(sorted_sum, use_container_width=True)

        st.markdown("#### 🔺 Top Rising Diseases (% change vs recent)")
        top_n = sorted_sum.head(10).copy()
        if not top_n.empty:
            chart_df = top_n[["disease_name", "pct_change_vs_recent"]].copy()
            chart_df["pct_change_vs_recent"] *= 100.0
            chart_df.set_index("disease_name", inplace=True)
            st.bar_chart(chart_df)
        else:
            st.info("No rising diseases detected.")
    else:
        st.info("No diseases detected yet.")


# -------------------------------------------------
# MAIN VISUALIZATION
# -------------------------------------------------
st.markdown("---")
left, right = st.columns([2.5, 1.5])

with left:
    st.subheader("🔍 Global Disease Time Series + Forecast")

    diseases = sorted(clean["disease_name"].unique())
    pick = st.selectbox("Select a disease", diseases)

    hist = clean[clean["disease_name"] == pick].sort_values("date")
    fc = forecasts[forecasts["disease_name"] == pick].sort_values("date")

    fig, ax = plt.subplots(figsize=(9, 4))
    ax.plot(
        hist["date"],
        hist["mention_count"],
        marker="o",
        linestyle="-",
        label="Actual",
    )

    if not fc.empty:
        ax.plot(
            fc["date"],
            fc["forecast"],
            linestyle="--",
            label=f"{forecast_days}-day Forecast",
        )
        if {"lower_95", "upper_95"}.issubset(fc.columns):
            ax.fill_between(
                fc["date"],
                fc["lower_95"],
                fc["upper_95"],
                alpha=0.2,
                label="95% CI",
            )

    ax.set_title(f"{pick} — Global Mentions & {forecast_days}-day Forecast")
    ax.set_xlabel("Date")
    ax.set_ylabel("Mention count")
    ax.grid(True, alpha=0.3)
    ax.legend()
    st.pyplot(fig)

    st.markdown("### 📅 Recent Global Stats (Last 7 Days)")
    recent = hist.tail(7)
    if not recent.empty:
        stats = recent[["date", "mention_count"]].copy().set_index("date")
        st.write(stats.describe())
    else:
        st.info("Not enough data yet.")

with right:
    st.subheader("🧮 Forecast Summary (Global)")

    if pick in summary["disease_name"].values:
        row = summary[summary["disease_name"] == pick].iloc[0]
        pct = row["pct_change_vs_recent"] * 100.0

        st.markdown(
            f"""
        **Disease:** `{row['disease_name']}`  
        **Model used:** `{row['model_used']}`  

        **Recent mean:** `{row['recent_actual_mean']}`  
        **Forecast mean:** `{row['forecast_next_mean']}`  

        **95% CI:**  
        - Lower: `{row['forecast_lower_95']}`  
        - Upper: `{row['forecast_upper_95']}`  

        **% change:** `{pct:.1f}%`  
        **Status:** {"🟢 Rising" if row["is_rising"] else "🟡 Stable"}
        """
        )
    else:
        st.info("No summary available.")


# -------------------------------------------------
# MAP + HOTZONES
# -------------------------------------------------
st.markdown("---")
st.subheader("🌍 Global Map of Disease Mentions")

if geo_points is None or geo_points.empty or "lat" not in geo_points.columns:
    st.info("No geo_points data with coordinates yet.")
else:
    geo = geo_points.dropna(subset=["lat", "lon"])

    if country_pick != "All Countries":
        geo = geo[geo["country"] == country_pick]

    if geo.empty:
        st.info("No geo-tagged points for this selection.")
    else:
        layer = pdk.Layer(
            "HeatmapLayer",
            geo,
            get_position='[lon, lat]',
            get_weight="mention_count",
            radius_pixels=40,
        )

        view_state = pdk.ViewState(
            latitude=float(geo["lat"].mean()),
            longitude=float(geo["lon"].mean()),
            zoom=2,
        )

        deck = pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            tooltip={
                "text": "Disease: {disease_name}\nCountry: {country}\nMentions: {mention_count}"
            },
        )

        st.pydeck_chart(deck)

# Country hotzones
st.markdown("### 🔥 Country-Level Hotzones (Recent 7-Day Change)")

if geo_points is None or geo_points.empty:
    st.info("No geo_points data available yet.")
else:
    if country_pick == "All Countries":
        st.caption("Select a specific country in the sidebar.")
    else:
        hot = compute_country_hotzones(geo_points, country_pick)
        if hot.empty:
            st.info("Not enough data for hotzones.")
        else:
            st.dataframe(hot, use_container_width=True)


# -------------------------------------------------
# RAW TABLES
# -------------------------------------------------
st.markdown("---")
with st.expander("🔬 Raw time series, forecasts & geo points"):
    st.write("**Clean time series (first 20 rows):**")
    st.dataframe(clean.head(20))

    st.write("**Forecasts (first 20 rows):**")
    st.dataframe(forecasts.head(20))

    if geo_points is not None:
        st.write("**Geo points (first 20 rows):**")
        st.dataframe(geo_points.head(20))
    else:
        st.write("No geo_points.csv file yet.")
