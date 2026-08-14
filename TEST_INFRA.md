# Studio Ghibli Interactive Edition — Test Infrastructure & Verification Specification

## Overview
This document specifies the opaque-box automated test infrastructure, verification methodology, and execution instructions for the **Studio Ghibli Interactive Edition** project (`englishForEveryoneOne`).

The test suite ensures 100% file coverage, static DOM element structure integrity, dataset parity against `output_json/all_pages_consolidated.json`, and comprehensive end-to-end (E2E) interactive browser functional verification using Python Playwright and `unittest`.

---

## 1. Verification Methodology & Tiered Test Architecture

The testing framework is structured into 4 verification tiers:

### Tier 1: Static DOM Structure & Dataset Parity
- **Script**: `verify_generated_pages.py`
- **Scope**: All 169 exercise HTML files (`ghibli_p008.html` through `ghibli_p176.html`).
- **Verifications**:
  1. **File Existence**: Verifies that all 169 expected exercise HTML files exist on disk.
  2. **DOM Element Integrity**: Validates presence of required core UI components on every page:
     - `#mascotBubble` (or `.mascot-bubble`): Kodama companion mascot speech bubble container.
     - `#ghibliCheckAnswersBtn` (or `.ghibli-check-btn`): Instant answer grading trigger button.
     - `#ghibliScoreBadge` (or `.ghibli-score-badge` / `#ghibliScoreText`): Live score badge element.
     - `.tod-btn`: Time-of-Day theme switcher buttons (Day, Sunset, Night).
     - `.chapter-nav-bar`: Previous / Next / Home navigation pill bar.
  3. **Input Parity**: Checks that interactive input controls (inputs, options, drop slots, matching selectors) match item counts defined in `output_json/all_pages_consolidated.json`.
  4. **Audio Path Integrity**: Validates `data-audio` attributes and `<audio>` src paths.
  5. **Navigation Target Integrity**: Validates `href` targets in `.chapter-nav-bar` links.

---

### Tier 2: E2E Browser Interaction — Rendering & Navigation (R1 & R2)
- **Script**: `run_e2e_tests.py` (Class `TestGhibliE2E`)
- **Scope**: Headless Chromium browser automation via Playwright sync API.
- **Verifications**:
  - **R1 Rendering & Acceptance**: Pages load without JavaScript errors; text inputs accept user typing and user interaction.
  - **R2 Atmospheric Theme Switching**: Clicking `.tod-btn` for `day`, `sunset`, and `night` dynamically updates body background class (`theme-day`, `theme-sunset`, `theme-night`) or `data-theme` attribute.
  - **R2 Navigation Links**: Links inside `.chapter-nav-bar` exist, display correct labels, and link to valid relative endpoints.
  - **R2 Kodama Mascot Widget**: Speech bubble `#mascotBubble` is visible and populated with story/narration text.
  - **R2 Audio Playback Trigger**: Clicking `.ghibli-audio-play-btn` / `[data-audio]` triggers audio engine without unhandled exception.

---

### Tier 3: E2E Interactive Grading & Progress Tracking (R3)
- **Script**: `run_e2e_tests.py`
- **Verifications**:
  - **Instant Check Answers Validation**: Clicking `#ghibliCheckAnswersBtn` runs evaluation logic over user inputs.
  - **Visual Feedback Highlighting**: Inputs/cards receive `.correct` or `.incorrect` CSS class decoration.
  - **Score Badge Update**: Live score badge text (`#ghibliScoreText`) updates to display accurate `Score: X / Y`.
  - **Reset Functionality**: Clicking `#ghibliResetBtn` clears all input fields and resets score / highlight decorations.

---

### Tier 4: Cross-Page Sample Matrix Verification
- **Script**: `run_e2e_tests.py` (`test_sample_matrix_execution`)
- **Sample Matrix Pages**: `ghibli_p008.html`, `ghibli_p012.html`, `ghibli_p025.html`, `ghibli_p050.html`, `ghibli_p100.html`, `ghibli_p176.html`.
- **Scope**: Executes full verification sweep across representative pages spanning the entire textbook (beginning, early units, middle units, late units, final page).

---

## 2. Test Execution Guide

All tests run using Python inside the project virtual environment (`venv`).

### Prerequisites
- Python 3.14+ inside `venv`.
- Dependencies: `playwright`, `beautifulsoup4`.

### Running Tier 1 Static DOM & Parity Validator
```cmd
cmd /c "venv\Scripts\python.exe verify_generated_pages.py"
```
- **Exit Code 0**: 100% of 169 exercise HTML files exist and pass DOM element & input parity checks.
- **Exit Code 1**: Files missing or DOM/parity violations detected.

### Running Tiers 2-4 Playwright E2E Browser Test Suite
```cmd
cmd /c "venv\Scripts\python.exe run_e2e_tests.py"
```
- Spawns background local HTTP server on `127.0.0.1:8889`.
- Runs Playwright Chromium headless test runner using `unittest`.
- Prints detailed test results for R1, R2, R3, and sample matrix execution.

---

## 3. Test Suite Artifacts

| File | Description | Role |
|------|-------------|------|
| `TEST_INFRA.md` | Test infrastructure & methodology guide | Specification |
| `verify_generated_pages.py` | Tier 1 static DOM structure & parity validator | Validator Script |
| `run_e2e_tests.py` | Tiers 2-4 Playwright E2E browser test suite | Test Runner |
| `TEST_READY.md` | Test suite completion signal & coverage table | Release Artifact |
