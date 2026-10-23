from datetime import date, timedelta

import pandas as pd


def fetch_minutes(symbols: list[str], lookback_days: int = 7) -> pd.DataFrame:
    """Fetch recent minute bars; Yahoo limits 1-minute history to a short window."""
    import yfinance as yf

    end = date.today() + timedelta(days=1)
    start = end - timedelta(days=lookback_days)
    frames = []
    for symbol in symbols:
        frame = yf.download(
            symbol,
            start=start.isoformat(),
            end=end.isoformat(),
            interval="1m",
            progress=False,
            auto_adjust=False,
            multi_level_index=False,
        )
        if frame.empty:
            raise RuntimeError(f"Yahoo Finance returned no minute bars for {symbol}")
        frame = frame.rename_axis("timestamp").reset_index()
        frame.columns = [str(column).lower().replace(" ", "_") for column in frame.columns]
        frame.insert(0, "symbol", symbol)
        frames.append(frame)
    if not frames:
        raise RuntimeError("Yahoo Finance returned no minute bars for configured symbols")
    return pd.concat(frames, ignore_index=True)
