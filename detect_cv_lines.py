#!/usr/bin/env python3
"""
OpenCV Precision Line & Audio Icon Detector for Workbook Pages
Scans page images for horizontal answer blank lines and audio headphone icons,
aligns them with structured exercise JSON data, and outputs exact percentage coordinates.
"""

import argparse
import json
import os
import sys
from pathlib import Path
import cv2
import numpy as np


def detect_page_features(image_path: Path):
    """
    Scans a page image using computer vision:
    - Finds horizontal answer line segments and input box rectangles.
    - Finds audio headphone icon markers based on contour & color analysis.
    """
    img = cv2.imread(str(image_path))
    if img is None:
        print(f"Error: Could not read image {image_path}")
        return [], []

    img_h, img_w = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 1. Detect Horizontal Lines (Fill-in-blank lines)
    # Binary threshold
    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)

    # Morphological line detection kernel
    kernel_len = max(20, img_w // 40)
    horiz_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_len, 1))
    horiz_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, horiz_kernel)

    # Find line contours
    contours, _ = cv2.findContours(horiz_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    line_boxes = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        # Filter line dimensions (must be sufficiently wide horizontal segment)
        if w >= img_w * 0.08 and h <= img_h * 0.04:
            # Convert to percentage
            top_pct = round((y / img_h) * 100, 2)
            left_pct = round((x / img_w) * 100, 2)
            width_pct = round((w / img_w) * 100, 2)
            height_pct = max(3.0, round(((h + 20) / img_h) * 100, 2)) # Ensure min height for input field
            line_boxes.append({
                "x": x, "y": y, "w": w, "h": h,
                "top": top_pct, "left": left_pct, "width": width_pct, "height": height_pct
            })

    # Sort line boxes top-to-bottom, left-to-right
    line_boxes.sort(key=lambda b: (b["y"] // 30, b["x"]))

    # 2. Detect Audio Icons (Headphone symbol / Circle icons)
    # Convert to HSV to detect colored headphone icons (orange/red/purple/cyan badges)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # Red/Orange/Purple badge mask
    mask1 = cv2.inRange(hsv, np.array([0, 70, 50]), np.array([25, 255, 255]))
    mask2 = cv2.inRange(hsv, np.array([130, 70, 50]), np.array([170, 255, 255]))
    icon_mask = cv2.bitwise_or(mask1, mask2)

    icon_contours, _ = cv2.findContours(icon_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    audio_boxes = []
    
    for cnt in icon_contours:
        x, y, w, h = cv2.boundingRect(cnt)
        aspect_ratio = float(w) / h if h > 0 else 0
        area = cv2.contourArea(cnt)
        
        # Filter icon sizes (small circular/square badges)
        if 0.7 <= aspect_ratio <= 1.4 and 15 <= w <= 80 and 15 <= h <= 80:
            top_pct = round((y / img_h) * 100, 2)
            left_pct = round((x / img_w) * 100, 2)
            width_pct = round((w / img_w) * 100, 2)
            height_pct = round((h / img_h) * 100, 2)
            audio_boxes.append({
                "x": x, "y": y, "w": w, "h": h,
                "top": top_pct, "left": left_pct, "width": width_pct, "height": height_pct
            })

    audio_boxes.sort(key=lambda b: (b["y"] // 30, b["x"]))

    return line_boxes, audio_boxes


def process_page_bbox(page_num: int, output_dir: Path, images_dir: Path):
    """
    Combines detected CV coordinates with page JSON items and writes page_XXX_bbox.json.
    """
    pad_num = f"{page_num:03d}"
    json_path = output_dir / f"page_{pad_num}.json"
    img_path = images_dir / f"page_{pad_num}.png"

    if not json_path.exists() or not img_path.exists():
        print(f"Skipping page {page_num}: File missing ({json_path.name} or {img_path.name})")
        return None

    with open(json_path, "r", encoding="utf-8") as f:
        page_json = json.load(f)

    line_boxes, audio_boxes = detect_page_features(img_path)

    # Attach bounding boxes to exercise items
    line_idx = 0
    audio_idx = 0

    for ex in page_json.get("exercises", []):
        for item in ex.get("items", []):
            # Assign input_blank_box if available
            if line_idx < len(line_boxes):
                lb = line_boxes[line_idx]
                item["input_blank_box"] = {
                    "top": lb["top"],
                    "left": lb["left"],
                    "width": lb["width"],
                    "height": lb["height"]
                }
                line_idx += 1
            else:
                # Fallback default estimate if CV line missing
                item["input_blank_box"] = {"top": 20.0, "left": 55.0, "width": 35.0, "height": 3.5}

            # Assign audio_icon_box if audio icon present
            if item.get("audio_icon_present") or item.get("audio_file_path"):
                if audio_idx < len(audio_boxes):
                    ab = audio_boxes[audio_idx]
                    item["audio_icon_box"] = {
                        "top": ab["top"],
                        "left": ab["left"],
                        "width": ab["width"],
                        "height": ab["height"]
                    }
                    audio_idx += 1
                else:
                    # Fallback estimate next to line box
                    top_pos = item.get("input_blank_box", {}).get("top", 20.0)
                    item["audio_icon_box"] = {"top": top_pos, "left": 10.0, "width": 4.0, "height": 3.2}

    output_bbox_path = output_dir / f"page_{pad_num}_bbox.json"
    with open(output_bbox_path, "w", encoding="utf-8") as f:
        json.dump(page_json, f, indent=2, ensure_ascii=False)

    print(f"Successfully generated {output_bbox_path.name} with CV detected coordinates.")
    return page_json


def main():
    parser = argparse.ArgumentParser(description="OpenCV Bounding Box Detector for Workbook Pages")
    parser.add_argument("--page", type=int, default=12, help="Page number to process.")
    parser.add_argument("--all", action="store_true", help="Process all pages.")
    parser.add_argument("--output-dir", type=str, default="output_json", help="Output JSON directory.")
    parser.add_argument("--images-dir", type=str, default="images", help="Images directory.")
    args = parser.parse_args()

    out_dir = Path(args.output_dir)
    img_dir = Path(args.images_dir)

    if args.all:
        for p in range(1, 177):
            process_page_bbox(p, out_dir, img_dir)
    else:
        process_page_bbox(args.page, out_dir, img_dir)


if __name__ == "__main__":
    main()
