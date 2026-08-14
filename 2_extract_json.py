#!/usr/bin/env python3
"""
Step 3: Batch Extraction Script
Iterates through page images in images/, sends each image to Gemini Vision API
using Structured Outputs (google-genai SDK + Pydantic schema), and saves JSON output.
"""

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import List, Dict, Any

from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image
from tqdm import tqdm

# Import structured schema
from schema import PageExtraction

# Load environment variables (GEMINI_API_KEY from .env if present)
load_dotenv()


SYSTEM_INSTRUCTION = """
You are an expert educational content parser and OCR vision assistant specialized in language learning textbooks.
Your task is to analyze the provided page image from the "English for Everyone Practice Book" and accurately extract all exercises into structured JSON according to the provided schema.

Guidelines for Extraction:
1. Header & Context:
   - Identify the unit number (if present, e.g. "Unit 1" -> 1) and unit title (e.g. "Making friends").
   - Determine the page number from the page header/footer or filename.

2. Exercises:
   - Identify each distinct exercise box on the page.
   - Extract the exercise ID (e.g., "1.1", "1.2", "2.1").
   - Determine the exercise_type from: "multiple_choice", "fill_in_blank", "matching", "sentence_ordering", "true_false", "audio_listen".
   - Extract the complete instruction text (e.g., "REWRITE THE SENTENCES, CORRECTING THE ERRORS", "CROSS OUT THE INCORRECT WORD IN EACH SENTENCE").

3. Question Items:
   - For each numbered item (1, 2, 3...):
     - Extract item_number.
     - prompt_text: Include any visual context, sample sentence, picture caption, or given clue text.
     - question: The main text of the prompt, sentence with blank, sentence to reorder, or item text.
     - options: For multiple choice or matching, list all available options/choices shown in boxes or dropdown-style visuals.
     - correct_answer: Extract the highlighted, filled-in sample answer, underlined answer, or checked answer if visible on the page (e.g. item 0 or sample item usually shows the filled answer). If not filled, infer the correct answer from the prompt text or given clues if possible, or provide the target response string.
     - audio_icon_present: Set to true if a headphone symbol / audio track icon is near the item or exercise.
     - audio_track_ref: Extract the track reference string if shown next to the audio icon (e.g., "1.4" or "12").

4. Output Quality:
   - Preserve exact spelling and punctuation.
   - Maintain the sequential order of items as displayed on the page.
"""


