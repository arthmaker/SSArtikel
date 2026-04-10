from __future__ import annotations

import json
from pathlib import Path


def load_titles_payload(path: Path) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    titles = payload.get("titles", [])
    pairs = payload.get("pairs", [])
    if len(titles) != 10 or len(pairs) != 5:
        raise ValueError("Payload judul tidak valid. Harus berisi 10 judul dan 5 pasangan.")
    return payload


def build_prompts(pairs: list[list[str]], template_path: Path) -> list[str]:
    base_prompt = template_path.read_text(encoding="utf-8").strip()
    prompts: list[str] = []
    for pair in pairs:
        prompts.append(f"{pair[0]}\n{pair[1]}\n\n{base_prompt}\n")
    return prompts
