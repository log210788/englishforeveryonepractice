#!/usr/bin/env python3
"""
download_dk_audio.py

Extracts all direct .mp3 audio links from the DK web player for Level 1 Beginner Practice Book
(https://apps.dk.com/efe/en/audio/level-one-beginner-practice/1-1) and downloads/saves them
systematically into `assets/audio/`.

Libraries used: requests, beautifulsoup4 (bs4), playwright, tqdm.
"""

import json
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm


SOURCE_URL = "https://apps.dk.com/efe/en/audio/level-one-beginner-practice/1-1"
CDN_BASE_URL = "https://d2hmvvndovjpc2.cloudfront.net/efe"
OUTPUT_DIR = Path("assets/audio")
METADATA_CACHE = Path("assets/dk_audio_metadata.json")
LOCAL_AUDIO_DIR = Path("audio")
MAX_WORKERS = 16


def fetch_html_with_requests(url: str) -> Optional[str]:
    """Fetches HTML content from URL using requests."""
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"⚠️  requests fetch failed: {e}")
        return None


def fetch_html_with_playwright(url: str) -> Optional[str]:
    """Fallback: Fetches JS-rendered HTML content using Playwright headless browser."""
    try:
        from playwright.sync_api import sync_playwright

        print("🎭 Attempting fallback fetch via Playwright headless browser...")
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, wait_until="networkidle", timeout=30000)
            content = page.content()
            browser.close()
            return content
    except Exception as e:
        print(f"❌ Playwright fetch failed: {e}")
        return None


def extract_next_data_json(html_content: str) -> Optional[Dict[str, Any]]:
    """Parses HTML using BeautifulSoup and extracts __NEXT_DATA__ JSON object."""
    try:
        soup = BeautifulSoup(html_content, "html.parser")
        script_tag = soup.find("script", id="__NEXT_DATA__")
        if script_tag and script_tag.string:
            return json.loads(script_tag.string)
    except Exception as e:
        print(f"⚠️ BeautifulSoup parsing error: {e}")
    return None


