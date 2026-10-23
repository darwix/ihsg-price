import json
from pathlib import Path

ROOT = Path.cwd()
START = "<!-- data-coverage:start -->"
END = "<!-- data-coverage:end -->"


def render_coverage(metadata_path: Path) -> str:
    if not metadata_path.exists():
        return "No collected minute data yet."
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    symbols = metadata.get("symbols", metadata)
    if not symbols:
        return "No collected minute data yet."
    rows = [
        f"Last successful scrape (UTC): {metadata.get('last_successful_run', 'unknown')}",
        "",
        "| Symbol | Latest minute date | Minute rows (run) | Latest daily date | Daily rows (run) |",
        "| --- | --- | ---: | --- | ---: |",
    ]
    for symbol, status in sorted(symbols.items()):
        if isinstance(status, list):
            status = {"minute_dates": status}
        minute_dates = status.get("minute_dates", [])
        daily_dates = status.get("daily_dates", [])
        rows.append(
            f"| {symbol} | {minute_dates[-1] if minute_dates else '-'} | "
            f"{status.get('minute_rows_last_run', '-')} | "
            f"{daily_dates[-1] if daily_dates else '-'} | {status.get('daily_rows_last_run', '-')} |"
        )
    return "\n".join(rows)


def update_readme(readme: Path, coverage: str) -> None:
    content = readme.read_text(encoding="utf-8")
    start = content.index(START) + len(START)
    end = content.index(END, start)
    readme.write_text(content[:start] + "\n" + coverage + "\n" + content[end:], encoding="utf-8")


def main() -> None:
    update_readme(ROOT / "README.md", render_coverage(ROOT / "data" / "metadata.json"))


if __name__ == "__main__":
    main()
