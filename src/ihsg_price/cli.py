import argparse
from pathlib import Path

import yaml

from ihsg_price.scraper import fetch_minutes
from ihsg_price.metadata import record_scraped_dates
from ihsg_price.storage import upsert_minutes


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch and store IDX 1-minute bars")
    parser.add_argument("--config", type=Path, default=Path("config.yaml"))
    parser.add_argument("--output", type=Path, default=Path("data/minutes"))
    parser.add_argument("--metadata", type=Path, default=Path("data/metadata.json"))
    args = parser.parse_args()
    config = yaml.safe_load(args.config.read_text(encoding="utf-8"))
    symbols = config.get("symbols", [])
    if not symbols:
        raise SystemExit("config.yaml must define a non-empty symbols list")
    bars = fetch_minutes(symbols)
    count = upsert_minutes(args.output, bars)
    record_scraped_dates(args.metadata, bars)
    print(f"Stored {len(bars)} fetched bars across daily CSVs; touched partitions contain {count} unique bars.")


if __name__ == "__main__":
    main()