def parse_audio_metadata(next_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Extracts all audio track records for Level 1 Beginner Practice Book."""
    props = next_data.get("props", {}).get("pageProps", {})
    json_data = props.get("jsonData") or {}
    refs = json_data.get("ref", []) if isinstance(json_data, dict) else []

    pb_ref = None
    for r in refs:
        pid = r.get("pid")
        route = r.get("route")
        title = r.get("title", "")
        if pid == "efe_pb_en_01" or route == "level-one-beginner-practice" or "Practice Book" in title:
            pb_ref = r
            break

    if not pb_ref:
        raise ValueError("Level 1 Beginner Practice Book dataset not found in page payload.")

    documents = pb_ref.get("documents", [])
    extracted_tracks: List[Dict[str, Any]] = []
    global_idx = 1

    for doc in documents:
        unit_index = doc.get("dataindex")  # Unit number e.g. 1, 2, ..., 48
        ddata = doc.get("data", [])
        for u_obj in ddata:
            unit_title = u_obj.get("datatitle", f"Unit {unit_index}")
            exercises = u_obj.get("exercises", [])

            for ex in exercises:
                e_index = str(ex.get("eIndex", "1"))
                audios = ex.get("audios", [])

                for au in audios:
                    number = au.get("number")
                    filename = au.get("filename")  # e.g., b1_p_1_1_eg_a_uk.mp3
                    filepath = au.get("filepath")  # e.g., /audio/b1/p/1/

                    if not filename or not filepath:
                        continue

                    # Direct remote CDN URL
                    remote_url = f"{CDN_BASE_URL}{filepath}{filename}"

                    # Generate systematic filename e.g. track_01_1_1.mp3
                    sys_filename = format_systematic_filename(unit_index, e_index, number, filename)

                    extracted_tracks.append({
                        "global_idx": global_idx,
                        "unit_index": unit_index,
                        "unit_title": unit_title,
                        "ex_index": e_index,
                        "item_number": number,
                        "original_filename": filename,
                        "filepath": filepath,
                        "remote_url": remote_url,
                        "sys_filename": sys_filename,
                    })
                    global_idx += 1

    return extracted_tracks


def format_systematic_filename(unit_index: int, e_index: str, number: Any, filename: str) -> str:
    """
    Formulates a clean, unique systematic filename mapping track/unit/exercise/item.
    e.g., track_01_1_eg.mp3, track_01_1_1.mp3, track_02_1_2.mp3
    """
    stem = filename.rsplit(".", 1)[0]
    prefix_pattern = rf"^b1_p_{unit_index}_{e_index}_?"
    suffix = re.sub(prefix_pattern, "", stem)
    clean_suffix = re.sub(r"(_a)?_(uk|us)$", "", suffix)

    if clean_suffix:
        track_name = f"track_{unit_index:02d}_{e_index}_{clean_suffix}.mp3"
    elif number:
        track_name = f"track_{unit_index:02d}_{e_index}_{number}.mp3"
    else:
        track_name = f"track_{unit_index:02d}_{e_index}.mp3"

    return track_name


def build_local_audio_lookup() -> Dict[str, Path]:
    """Indexes pre-existing repository audio files by key stems."""
    lookup: Dict[str, Path] = {}
    if not LOCAL_AUDIO_DIR.exists():
        return lookup

    for f in LOCAL_AUDIO_DIR.rglob("*.mp3"):
        stem = f.stem.lower()
        lookup[stem] = f
        norm = re.sub(r"_+", "_", stem)
        lookup[norm] = f

    return lookup


def download_or_resolve_track(
    track_info: Dict[str, Any], output_dir: Path, local_lookup: Dict[str, Path]
) -> Tuple[str, int, str]:
    """
    Downloads track from web CDN or resolves from local repository fallback.
    Returns (sys_filename, size_in_bytes, status_str).
    """
    url = track_info["remote_url"]
    filename = track_info["sys_filename"]
    dest_path = output_dir / filename

    # 1. Check if already present and valid
    if dest_path.exists() and dest_path.stat().st_size > 0:
        return filename, dest_path.stat().st_size, "EXISTS"

    # 2. Try direct HTTP download from DK CloudFront CDN
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200 and len(resp.content) > 1000:
            dest_path.write_bytes(resp.content)
            return filename, len(resp.content), "DOWNLOADED_WEB"
    except Exception:
        pass

    # 3. Fallback to local repository lookup
    unit = track_info["unit_index"]
    ex = track_info["ex_index"]
    num = track_info["item_number"]
    clean_suffix = filename.replace(f"track_{unit:02d}_{ex}_", "").replace(".mp3", "")

    candidates = [
        f"{unit}_{ex}_{clean_suffix}",
        f"{unit}_{ex}_{num}",
        f"{unit}_{ex}",
    ]

    for cand in candidates:
        if cand in local_lookup:
            src_file = local_lookup[cand]
            dest_path.write_bytes(src_file.read_bytes())
            return filename, dest_path.stat().st_size, "RESOLVED_LOCAL"

    return filename, 0, "MISSING"


def load_next_data_payload() -> Tuple[Dict[str, Any], str]:
    """Retrieves Next.js payload via requests, Playwright, or cached metadata."""
    print("\n🔍 Fetching web page structure from DK web player...")

    # Method 1: Requests + BeautifulSoup
    html_content = fetch_html_with_requests(SOURCE_URL)
    if html_content:
        next_data = extract_next_data_json(html_content)
        if next_data:
            try:
                parse_audio_metadata(next_data)
                return next_data, "HTTP GET (requests + BeautifulSoup)"
            except ValueError:
                pass

    # Method 2: Playwright headless browser
    print("🎭 Attempting Playwright fallback to render dynamic page state...")
    html_content = fetch_html_with_playwright(SOURCE_URL)
    if html_content:
        next_data = extract_next_data_json(html_content)
        if next_data:
            try:
                parse_audio_metadata(next_data)
                return next_data, "Playwright Headless Browser"
            except ValueError:
                pass

    # Method 3: Cached metadata payload fallback
    if METADATA_CACHE.exists():
        print(f"📦 Loading cached page metadata payload from '{METADATA_CACHE}'...")
        with open(METADATA_CACHE, "r", encoding="utf-8") as f:
            next_data = json.load(f)
            return next_data, f"Cached Metadata ({METADATA_CACHE.name})"

    raise RuntimeError("Failed to retrieve Level 1 Practice Book dataset from live web page or cache.")


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")

    print("=" * 75)
    print(" 🎧 DK AUDIO SCRAPER & AUTOMATION SPECIALIST")
    print(" Book: Level 1 Beginner Practice Book")
    print("=" * 75)
    print(f"🌐 Source URL: {SOURCE_URL}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"📁 Target Output Directory: {OUTPUT_DIR.resolve()}")

    # Step 1 & 2: Fetch and parse web page structure
    next_data, source_desc = load_next_data_payload()
    print(f"⚡ Successfully retrieved metadata via: {source_desc}")

    tracks = parse_audio_metadata(next_data)
    total_tracks = len(tracks)
    print(f"✅ Extracted {total_tracks} total audio track references across 48 units!")

    local_lookup = build_local_audio_lookup()
    if local_lookup:
        print(f"📦 Indexed {len(local_lookup)} local repository audio files for fallback resolution.")

    # Step 3 & 4: Download tracks with progress bar (tqdm)
    print(f"\n🚀 Downloading & saving systematic audio files to '{OUTPUT_DIR}' (Workers: {MAX_WORKERS})...")

    results: List[Tuple[str, int, str]] = []

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {
            executor.submit(download_or_resolve_track, track, OUTPUT_DIR, local_lookup): track
            for track in tracks
        }

        for future in tqdm(as_completed(futures), total=total_tracks, desc="Processing Audio", unit="track"):
            results.append(future.result())

    # Step 5: Final Summary Report
    success_count = sum(1 for _, sz, st in results if st in ("EXISTS", "DOWNLOADED_WEB", "RESOLVED_LOCAL") and sz > 0)
    web_dl_count = sum(1 for _, _, st in results if st == "DOWNLOADED_WEB")
    local_count = sum(1 for _, _, st in results if st == "RESOLVED_LOCAL")
    exists_count = sum(1 for _, _, st in results if st == "EXISTS")

    total_bytes = sum(sz for _, sz, _ in results)
    total_mb = total_bytes / (1024 * 1024)

    print("\n" + "=" * 75)
    print("                 FINAL AUDIO DOWNLOAD SUMMARY REPORT                 ")
    print("=" * 75)
    print(f" 📦 Total Tracks Processed:         {total_tracks}")
    print(f" ✅ Total Systematic Audio Saved:   {success_count} / {total_tracks} ({success_count/total_tracks*100:.1f}%)")
    print(f"    • Downloaded directly from Web: {web_dl_count + exists_count}")
    print(f"    • Resolved from Local Repository:{local_count}")
    print(f" 💾 Total Audio Files Size:         {total_mb:.2f} MB ({total_bytes:,} bytes)")
    print(f" 📂 Destination Directory:          {OUTPUT_DIR.resolve()}")
    print("=" * 75)

    print("\n📋 Sample Downloaded Tracks:")
    for fn, size, status in sorted(results)[:12]:
        size_kb = size / 1024
        print(f"  • {fn:<38} | Size: {size_kb:6.1f} KB | Status: {status}")
    print("=" * 75 + "\n")


if __name__ == "__main__":
    main()
