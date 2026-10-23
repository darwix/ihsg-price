from pathlib import Path

import pandas as pd


def upsert_minutes(path: Path, bars: pd.DataFrame) -> int:
    path.mkdir(parents=True, exist_ok=True)
    records = bars.copy()
    timestamps = pd.to_datetime(records["timestamp"], utc=True)
    records["timestamp"] = timestamps.astype(str)
    records["date"] = timestamps.dt.tz_convert("Asia/Jakarta").dt.strftime("%Y-%m-%d")
    total_rows = 0
    for trading_date, daily in records.groupby("date", sort=True):
        daily_path = path / f"{trading_date}.csv"
        daily = daily.drop(columns="date")
        if daily_path.exists():
            daily = pd.concat([pd.read_csv(daily_path), daily], ignore_index=True)
        keys = ["symbol", "timestamp"]
        values = [column for column in daily.columns if column not in keys]
        daily[values] = daily.groupby(keys, sort=False)[values].ffill()
        daily = daily.drop_duplicates(keys, keep="last").sort_values(keys)
        temporary_path = daily_path.with_suffix(".csv.tmp")
        daily.to_csv(temporary_path, index=False)
        temporary_path.replace(daily_path)
        total_rows += len(daily)
    return total_rows
