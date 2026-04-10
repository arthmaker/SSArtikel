from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


class RunLogger:
    def __init__(self, root: Path, run_id: str) -> None:
        self.root = root
        self.run_id = run_id
        self.started_at = self.now_iso()
        self.log_path = root / "storage" / "logs" / f"{run_id}.log"
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def now_iso(self) -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    def _write(self, level: str, message: str, extra: dict | None = None) -> None:
        payload = {"time": self.now_iso(), "level": level, "message": message, "extra": extra or {}}
        with self.log_path.open("a", encoding="utf-8") as fp:
            fp.write(json.dumps(payload, ensure_ascii=False) + "\n")

    def info(self, message: str, extra: dict | None = None) -> None:
        self._write("INFO", message, extra)

    def warning(self, message: str, extra: dict | None = None) -> None:
        self._write("WARNING", message, extra)

    def exception(self, message: str, exc: Exception) -> None:
        self._write("ERROR", message, {"exception": str(exc)})

    def save_raw(self, tab_index: int, raw_text: str) -> str:
        path = self.root / "storage" / "raw" / f"{self.run_id}_tab{tab_index}.txt"
        path.write_text(raw_text, encoding="utf-8")
        return str(path.relative_to(self.root)).replace("\\", "/")

    def save_parsed(self, tab_index: int, articles: list[str]) -> list[str]:
        paths: list[str] = []
        for i, article in enumerate(articles, start=1):
            path = self.root / "storage" / "parsed" / f"{self.run_id}_tab{tab_index}_article{i}.html"
            path.write_text(article, encoding="utf-8")
            paths.append(str(path.relative_to(self.root)).replace("\\", "/"))
        return paths

    def save_run_metadata(self, metadata: dict) -> None:
        path = self.root / "storage" / "runs" / f"{self.run_id}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
