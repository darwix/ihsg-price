from pathlib import Path

import pandas as pd


def _upsert_file(path: Path, bars: pd.DataFrame) -> int:
    try:
        missing = {"symbol", "timestamp"} - set(bars.columns)
        if missing:
            raise ValueError(f"missing required columns: {', '.join(sorted(missing))}")
        if path.exists():
            bars = pd.concat([pd.read_csv(path), bars], ignore_index=True)
        keys = ["symbol", "timestamp"]
        values = [column for column in bars.columns if column not in keys]
        bars[values] = bars.groupby(keys, sort=False)[values].ffill()
        bars = bars.drop_duplicates(keys, keep="last").sort_values(keys)
        temporary_path = path.with_suffix(".csv.tmp")
        bars.to_csv(temporary_path, index=False)
        temporary_path.replace(path)
        return len(bars)
    except (OSError, ValueError, KeyError, pd.errors.ParserError, pd.errors.EmptyDataError) as exc:
        raise RuntimeError(f"Could not update CSV {path}: {exc}") from exc


def _safe_symbol(symbol: str) -> str:
    safe_symbol = "".join(char for char in str(symbol) if char.isalnum() or char in "._-")
    if safe_symbol in {"", ".", ".."}:
        raise ValueError(f"Invalid symbol for output path: {symbol!r}")
    return safe_symbol


def _validate_bars(path: Path, bars: pd.DataFrame) -> None:
    missing = {"symbol", "timestamp"} - set(bars.columns)
    if missing:
        raise ValueError(f"Invalid bars for {path}: missing required columns {', '.join(sorted(missing))}")


def upsert_bars(path: Path, bars: pd.DataFrame) -> int:
    _validate_bars(path, bars)
    path.mkdir(parents=True, exist_ok=True)
    records = bars.copy()
    try:
        timestamps = pd.to_datetime(records["timestamp"], utc=True)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid timestamps in bars for {path}: {exc}") from exc
    records["timestamp"] = timestamps.astype(str)
    records["date"] = timestamps.dt.tz_convert("Asia/Jakarta").dt.strftime("%Y-%m-%d")
    total_rows = 0
    for (symbol, trading_date), daily in records.groupby(["symbol", "date"], sort=True):
        symbol_dir = path / _safe_symbol(symbol)
        symbol_dir.mkdir(parents=True, exist_ok=True)
        daily_path = symbol_dir / f"{trading_date}.csv"
        total_rows += _upsert_file(daily_path, daily.drop(columns="date"))
    return total_rows


def upsert_daily(path: Path, bars: pd.DataFrame) -> int:
    _validate_bars(path, bars)
    path.mkdir(parents=True, exist_ok=True)
    records = bars.copy()
    try:
        records["timestamp"] = pd.to_datetime(records["timestamp"], utc=True).astype(str)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Invalid timestamps in bars for {path}: {exc}") from exc
    return sum(
        _upsert_file(path / f"{_safe_symbol(symbol)}.csv", symbol_bars)
        for symbol, symbol_bars in records.groupby("symbol", sort=True)
    )
