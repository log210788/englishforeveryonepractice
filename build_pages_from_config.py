import json
import os
import re

with open('images/everyDayThings/items_config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

p24_items = config['p24']
p25_items = config['p25']

def get_img_src(rel_path):
    if os.path.exists(rel_path):
        mtime = int(os.path.getmtime(rel_path))
        return f"{rel_path}?v={mtime}"
    return rel_path

p24_words = [
    'wallet', 'notepad', 'sunglasses', 'keys', 'ID card', 'letter',
    'toothbrush', 'hairbrush', 'pencil', 'dictionary', 'apple', 'book',
    'passport', 'magazine', 'camera', 'glasses'
]

p25_words = [
    'pen', 'necklace', 'newspaper', 'bottle of water', 'laptop', 'earphones',
    'tablet', 'mirror', 'coins', 'map', 'umbrella', 'sandwich'
]

# ----------------- PAGE 24 -----------------
with open('ghibli_p024.html', 'r', encoding='utf-8') as f:
    p24_raw = f.read()

cards24 = []
for it in p24_items:
    img_url = get_img_src(it['img'])
    if it['is_example']:
        c = f'''          <div class="ghibli-char-card example-card" style="display:flex; flex-direction:column; align-items:center; text-align:center; padding:18px 16px; background:rgba(255,255,255,0.95); border-radius:20px; border:2px solid #2d5a27; box-shadow:0 6px 18px rgba(45,90,39,0.12); box-sizing:border-box; width:100%;">
            <div style="display:flex; justify-content:space-between; align-items:center; width:100%; margin-bottom:12px;">
              <div style="display:flex; align-items:center; gap:8px;">
                <span class="item-index" style="font-weight:800; color:#2d5a27; font-size:1.1rem;">{it['num']}</span>
                <span class="ghibli-example-badge" style="background:#2d5a27; color:#fff; padding:3px 10px; border-radius:12px; font-weight:700; font-size:0.75rem; text-transform:uppercase;">Example</span>
              </div>
              <div style="display:flex; align-items:center; gap:6px;">
                <button class="ghibli-audio-play-btn" data-audio="{it['audio']}" title="Play Audio"><i class="fa-solid fa-play"></i></button>
                <div class="voice-recorder-controls">
                  <button class="voice-btn rec-btn" data-id="{it['rec_id']}"><i class="fa-solid fa-microphone"></i> Rec</button>
                  <button class="voice-btn play-rec-btn hidden" data-id="{it['rec_id']}"><i class="fa-solid fa-play"></i> My Voice</button>
                </div>
              </div>
            </div>
            <div class="everyday-obj-img-wrap" style="width:100%; height:130px; display:flex; align-items:center; justify-content:center; background:#fbf8f2; border-radius:14px; border:1px solid #ebdcc5; margin-bottom:14px; padding:8px; box-sizing:border-box;">
              <img src="{img_url}" alt="{it['correct']}" style="max-width:100%; max-height:100%; object-fit:contain; filter:drop-shadow(0 4px 6px rgba(0,0,0,0.12));" loading="eager" decoding="async">
            </div>
            <div class="ghibli-input-wrap" style="width:100%; box-sizing:border-box;">
              <input type="text" class="ghibli-input example-input" data-correct="{it['correct']}" value="{it['correct']}" readonly style="width:100%; min-width:0; max-width:100%; box-sizing:border-box; text-align:center; font-size:1.02rem; font-weight:700; padding:10px 12px; border-radius:12px; border-color:#2d5a27; background:rgba(45,90,39,0.12); color:#2d5a27;">
            </div>
          </div>'''
    else:
        c = f'''          <div class="ghibli-char-card" style="display:flex; flex-direction:column; align-items:center; text-align:center; padding:18px 16px; background:rgba(255,255,255,0.92); border-radius:20px; border:1.5px solid #e2d7c3; box-shadow:0 6px 18px rgba(0,0,0,0.06); box-sizing:border-box; width:100%;">
            <div style="display:flex; justify-content:space-between; align-items:center; width:100%; margin-bottom:12px;">
              <span class="item-index" style="font-weight:800; color:#2d5a27; font-size:1.1rem;">{it['num']}</span>
              <div style="display:flex; align-items:center; gap:6px;">
                <button class="ghibli-audio-play-btn" data-audio="{it['audio']}" title="Play Audio"><i class="fa-solid fa-play"></i></button>
                <div class="voice-recorder-controls">
                  <button class="voice-btn rec-btn" data-id="{it['rec_id']}"><i class="fa-solid fa-microphone"></i> Rec</button>
                  <button class="voice-btn play-rec-btn hidden" data-id="{it['rec_id']}"><i class="fa-solid fa-play"></i> My Voice</button>
                </div>
              </div>
            </div>
            <div class="everyday-obj-img-wrap" style="width:100%; height:130px; display:flex; align-items:center; justify-content:center; background:#fbf8f2; border-radius:14px; border:1px solid #ebdcc5; margin-bottom:14px; padding:8px; box-sizing:border-box;">
              <img src="{img_url}" alt="Everyday Object" style="max-width:100%; max-height:100%; object-fit:contain; filter:drop-shadow(0 4px 6px rgba(0,0,0,0.12));" loading="eager" decoding="async">
            </div>
            <div class="ghibli-input-wrap" style="width:100%; box-sizing:border-box;">
              <input type="text" class="ghibli-input" data-correct="{it['correct']}" placeholder="Type answer..." autocomplete="off" style="width:100%; min-width:0; max-width:100%; box-sizing:border-box; text-align:center; font-size:1.02rem; font-weight:600; padding:10px 12px; border-radius:12px; border:1.5px solid #d4c5a9; background:#fff;">
            </div>
          </div>'''
    cards24.append(c)

chips24 = ' '.join([f'<span class="word-chip word-panel-tag" style="background:#fff; padding:6px 14px; border-radius:12px; font-weight:600; font-size:0.95rem; color:#2b261f; border:1.5px solid #dcd1be; box-shadow:0 2px 4px rgba(0,0,0,0.04); display:inline-block; margin:4px; cursor:default;">{w}</span>' for w in p24_words])

sec24 = f'''    <section class="ghibli-section">
      <div class="ghibli-section-header">
        <div class="ghibli-ex-num">7.1</div>
        <div>
          <h3 class="ghibli-ex-instruction">EVERYDAY THINGS • WRITE THE WORDS FROM THE PANEL UNDER THE CORRECT PICTURES</h3>
          <p class="ghibli-ex-subtext">Look at each illustration, listen to the pronunciation, and type the correct word under each picture!</p>
        </div>
      </div>
      <div class="ghibli-word-bank-panel" style="background:rgba(255,255,255,0.75); backdrop-filter:blur(10px); border-radius:18px; padding:18px 22px; margin-bottom:28px; border:1.5px solid #d4c5a9; box-shadow:0 4px 14px rgba(0,0,0,0.05);">
        <div style="display:flex; align-items:center; gap:8px; margin-bottom:12px; font-weight:800; color:#2d5a27; font-size:1rem;"><i class="fa-solid fa-layer-group"></i> <span>Word Panel</span></div>
        <div style="display:flex; flex-wrap:wrap; gap:8px;">{chips24}</div>
      </div>
      <div class="everyday-grid" style="display:grid; grid-template-columns:repeat(auto-fill, minmax(210px, 1fr)); gap:20px;">
{chr(10).join(cards24)}
      </div>
    </section>'''

p24_final = re.sub(r'<section class="ghibli-section">.*?</section>', sec24, p24_raw, flags=re.DOTALL)
p24_final = p24_final.replace('Unit 1 • Lesson: Everyday Things', 'Unit 7 • Lesson: Everyday Things')
p24_final = p24_final.replace('Unit 1 • Page 24', 'Unit 7 • Page 24')

with open('ghibli_p024.html', 'w', encoding='utf-8') as f:
    f.write(p24_final)
with open('ghibli_page024.html', 'w', encoding='utf-8') as f:
    f.write(p24_final)
print('Updated ghibli_p024.html & ghibli_page024.html')

# ----------------- PAGE 25 (Same Format as Page 24, Exercise 7.1 Continued) -----------------
with open('ghibli_p025.html', 'r', encoding='utf-8') as f:
    p25_raw = f.read()

cards25 = []
for it in p25_items:
    img_url = get_img_src(it['img'])
    c = f'''          <div class="ghibli-char-card" style="display:flex; flex-direction:column; align-items:center; text-align:center; padding:18px 16px; background:rgba(255,255,255,0.92); border-radius:20px; border:1.5px solid #e2d7c3; box-shadow:0 6px 18px rgba(0,0,0,0.06); box-sizing:border-box; width:100%;">
            <div style="display:flex; justify-content:space-between; align-items:center; width:100%; margin-bottom:12px;">
              <span class="item-index" style="font-weight:800; color:#2d5a27; font-size:1.1rem;">{it['num']}</span>
              <div style="display:flex; align-items:center; gap:6px;">
                <button class="ghibli-audio-play-btn" data-audio="{it['audio']}" title="Play Audio"><i class="fa-solid fa-play"></i></button>
                <div class="voice-recorder-controls">
                  <button class="voice-btn rec-btn" data-id="{it['rec_id']}"><i class="fa-solid fa-microphone"></i> Rec</button>
                  <button class="voice-btn play-rec-btn hidden" data-id="{it['rec_id']}"><i class="fa-solid fa-play"></i> My Voice</button>
                </div>
              </div>
            </div>
            <div class="everyday-obj-img-wrap" style="width:100%; height:130px; display:flex; align-items:center; justify-content:center; background:#fbf8f2; border-radius:14px; border:1px solid #ebdcc5; margin-bottom:14px; padding:8px; box-sizing:border-box;">
              <img src="{img_url}" alt="Everyday Object" style="max-width:100%; max-height:100%; object-fit:contain; filter:drop-shadow(0 4px 6px rgba(0,0,0,0.12));" loading="eager" decoding="async">
            </div>
            <div class="ghibli-input-wrap" style="width:100%; box-sizing:border-box;">
              <input type="text" class="ghibli-input" data-correct="{it['correct']}" placeholder="Type answer..." autocomplete="off" style="width:100%; min-width:0; max-width:100%; box-sizing:border-box; text-align:center; font-size:1.02rem; font-weight:600; padding:10px 12px; border-radius:12px; border:1.5px solid #d4c5a9; background:#fff;">
            </div>
          </div>'''
    cards25.append(c)

chips25 = ' '.join([f'<span class="word-chip word-panel-tag" style="background:#fff; padding:6px 14px; border-radius:12px; font-weight:600; font-size:0.95rem; color:#2b261f; border:1.5px solid #dcd1be; box-shadow:0 2px 4px rgba(0,0,0,0.04); display:inline-block; margin:4px; cursor:default;">{w}</span>' for w in p25_words])

sec25 = f'''    <section class="ghibli-section">
      <div class="ghibli-section-header">
        <div class="ghibli-ex-num">7.1</div>
        <div>
          <h3 class="ghibli-ex-instruction">EVERYDAY THINGS • WRITE THE WORDS FROM THE PANEL UNDER THE CORRECT PICTURES</h3>
          <p class="ghibli-ex-subtext">Look at each illustration, listen to the pronunciation, and type the correct word under each picture!</p>
        </div>
      </div>
      <div class="ghibli-word-bank-panel" style="background:rgba(255,255,255,0.75); backdrop-filter:blur(10px); border-radius:18px; padding:18px 22px; margin-bottom:28px; border:1.5px solid #d4c5a9; box-shadow:0 4px 14px rgba(0,0,0,0.05);">
        <div style="display:flex; align-items:center; gap:8px; margin-bottom:12px; font-weight:800; color:#2d5a27; font-size:1rem;"><i class="fa-solid fa-layer-group"></i> <span>Word Panel</span></div>
        <div style="display:flex; flex-wrap:wrap; gap:8px;">{chips25}</div>
      </div>
      <div class="everyday-grid" style="display:grid; grid-template-columns:repeat(auto-fill, minmax(210px, 1fr)); gap:20px;">
{chr(10).join(cards25)}
      </div>
    </section>'''

p25_final = re.sub(r'<section class="ghibli-section">.*?</section>', sec25, p25_raw, flags=re.DOTALL)
p25_final = p25_final.replace('Unit 1 • Lesson: Everyday Things', 'Unit 7 • Lesson: Everyday Things')
p25_final = p25_final.replace('Unit 1 • Page 25', 'Unit 7 • Page 25')

# Ensure critical CSS includes everyday-grid on page 25 as well
if '.everyday-grid' not in p25_final:
    p25_final = p25_final.replace('</style>', '''    .everyday-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(210px, 1fr)); gap: 20px; }
    @media (max-width: 600px) {
      .everyday-grid { grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 14px; }
    }
  </style>''')

with open('ghibli_p025.html', 'w', encoding='utf-8') as f:
    f.write(p25_final)
with open('ghibli_page025.html', 'w', encoding='utf-8') as f:
    f.write(p25_final)
print('Updated ghibli_p025.html & ghibli_page025.html')
