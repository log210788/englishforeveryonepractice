# Project: Studio Ghibli Interactive Edition Expansion

## Architecture
- Code base: HTML5 + CSS3 + Vanilla JavaScript + Python Generator + Python Playwright Test Suite
- Pages: `ghibli_p008.html` through `ghibli_p176.html` (169 exercise pages + `index.html` Home Hub)
- Data Source: `output_json/all_pages_consolidated.json`
- Shared Runtime Core:
  - `ghibli_theme.css`: Responsive CSS tokens, Time-of-Day background themes (Day, Sunset, Night), Kodama mascot UI, score badges, exercise styling.
  - `ghibli_page_engine.js`: Time-of-Day theme switcher, Audio player (`audio/{unit}/{file}.mp3` + SpeechSynthesis fallback), Voice recorder (`MediaRecorder`), Kodama mascot widget (Pomodoro timer & Teacher Lewis story narration), Page navigation bar engine, Instant grading engine (validating text/options/drag-drop/matching, sound chimes, score badges, mascot celebrate/encouragement reactions).
  - `ghibli_audio.js`: Web Audio API sound synthesizer (kalimba/marimba click notes, waterdrop pops, acoustic glass chimes, fanfare).
- Page Generator: `generate_ghibli_pages.py` (Python 3.14 script parsing JSON and generating modular HTML files).
- Automated Testing & E2E Suite:
  - `TEST_INFRA.md`: Test framework documentation and instructions.
  - `verify_generated_pages.py`: Static DOM structure, parity, and link validator across all 169 HTML pages.
  - `run_e2e_tests.py`: Python Playwright browser automated test runner (Tiers 1-4).

## Feature Inventory
Every feature from the Survey phase appears here with its assigned milestone.
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| F1 | Page Generation Pipeline | Python script `generate_ghibli_pages.py` parsing `output_json/all_pages_consolidated.json` to generate 169 interactive HTML pages (`ghibli_p008.html`..`ghibli_p176.html`). | M1 | survey |
| F2 | Shared UI & Theme Engine | CSS (`ghibli_theme.css`) & JS (`ghibli_page_engine.js`) providing Day/Sunset/Night theme switcher, background overlays, Kodama widget, voice recorder, audio player with speech synthesis fallback, page navigation bar. | M1 | survey |
| F3 | Exercise Types Support | Full interactive UI and data binding for all 6 exercise types (`fill_in_blank`, `sentence_ordering`, `multiple_choice`, `matching`, `audio_listen`, `true_false`). | M2 | survey |
| F4 | Instant Grading & Mascot Feedback | Instant answer validation against `correct_answer`, correct/incorrect input highlight, sound chimes, score badges, mascot reactions (celebrate/encouragement). | M2 | survey |
| F5 | E2E Testing Framework & Harness | Setup `TEST_INFRA.md`, `verify_generated_pages.py`, and `run_e2e_tests.py` using Playwright and unittest. | E2E Track | survey |
| F6 | Full Page Generation Execution | Run `generate_ghibli_pages.py` to generate all 169 HTML files and verify 100% file creation and DOM integrity. | M3 | survey |
| F7 | Final E2E Test Pass & Adversarial Hardening | Pass 100% of E2E test suite (Tiers 1-4), execute Tier 5 adversarial testing, and pass Forensic Audit. | M4 | survey |

## Code Layout
- Root: `e:\class aids\code\englishForEveryoneOne\`
  - `generate_ghibli_pages.py`
  - `ghibli_theme.css`
  - `ghibli_page_engine.js`
  - `verify_generated_pages.py`
  - `run_e2e_tests.py`
  - `TEST_INFRA.md`
  - `TEST_READY.md`
  - `ghibli_p008.html` .. `ghibli_p176.html`
  - `output_json/all_pages_consolidated.json`
  - `audio/`, `images/`, `css/`, `js/`

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| 1 | Shared Framework & Generator Engine | Create `ghibli_theme.css`, `ghibli_page_engine.js`, and `generate_ghibli_pages.py` core architecture. | None | DONE |
| 2 | Exercise UI Component Builders | Implement rendering and interactive grading logic for all 6 exercise types (`fill_in_blank`, `sentence_ordering`, `multiple_choice`, `matching`, `audio_listen`, `true_false`). | M1 | DONE |
| 3 | Complete Page Batch Generation | Run `generate_ghibli_pages.py` to produce all 169 HTML files (`ghibli_p008.html` .. `ghibli_p176.html`) and verify DOM integrity via `verify_generated_pages.py`. | M2 | DONE |
| 4 | Final E2E Verification & Hardening | Pass 100% of E2E tests (Tiers 1-4), execute Tier 5 adversarial coverage hardening, and pass Forensic Integrity Audit. | M3, E2E Track | DONE |

## Interface Contracts
### `generate_ghibli_pages.py` ↔ HTML Pages
- Reads `output_json/all_pages_consolidated.json`.
- Writes `ghibli_p008.html` .. `ghibli_p176.html`.
- Each HTML page embeds `<link rel="stylesheet" href="ghibli_theme.css">` and `<script src="ghibli_audio.js"></script><script src="ghibli_page_engine.js"></script>`.

### `ghibli_page_engine.js` ↔ DOM Elements
- `#mascotBubble`: Text popover for Kodama reactions and Teacher Lewis story narration.
- `.tod-btn[data-theme]`: Event listeners for theme switching (`day`, `sunset`, `night`).
- `#ghibliCheckAnswersBtn`: Validates all `.ghibli-input`, `.ghibli-option`, `.ghibli-drop-slot`, `.ghibli-matching-select` elements on page.
- `#ghibliScoreBadge`: Displays `Score: X / Y`.
- `.ghibli-audio-btn[data-audio]`: Plays native audio MP3 or triggers `window.speechSynthesis`.
- `.ghibli-rec-btn`: Handles voice recording and playback.
- `.chapter-nav-bar`: Previous Page (`.nav-prev`), Next Page (`.nav-next`), Home Hub (`.nav-home`).
