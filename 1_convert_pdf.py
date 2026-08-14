#!/usr/bin/env python3
"""
Step 1: PDF to Image Conversion Script
Converts pages of a PDF book into high-quality PNG images using pdf2image and Poppler.
"""

import argparse
import os
import shutil
import sys
from pathlib import Path
from pdf2image import convert_from_path, pdfinfo_from_path
from tqdm import tqdm


def find_poppler_path() -> str | None:
    """
    Attempts to locate pdftoppm / poppler binary directory on Windows/Linux/macOS.
    """
    # 1. Check if pdftoppm is already accessible in system PATH
    pdftoppm_in_path = shutil.which("pdftoppm")
    if pdftoppm_in_path:
        return os.path.dirname(pdftoppm_in_path)

    # 2. Common Windows installation locations
    possible_paths = [
        os.getenv("POPPLER_PATH"),
        r"C:\Program Files\poppler\bin",
        r"C:\Program Files (x86)\poppler\bin",
        r"C:\poppler\bin",
        r"C:\poppler\Library\bin",
    ]

    local_app_data = os.getenv("LOCALAPPDATA", "")
    if local_app_data:
        possible_paths.extend([
            os.path.join(local_app_data, "Programs", "poppler", "bin"),
            os.path.join(local_app_data, "Programs", "poppler", "Library", "bin"),
            os.path.join(local_app_data, "Microsoft", "WinGet", "Packages"),
        ])

    user_profile = os.getenv("USERPROFILE", "")
    if user_profile:
        possible_paths.append(os.path.join(user_profile, "AppData", "Local", "Microsoft", "WinGet", "Packages"))

    for p in possible_paths:
        if not p:
            continue
        # Direct check
        if os.path.isdir(p) and (os.path.exists(os.path.join(p, "pdftoppm.exe")) or os.path.exists(os.path.join(p, "pdftoppm"))):
            return p
        # Search winget package directories recursively for pdftoppm.exe
        if os.path.exists(p):
            for root, dirs, files in os.walk(p):
                if "pdftoppm.exe" in files or "pdftoppm" in files:
                    return root

    return None


def locate_or_setup_input_pdf(input_folder: Path, custom_input: str | None = None) -> Path:
    """
    Ensures input folder exists and locates the PDF to process.
    """
    input_folder.mkdir(parents=True, exist_ok=True)

    if custom_input:
        custom_path = Path(custom_input)
        if custom_path.exists():
            return custom_path
        else:
            raise FileNotFoundError(f"Specified input PDF not found: {custom_input}")

    # Check inside input_folder
    pdf_files = list(input_folder.glob("*.pdf"))
    if pdf_files:
        return pdf_files[0]

    # Check root directory for any PDF file and copy/move to input/book.pdf
    root_pdfs = list(Path(".").glob("*.pdf"))
    if root_pdfs:
        target_pdf = input_folder / "book.pdf"
        print(f"Found PDF in root directory: {root_pdfs[0].name}")
        print(f"Copying to {target_pdf}...")
        shutil.copy(root_pdfs[0], target_pdf)
        return target_pdf

    raise FileNotFoundError(
        "No PDF file found in input/ or current directory! "
        "Please place your PDF file in the input/ folder (e.g. input/book.pdf)."
    )


def convert_pdf_to_images(
    pdf_path: Path,
    output_folder: Path,
    dpi: int = 175,
    poppler_path: str | None = None,
    max_pages: int | None = None
):
    """
    Converts PDF pages into PNG images.
    """
    output_folder.mkdir(parents=True, exist_ok=True)

    print(f"📄 Processing PDF: {pdf_path}")
    print(f"⚙️ Target DPI: {dpi}")

    # Verify Poppler
    effective_poppler = poppler_path or find_poppler_path()
    if effective_poppler:
        print(f"✅ Poppler detected at: {effective_poppler}")
    else:
        print("⚠️ Warning: Poppler executable not found in PATH or standard paths.")
        print("   If conversion fails, please install Poppler or pass --poppler-path.")

    try:
        info = pdfinfo_from_path(str(pdf_path), poppler_path=effective_poppler)
        total_pages = info["Pages"]
        print(f"📖 Total pages in PDF: {total_pages}")
    except Exception as e:
        print(f"❌ Failed to read PDF metadata: {e}")
        total_pages = None

    pages_to_convert = total_pages if total_pages else (max_pages or 500)
    if max_pages and max_pages < pages_to_convert:
        pages_to_convert = max_pages

    print(f"🖼️ Converting {pages_to_convert} pages into '{output_folder}' directory...")

    # We convert page by page or in small batches to save RAM
    batch_size = 10
    saved_count = 0

    with tqdm(total=pages_to_convert, desc="Converting PDF to Images") as pbar:
        for first_page in range(1, pages_to_convert + 1, batch_size):
            last_page = min(first_page + batch_size - 1, pages_to_convert)
            try:
                images = convert_from_path(
                    str(pdf_path),
                    dpi=dpi,
                    first_page=first_page,
                    last_page=last_page,
                    poppler_path=effective_poppler,
                    fmt="png"
                )
                for idx, img in enumerate(images):
                    page_num = first_page + idx
                    img_filename = output_folder / f"page_{page_num:03d}.png"
                    img.save(img_filename, "PNG")
                    saved_count += 1
                    pbar.update(1)
            except Exception as err:
                print(f"\n❌ Error converting pages {first_page}-{last_page}: {err}")
                break

    print(f"✨ Successfully converted {saved_count} pages into '{output_folder}'.")


def main():
    parser = argparse.ArgumentParser(description="Convert PDF book pages to PNG images.")
    parser.add_argument("--input-pdf", type=str, default=None, help="Path to input PDF file.")
    parser.add_argument("--output-dir", type=str, default="images", help="Directory to save image files.")
    parser.add_argument("--dpi", type=int, default=175, help="Image resolution DPI (150-200 recommended).")
    parser.add_argument("--poppler-path", type=str, default=None, help="Explicit path to Poppler bin directory.")
    parser.add_argument("--max-pages", type=int, default=None, help="Limit maximum pages to convert (for testing).")
    args = parser.parse_args()

    input_dir = Path("input")
    output_dir = Path(args.output_dir)

    try:
        pdf_file = locate_or_setup_input_pdf(input_dir, args.input_pdf)
        convert_pdf_to_images(
            pdf_path=pdf_file,
            output_folder=output_dir,
            dpi=args.dpi,
            poppler_path=args.poppler_path,
            max_pages=args.max_pages
        )
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")
    main()
