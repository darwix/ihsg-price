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
Last successful scrape (UTC): 2026-11-18T18:59:31.401338+00:00

| Symbol | Latest minute date | Minute rows (run) | Latest daily date | Daily rows (run) |
| --- | --- | ---: | --- | ---: |
| ADRO.JK | 2026-11-18 | 1601 | 2026-11-18 | 23 |
| ANDI.JK | 2026-10-26 | 1124 | 2026-10-26 | 21 |
| ASII.JK | 2026-11-18 | 1600 | 2026-11-18 | 23 |
| BBCA.JK | 2026-11-18 | 1610 | 2026-11-18 | 23 |
| BBNI.JK | 2026-11-18 | 1600 | 2026-11-18 | 23 |
| BBRI.JK | 2026-11-18 | 1610 | 2026-11-18 | 23 |
| BMRI.JK | 2026-11-18 | 1611 | 2026-11-18 | 23 |
| BUMI.JK | 2026-10-26 | 1611 | 2026-10-26 | 21 |
| BUVA.JK | 2026-10-26 | 1601 | 2026-10-26 | 21 |
| EXCL.JK | 2026-11-18 | 1576 | 2026-11-18 | 23 |
| GGRM.JK | 2026-11-18 | 1281 | 2026-11-18 | 23 |
| HMSP.JK | 2026-11-18 | 898 | 2026-11-18 | 23 |
| ICBP.JK | 2026-11-18 | 1522 | 2026-11-18 | 23 |
| INCO.JK | 2026-11-18 | 1530 | 2026-11-18 | 23 |
| INDF.JK | 2026-11-18 | 1537 | 2026-11-18 | 23 |
| ISAT.JK | 2026-11-18 | 1581 | 2026-11-18 | 23 |
| JSMR.JK | 2026-11-18 | 1282 | 2026-11-18 | 23 |
| KLBF.JK | 2026-11-18 | 1578 | 2026-11-18 | 23 |
| PGAS.JK | 2026-11-18 | 1578 | 2026-11-18 | 23 |
| PTBA.JK | 2026-11-18 | 1585 | 2026-11-18 | 23 |
| SEMA.JK | 2026-10-26 | 1516 | 2026-10-26 | 21 |
| TINS.JK | 2026-11-18 | 1602 | 2026-11-18 | 23 |
| TLKM.JK | 2026-11-18 | 1601 | 2026-11-18 | 23 |
| UNVR.JK | 2026-11-18 | 1548 | 2026-11-18 | 23 |
<!-- data-coverage:end -->

Dates in metadata are Jakarta dates on which Yahoo returned bars. They record days with data, not proof that every trading minute was returned. Daily bars refetch the last month to repair recent missed runs. Minute files use one file per IDX trading date, for example `data/minutes/BBCA.JK/2026-10-23.csv`; daily files keep all dates in `data/daily/BBCA.JK.csv`. Timestamps inside each CSV are UTC. The seven-day minute fetch is a recovery window, not a guarantee that Yahoo supplies every trading minute or seven full calendar days. The scraper fails if any configured symbol returns no bars at either interval, preventing a partial run from appearing successful.
