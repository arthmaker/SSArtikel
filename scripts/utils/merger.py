from __future__ import annotations

from pathlib import Path

MARKER_LINE = "_" * 106


def merge_articles(article_map: dict[int, str], logger) -> tuple[Path, Path]:
    """Merge 10 artikel sesuai marker wajib."""
    ordered = [article_map.get(i, f"<!-- MISSING ARTICLE {i} -->") for i in range(1, 11)]

    chunks = [MARKER_LINE, ""]
    for article in ordered:
        chunks.append("-###-")
        chunks.append(article)
        chunks.append("-$$$-")
    chunks.append("")
    chunks.append(MARKER_LINE)

    merged_text = "\n".join(chunks)

    txt_path = logger.root / "storage" / "output" / f"{logger.run_id}_merged.txt"
    html_path = logger.root / "storage" / "output" / f"{logger.run_id}_merged.html"
    txt_path.write_text(merged_text, encoding="utf-8")

    html_wrap = f"<pre>\n{merged_text}\n</pre>"
    html_path.write_text(html_wrap, encoding="utf-8")

    return txt_path, html_path
