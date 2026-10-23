import json
from pathlib import Path

import pandas as pd


def record_scraped_dates(path: Path, bars: pd.DataFrame) -> dict[str, list[str]]:
    metadata = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    timestamps = pd.to_datetime(bars["timestamp"], utc=True)
    dates = timestamps.dt.tz_convert("Asia/Jakarta").dt.strftime("%Y-%m-%d")
    for symbol, symbol_dates in bars.assign(_date=dates).groupby("symbol")["_date"]:
        metadata[symbol] = sorted(set(metadata.get(symbol, [])) | set(symbol_dates))
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = path.with_suffix(".json.tmp")
    temporary_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    temporary_path.replace(path)
    return metadata
