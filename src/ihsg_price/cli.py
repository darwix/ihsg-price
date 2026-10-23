import argparse
from pathlib import Path

import yaml

from ihsg_price.metadata import record_scrape_status
from ihsg_price.scraper import fetch_daily, fetch_minutes
from ihsg_price.storage import upsert_bars, upsert_daily


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch and store IDX 1-minute bars")
    parser.add_argument("--config", type=Path, default=Path("config.yaml"))
    parser.add_argument("--minutes-output", type=Path, default=Path("data/minutes"))
    parser.add_argument("--daily-output", type=Path, default=Path("data/daily"))
    parser.add_argument("--metadata", type=Path, default=Path("data/metadata.json"))
    args = parser.parse_args()
    try:
        config = yaml.safe_load(args.config.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        parser.error(f"cannot read config {args.config}: {exc}")
    if not isinstance(config, dict):
        parser.error(f"config {args.config} must contain a YAML mapping")
    symbols = config.get("symbols")
    if not isinstance(symbols, list) or not symbols or any(not isinstance(symbol, str) or not symbol.strip() for symbol in symbols):
        parser.error("config must define a non-empty list of symbol strings")
    minute_bars = fetch_minutes(symbols)
    daily_bars = fetch_daily(symbols)
    minute_count = upsert_bars(args.minutes_output, minute_bars)
    daily_count = upsert_daily(args.daily_output, daily_bars)
    record_scrape_status(args.metadata, minute_bars, daily_bars)
    print(f"Stored {len(minute_bars)} minute and {len(daily_bars)} daily bars; touched partitions contain {minute_count} and {daily_count} rows.")


if __name__ == "__main__":
    main()
