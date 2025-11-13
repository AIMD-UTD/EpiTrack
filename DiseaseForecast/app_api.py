
import os
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime

OUT_DIR = os.environ.get("OUT_DIR", "/mnt/data/model_outputs")
CLEAN = os.path.join(OUT_DIR, "clean_timeseries.csv")
SUMMARY = os.path.join(OUT_DIR, "rising_diseases.csv")

app = FastAPI(title="Disease Mention Forecast API")

@app.get("/rising")
def rising():
    if not os.path.exists(SUMMARY):
        raise HTTPException(404, "Run pipeline_train.py first")
    df = pd.read_csv(SUMMARY)
    return JSONResponse(df.to_dict(orient="records"))

@app.get("/forecast/{disease}")
def forecast(disease: str):
    if not os.path.exists(CLEAN):
        raise HTTPException(404, "Run pipeline_train.py first")
    df = pd.read_csv(CLEAN, parse_dates=["date"])
    sub = df[df["disease_name"].str.lower()==disease.lower()].sort_values("date")
    if sub.empty:
        raise HTTPException(404, f"No data for disease '{disease}'")
    return JSONResponse(sub[["date","mention_count","sentiment_score","source_reliability"]].assign(date=sub["date"].dt.strftime("%Y-%m-%d")).to_dict(orient="records"))
