#!/usr/bin/env python3
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional

ROOT = Path(__file__).resolve().parent.parent

CASE_DIR = ROOT / "notes" / "case-studies"
TIL_DIR = ROOT / "til"

START_MARK = "<!-- START:INDEX -->"
END_MARK = "<!-- END:INDEX -->"


@dataclass
class Entry:
    title: str
    date: datetime
    relpath: str


def parse_frontmatter(md: str) -> dict:
    """Parse very simple YAML-like front matter; fallback to first H1 if needed."""
    fm = {}
    if md.lstrip().startswith("---"):
        # find the closing '---' after the first line
        parts = md.lstrip().split("\n")
        # find index of next '---'
        try:
            end_idx = next(
                i
                for i, line in enumerate(parts[1:], start=1)
                if line.strip() == "---"
            )
            block = "\n".join(parts[1:end_idx])
            for line in block.splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    fm[k.strip().lower()] = v.strip().strip('"').strip("'")
        except StopIteration:
            pass
    # fallback title from first heading
    if "title" not in fm:
        m = re.search(r"^\s*#\s+(.+)$", md, flags=re.MULTILINE)
        if m:
            fm["title"] = m.group(1).strip()
    return fm


def parse_date_from_any(fm: dict, path: Path) -> Optional[datetime]:
    # from front matter
    for key in ("date", "Date"):
        if key in fm:
            try:
                return datetime.fromisoformat(fm[key].strip())
            except Exception:
                pass
    # from filename
    m = re.search(r"(\d{4}-\d{2}-\d{2})", path.name)
    if m:
        try:
            return datetime.fromisoformat(m.group(1))
        except Exception:
            pass
    return None


def collect_entries() -> tuple[List[Entry], List[Entry]]:
    cases: List[Entry] = []
    tils: List[Entry] = []

    if CASE_DIR.exists():
        for p in CASE_DIR.glob("*.md"):
            md = p.read_text(encoding="utf-8", errors="ignore")
            fm = parse_frontmatter(md)
            date = parse_date_from_any(fm, p) or datetime.min
            title = fm.get("title", p.stem.replace("-", " ").title())
            cases.append(
                Entry(
                    title=title,
                    date=date,
                    relpath=str(p.relative_to(ROOT)).replace("\\", "/"),
                )
            )

    if TIL_DIR.exists():
        for p in TIL_DIR.glob("**/*.md"):
            md = p.read_text(encoding="utf-8", errors="ignore")
            fm = parse_frontmatter(md)
            date = parse_date_from_any(fm, p) or datetime.min
            title = fm.get("title", p.stem.replace("-", " ").title())
            tils.append(
                Entry(
                    title=title,
                    date=date,
                    relpath=str(p.relative_to(ROOT)).replace("\\", "/"),
                )
            )

    # sort desc by date
    cases.sort(key=lambda e: e.date, reverse=True)
    tils.sort(key=lambda e: e.date, reverse=True)
    return cases, tils


def render_index(
    cases: List[Entry], tils: List[Entry], til_limit: int = 20
) -> str:
    lines = []
    lines.append("## Case studies")
    if cases:
        for e in cases:
            lines.append(f"- {e.date.date()} — [{e.title}]({e.relpath})")
    else:
        lines.append("- _(none yet)_")

    lines.append("")
    lines.append("## TIL: Latest Lessons")
    for e in tils[:til_limit]:
        lines.append(f"- {e.date.date()} — [{e.title}]({e.relpath})")

    lines.append("")
    lines.append(
        f"_Last updated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}_"
    )
    return "\n".join(lines)


def update_readme(readme_path: Path, new_block: str) -> bool:
    if not readme_path.exists():
        # create a minimal README with markers
        content = f"# TIL & Notes\n\n{START_MARK}\n{new_block}\n{END_MARK}\n"
        readme_path.write_text(content, encoding="utf-8")
        return True

    content = readme_path.read_text(encoding="utf-8")
    if START_MARK in content and END_MARK in content:
        pattern = re.compile(
            re.escape(START_MARK) + r".*?" + re.escape(END_MARK), re.DOTALL
        )
        new_content = pattern.sub(
            f"{START_MARK}\n{new_block}\n{END_MARK}", content
        )
    else:
        # append markers at the end
        new_content = (
            content.rstrip() + f"\n\n{START_MARK}\n{new_block}\n{END_MARK}\n"
        )

    changed = new_content != content
    if changed:
        readme_path.write_text(new_content, encoding="utf-8")
    return changed


def main() -> int:
    cases, tils = collect_entries()
    block = render_index(cases, tils)
    changed = update_readme(ROOT / "README.md", block)
    print("README updated." if changed else "No changes needed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
