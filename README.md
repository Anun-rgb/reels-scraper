# IG Reels Scraper (Personal / Educational)

Just a toy scraper I made for myself.

## What it does

- Opens Instagram Reels in a real browser
- Scrolls the feed
- If a caption matches my keywords, it hands the reel off to yt-dlp and downloads it

## Heads up

- This probably breaks Instagram's ToS. It's for my own learning.
- Respect copyright. Don't redistribute anything you download.
- Login is done manually in the opened browser.

## Setup

    pip install -r requirements.txt
    pip install yt-dlp

`yt-dlp` also needs to be on PATH.

## Run

    python reels_scraper.py

Log in once in the browser window, then let it scroll.
Ctrl+C to stop.

## Notes

- Paths and browser choices are hardcoded.
- No tests, no error handling worth mentioning. It's a sketch.
