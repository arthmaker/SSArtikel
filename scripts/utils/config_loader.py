from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class AppConfig:
    chatgpt_url: str
    chrome_executable_path: str
    chrome_user_data_dir: str
    chrome_profile: str
    prompt_template_path: Path
    timeout_ms: int
    response_timeout_ms: int
    output_root: Path


def load_config(config_path: Path, root: Path) -> AppConfig:
    raw = json.loads(config_path.read_text(encoding="utf-8"))

    return AppConfig(
        chatgpt_url=raw["chatgpt_url"],
        chrome_executable_path=raw["chrome_executable_path"],
        chrome_user_data_dir=raw["chrome_user_data_dir"],
        chrome_profile=raw["chrome_profile"],
        prompt_template_path=root / raw.get("prompt_template", "templates/base_prompt.txt"),
        timeout_ms=int(raw.get("timeout_ms", 30000)),
        response_timeout_ms=int(raw.get("response_timeout_ms", 300000)),
        output_root=root / raw.get("output_root", "storage"),
    )
