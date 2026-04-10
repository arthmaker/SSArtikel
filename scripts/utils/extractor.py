from __future__ import annotations

import re


def normalize_html_block(block: str) -> str:
    block = block.strip()
    block = re.sub(r"\n{3,}", "\n\n", block)
    return block


def extract_html_code_blocks(text: str) -> list[str]:
    """Ambil code block HTML dari text markdown ChatGPT."""
    pattern = re.compile(r"```(?:html|HTML)?\s*(.*?)```", re.DOTALL)
    matches = pattern.findall(text)
    cleaned = [normalize_html_block(match) for match in matches if match.strip()]
    return cleaned
