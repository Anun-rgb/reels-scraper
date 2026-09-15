"""
Instagram Reels scraper (educational sample).

Disclaimer:
  This may violate Instagram's Terms of Service.
  Use it only for your own learning / research, and respect copyright.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import browser_cookie3
from playwright.sync_api import sync_playwright

URL = "https://www.instagram.com/reels/"

# An empty list means "match everything"
KEYWORDS = []

OUTPUT_DIR = Path("videos")
OUTPUT_TEMPLATE = str(OUTPUT_DIR / "%(uploader)s__%(id)s.%(ext)s")
WAIT_MS = 500
BROWSER = "firefox"  


def load_cookies() -> list[dict]:
    """Borrow instagram.com cookies from Firefox."""
    cj = browser_cookie3.firefox(domain_name="instagram.com")
    return [
        {"name": c.name, "value": c.value,
         "domain": c.domain, "path": c.path or "/"}
        for c in cj
    ]


def walk(obj):
    """Recursively walk JSON and yield (code, caption)."""
    if isinstance(obj, dict):
        code = obj.get("code") or obj.get("shortcode")
        cap = obj.get("caption")
        if isinstance(cap, dict):
            cap = cap.get("text", "")
        if isinstance(code, str) and len(code) >= 8 and isinstance(cap, str):
            yield code, cap
        for v in obj.values():
            yield from walk(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from walk(v)


def download(code: str) -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    subprocess.run(
        [
            "yt-dlp",
            f"https://www.instagram.com/reel/{code}/",
            "--cookies-from-browser", BROWSER,
            "-o", OUTPUT_TEMPLATE,
            "--no-warnings",
        ],
        check=False,
    )


def main() -> int:
    seen: set[str] = set()
    hits = 0

    def on_response(resp):
        nonlocal hits
        if "/graphql/query" not in resp.url and "/api/v1/" not in resp.url:
            return
        try:
            data = resp.json()
        except Exception:
            return
        for code, caption in walk(data):
            if code in seen:
                continue
            seen.add(code)
            if KEYWORDS and not any(k in caption for k in KEYWORDS):
                continue
            hits += 1
            print(f"HIT [{hits}] {code}  |  {caption[:60]!r}")
            download(code)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        ctx = browser.new_context(locale="ja-JP")
        ctx.add_cookies(load_cookies())
        page = ctx.new_page()
        page.on("response", on_response)

        page.goto(URL, wait_until="networkidle", timeout=60_000)
        print("Started. Press Ctrl+C to stop.")

        try:
            while True:
                page.keyboard.press("ArrowDown")
                page.wait_for_timeout(WAIT_MS)
                print(f"  ↓  checked={len(seen)}  hits={hits}")
        except KeyboardInterrupt:
            print("\nStopped.")
        finally:
            browser.close()

    return 0


if __name__ == "__main__":
    sys.exit(main())