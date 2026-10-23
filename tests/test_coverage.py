import json

import pandas as pd

import ihsg_price.coverage as coverage
from ihsg_price.coverage import render_coverage, update_readme
from ihsg_price.metadata import record_scraped_dates


def test_record_scraped_dates_merges_unique_jakarta_dates(tmp_path):
    metadata_path = tmp_path / "data" / "metadata.json"
    bars = pd.DataFrame(
        [
            {"symbol": "BBCA.JK", "timestamp": "2026-10-21T02:00:00Z"},
            {"symbol": "BBCA.JK", "timestamp": "2026-10-21T03:00:00Z"},
        ]
    )

    result = record_scraped_dates(metadata_path, bars)

    assert result == {"BBCA.JK": ["2026-10-21"]}
    assert json.loads(metadata_path.read_text()) == result


def test_render_coverage_uses_metadata(tmp_path):
    metadata = tmp_path / "metadata.json"
    metadata.write_text(json.dumps({"BBCA.JK": ["2026-10-20", "2026-10-21"]}))

    result = render_coverage(metadata)

    assert "| BBCA.JK | 2026-10-20 | 2026-10-21 | 2 |" in result


def test_update_readme_replaces_only_coverage_block(tmp_path):
    readme = tmp_path / "README.md"
    readme.write_text(f"before\n<!-- data-coverage:start -->\nold\n<!-- data-coverage:end -->\nafter\n")

    update_readme(readme, "new")

    assert readme.read_text() == "before\n<!-- data-coverage:start -->\nnew\n<!-- data-coverage:end -->\nafter\n"


def test_main_uses_repository_working_directory(tmp_path, monkeypatch):
    (tmp_path / "data").mkdir()
    (tmp_path / "data" / "metadata.json").write_text(json.dumps({"BBCA.JK": ["2026-10-21"]}))
    readme = tmp_path / "README.md"
    readme.write_text("<!-- data-coverage:start -->\nold\n<!-- data-coverage:end -->\n")
    monkeypatch.setattr(coverage, "ROOT", tmp_path)

    coverage.main()

    assert "| BBCA.JK | 2026-10-21 | 2026-10-21 | 1 |" in readme.read_text()
