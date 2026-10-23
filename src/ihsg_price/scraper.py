from datetime import date, timedelta
from concurrent.futures import ThreadPoolExecutor

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

    if not symbols:
        raise RuntimeError(f"Yahoo Finance returned no {interval} bars for configured symbols")

    def fetch_one(symbol: str) -> pd.DataFrame:
        try:
            frame = yf.download(
                symbol,
                interval=interval,
                progress=False,
                auto_adjust=False,
                multi_level_index=False,
                **date_range,
            )
        except Exception as exc:
            raise RuntimeError(f"Yahoo Finance {interval} fetch failed for {symbol}: {exc}") from exc
        if frame is None or frame.empty:
            raise RuntimeError(f"Yahoo Finance returned no {interval} bars for {symbol}")
        try:
            frame = frame.rename_axis("timestamp").reset_index()
            frame.columns = [str(column).lower().replace(" ", "_") for column in frame.columns]
            frame.insert(0, "symbol", symbol)
            return frame
        except Exception as exc:
            raise RuntimeError(f"Invalid Yahoo Finance {interval} response for {symbol}: {exc}") from exc

    with ThreadPoolExecutor(max_workers=min(4, len(symbols))) as pool:
        frames = list(pool.map(fetch_one, symbols))
    return pd.concat(frames, ignore_index=True)
