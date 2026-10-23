import json

import pandas as pd

import ihsg_price.coverage as coverage
from ihsg_price.coverage import render_coverage, update_readme
from ihsg_price.metadata import record_scrape_status


def test_record_scrape_status_tracks_dates_run_time_and_rows(tmp_path):
    metadata_path = tmp_path / "data" / "metadata.json"
    minute_bars = pd.DataFrame(
        [
            {"symbol": "BBCA.JK", "timestamp": "2026-10-21T02:00:00Z"},
            {"symbol": "BBCA.JK", "timestamp": "2026-10-21T03:00:00Z"},
        ]
    )
    daily_bars = pd.DataFrame([{"symbol": "BBCA.JK", "timestamp": "2026-10-21T02:00:00Z"}])

    result = record_scrape_status(metadata_path, minute_bars, daily_bars, pd.Timestamp("2026-10-23T10:30:00Z").to_pydatetime())

    assert result["last_successful_run"] == "2026-10-23T10:30:00+00:00"
    assert result["symbols"]["BBCA.JK"] == {
        "minute_dates": ["2026-10-21"],
        "daily_dates": ["2026-10-21"],
        "minute_rows_last_run": 2,
        "daily_rows_last_run": 1,
    }
    assert json.loads(metadata_path.read_text()) == result


def test_record_scrape_status_keeps_tickers_not_fetched_this_run(tmp_path):
    metadata_path = tmp_path / "metadata.json"
    metadata_path.write_text(json.dumps({"symbols": {
        "KLBF.JK": {"minute_dates": ["2026-10-20"], "daily_dates": ["2026-10-20"]}
    }}))
    bars = pd.DataFrame([{"symbol": "BBCA.JK", "timestamp": "2026-10-21T02:00:00Z"}])

    result = record_scrape_status(metadata_path, bars, bars)

    assert result["symbols"]["KLBF.JK"]["minute_dates"] == ["2026-10-20"]


def test_record_scrape_status_reports_corrupt_metadata_path(tmp_path):
    metadata_path = tmp_path / "metadata.json"
    metadata_path.write_text("not-json")
    bars = pd.DataFrame([{"symbol": "BBCA.JK", "timestamp": "2026-10-21T02:00:00Z"}])

    import pytest
    with pytest.raises(RuntimeError, match="Could not read scrape metadata.*metadata.json") as error:
        record_scrape_status(metadata_path, bars, bars)
    assert isinstance(error.value.__cause__, json.JSONDecodeError)


def test_render_coverage_uses_metadata(tmp_path):
    metadata = tmp_path / "metadata.json"
    metadata.write_text(json.dumps({
        "last_successful_run": "2026-10-23T10:30:00+00:00",
        "symbols": {"BBCA.JK": {
            "minute_dates": ["2026-10-20", "2026-10-21"],
            "daily_dates": ["2026-10-20", "2026-10-21"],
            "minute_rows_last_run": 500,
            "daily_rows_last_run": 20,
        }},
    }))

    result = render_coverage(metadata)

    assert "Last successful scrape (UTC): 2026-10-23T10:30:00+00:00" in result
    assert "| BBCA.JK | 2026-10-21 | 500 | 2026-10-21 | 20 |" in result


def test_render_coverage_uses_ascii_dash_for_missing_values(tmp_path):
    metadata = tmp_path / "metadata.json"
    metadata.write_text(json.dumps({"symbols": {"BBCA.JK": {"minute_dates": ["2026-10-21"]}}}))

    result = render_coverage(metadata)

    assert "| BBCA.JK | 2026-10-21 | - | - | - |" in result


def test_update_readme_replaces_only_coverage_block(tmp_path):
    readme = tmp_path / "README.md"
    readme.write_text(f"before\n<!-- data-coverage:start -->\nold\n<!-- data-coverage:end -->\nafter\n")

    update_readme(readme, "new")

    assert readme.read_text() == "before\n<!-- data-coverage:start -->\nnew\n<!-- data-coverage:end -->\nafter\n"


def test_main_uses_repository_working_directory(tmp_path, monkeypatch):
    (tmp_path / "data").mkdir()
    (tmp_path / "data" / "metadata.json").write_text(json.dumps({"symbols": {"BBCA.JK": {
        "minute_dates": ["2026-10-21"], "daily_dates": ["2026-10-21"],
        "minute_rows_last_run": 1, "daily_rows_last_run": 1,
    }}}))
    readme = tmp_path / "README.md"
    readme.write_text("<!-- data-coverage:start -->\nold\n<!-- data-coverage:end -->\n")
    monkeypatch.setattr(coverage, "ROOT", tmp_path)

    coverage.main()

    assert "| BBCA.JK | 2026-10-21 | 1 | 2026-10-21 | 1 |" in readme.read_text()
