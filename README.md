# ihsg-price

Fetch recent 1-minute OHLCV bars for symbols in `config.yaml` and upsert them into readable, date-partitioned CSV files in `data/minute-bars/`.

## Run locally

```sh
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install .
ihsg-price
```

Use `ihsg-price --config config.yaml --output data/minute-bars` to set paths. The scheduled GitHub Actions workflow runs on weekdays after the IDX session and commits only changed daily CSV files. Reruns replace matching `(symbol, timestamp)` rows.

Yahoo Finance limits 1-minute history to a short recent window. The scraper refetches seven days on every run and upserts by symbol and timestamp to repair recent missed runs. Yahoo's unofficial endpoint can change or throttle requests; this workflow is not a guaranteed data feed.

## Data coverage

The repository does not contain daily CSVs yet, so no collected date range is available. After the first successful run, inspect each symbol's earliest and latest stored minute with:

```sh
python -c "import glob,pandas as pd; d=pd.concat(pd.read_csv(p) for p in glob.glob('data/minute-bars/*.csv')); print(d.groupby('symbol')['timestamp'].agg(['min','max','count']))"
```

Files use the IDX trading date in Jakarta time, for example `data/minute-bars/2026-10-23.csv`. Timestamps inside each CSV are UTC. The seven-day fetch window is a recovery window, not a guarantee that Yahoo supplies every trading minute or seven full calendar days. The scraper fails if any configured symbol returns no bars, preventing a partial fetch from appearing successful.
