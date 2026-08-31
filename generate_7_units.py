#!/usr/bin/env python3
"""
generate_7_units.py
Generates the 7 primary Unit HTML files according to the user's specification:
- Unit 1: 1.1 to 8.10 (Pages 12-29)
- Unit 2: 9.1 to 14.8 (Pages 30-45)
- Unit 3: 15.1 to 19.9 (Pages 46-63)
- Unit 4: 20.1 to 26.4 (Pages 64-85)
- Unit 5: 27.1 to 35.6 (Pages 86-115)
- Unit 6: 36.1 to 42.6 (Pages 116-137)
- Unit 7: 43.1 to 48.8 (Pages 138-155)
"""

import json
import os
import sys
import re
import html
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

import generate_ghibli_pages as gen

UNITS_SPEC = [
    {
        "unit_id": 1,
        "title": "Introducing Yourself & Your Belongings",
        "icon": "fa-seedling",
        "emoji": "🌿",
        "start_page": 12,
        "end_page": 29,
        "exercise_range": "1.1 – 8.10",
        "theme_bg": "images/ghibli/bg.jpg",
        "theme_night": "images/ghibli/night.jpg",
        "theme_sunset": "images/ghibli/sunset.jpg",
        "accent": "#2d5a27",
        "desc": "Master greetings, saying your name, countries, family members, possessions, and demonstrative pronouns (this, that, these, those)."
    },
    {
        "unit_id": 2,
        "title": "Jobs, Time & Daily Life",
        "icon": "fa-train",
        "emoji": "🚂",
        "start_page": 30,
        "end_page": 45,
        "exercise_range": "9.1 – 14.8",
        "theme_bg": "images/ghibli/bg.jpg",
        "theme_night": "images/ghibli/night.jpg",
        "theme_sunset": "images/ghibli/sunset.jpg",
        "accent": "#3a6073",
        "desc": "Learn occupations, talking about your job, telling the time, daily habits, and weekly schedules using present simple."
    },
    {
        "unit_id": 3,
        "title": "Negatives & Questions",
        "icon": "fa-cloud",
        "emoji": "☁️",
        "start_page": 46,
        "end_page": 63,
        "exercise_range": "15.1 – 19.9",
        "theme_bg": "images/ghibli/bg.jpg",
        "theme_night": "images/ghibli/night.jpg",
        "theme_sunset": "images/ghibli/sunset.jpg",
        "accent": "#4a69bd",
        "desc": "Form negative statements with 'to be' and present simple, ask simple and open questions, and give short natural answers."
    },
    {
        "unit_id": 4,
        "title": "Towns, Places & Giving Directions",
        "icon": "fa-anchor",
        "emoji": "⚓",
        "start_page": 64,
        "end_page": 85,
        "exercise_range": "20.1 – 26.4",
        "theme_bg": "images/ghibli/bg.jpg",
        "theme_night": "images/ghibli/night.jpg",
        "theme_sunset": "images/ghibli/sunset.jpg",
        "accent": "#1e3799",
        "desc": "Explore town places, describe locations with 'there is/are', use articles ('a/the'), give directions, and explain reasons with 'because'."
    },
    {
        "unit_id": 5,
        "title": "Around the House, Food & Shopping",
        "icon": "fa-tree",
        "emoji": "🌳",
        "start_page": 86,
        "end_page": 115,
        "exercise_range": "27.1 – 35.6",
        "theme_bg": "images/ghibli/bg.jpg",
        "theme_night": "images/ghibli/night.jpg",
        "theme_sunset": "images/ghibli/sunset.jpg",
        "accent": "#38ada9",
        "desc": "Vocabulary for household items, asking 'What do you have?', food & drink, countable & uncountable nouns, quantities, and shopping."
    },
    {
        "unit_id": 6,
        "title": "Sports, Free Time & Preferences",
        "icon": "fa-person-swimming",
        "emoji": "⛵",
        "start_page": 116,
        "end_page": 137,
        "exercise_range": "36.1 – 42.6",
        "theme_bg": "images/ghibli/bg.jpg",
        "theme_night": "images/ghibli/night.jpg",
        "theme_sunset": "images/ghibli/sunset.jpg",
        "accent": "#e58e26",
        "desc": "Talk about sports using 'go' and 'play', pastimes, frequency adverbs (always/never), likes/dislikes, and music preferences."
    },
    {
        "unit_id": 7,
        "title": "Abilities, Actions & Studying",
        "icon": "fa-graduation-cap",
        "emoji": "📚",
        "start_page": 138,
        "end_page": 155,
        "exercise_range": "43.1 – 48.8",
        "theme_bg": "images/ghibli/bg.jpg",
        "theme_night": "images/ghibli/night.jpg",
        "theme_sunset": "images/ghibli/sunset.jpg",
        "accent": "#6a89cc",
        "desc": "Express what you can and cannot do, describe actions with adverbs, state wishes and ambitions ('would like'), and talk about studies."
    }
]

def load_pages_by_number():
    all_pages = gen.load_pages()
    pages_dict = {}
    for p in all_pages:
        pages_dict[p["page_number"]] = p
    return pages_dict

