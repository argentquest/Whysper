#!/usr/bin/env python3
"""
Scrape all SVG icons from https://icons.terrastruct.com/ and name them
based on their captions.

Caption resolution priority per icon:
1) <figcaption> text if inside a <figure>
2) <img alt> text
3) Title-like attributes on parents: aria-label, data-title, title
4) Sibling elements with classes containing 'caption' or 'label'
5) Link text if the image is wrapped by <a>

Files are saved as: ./icons_by_caption/<caption-slug>.svg
If duplicates occur, numeric suffixes are added.

Includes retry-on-403 policy:
- On HTTP 403 (or request errors), waits 4 seconds and retries up to max_retries.
- Baseline politeness delay (REQUEST_DELAY_SEC) before every request.
"""

import os
import re
import time
import sys
import unicodedata
from typing import Optional, List, Tuple, Set
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

START_URL = "https://icons.terrastruct.com/"
OUTPUT_DIR = "icons_by_caption"

# Politeness & robustness
REQUEST_DELAY_SEC = 0.5  # baseline delay between requests
RETRY_WAIT_SEC = 4  # wait between retries on 403 or transient errors
TIMEOUT = 20  # request timeout in seconds
MAX_PAGES = 5000  # safety cap for crawling breadth
SAME_DOMAIN_ONLY = True
MAX_RETRIES = 3  # number of retries on 403 / request errors

# ---------- Utilities ----------


def slugify(text: str) -> str:
    """
    Convert caption text into a filesystem-safe slug.
    - normalize unicode to ASCII-like
    - lowercase
    - replace non-alphanumerics with hyphens
    - trim to a reasonable length
    """
    if not text:
        return "unnamed"
    text = unicodedata.normalize("NFKC", text).strip().lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = text.strip("-")
    return text[:120] or "unnamed"


def normalize_link(href: Optional[str], base_url: str) -> Optional[str]:
    """
    Make absolute URLs; ignore fragments and non-http schemes.
    """
    if not href:
        return None
    if href.startswith("#") or href.startswith("mailto:") or href.startswith("javascript:"):
        return None
    return urljoin(base_url, href)


def is_same_domain(url: str, root_netloc: str) -> bool:
    """
    Restrict crawling to the same host.
    """
    try:
        netloc = urlparse(url).netloc
        return (netloc == root_netloc) or (netloc == "")
    except Exception:
        return False


def fetch(url: str, session: requests.Session, max_retries: int = MAX_RETRIES) -> Optional[requests.Response]:
    """
    Polite GET with delay and retry handling.
    - Waits REQUEST_DELAY_SEC before each request (baseline politeness).
    - If we receive HTTP 403, wait RETRY_WAIT_SEC seconds and retry (up to max_retries).
    - Retries on transient RequestException similarly.
    """
    attempt = 0
    while attempt <= max_retries:
        # baseline delay for politeness
        time.sleep(REQUEST_DELAY_SEC)
        try:
            resp = session.get(url, timeout=TIMEOUT)
            # Success
            if 200 <= resp.status_code < 300:
                return resp

            # Handle 403 with retry
            if resp.status_code == 403 and attempt < max_retries:
                attempt += 1
                print(
                    f"[WARN] 403 for {url}. Waiting {RETRY_WAIT_SEC}s and retrying (attempt {attempt}/{max_retries})..."
                )
                time.sleep(RETRY_WAIT_SEC)
                continue

            # Other non-2xx responses: log and stop
            print(f"[WARN] HTTP {resp.status_code} for {url}.")
            return None

        except requests.RequestException as e:
            if attempt < max_retries:
                attempt += 1
                print(
                    f"[WARN] Request error for {url}: {e}. Waiting {RETRY_WAIT_SEC}s and retrying (attempt {attempt}/{max_retries})...")
                time.sleep(RETRY_WAIT_SEC)
                continue
            print(f"[ERR] Exhausted retries for {url}: {e}")
            return None

    return None


def ensure_unique_path(dirpath: str, basename: str, ext: str = ".svg") -> str:
    """
    Ensure we don’t overwrite existing files—append -1, -2, ... if needed.
    """
    target = os.path.join(dirpath, basename + ext)
    if not os.path.exists(target):
        return target
    i = 1
    while True:
        candidate = os.path.join(dirpath, f"{basename}-{i}{ext}")
        if not os.path.exists(candidate):
            return candidate
        i += 1


# ---------- Caption detection ----------


def find_caption_near_tag(tag) -> Optional[str]:
    """
    Try multiple strategies to find a human-readable caption near an icon element.
    1) <figure> -> <figcaption>
    2) <img alt>
    3) Title-like attributes along parents (aria-label, data-title, title)
    4) Siblings with classes including 'caption' or 'label'
    5) Link text if inside an <a>
    """
    # 1) Figure / figcaption
    figure = tag.find_parent("figure")
    if figure:
        fc = figure.find("figcaption")
        if fc:
            txt = fc.get_text(strip=True)
            if txt:
                return txt

    # 2) Alt on <img>
    if tag.name == "img":
        alt = tag.get("alt")
        if alt and alt.strip():
            return alt.strip()

    # 3) Title-like attributes along parents
    for parent in tag.parents:
        for attr in ("aria-label", "data-title", "title"):
            val = parent.get(attr)
            if val and val.strip():
                return val.strip()

    # 4) Siblings with caption-ish classes
    if tag.parent:
        for sib in tag.parent.find_all(["span", "div", "p"], limit=10):
            classes = " ".join(sib.get("class", []))
            if "caption" in classes or "label" in classes:
                txt = sib.get_text(strip=True)
                if txt:
                    return txt

    # 5) Fallback: link text if <a> wraps the tag
    anchor = tag.find_parent("a")
    if anchor:
        txt = anchor.get_text(strip=True)
        if txt:
            return txt

    return None


