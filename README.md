# ihsg-price

Fetch 1-minute and daily OHLCV bars for symbols in `config.yaml` and upsert them into readable, date-partitioned CSV files under `data/minutes/{symbol}/` and `data/daily/{symbol}/`.

## Run locally

```sh
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install .
ihsg-price
```

Use `ihsg-price --config config.yaml --minutes-output data/minutes --daily-output data/daily --metadata data/metadata.json` to set paths. The scraper records successful run time, per-ticker date coverage, and fetched row counts in `data/metadata.json`. GitHub Actions refreshes the coverage table below after each successful run and commits it with changed CSV files. Reruns replace matching `(symbol, timestamp)` rows.

Yahoo Finance limits 1-minute history to a short recent window. The scraper refetches seven days on every run and upserts by symbol and timestamp to repair recent missed runs. Yahoo's unofficial endpoint can change or throttle requests; this workflow is not a guaranteed data feed.

## Data coverage

<!-- data-coverage:start -->
| Symbol | First scraped date | Latest scraped date | Dates scraped |
| --- | --- | --- | ---: |
| BBCA.JK | 2026-10-19 | 2026-10-23 | 5 |
| KLBF.JK | 2026-10-19 | 2026-10-23 | 5 |
<!-- data-coverage:end -->

Dates in metadata are Jakarta dates on which Yahoo returned bars. They record days with data, not proof that every trading minute was returned. Daily bars refetch the last month to repair recent missed runs. Each symbol has its own directory, with one file per IDX trading date, for example `data/minutes/BBCA.JK/2026-10-23.csv` and `data/daily/BBCA.JK/2026-10-23.csv`; timestamps inside each CSV are UTC. The seven-day minute fetch is a recovery window, not a guarantee that Yahoo supplies every trading minute or seven full calendar days. The scraper fails if any configured symbol returns no bars at either interval, preventing a partial run from appearing successful.