def generate_unit_html(unit_spec, pages_dict):
    unit_id = unit_spec["unit_id"]
    unit_title = unit_spec["title"]
    start_p = unit_spec["start_page"]
    end_p = unit_spec["end_page"]
    ex_range = unit_spec["exercise_range"]
    desc = unit_spec["desc"]
    emoji = unit_spec["emoji"]
    accent = unit_spec["accent"]

    unit_pages = []
    for p_num in range(start_p, end_p + 1):
        if p_num in pages_dict:
            unit_pages.append(pages_dict[p_num])

    # Count total interactive items
    total_items = 0
    for p in unit_pages:
        total_items += gen.count_total_items(p.get("exercises", []))

    # Build Navigation Bar
    nav_pills_html = []
    for u in UNITS_SPEC:
        active_cls = " active" if u["unit_id"] == unit_id else ""
        nav_pills_html.append(f'<a href="unit{u["unit_id"]}.html" class="ch-nav-pill{active_cls}">Unit {u["unit_id"]}</a>')
    nav_pills_str = "\n".join(nav_pills_html)

    prev_link = f'unit{unit_id - 1}.html' if unit_id > 1 else 'index.html'
    next_link = f'unit{unit_id + 1}.html' if unit_id < 7 else 'index.html'
    prev_label = f'Unit {unit_id - 1}' if unit_id > 1 else 'Home Hub'
    next_label = f'Unit {unit_id + 1}' if unit_id < 7 else 'Finish Course 🌿'

    # Build exercises section with page markers
    exercises_html = []
    for p in unit_pages:
        p_num = p["page_number"]
        ex_list = p.get("exercises", [])
        if not ex_list:
            continue
        
        _, sub_title, sub_desc, new_lang, vocab, new_skill = gen.get_unit_info(p_num)

        exercises_html.append(f'''
      <!-- PAGE {p_num} SECTION -->
      <div class="page-divider-banner" style="margin: 36px 0 20px 0; display: flex; align-items: center; justify-content: space-between; padding: 12px 20px; background: rgba(255,255,255,0.85); border-left: 5px solid {accent}; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.04);">
        <div>
          <span style="font-size: 0.85rem; font-weight: 800; text-transform: uppercase; letter-spacing: 1px; color: {accent};">📖 Page {p_num} • {html.escape(sub_title)}</span>
          <div style="font-size: 0.85rem; color: #555; margin-top: 2px;">{html.escape(new_lang)} • {html.escape(vocab)}</div>
        </div>
        <a href="ghibli_reader.html?page={p_num}" class="ghibli-btn ghibli-btn-secondary" style="font-size: 0.78rem; padding: 4px 12px;" title="Open in Continuous Reader">
          <i class="fa-solid fa-headphones"></i> Reader View
        </a>
      </div>
''')

        for ex_idx, ex in enumerate(ex_list):
            rendered_ex = gen.render_exercise(ex, ex_idx, p_num)
            exercises_html.append(rendered_ex)

    body_exercises = "\n".join(exercises_html)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Teacher Lewis's Practice Book • Unit {unit_id}: {html.escape(unit_title)} (Exercises {ex_range}) | Studio Ghibli Edition</title>
  
  <style>
    img {{ max-width: 100%; height: auto; display: block; }}
    .ghibli-avatar-wrap {{ width: 76px; height: 76px; position: relative; flex-shrink: 0; }}
    .ghibli-avatar-img {{ width: 76px; height: 76px; max-width: 76px; max-height: 76px; border-radius: 50%; object-fit: cover; }}
    .mascot-avatar-wrap {{ width: 220px; height: 220px; position: relative; flex-shrink: 0; }}
    .mascot-avatar {{ width: 220px; height: 220px; max-width: 220px; max-height: 220px; border-radius: 50%; object-fit: cover; }}
  </style>

  <!-- Google Fonts -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Outfit:wght@500;600;700;800&display=swap" rel="stylesheet">
  
  <!-- FontAwesome Icons -->
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  
  <!-- Shared CSS Tokens -->
  <link rel="stylesheet" href="ghibli_theme.css">
  
  <style>
    :root {{
      --ghibli-bg-url: url('images/ghibli/bg.jpg');
      --ghibli-accent-gold: {accent};
    }}
    body.theme-night {{ --ghibli-bg-url: url('images/ghibli/night.jpg'); }}
    body.theme-sunset {{ --ghibli-bg-url: url('images/ghibli/sunset.jpg'); }}
    .chapter-nav-bar {{ display: flex; align-items: center; justify-content: center; gap: 8px; padding: 10px 20px; flex-wrap: wrap; background: rgba(255,255,255,0.12); backdrop-filter: blur(8px); border-radius: 40px; margin: 0 auto 16px auto; max-width: 700px; }}
    .ch-nav-pill {{ display: inline-flex; align-items: center; gap: 6px; padding: 6px 14px; border-radius: 20px; font-size: 0.78rem; font-weight: 700; text-decoration: none; transition: all 0.2s; border: 2px solid transparent; color: rgba(255,255,255,0.85); background: rgba(255,255,255,0.15); }}
    .ch-nav-pill:hover {{ background: rgba(255,255,255,0.3); color: #fff; transform: translateY(-1px); }}
    .ch-nav-pill.active {{ background: var(--ghibli-accent-gold); color: #fff; border-color: rgba(255,255,255,0.4); }}
  </style>
</head>
<body class="theme-day">
  <div class="ghibli-bg-overlay"></div>
  <div class="ghibli-vignette"></div>
  <div id="firefliesContainer"></div>

  <div class="ghibli-container">
    <header class="ghibli-header">
      <a href="index.html" class="ghibli-brand">
        <div class="ghibli-logo-badge"><i class="fa-solid fa-seedling"></i></div>
        <div class="ghibli-title-wrap">
          <h1>Teacher Lewis's Practice Book</h1>
          <span class="ghibli-subtitle">{emoji} Unit {unit_id}: {html.escape(unit_title)} (Exercises {ex_range})</span>
        </div>
      </a>
      <div class="ghibli-header-actions">
        <a href="index.html" class="ghibli-btn ghibli-btn-secondary"><i class="fa-solid fa-house"></i> Home Hub</a>
        <a href="ghibli_reader.html?page={start_p}" class="ghibli-btn ghibli-btn-gold" title="Continuous Music Reader Mode"><i class="fa-solid fa-headphones"></i> Reader Mode</a>
        <button class="ghibli-btn ghibli-btn-secondary" id="toggleAmbientBtn" title="Toggle Background Music"><i class="fa-solid fa-music"></i> <span class="bgm-btn-text">Music: Off</span></button>
        <div class="tod-group">
          <button class="tod-btn active" data-theme="day">☀️ Day</button>
          <button class="tod-btn" data-theme="sunset">🌅 Sunset</button>
          <button class="tod-btn" data-theme="night">🌙 Night</button>
        </div>
        <div class="ghibli-score-badge" id="ghibliScoreBadge"><i class="fa-solid fa-star"></i> <span id="ghibliScoreText">Score: 0 / {total_items}</span></div>
        <button class="ghibli-btn ghibli-btn-primary" id="ghibliCheckAnswersBtn"><i class="fa-solid fa-circle-check"></i> Check Answers</button>
        <button class="ghibli-btn ghibli-btn-secondary" id="ghibliResetBtn"><i class="fa-solid fa-rotate-left"></i> Reset</button>
      </div>
    </header>

    <div class="chapter-nav-bar">
      {nav_pills_str}
    </div>

    <!-- Unit Hero Card -->
    <div class="ghibli-hero-card">
      <span class="ghibli-unit-tag"><i class="fa-solid {unit_spec['icon']}"></i> Unit {unit_id} (Exercises {ex_range} • Pages {start_p}–{end_p})</span>
      <h2 class="ghibli-hero-title">{html.escape(unit_title)}</h2>
      <p class="ghibli-hero-desc">{html.escape(desc)}</p>
    </div>

    <main class="ghibli-exercises-wrap">
      {body_exercises}
    </main>

    <!-- Bottom Navigation -->
    <div class="chapter-nav-bar" style="margin-top: 36px;">
      <a href="{prev_link}" class="ghibli-btn ghibli-btn-secondary"><i class="fa-solid fa-arrow-left"></i> {prev_label}</a>
      <span style="font-weight: 700; color: #fff; font-size: 0.9rem;">Unit {unit_id} of 7 • Pages {start_p}–{end_p}</span>
      <a href="{next_link}" class="ghibli-btn ghibli-btn-primary">{next_label} <i class="fa-solid fa-arrow-right"></i></a>
    </div>

    <!-- Kodama Mascot Widget -->
    <div class="kodama-widget" id="kodamaWidget">
      <div class="kodama-mascot-img-wrap">
        <img src="images/ghibli/mascot.jpg" alt="Kodama Mascot" class="kodama-mascot-img">
      </div>
      <div class="mascot-bubble" id="mascotBubble">
        Welcome to Unit {unit_id}: {html.escape(unit_title)}! Complete all exercises from {ex_range}! 🌿
      </div>
    </div>
  </div>

  <script src="ghibli_audio.js"></script>
  <script src="ghibli_page_engine.js"></script>
</body>
</html>
"""
    return html_content

def main():
    print("🚀 Generating 7 Primary Unit HTML Pages...")
    pages_dict = load_pages_by_number()
    print(f"Loaded {len(pages_dict)} pages from dataset.")

    for spec in UNITS_SPEC:
        u_id = spec["unit_id"]
        content = generate_unit_html(spec, pages_dict)
        
        # Write unitX.html and ghibli_unitX.html
        fn1 = f"unit{u_id}.html"
        fn2 = f"ghibli_unit{u_id}.html"
        
        with open(fn1, "w", encoding="utf-8") as f:
            f.write(content)
        with open(fn2, "w", encoding="utf-8") as f:
            f.write(content)
            
        print(f"  ✅ Generated {fn1} and {fn2} (Unit {u_id}: {spec['exercise_range']} • Pages {spec['start_page']}-{spec['end_page']})")

    print("✨ All 7 Unit files generated successfully!")

if __name__ == "__main__":
    main()
