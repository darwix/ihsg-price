import pandas as pd

from ihsg_price.storage import upsert_bars


def test_upsert_replaces_same_symbol_timestamp(tmp_path):
    path = tmp_path / "minutes"
    bars = pd.DataFrame(
        [
            {"symbol": "BBCA.JK", "timestamp": "2026-10-21T02:00:00Z", "open": 100.0, "high": 101.0, "low": 99.0, "close": 100.5, "volume": 10},
            {"symbol": "BBCA.JK", "timestamp": "2026-10-21T02:00:00Z", "open": 100.0, "high": 102.0, "low": 99.0, "close": 101.5, "volume": 12},
        ]
    )

    assert upsert_bars(path, bars) == 1
    stored = pd.read_csv(path / "BBCA.JK" / "2026-10-21.csv")
    assert len(stored) == 1
    assert stored.loc[0, "close"] == 101.5
    assert stored.loc[0, "volume"] == 12


def test_upsert_keeps_other_dates_and_old_values_when_update_is_blank(tmp_path):
    path = tmp_path / "minutes"
    original = pd.DataFrame(
        [
            {"symbol": "BBCA.JK", "timestamp": "2026-10-21T02:00:00Z", "close": 100.5, "volume": 10},
            {"symbol": "BBCA.JK", "timestamp": "2026-10-22T02:00:00Z", "close": 101.5, "volume": 12},
        ]
    )
    update = pd.DataFrame(
        [{"symbol": "BBCA.JK", "timestamp": "2026-10-21T02:00:00Z", "close": float("nan"), "volume": 11}]
    )

    upsert_bars(path, original)
    upsert_bars(path, update)

    first_day = pd.read_csv(path / "BBCA.JK" / "2026-10-21.csv")
    second_day = pd.read_csv(path / "BBCA.JK" / "2026-10-22.csv")
    assert first_day.loc[0, "close"] == 100.5
    assert first_day.loc[0, "volume"] == 11
    assert len(second_day) == 1


def test_fetch_fails_if_any_symbol_has_no_bars(monkeypatch):
    import sys
    from types import SimpleNamespace

    from ihsg_price.scraper import fetch_minutes

    calls = iter([pd.DataFrame({"Close": [100]}), pd.DataFrame()])
    monkeypatch.setitem(sys.modules, "yfinance", SimpleNamespace(download=lambda *args, **kwargs: next(calls)))

    import pytest

    with pytest.raises(RuntimeError, match="KLBF.JK"):
        fetch_minutes(["BBCA.JK", "KLBF.JK"])


def test_daily_fetch_requests_daily_bars(monkeypatch):
    import sys
    from types import SimpleNamespace

    from ihsg_price.scraper import fetch_daily

    calls = []
    def download(*args, **kwargs):
        calls.append((args, kwargs))
        return pd.DataFrame({"Close": [100]}, index=pd.DatetimeIndex(["2026-10-21"], name="Date"))

    monkeypatch.setitem(sys.modules, "yfinance", SimpleNamespace(download=download))

    result = fetch_daily(["BBCA.JK"])

    assert len(result) == 1
    assert calls[0][1]["interval"] == "1d"
    assert calls[0][1]["period"] == "1mo"
