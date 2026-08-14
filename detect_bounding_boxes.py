#!/usr/bin/env python3
"""
Bounding Box Detection Script using Gemini Vision API
Detects precise [ymin, xmin, ymax, xmax] 2D bounding boxes (0-1000 scale)
for exercise items, input blanks, and audio icons on page images.
"""

import json
import os
import sys
from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image

load_dotenv()

class BBoxItem(BaseModel):
    item_number: int = Field(description="Question item number (e.g. 1, 2, 3)")
    question_text: str = Field(description="Full text of the question or prompt")
    correct_answer: str = Field(description="Correct answer string")
    question_box_2d: List[int] = Field(description="[ymin, xmin, ymax, xmax] on a 0-1000 scale for the whole question item bounding box")
    input_blank_box_2d: Optional[List[int]] = Field(default=None, description="[ymin, xmin, ymax, xmax] on a 0-1000 scale for the specific blank space or input box where user writes/selects the answer")
    audio_icon_box_2d: Optional[List[int]] = Field(default=None, description="[ymin, xmin, ymax, xmax] on a 0-1000 scale for the headphone audio icon if present")
    audio_file_path: Optional[str] = Field(default="audio/1/1_1.mp3", description="Audio track file path if applicable")

class PageBBoxExtraction(BaseModel):
    page_number: int
    unit_title: str
    items: List[BBoxItem]

def extract_bbox_for_page(image_path: str, page_num: int = 12):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY not found.")
        sys.exit(1)

    client = genai.Client(api_key=api_key)
    
    img = Image.open(image_path)
    
    prompt = """
    Analyze this textbook page image and extract exact 2D bounding boxes for each numbered exercise question item on the page.
    Bounding box coordinates must be integers normalized to a 0-1000 scale: [ymin, xmin, ymax, xmax].
    
    For each numbered item:
    1. question_box_2d: [ymin, xmin, ymax, xmax] around the entire row/item area.
    2. input_blank_box_2d: [ymin, xmin, ymax, xmax] around the blank line / box where the student writes the answer.
    3. audio_icon_box_2d: [ymin, xmin, ymax, xmax] around the headphone/speaker audio icon if visible near the question.
    """
    
    print(f"Sending {image_path} to Gemini Vision API for Bounding Box detection...")
    
    response = client.models.generate_content(
        model="models/gemini-flash-latest",
        contents=[img, prompt],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=PageBBoxExtraction,
            temperature=0.1
        )
    )
    
    result = json.loads(response.text)
    output_file = f"output_json/page_{page_num:03d}_bbox.json"
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
        
    print(f"Successfully saved bounding box extraction to {output_file}!")
    return result

if __name__ == "__main__":
    extract_bbox_for_page("images/page_012.png", 12)
