# Teacher Lewis's Practice Book - Studio Ghibli Interactive Edition

An automated AI pipeline and interactive Studio Ghibli web application for **Teacher Lewis's Practice Book**, featuring interactive exercise rewrites, native audio playback, voice recording, mascot interactions, and a collectible sticker inventory system.

---

## 📁 Project Structure

```
englishForEveryoneOne/
├── input/                      # Place your input PDF here (e.g. book.pdf)
├── images/                     # Generated PNG page images (page_001.png, ...)
├── output_json/                # Individual page JSON outputs & consolidated file
├── logs/                       # Failure logs (failed_pages.json)
├── venv/                       # Virtual environment directory
├── requirements.txt            # Python dependencies
├── schema.py                   # Pydantic structured output models
├── 1_convert_pdf.py            # Step 1: PDF to PNG page conversion script
├── 2_extract_json.py           # Step 3: Gemini Vision API batch extraction script
├── 3_verify_outputs.py         # Step 4: Verification & consolidation script
└── README.md                   # Complete setup and execution guide
```

---

## 🛠️ Requirements & Installation

### 1. Environment Setup

Clone/navigate to the project directory and create a virtual environment:

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# On Linux/macOS:
source venv/bin/activate

# Upgrade pip and install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Set Up API Key

Obtain a Google Gemini API Key from Google AI Studio and set the environment variable:

```bash
# Windows (PowerShell):
$env:GEMINI_API_KEY="YOUR_GEMINI_API_KEY"

# Linux/macOS:
export GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
```

Or create a `.env` file in the project root:
```env
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
```

### 3. Poppler Requirement

`pdf2image` requires Poppler to render PDF pages into images.
- **Windows**: Install via winget:
  ```bash
  winget install oschwartz10612.Poppler
  ```
- **Linux**: `sudo apt install poppler-utils`
- **macOS**: `brew install poppler`

`1_convert_pdf.py` automatically detects Poppler in your system PATH and standard Windows install paths.

---

## 🚀 Execution Guide

### Step 1: Convert PDF to Page Images

Place your PDF in `input/book.pdf` (or leave it in the project root folder for auto-detection):

```bash
python 1_convert_pdf.py --dpi 175
```

Options:
- `--dpi`: Image resolution (default: `175`, recommended `150-200`).
- `--input-pdf`: Path to custom PDF file.
- `--max-pages`: Convert only a subset of pages (useful for testing, e.g. `--max-pages 5`).

---

### Step 2: Define Schema (`schema.py`)

`schema.py` defines the Pydantic models used by Gemini Vision for Structured Outputs:
- `PageExtraction`: Page metadata, unit title/number, list of exercises.
- `Exercise`: Exercise ID (`1.1`), type (`multiple_choice`, `fill_in_blank`, `matching`, `sentence_ordering`, `true_false`, `audio_listen`), instructions.
- `QuestionItem`: Question text, visual prompt context, multiple-choice options, correct answers, audio track icons & refs.

---

### Step 3: Batch Extract JSON Data via Gemini Vision

Run the extraction script across converted page images:

```bash
python 2_extract_json.py --model gemini-2.5-flash
```

Options:
- `--model`: Model choice (`gemini-2.5-flash`, `gemini-2.5-pro`).
- `--retries`: Max backoff retries per page (default: `5`).
- `--force`: Force re-extraction of pages that already have JSON files.

Features:
- **Resumption**: Skips pages that were already processed successfully.
- **Exponential Backoff**: Handles rate limits automatically.
- **Failure Logging**: Failed pages are logged to `logs/failed_pages.json`.

---

### Step 4: Verification & Consolidation

Run the verification script to validate JSON outputs and view exercise statistics:

```bash
python 3_verify_outputs.py
```

Output:
- Detailed terminal report showing total pages processed, success/fail counts, exercise totals, and breakdown by exercise type.
- Consolidated JSON file saved to `output_json/all_pages_consolidated.json`.

### Step 5: Map Audio Tracks (Optional)

Place your audio files (`.mp3`, `.wav`, `.m4a`) into the `audio/` folder and run:

```bash
python 4_map_audio.py
```

Features:
- Scans `audio/` and matches track filenames (e.g. `1.4.mp3`, `track_1_4.mp3`, `01_04.mp3`) against extracted `audio_track_ref` values (`"1.4"`).
- Automatically updates `audio_file_path` in JSON extractions so web/app frontends can play native audio clips directly!

```json
{
  "page_number": 12,
  "unit_number": 1,
  "unit_title": "Making friends",
  "exercises": [
    {
      "exercise_id": "1.1",
      "exercise_type": "fill_in_blank",
      "instruction": "FILL IN THE BLANKS WITH 'AM', 'IS', OR 'ARE'",
      "items": [
        {
          "item_number": 1,
          "prompt_text": "Sample prompt context",
          "question": "He ___ a teacher.",
          "options": ["am", "is", "are"],
          "correct_answer": "is",
          "audio_icon_present": true,
          "audio_track_ref": "1.2"
        }
      ]
    }
  ]
}
```
