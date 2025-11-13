
# Disease Mention Forecast – Starter Kit

This folder has everything to run the pipeline, train models, and serve results.

## Files
- `pipeline_train.py` — ETL + modeling (builds daily time series and forecasts)
- `app_api.py` — FastAPI app that serves rising diseases and per-disease series
- `streamlit_app.py` — simple dashboard
- `requirements.txt` — Python dependencies

## Quickstart (local)
1) Put your CSV at `/mnt/data/articles.csv` (or set `ARTICLES_CSV=/path/to/your.csv`).
2) (Optional) Create a virtualenv and install requirements:
   ```bash
   pip install -r requirements.txt
   ```
3) Run the pipeline (writes outputs to `/mnt/data/model_outputs` by default):
   ```bash
   python pipeline_train.py
   ```
4) Open the dashboard:
   ```bash
   streamlit run streamlit_app.py
   ```
5) Or run the API:
   ```bash
   uvicorn app_api:app --reload --host 0.0.0.0 --port 8000
   ```

## Environment variables
- `ARTICLES_CSV` — path to your raw articles file.
- `OUT_DIR` — where to write outputs (CSV + plots). Default: `/mnt/data/model_outputs`
- `H` — forecast horizon in days (default 14)

## Data fields that help the model
- `published_date` — time axis
- `title`, `content` — used to extract disease mentions & sentiment
- `source` — used for a basic reliability score
- Optional improvements: `region`, structured `sentiment`, canonical `disease_id`

## How to expand
- Replace regex with spaCy NER for `disease_name`
- Use SARIMAX or Prophet with additional regressors (region, sentiment)
- Append daily with a scheduler (CRON/GitHub Actions) and refresh the dashboard/API
