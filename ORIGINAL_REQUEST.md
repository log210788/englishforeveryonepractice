# Original User Request

## Initial Request — 2026-08-13T07:19:33Z

Expand the Studio Ghibli Interactive Edition (`englishForEveryoneOne`) into individual interactive HTML pages for all textbook pages in `output_json/all_pages_consolidated.json`. Each page containing exercises (pages 8 through 176) should have its own dedicated HTML page (e.g., `ghibli_p008.html`, `ghibli_p009.html`, `ghibli_p016.html`, etc.).

Working directory: e:\class aids\code\englishForEveryoneOne
Integrity mode: development

## Requirements

### R1. Textbook Page-by-Page Interactive Implementation
- Create individual HTML files corresponding to each page in `output_json/all_pages_consolidated.json` (e.g., `ghibli_p008.html` through `ghibli_p176.html` for pages with exercises).
- Extract and build all exact exercises, items, questions, and options from the JSON data for each page.
- Support all exercise types: fill-in-the-blank, sentence rewrites, multiple choice, audio matching, and drag-and-drop order.

### R2. Studio Ghibli Theme & Navigation Framework
- Every page must include:
  - Atmospheric Time-of-Day theme switcher (Day, Sunset, Night).
  - Background imagery mapped to the chapter's location theme.
  - Native audio play buttons mapped to `audio/{unit}/{file}.mp3` (with web speech synthesis fallbacks).
  - Voice recorder (`Rec` / `My Voice`) for speaking practice on items.
  - Kodama companion mascot widget with Pomodoro timer and Teacher Lewis story narration.
  - Page/Chapter navigation bar allowing easy movement to previous/next pages and returning to Home Hub (`index.html`).

### R3. Interactive Grading & Progress Tracking
- Instant "Check Answers" validation for every page that highlights correct/incorrect inputs, plays sound chimes, updates score badges, and triggers responsive mascot reactions (celebrate/encouragement).

## Acceptance Criteria

### Content & Page Coverage
- [ ] Every page in `output_json/all_pages_consolidated.json` with exercises has a working `ghibli_pXXX.html` file.
- [ ] All inputs accept student responses and validate accurately against `correct_answer` fields in the dataset.

### Visual & Interactive Quality
- [ ] Audio playback, voice recording, and time-of-day background switching function on every generated page without console errors.
- [ ] Next/Previous page buttons allow smooth step-by-step reading through the whole book.
