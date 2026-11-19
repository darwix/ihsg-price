# ihsg-price

Fetch 1-minute and daily OHLCV bars for symbols in `config.yaml`. Minute bars go in date-partitioned files under `data/minutes/{symbol}/`; each ticker's daily bars go in one file, such as `data/daily/BBCA.JK.csv`.

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
Last successful scrape (UTC): 2026-11-19T19:07:56.118659+00:00

| Symbol | Latest minute date | Minute rows (run) | Latest daily date | Daily rows (run) |
| --- | --- | ---: | --- | ---: |
| ADRO.JK | 2026-11-19 | 1600 | 2026-11-19 | 24 |
| ANDI.JK | 2026-10-26 | 1124 | 2026-10-26 | 21 |
| ASII.JK | 2026-11-19 | 1601 | 2026-11-19 | 24 |
| BBCA.JK | 2026-11-19 | 1610 | 2026-11-19 | 24 |
| BBNI.JK | 2026-11-19 | 1597 | 2026-11-19 | 24 |
| BBRI.JK | 2026-11-19 | 1610 | 2026-11-19 | 24 |
| BMRI.JK | 2026-11-19 | 1611 | 2026-11-19 | 24 |
| BUMI.JK | 2026-10-26 | 1611 | 2026-10-26 | 21 |
| BUVA.JK | 2026-10-26 | 1601 | 2026-10-26 | 21 |
| EXCL.JK | 2026-11-19 | 1577 | 2026-11-19 | 24 |
| GGRM.JK | 2026-11-19 | 1283 | 2026-11-19 | 24 |
| HMSP.JK | 2026-11-19 | 877 | 2026-11-19 | 24 |
| ICBP.JK | 2026-11-19 | 1500 | 2026-11-19 | 24 |
| INCO.JK | 2026-11-19 | 1561 | 2026-11-19 | 24 |
| INDF.JK | 2026-11-19 | 1520 | 2026-11-19 | 24 |
| ISAT.JK | 2026-11-19 | 1587 | 2026-11-19 | 24 |
| JSMR.JK | 2026-11-19 | 1272 | 2026-11-19 | 24 |
| KLBF.JK | 2026-11-19 | 1575 | 2026-11-19 | 24 |
| PGAS.JK | 2026-11-19 | 1584 | 2026-11-19 | 24 |
| PTBA.JK | 2026-11-19 | 1582 | 2026-11-19 | 24 |
| SEMA.JK | 2026-10-26 | 1516 | 2026-10-26 | 21 |
| TINS.JK | 2026-11-19 | 1603 | 2026-11-19 | 24 |
| TLKM.JK | 2026-11-19 | 1604 | 2026-11-19 | 24 |
| UNVR.JK | 2026-11-19 | 1548 | 2026-11-19 | 24 |
<!-- data-coverage:end -->

Dates in metadata are Jakarta dates on which Yahoo returned bars. They record days with data, not proof that every trading minute was returned. Daily bars refetch the last month to repair recent missed runs. Minute files use one file per IDX trading date, for example `data/minutes/BBCA.JK/2026-10-23.csv`; daily files keep all dates in `data/daily/BBCA.JK.csv`. Timestamps inside each CSV are UTC. The seven-day minute fetch is a recovery window, not a guarantee that Yahoo supplies every trading minute or seven full calendar days. The scraper fails if any configured symbol returns no bars at either interval, preventing a partial run from appearing successful.
