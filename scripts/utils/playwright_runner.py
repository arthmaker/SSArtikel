from __future__ import annotations

import time
from typing import Any

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright

from .extractor import extract_html_code_blocks


def _first_visible_selector(page, selectors: list[str], timeout_ms: int):
    for selector in selectors:
        try:
            locator = page.locator(selector).first
            locator.wait_for(state="visible", timeout=timeout_ms)
            return locator
        except PlaywrightTimeoutError:
            continue
    raise PlaywrightTimeoutError(f"Tidak menemukan selector yang visible dari kandidat: {selectors}")


def _submit_prompt(page, prompt: str, timeout_ms: int) -> None:
    input_selectors = [
        "textarea[placeholder*='Message']",
        "textarea[data-id='root']",
        "#prompt-textarea",
        "div[contenteditable='true']",
    ]
    box = _first_visible_selector(page, input_selectors, timeout_ms)
    box.click()
    box.fill(prompt)
    box.press("Control+Enter")


def _wait_response_done(page, timeout_ms: int) -> None:
    stop_btn_selector = "button:has-text('Stop generating')"
    start = time.time()
    while True:
        elapsed_ms = int((time.time() - start) * 1000)
        if elapsed_ms > timeout_ms:
            raise TimeoutError("Timeout menunggu response ChatGPT selesai.")
        if page.locator(stop_btn_selector).count() == 0:
            break
        time.sleep(1.2)


def _extract_last_response_text(page) -> str:
    answer_selectors = [
        "article div.markdown",
        "div[data-message-author-role='assistant'] div.markdown",
        "div[data-testid='conversation-turn-assistant'] div.markdown",
    ]
    last_text = ""
    for sel in answer_selectors:
        locator = page.locator(sel)
        count = locator.count()
        if count > 0:
            last_text = locator.nth(count - 1).inner_text()
    return last_text


def process_pairs(config, prompts: list[str], logger, retry_failed: bool = False) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=config.chrome_user_data_dir,
            headless=False,
            executable_path=config.chrome_executable_path,
            args=[f"--profile-directory={config.chrome_profile}"],
            viewport={"width": 1400, "height": 950},
        )

        pages = []
        for idx in range(5):
            page = context.new_page()
            page.goto(config.chatgpt_url, wait_until="domcontentloaded", timeout=config.timeout_ms)
            pages.append(page)
            logger.info("Tab opened", {"tab_index": idx + 1})

        for idx, page in enumerate(pages, start=1):
            prompt = prompts[idx - 1]
            tab_result = {"tab_index": idx, "status": "error", "raw_last_response": "", "articles": [], "article_map": {}}

            try:
                _submit_prompt(page, prompt, config.timeout_ms)
                _wait_response_done(page, config.response_timeout_ms)
                raw = _extract_last_response_text(page)
                tab_result["raw_last_response"] = raw

                blocks = extract_html_code_blocks(raw)
                if len(blocks) < 2:
                    raise ValueError(f"Tab {idx} hanya menghasilkan {len(blocks)} code block HTML.")

                tab_result["articles"] = [blocks[0], blocks[1]]
                article_a = ((idx - 1) * 2) + 1
                article_b = article_a + 1
                tab_result["article_map"] = {article_a: blocks[0], article_b: blocks[1]}
                tab_result["status"] = "ok"
                logger.info("Tab success", {"tab_index": idx, "article_indexes": [article_a, article_b]})
            except Exception as exc:  # noqa: BLE001
                tab_result["error"] = f"Tab {idx} error: {exc}"
                logger.warning("Tab failed", {"tab_index": idx, "error": str(exc)})

                if retry_failed:
                    try:
                        logger.info("Retry tab", {"tab_index": idx})
                        _submit_prompt(page, prompt, config.timeout_ms)
                        _wait_response_done(page, config.response_timeout_ms)
                        raw = _extract_last_response_text(page)
                        tab_result["raw_last_response"] = raw
                        blocks = extract_html_code_blocks(raw)
                        if len(blocks) < 2:
                            raise ValueError("Retry tetap gagal menghasilkan 2 block HTML.")
                        article_a = ((idx - 1) * 2) + 1
                        article_b = article_a + 1
                        tab_result["articles"] = [blocks[0], blocks[1]]
                        tab_result["article_map"] = {article_a: blocks[0], article_b: blocks[1]}
                        tab_result["status"] = "ok"
                        tab_result.pop("error", None)
                    except Exception as retry_exc:  # noqa: BLE001
                        tab_result["error"] = f"Tab {idx} retry gagal: {retry_exc}"
                        logger.warning("Retry tab failed", {"tab_index": idx, "error": str(retry_exc)})

            results.append(tab_result)

        context.close()

    return results
