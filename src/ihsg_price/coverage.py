from pathlib import Path
import json

ROOT = Path.cwd()
START = "<!-- data-coverage:start -->"
END = "<!-- data-coverage:end -->"


def render_coverage(metadata_path: Path) -> str:
    if not metadata_path.exists():
        return "No collected minute data yet."
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    if not metadata:
        return "No collected minute data yet."
    rows = ["| Symbol | First scraped date | Latest scraped date | Dates scraped |", "| --- | --- | --- | ---: |"]
    for symbol, dates in sorted(metadata.items()):
        rows.append(f"| {symbol} | {dates[0]} | {dates[-1]} | {len(dates)} |")
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