def get_gemini_client() -> genai.Client:
    """Initializes and returns the Google GenAI client."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ Error: GEMINI_API_KEY environment variable is not set.")
        print("   Please export GEMINI_API_KEY='your_api_key' or add it to a .env file.")
        sys.exit(1)
    return genai.Client(api_key=api_key)


def extract_page_with_retry(
    client: genai.Client,
    image_path: Path,
    page_num: int,
    model_name: str,
    max_retries: int = 5
) -> Dict[str, Any] | None:
    """
    Sends page image to Gemini Vision with structured schema and exponential backoff retry.
    """
    image = Image.open(image_path)
    
    prompt = f"Parse page {page_num} of the English for Everyone practice book according to the response schema."

    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_INSTRUCTION,
        response_mime_type="application/json",
        response_schema=PageExtraction,
        temperature=0.1
    )

    candidate_models = []
    for m in [model_name, "gemini-3.5-flash", "gemini-3.1-flash-lite"]:
        if m not in candidate_models:
            candidate_models.append(m)

    model_idx = 0
    attempt = 0
    while True:
        attempt += 1
        current_model = candidate_models[model_idx]
        try:
            response = client.models.generate_content(
                model=current_model,
                contents=[image, prompt],
                config=config,
            )

            # Response text should be structured JSON string matching PageExtraction schema
            response_text = response.text
            if not response_text:
                raise ValueError("Empty response text returned from Gemini API.")

            data = json.loads(response_text)
            
            # Guarantee page_number is correctly set
            if "page_number" not in data or not data["page_number"]:
                data["page_number"] = page_num

            return data

        except Exception as e:
            err_str = str(e)
            print(f"\n  ⚠️ Attempt {attempt} ({current_model}) failed for page {page_num}: {err_str}", flush=True)

            # Smart 429 Rate Limit / Quota Exhaustion retry handling (try next candidate model first)
            if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str or "quota" in err_str.lower():
                # Switch to next candidate model if available
                if model_idx + 1 < len(candidate_models):
                    model_idx += 1
                    print(f"     🔄 Switching to fallback model: {candidate_models[model_idx]}...", flush=True)
                    attempt -= 1
                    continue
                else:
                    # Reset model index to 0 and sleep
                    model_idx = 0
                    delay_match = re.search(r"retry in (\d+(?:\.\d+)?)s", err_str, re.IGNORECASE) or re.search(r"retryDelay': '(\d+)s'", err_str)
                    sleep_time = float(delay_match.group(1)) + 2.0 if delay_match else 15.0
                    print(f"     ⏳ All candidate models rate-limited. Waiting {sleep_time:.1f}s before retrying (attempt {attempt})...", flush=True)
                    time.sleep(sleep_time)
                    attempt -= 1
            elif attempt < max_retries:
                sleep_time = (2 ** attempt) + (attempt * 0.5)
                print(f"     Retrying in {sleep_time:.1f}s...", flush=True)
                time.sleep(sleep_time)
            else:
                print(f"  ❌ All {max_retries} non-rate-limit attempts failed for page {page_num}.", flush=True)
                return None


def parse_page_number_from_filename(filename: str) -> int:
    """Extracts integer page number from filenames like page_001.png or page_12.png."""
    match = re.search(r"page_(\d+)", filename, re.IGNORECASE)
    if match:
        return int(match.group(1))
    # Fallback to any digits
    digits = re.findall(r"\d+", filename)
    if digits:
        return int(digits[-1])
    return 1


def batch_extract(
    images_dir: Path,
    output_dir: Path,
    logs_dir: Path,
    model_name: str = "gemini-3.6-flash",
    max_retries: int = 5,
    force_reprocess: bool = False
):
    """
    Iterates through all page images in images_dir, extracts JSON, and logs results.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)

    image_files = sorted(
        [f for f in images_dir.glob("*.png")] + [f for f in images_dir.glob("*.jpg")],
        key=lambda p: parse_page_number_from_filename(p.name)
    )

    if not image_files:
        print(f"❌ No page images found in '{images_dir}'. Run 1_convert_pdf.py first.")
        sys.exit(1)

    print(f"🚀 Initializing Gemini Vision Client...")
    client = get_gemini_client()
    print(f"🤖 Using Model: {model_name}")
    print(f"🖼️ Found {len(image_files)} page images to process.")

    failed_pages: List[Dict[str, Any]] = []
    success_count = 0
    skipped_count = 0

    with tqdm(total=len(image_files), desc="Extracting Page JSONs") as pbar:
        for img_path in image_files:
            page_num = parse_page_number_from_filename(img_path.name)
            output_json_path = output_dir / f"page_{page_num:03d}.json"

            # Check for resumption
            if not force_reprocess and output_json_path.exists() and output_json_path.stat().st_size > 10:
                skipped_count += 1
                pbar.update(1)
                continue

            extracted_data = extract_page_with_retry(
                client=client,
                image_path=img_path,
                page_num=page_num,
                model_name=model_name,
                max_retries=max_retries
            )

            if extracted_data:
                with open(output_json_path, "w", encoding="utf-8") as f:
                    json.dump(extracted_data, f, indent=2, ensure_ascii=False)
                success_count += 1
            else:
                failed_pages.append({
                    "page_number": page_num,
                    "image_file": img_path.name,
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                })

            pbar.update(1)

    # Save failed log
    failed_log_path = logs_dir / "failed_pages.json"
    with open(failed_log_path, "w", encoding="utf-8") as f:
        json.dump(failed_pages, f, indent=2)

    print("\n🏁 Extraction Batch Complete!")
    print(f"   ✅ Successful: {success_count}")
    print(f"   ⏭️ Skipped (already processed): {skipped_count}")
    print(f"   ❌ Failed: {len(failed_pages)}")
    if failed_pages:
        print(f"   📋 Failed pages logged to: {failed_log_path}")


def main():
    parser = argparse.ArgumentParser(description="Batch extract page JSONs using Gemini Vision & Pydantic schema.")
    parser.add_argument("--images-dir", type=str, default="images", help="Directory containing page images.")
    parser.add_argument("--output-dir", type=str, default="output_json", help="Directory to save JSON outputs.")
    parser.add_argument("--logs-dir", type=str, default="logs", help="Directory to save logs.")
    parser.add_argument("--model", type=str, default="gemini-3.6-flash", help="Gemini model name (e.g. gemini-3.6-flash).")
    parser.add_argument("--retries", type=int, default=5, help="Max retry attempts for failed pages.")
    parser.add_argument("--force", action="store_true", help="Force reprocessing even if JSON already exists.")
    args = parser.parse_args()

    batch_extract(
        images_dir=Path(args.images_dir),
        output_dir=Path(args.output_dir),
        logs_dir=Path(args.logs_dir),
        model_name=args.model,
        max_retries=args.retries,
        force_reprocess=args.force
    )


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")
    main()
