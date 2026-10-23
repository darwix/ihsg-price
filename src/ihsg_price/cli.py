import argparse
from pathlib import Path

import yaml

from ihsg_price.metadata import record_scrape_status
from ihsg_price.scraper import fetch_daily, fetch_minutes
from ihsg_price.storage import upsert_bars


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch and store IDX 1-minute bars")
    parser.add_argument("--config", type=Path, default=Path("config.yaml"))
    parser.add_argument("--minutes-output", type=Path, default=Path("data/minutes"))
    parser.add_argument("--daily-output", type=Path, default=Path("data/daily"))
    parser.add_argument("--metadata", type=Path, default=Path("data/metadata.json"))
    args = parser.parse_args()
    config = yaml.safe_load(args.config.read_text(encoding="utf-8"))
    symbols = config.get("symbols", [])
    if not symbols:
        raise SystemExit("config.yaml must define a non-empty symbols list")
    minute_bars = fetch_minutes(symbols)
    daily_bars = fetch_daily(symbols)
    minute_count = upsert_bars(args.minutes_output, minute_bars)
    daily_count = upsert_bars(args.daily_output, daily_bars)
    record_scrape_status(args.metadata, minute_bars, daily_bars)
    print(f"Stored {len(minute_bars)} minute and {len(daily_bars)} daily bars; touched partitions contain {minute_count} and {daily_count} rows.")


if __name__ == "__main__":
    main()