# ---------- Extract icon candidates from a page ----------


def extract_icon_candidates(soup: BeautifulSoup, base_url: str) -> List[Tuple[str, str]]:
    """
    Find likely icon elements and return list of (svg_url, caption_text).
    We look at:
      - ...svg|png (attempt png->svg switch)
      - ...svg (use link text as fallback caption)
    """
    candidates: Set[Tuple[str, str]] = set()

    # IMG tags: prefer svg; if png, try to resolve to svg by replacing extension
    for img in soup.find_all("img", src=True):
        src = normalize_link(img["src"], base_url)
        if not src:
            continue
        caption = find_caption_near_tag(img)

        if src.lower().endswith(".svg"):
            candidates.add((src, caption or ""))

        elif src.lower().endswith(".png"):
            # Try to find a parallel .svg for the same asset name
            svg_guess = re.sub(r"\.png(\?.*)?$", ".svg", src, flags=re.IGNORECASE)
            candidates.add((svg_guess, caption or ""))

    # Anchors directly linking to .svg (with their text as caption fallback)
    for a in soup.find_all("a", href=True):
        href = normalize_link(a["href"], base_url)
        if not href:
            continue
        if href.lower().endswith(".svg"):
            caption = find_caption_near_tag(a) or a.get_text(strip=True) or ""
            candidates.add((href, caption))

    # Inline #id typically points to sprites; ignoring here
    return list(candidates)


# ---------- Main crawl ----------


def crawl_and_download_svgs(start_url: str = START_URL, output_dir: str = OUTPUT_DIR):
    os.makedirs(output_dir, exist_ok=True)

    root = urlparse(start_url)
    root_netloc = root.netloc
    base_url = f"{root.scheme}://{root.netloc}/"

    session = requests.Session()
    # Use browser-like headers; include referer to reduce false 403s
    session.headers.update(
        {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://icons.terrastruct.com/",
        }
    )

    visited_pages: Set[str] = set()
    to_visit: List[str] = [start_url]
    downloaded = 0
    seen_svg_urls: Set[str] = set()

    while to_visit and len(visited_pages) < MAX_PAGES:
        current = to_visit.pop(0)
        current = current.split("#")[0]
        if current in visited_pages:
            continue
        if SAME_DOMAIN_ONLY and not is_same_domain(current, root_netloc):
            continue

        resp = fetch(current, session)
        if not resp:
            continue

        visited_pages.add(current)
        ctype = resp.headers.get("Content-Type", "").lower()

        # Parse pages only if HTML
        if "text/html" not in ctype:
            continue

        soup = BeautifulSoup(resp.text, "html.parser")

        # Enqueue internal links
        for a in soup.find_all("a", href=True):
            link = normalize_link(a["href"], base_url)
            if not link:
                continue
            if SAME_DOMAIN_ONLY and not is_same_domain(link, root_netloc):
                continue
            if link not in visited_pages and link not in to_visit:
                to_visit.append(link)

        # Collect icon candidates with captions
        icon_pairs = extract_icon_candidates(soup, base_url)

        # Download SVGs with caption-based names
        for svg_url, caption in icon_pairs:
            if not svg_url.lower().endswith(".svg"):
                continue
            if svg_url in seen_svg_urls:
                continue

            svg_resp = fetch(svg_url, session)
            if not svg_resp:
                continue

            svg_ctype = svg_resp.headers.get("Content-Type", "").lower()
            if ("image/svg" not in svg_ctype) and (not svg_url.lower().endswith(".svg")):
                # Skip non-SVG responses
                continue

            base_name = slugify(caption) if caption else slugify(os.path.basename(urlparse(svg_url).path))
            target_path = ensure_unique_path(output_dir, base_name, ext=".svg")

            try:
                with open(target_path, "wb") as f:
                    f.write(svg_resp.content)
                seen_svg_urls.add(svg_url)
                downloaded += 1
                print(f"[OK] {caption or '(no-caption)'} -> {target_path}")
            except OSError as e:
                print(f"[ERR] Failed to save {svg_url} as {target_path}: {e}")

    print(f"\n[DONE] Downloaded {downloaded} SVG icon(s) into '{output_dir}'.")
    print(f"Visited {len(visited_pages)} page(s).")


if __name__ == "__main__":
    start = START_URL if len(sys.argv) < 2 else sys.argv[1]
    outdir = OUTPUT_DIR if len(sys.argv) < 3 else sys.argv[2]
    crawl_and_download_svgs(start_url=start, output_dir=outdir)
