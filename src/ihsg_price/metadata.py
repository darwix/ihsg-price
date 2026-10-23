import json
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


def _dates(bars: pd.DataFrame) -> dict[str, list[str]]:
    timestamps = pd.to_datetime(bars["timestamp"], utc=True)
    dated_bars = bars.assign(_date=timestamps.dt.tz_convert("Asia/Jakarta").dt.strftime("%Y-%m-%d"))
    return {symbol: sorted(set(dates)) for symbol, dates in dated_bars.groupby("symbol")["_date"]}


def record_scrape_status(
    path: Path,
    minute_bars: pd.DataFrame,
    daily_bars: pd.DataFrame,
    now: datetime | None = None,
) -> dict:
    old = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    old_symbols = old.get("symbols", old)
    symbols = old_symbols.copy()
    minute_dates = _dates(minute_bars)
    daily_dates = _dates(daily_bars)
    for symbol in set(minute_bars["symbol"]) | set(daily_bars["symbol"]):
        previous = symbols.get(symbol, {})
        if isinstance(previous, list):
            previous = {"minute_dates": previous}
        symbols[symbol] = {
            "minute_dates": sorted(set(previous.get("minute_dates", [])) | set(minute_dates.get(symbol, []))),
            "daily_dates": sorted(set(previous.get("daily_dates", [])) | set(daily_dates.get(symbol, []))),
            "minute_rows_last_run": int((minute_bars["symbol"] == symbol).sum()),
            "daily_rows_last_run": int((daily_bars["symbol"] == symbol).sum()),
        }
    metadata = {
        "last_successful_run": (now or datetime.now(timezone.utc)).astimezone(timezone.utc).isoformat(),
        "symbols": symbols,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = path.with_suffix(".json.tmp")
    temporary_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    temporary_path.replace(path)
    return metadata
