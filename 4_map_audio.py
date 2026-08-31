#!/usr/bin/env python3
"""
Step 5 (Optional / Bonus): Audio Mapper Script
Scans the audio/ directory for track files (.mp3, .m4a, .wav, .ogg, .flac, .aac),
matches them against extracted JSON exercises and items using unit number, exercise ID,
item number, example tags, and word tokens, and updates JSON extractions with exact relative audio file paths.
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional


def build_audio_lookup(audio_dir: Path) -> Dict[str, str]:
    """
    Scans audio_dir for audio files and creates a comprehensive lookup map:
    normalized stem key -> relative file path string (e.g. 'audio/1/1_4_1.mp3')
    """
    audio_extensions = {".mp3", ".m4a", ".wav", ".ogg", ".flac", ".aac"}
    lookup: Dict[str, str] = {}

    if not audio_dir.exists():
        return lookup

    for file_path in audio_dir.rglob("*"):
        if file_path.is_file() and file_path.suffix.lower() in audio_extensions:
            # Relative path from project root (with forward slashes)
            rel_path = file_path.as_posix()

            stem = file_path.stem.lower()
            lookup[stem] = rel_path

            # Normalize underscores (e.g., '1_4__eg' -> '1_4_eg')
            norm_stem = re.sub(r"_+", "_", stem)
            lookup[norm_stem] = rel_path

            # Dot notation key (e.g. '1.4.1', '1.4.eg')
            dot_key = norm_stem.replace("_", ".")
            lookup[dot_key] = rel_path

            # Strip dialect/locale suffixes like _a_usuk, _usuk, _uk, _us, _a, _b, _c
            clean_stem = re.sub(r"(_a_usuk|_usuk|_uk|_us|_a|_b|_c)$", "", norm_stem)
            if clean_stem != norm_stem:
                lookup[clean_stem] = rel_path
                lookup[clean_stem.replace("_", ".")] = rel_path

            # Strip track_ prefix and keep unit + exercise + item (e.g. 'track_01_1_1' -> '1_1_1')
            m = re.match(r"^track_(\d+)_(.+)", norm_stem)
            if m:
                unit_num = str(int(m.group(1)))
                rest = m.group(2)
                alias = f"{unit_num}_{rest}"
                lookup[alias] = rel_path
                lookup[alias.replace("_", ".")] = rel_path

                clean_alias = re.sub(r"(_a_usuk|_usuk|_uk|_us|_a|_b|_c)$", "", alias)
                if clean_alias != alias:
                    lookup[clean_alias] = rel_path
                    lookup[clean_alias.replace("_", ".")] = rel_path

    return lookup



def normalize_track_ref(track_ref: str) -> Optional[str]:
    """Converts user or schema track ref like '1.4' or 'Track 1.4' to standard '1_4' key."""
    if not track_ref:
        return None
    match = re.search(r"(\d+)[._\-\s]+(\d+)", track_ref)
    if match:
        return f"{int(match.group(1))}_{int(match.group(2))}"
    digits = re.findall(r"\d+", track_ref)
    if digits:
        return str(int(digits[0]))
    return None


def map_audio_to_json(
    audio_dir: Path,
    output_dir: Path,
    consolidate_filename: str = "all_pages_consolidated.json"
):
    """
    Maps audio files in audio_dir to JSON extractions in output_dir.
    """
    audio_dir.mkdir(parents=True, exist_ok=True)
    if not output_dir.exists():
        print(f"❌ Output directory '{output_dir}' does not exist. Run 2_extract_json.py first.")
        sys.exit(1)

    print(f"🎵 Scanning audio directory: {audio_dir}")
    lookup = build_audio_lookup(audio_dir)
    print(f"🎧 Found {len(lookup)} unique audio lookup keys indexed.")

    json_files = sorted(
        [f for f in output_dir.glob("page_*.json") if f.name != consolidate_filename]
    )

    total_items = 0
    mapped_items_count = 0
    unmapped_audio_exercises = []

    for json_file in json_files:
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            continue

        modified = False
        unit_num = data.get("unit_number")
        exercises = data.get("exercises", [])

        for ex in exercises:
            ex_id = ex.get("exercise_id", "")
            ex_match = re.search(r"(\d+)\.(\d+)", ex_id)
            if ex_match:
                u, e = ex_match.group(1), ex_match.group(2)
            else:
                u, e = str(unit_num or ""), ex_id

            # Exercise-level audio stem (e.g. '1_1' or '3_14')
            ex_stem = f"{u}_{e}"
            ex_audio_path = lookup.get(ex_stem) or lookup.get(f"{u}_{e}_")

            for item in ex.get("items", []):
                total_items += 1
                item_num = item.get("item_number")
                track_ref = item.get("audio_track_ref")
                audio_present = item.get("audio_icon_present", False)
                found_path = None

                candidates = []

                # 1. Direct candidate matching by item number / example tag
                if item_num == 0:
                    candidates.extend([f"{u}_{e}_eg", f"{u}_{e}__eg", f"{u}_{e}_0"])
                elif item_num is not None:
                    candidates.append(f"{u}_{e}_{item_num}")

                # 2. Track ref candidate
                if track_ref:
                    norm_ref = normalize_track_ref(track_ref)
                    if norm_ref:
                        candidates.append(norm_ref)

                # 3. Word token matching (e.g. 2_1_argentina, 3_4_eight)
                target_words = []
                for text_field in [item.get("correct_answer"), item.get("question"), item.get("prompt_text")]:
                    if isinstance(text_field, str):
                        clean_word = re.sub(r"[^a-zA-Z]", "", text_field.lower())
                        if clean_word and len(clean_word) >= 3:
                            target_words.append(clean_word)
                    elif isinstance(text_field, list):
                        for word in text_field:
                            clean_word = re.sub(r"[^a-zA-Z]", "", str(word).lower())
                            if clean_word and len(clean_word) >= 3:
                                target_words.append(clean_word)

                for word in target_words:
                    candidates.append(f"{u}_{e}_{word}")

                # Check candidates in lookup
                for cand in candidates:
                    if cand in lookup:
                        found_path = lookup[cand]
                        break

                # 4. Fallback to exercise-level audio if audio icon present or listening exercise
                if not found_path and (audio_present or track_ref or ex.get("exercise_type") == "audio_listen"):
                    if ex_audio_path:
                        found_path = ex_audio_path

                if found_path:
                    item["audio_file_path"] = found_path
                    item["audio_icon_present"] = True
                    mapped_items_count += 1
                    modified = True

        if modified:
            with open(json_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

    print("\n" + "=" * 60)
    print("           ENHANCED AUDIO MAPPING REPORT           ")
    print("=" * 60)
    print(f" 📁 Audio Track Lookup Keys:           {len(lookup)}")
    print(f" ❓ Total Items Scanned in JSONs:      {total_items}")
    print(f" ✅ Successfully Mapped Audio Files:   {mapped_items_count}")
    print("=" * 60 + "\n")

    # Update consolidated file if present
    consolidated_path = output_dir / consolidate_filename
    if consolidated_path.exists():
        print(f"🔄 Updating consolidated file: {consolidated_path}")
        import importlib
        verify_mod = importlib.import_module("3_verify_outputs")
        verify_mod.verify_and_consolidate(output_dir, Path("images"), Path("logs"), consolidate_filename)


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Map audio files to extracted JSON audio track references.")
    parser.add_argument("--audio-dir", type=str, default="audio", help="Directory containing audio files.")
    parser.add_argument("--output-dir", type=str, default="output_json", help="Directory containing JSON files.")
    args = parser.parse_args()

    map_audio_to_json(
        audio_dir=Path(args.audio_dir),
        output_dir=Path(args.output_dir)
    )


if __name__ == "__main__":
    main()
