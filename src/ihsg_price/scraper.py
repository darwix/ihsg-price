from datetime import date, timedelta

import pandas as pd


def fetch_minutes(symbols: list[str], lookback_days: int = 7) -> pd.DataFrame:
    """Fetch recent minute bars; Yahoo limits 1-minute history to a short window."""
    end = date.today() + timedelta(days=1)
    start = end - timedelta(days=lookback_days)
    return _fetch(symbols, "1m", start=start.isoformat(), end=end.isoformat())


def fetch_daily(symbols: list[str], period: str = "1mo") -> pd.DataFrame:
    """Fetch recent daily OHLCV bars, including an overlap for recovery."""
    return _fetch(symbols, "1d", period=period)


def _fetch(symbols: list[str], interval: str, **date_range: str) -> pd.DataFrame:
    import yfinance as yf

    frames = []
    for symbol in symbols:
        frame = yf.download(
            symbol,
            interval=interval,
            progress=False,
            auto_adjust=False,
            multi_level_index=False,
            **date_range,
        )
        if frame.empty:
            raise RuntimeError(f"Yahoo Finance returned no {interval} bars for {symbol}")
        frame = frame.rename_axis("timestamp").reset_index()
        frame.columns = [str(column).lower().replace(" ", "_") for column in frame.columns]
        frame.insert(0, "symbol", symbol)
        frames.append(frame)
    if not frames:
        raise RuntimeError(f"Yahoo Finance returned no {interval} bars for configured symbols")
    return pd.concat(frames, ignore_index=True)
