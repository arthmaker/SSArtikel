#!/usr/bin/env python3
"""Entry point automation ChatGPT multi-tab untuk generate 10 artikel."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from utils.config_loader import load_config
from utils.logger import RunLogger
from utils.prompt_builder import load_titles_payload, build_prompts
from utils.playwright_runner import process_pairs
from utils.merger import merge_articles


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--titles", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--retry-failed-tabs", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(__file__).resolve().parent.parent
    config = load_config(Path(args.config), root)
    titles_payload = load_titles_payload(Path(args.titles))

    logger = RunLogger(root, args.run_id)
    logger.info("Automation started", extra={"run_id": args.run_id})

    metadata = {
        "run_id": args.run_id,
        "started_at": logger.started_at,
        "status": "running",
        "titles": titles_payload["titles"],
        "pairs": titles_payload["pairs"],
        "errors": [],
        "paths": {},
    }
    logger.save_run_metadata(metadata)

    try:
        prompts = build_prompts(titles_payload["pairs"], config.prompt_template_path)
        tab_results = process_pairs(config, prompts, logger, retry_failed=args.retry_failed_tabs)

        articles = {}
        for tab_result in tab_results:
            tab_idx = tab_result["tab_index"]
            raw_path = logger.save_raw(tab_idx, tab_result.get("raw_last_response", ""))
            metadata["paths"].setdefault("raw", []).append(raw_path)

            if tab_result["status"] != "ok":
                metadata["errors"].append(tab_result["error"])
                continue

            parsed_paths = logger.save_parsed(tab_idx, tab_result["articles"])
            metadata["paths"].setdefault("parsed", []).extend(parsed_paths)
            articles.update(tab_result["article_map"])

        merged_txt, merged_html = merge_articles(articles, logger)
        metadata["paths"]["merged_txt"] = str(merged_txt.relative_to(root)).replace("\\", "/")
        metadata["paths"]["merged_html"] = str(merged_html.relative_to(root)).replace("\\", "/")

        metadata["status"] = "completed_with_errors" if metadata["errors"] else "completed"
        metadata["finished_at"] = logger.now_iso()
        logger.save_run_metadata(metadata)

        logger.info("Automation finished", extra={"status": metadata["status"], "errors": metadata["errors"]})
        return 0 if not metadata["errors"] else 2
    except Exception as exc:  # noqa: BLE001
        metadata["status"] = "failed"
        metadata["errors"].append(str(exc))
        metadata["finished_at"] = logger.now_iso()
        logger.save_run_metadata(metadata)
        logger.exception("Automation failed", exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())
