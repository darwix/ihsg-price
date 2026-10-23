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
    try:
        old = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Could not read scrape metadata {path}: {exc}") from exc
    if not isinstance(old, dict):
        raise ValueError(f"Invalid scrape metadata {path}: expected a JSON object")
    old_symbols = old.get("symbols", old)
    if not isinstance(old_symbols, dict):
        raise ValueError(f"Invalid scrape metadata {path}: symbols must be a JSON object")
    symbols = old_symbols.copy()
    try:
        minute_dates = _dates(minute_bars)
        daily_dates = _dates(daily_bars)
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"Cannot record scrape dates in {path}: {exc}") from exc
    for symbol in set(minute_bars["symbol"]) | set(daily_bars["symbol"]):
        previous = symbols.get(symbol, {})
        if isinstance(previous, list):
            previous = {"minute_dates": previous}
        if not isinstance(previous, dict):
            raise ValueError(f"Invalid scrape metadata for {symbol} in {path}: expected an object")
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
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = path.with_suffix(".json.tmp")
        temporary_path.write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
        temporary_path.replace(path)
    except OSError as exc:
        raise RuntimeError(f"Could not write scrape metadata {path}: {exc}") from exc
    return metadata
