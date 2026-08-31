# unit2_builders.py
# Specialized exercise builders for Unit 2 (Pages 30-45)
# Studio Ghibli Interactive Edition

import os
import re
import html
import json

def escape(val):
    return html.escape(str(val or ""))

def get_mtime_src(rel_path):
    if os.path.exists(rel_path):
        mtime = int(os.path.getmtime(rel_path))
        return f"{rel_path}?v={mtime}"
    return rel_path

def render_workplaces_10_4(ex, ex_idx, page_num):
    """Page 33 Ex 10.4: Match pictures of workplaces to correct labels."""
    ex_id = "10.4"
    instruction = "MATCH THE PICTURES TO THE CORRECT LABELS"
    
    items = [
        {"num": "1", "target": "theater", "audio": "audio/10/10_4_eg.mp3", "img": "images/jobs/workplaces/theater.png", "is_eg": True},
        {"num": "2", "target": "laboratory", "audio": "audio/10/10_4_1.mp3", "img": "images/jobs/workplaces/laboratory.png", "is_eg": False},
        {"num": "3", "target": "restaurant", "audio": "audio/10/10_4_2.mp3", "img": "images/jobs/workplaces/restaurant.png", "is_eg": False},
        {"num": "4", "target": "garden", "audio": "audio/10/10_4_3.mp3", "img": "images/jobs/workplaces/garden.png", "is_eg": False},
        {"num": "5", "target": "hospital", "audio": "audio/10/10_4_4.mp3", "img": "images/jobs/workplaces/hospital.png", "is_eg": False},
        {"num": "6", "target": "school", "audio": "audio/10/10_4_5.mp3", "img": "images/jobs/workplaces/school.png", "is_eg": False}
    ]
    
    options = ["theater", "laboratory", "restaurant", "garden", "hospital", "school"]
    
    cards = []
    for idx, it in enumerate(items):
        img_src = get_mtime_src(it["img"])
        correct = it["target"]
        item_id = f"p33_ex2_i{idx+1}"
        
        if it["is_eg"]:
            cards.append(f'''
            <div class="ghibli-char-card example-card" style="display:flex; flex-direction:column; align-items:center; text-align:center; padding:18px 16px; background:rgba(255,255,255,0.95); border-radius:20px; border:2px solid #2d5a27; box-shadow:0 6px 18px rgba(45,90,39,0.12); box-sizing:border-box;">
              <div style="display:flex; justify-content:space-between; align-items:center; width:100%; margin-bottom:12px;">
                <div style="display:flex; align-items:center; gap:8px;">
                  <span class="item-index" style="font-weight:800; color:#2d5a27; font-size:1.1rem;">{it["num"]}.</span>
                  <span class="ghibli-example-badge" style="background:#2d5a27; color:#fff; padding:3px 10px; border-radius:12px; font-weight:700; font-size:0.75rem; text-transform:uppercase;">Example</span>
                </div>
                <button class="ghibli-audio-play-btn" data-audio="{it["audio"]}" title="Play Audio"><i class="fa-solid fa-play"></i></button>
              </div>
              <div style="width:100%; height:130px; display:flex; align-items:center; justify-content:center; background:#fff; border-radius:14px; border:1px solid #ebdcc5; margin-bottom:14px; padding:6px; box-sizing:border-box;">
                <img src="{img_src}" alt="{correct}" style="max-width:100%; max-height:100%; object-fit:contain; filter:drop-shadow(0 4px 6px rgba(0,0,0,0.10));" loading="eager" decoding="async">
              </div>
              <div style="width:100%;">
                <input type="text" class="ghibli-input example-input" data-correct="{correct}" value="{correct}" readonly style="width:100%; text-align:center; font-weight:700; border-color:#2d5a27; background:rgba(45,90,39,0.12); color:#2d5a27;">
              </div>
            </div>
            ''')
        else:
            opt_tags = [f'<option value="{opt}">{opt}</option>' for opt in options]
            cards.append(f'''
            <div class="ghibli-char-card" style="display:flex; flex-direction:column; align-items:center; text-align:center; padding:18px 16px; background:rgba(255,255,255,0.92); border-radius:20px; border:1.5px solid #e2d7c3; box-shadow:0 6px 18px rgba(0,0,0,0.06); box-sizing:border-box;">
              <div style="display:flex; justify-content:space-between; align-items:center; width:100%; margin-bottom:12px;">
                <span class="item-index" style="font-weight:800; color:#2d5a27; font-size:1.1rem;">{it["num"]}.</span>
                <div style="display:flex; align-items:center; gap:6px;">
                  <button class="ghibli-audio-play-btn" data-audio="{it["audio"]}" title="Play Audio"><i class="fa-solid fa-play"></i></button>
                  <div class="voice-recorder-controls">
                    <button class="voice-btn rec-btn" data-id="{item_id}"><i class="fa-solid fa-microphone"></i> Rec</button>
                    <button class="voice-btn play-rec-btn hidden" data-id="{item_id}"><i class="fa-solid fa-play"></i> My Voice</button>
                  </div>
                </div>
              </div>
              <div style="width:100%; height:130px; display:flex; align-items:center; justify-content:center; background:#fff; border-radius:14px; border:1px solid #ebdcc5; margin-bottom:14px; padding:6px; box-sizing:border-box;">
                <img src="{img_src}" alt="Workplace" style="max-width:100%; max-height:100%; object-fit:contain; filter:drop-shadow(0 4px 6px rgba(0,0,0,0.10));" loading="eager" decoding="async">
              </div>
              <div style="width:100%;">
                <select class="ghibli-input ghibli-matching-select" data-correct="{correct}" style="width:100%; padding:10px 12px; border-radius:12px; border:1.5px solid #d4c5a9; background:#fff; font-weight:600; text-align:center; cursor:pointer;">
                  <option value="">-- Choose workplace --</option>
                  {'\n'.join(opt_tags)}
                </select>
              </div>
            </div>
            ''')
            
    chips_html = ' '.join([f'<span class="word-chip word-panel-tag" style="background:#fff; padding:6px 14px; border-radius:12px; font-weight:600; font-size:0.95rem; color:#2b261f; border:1.5px solid #dcd1be; box-shadow:0 2px 4px rgba(0,0,0,0.04); display:inline-block; margin:4px; cursor:default;">{w}</span>' for w in options])

    return f'''
    <section class="ghibli-section">
      <div class="ghibli-section-header">
        <div class="ghibli-ex-num">{ex_id}</div>
        <div>
          <h3 class="ghibli-ex-instruction">{instruction}</h3>
          <p class="ghibli-ex-subtext">Look at each illustration, listen to the pronunciation, and match the correct workplace!</p>
        </div>
      </div>
      <div class="ghibli-word-bank-panel" style="background:rgba(255,255,255,0.75); backdrop-filter:blur(10px); border-radius:18px; padding:18px 22px; margin-bottom:28px; border:1.5px solid #d4c5a9; box-shadow:0 4px 14px rgba(0,0,0,0.05);">
        <div style="display:flex; align-items:center; gap:8px; margin-bottom:12px; font-weight:800; color:#2d5a27; font-size:1rem;"><i class="fa-solid fa-building"></i> <span>Workplace Labels</span></div>
        <div style="display:flex; flex-wrap:wrap; gap:8px;">{chips_html}</div>
      </div>
      <div style="display:grid; grid-template-columns:repeat(auto-fill, minmax(220px, 1fr)); gap:20px;">
        {'\n'.join(cards)}
      </div>
    </section>
    '''

def render_spoken_scenes_10_6(ex, ex_idx, page_num):
    """Page 34 Ex 10.6: Spoken practice with character work scenes."""
    ex_id = "10.6"
    instruction = "LOOK AT THE PICTURES AND SAY THE SENTENCES OUT LOUD, USING THE WORDS IN THE PANEL"
    
    items = [
        {"name": "Eric", "pronoun": "He", "job": "waiter", "place": "restaurant", "prep": "in", "img": "images/jobs/scenes/eric_waiter.png", "is_eg": True},
        {"name": "Abby", "pronoun": "She", "job": "nurse", "place": "hospital", "prep": "in", "img": "images/jobs/scenes/abby_nurse.png", "is_eg": False},
        {"name": "Julie", "pronoun": "She", "job": "engineer", "place": "construction site", "prep": "on", "article": "an", "is_eg": False, "img": "images/jobs/scenes/julie_engineer.png"},
        {"name": "Simon", "pronoun": "He", "job": "gardener", "place": "park", "prep": "in", "img": "images/jobs/scenes/simon_gardener.png", "is_eg": False},
        {"name": "Adam", "pronoun": "He", "job": "police officer", "place": "police station", "prep": "in", "img": "images/jobs/scenes/adam_police.png", "is_eg": False},
        {"name": "Max", "pronoun": "He", "job": "farmer", "place": "farm", "prep": "on", "img": "images/jobs/scenes/max_farmer.png", "is_eg": False},
        {"name": "Carol", "pronoun": "She", "job": "hairdresser", "place": "beauty salon", "prep": "in", "img": "images/jobs/scenes/carol_hairdresser.png", "is_eg": False}
    ]
    
    words_panel = ["waiter", "police officer", "park", "nurse", "hairdresser", "restaurant", "engineer", "police station", "hospital", "beauty salon", "gardener", "farm", "construction site", "farmer"]
    chips_html = ' '.join([f'<span class="word-chip word-panel-tag" style="background:#fff; padding:6px 14px; border-radius:12px; font-weight:600; font-size:0.95rem; color:#2b261f; border:1.5px solid #dcd1be; box-shadow:0 2px 4px rgba(0,0,0,0.04); display:inline-block; margin:4px; cursor:default;">{w}</span>' for w in words_panel])
    
    cards = []
    for idx, it in enumerate(items):
        img_src = get_mtime_src(it["img"])
        art = it.get("article", "a")
        job_ans = f"is {art} {it['job']}."
        place_ans = f"works {it['prep']} a {it['place']}."
        item_id = f"p34_ex1_i{idx+1}"
        
        if it["is_eg"]:
            cards.append(f'''
            <div class="ghibli-char-card example-card" style="display:flex; flex-direction:column; align-items:center; text-align:center; padding:18px 16px; background:rgba(255,255,255,0.95); border-radius:20px; border:2px solid #2d5a27; box-shadow:0 6px 18px rgba(45,90,39,0.12); box-sizing:border-box;">
              <div style="display:flex; justify-content:space-between; align-items:center; width:100%; margin-bottom:12px;">
                <div style="display:flex; align-items:center; gap:8px;">
                  <span class="item-index" style="font-weight:800; color:#2d5a27; font-size:1.1rem;">{idx+1}.</span>
                  <span class="ghibli-example-badge" style="background:#2d5a27; color:#fff; padding:3px 10px; border-radius:12px; font-weight:700; font-size:0.75rem; text-transform:uppercase;">Example</span>
                </div>
                <div class="voice-recorder-controls">
                  <button class="voice-btn rec-btn" data-id="{item_id}"><i class="fa-solid fa-microphone"></i> Rec</button>
                  <button class="voice-btn play-rec-btn hidden" data-id="{item_id}"><i class="fa-solid fa-play"></i> My Voice</button>
                </div>
              </div>
              <div style="width:100%; height:160px; display:flex; align-items:center; justify-content:center; background:#fff; border-radius:14px; border:1px solid #ebdcc5; margin-bottom:14px; padding:6px; box-sizing:border-box;">
                <img src="{img_src}" alt="{it['name']}" style="max-width:100%; max-height:100%; object-fit:contain; filter:drop-shadow(0 4px 6px rgba(0,0,0,0.10));" loading="eager" decoding="async">
              </div>
              <div style="font-weight:700; color:#2d5a27; font-size:1.05rem; margin-bottom:6px;">{it['name']}</div>
              <div style="font-weight:600; color:#2b261f; line-height:1.5;">
                <span style="color:#2d5a27; font-weight:700;">{it['name']} is a {it['job']}.</span><br>
                <span style="color:#2d5a27; font-weight:700;">{it['pronoun']} works in a {it['place']}.</span>
              </div>
            </div>
            ''')
        else:
            cards.append(f'''
            <div class="ghibli-char-card" style="display:flex; flex-direction:column; align-items:center; text-align:center; padding:18px 16px; background:rgba(255,255,255,0.92); border-radius:20px; border:1.5px solid #e2d7c3; box-shadow:0 6px 18px rgba(0,0,0,0.06); box-sizing:border-box;">
              <div style="display:flex; justify-content:space-between; align-items:center; width:100%; margin-bottom:12px;">
                <span class="item-index" style="font-weight:800; color:#2d5a27; font-size:1.1rem;">{idx+1}.</span>
                <div class="voice-recorder-controls">
                  <button class="voice-btn rec-btn" data-id="{item_id}"><i class="fa-solid fa-microphone"></i> Rec</button>
                  <button class="voice-btn play-rec-btn hidden" data-id="{item_id}"><i class="fa-solid fa-play"></i> My Voice</button>
                </div>
              </div>
              <div style="width:100%; height:160px; display:flex; align-items:center; justify-content:center; background:#fff; border-radius:14px; border:1px solid #ebdcc5; margin-bottom:14px; padding:6px; box-sizing:border-box;">
                <img src="{img_src}" alt="{it['name']}" style="max-width:100%; max-height:100%; object-fit:contain; filter:drop-shadow(0 4px 6px rgba(0,0,0,0.10));" loading="eager" decoding="async">
              </div>
              <div style="font-weight:700; color:#2d5a27; font-size:1.05rem; margin-bottom:8px;">{it['name']}</div>
              <div style="width:100%; display:flex; flex-direction:column; gap:8px;">
                <div style="display:flex; align-items:center; justify-content:center; gap:6px; font-weight:600; font-size:0.95rem;">
                  <span>{it['name']}</span>
                  <input type="text" class="ghibli-input" data-correct="{job_ans}" placeholder="is {art} {it['job']}." style="flex:1; max-width:170px; text-align:center; padding:6px 10px; font-size:0.9rem; border-radius:10px;">
                </div>
                <div style="display:flex; align-items:center; justify-content:center; gap:6px; font-weight:600; font-size:0.95rem;">
                  <span>{it['pronoun']}</span>
                  <input type="text" class="ghibli-input" data-correct="{place_ans}" placeholder="works {it['prep']} a..." style="flex:1; max-width:170px; text-align:center; padding:6px 10px; font-size:0.9rem; border-radius:10px;">
                </div>
              </div>
            </div>
            ''')
            
    return f'''
    <section class="ghibli-section">
      <div class="ghibli-section-header">
        <div class="ghibli-ex-num">{ex_id}</div>
        <div>
          <h3 class="ghibli-ex-instruction">{instruction}</h3>
          <p class="ghibli-ex-subtext">Look at each person and workplace, say the sentences out loud, and use Rec to practice speaking!</p>
        </div>
      </div>
      <div class="ghibli-word-bank-panel" style="background:rgba(255,255,255,0.75); backdrop-filter:blur(10px); border-radius:18px; padding:18px 22px; margin-bottom:28px; border:1.5px solid #d4c5a9; box-shadow:0 4px 14px rgba(0,0,0,0.05);">
        <div style="display:flex; align-items:center; gap:8px; margin-bottom:12px; font-weight:800; color:#2d5a27; font-size:1rem;"><i class="fa-solid fa-layer-group"></i> <span>Word Panel</span></div>
        <div style="display:flex; flex-wrap:wrap; gap:8px;">{chips_html}</div>
      </div>
      <div style="display:grid; grid-template-columns:repeat(auto-fill, minmax(260px, 1fr)); gap:20px;">
        {'\n'.join(cards)}
      </div>
    </section>
    '''

def render_audio_listening_10_8(ex, ex_idx, page_num):
    """Page 35 Ex 10.8: Listen to audio and answer multiple choice questions."""
    ex_id = "10.8"
    instruction = "LISTEN TO THE AUDIO AND ANSWER THE QUESTIONS"
    
    questions = [
        {"num": "1", "q": "Pete is a...", "opts": ["farmer.", "contractor.", "gardener."], "correct": "farmer."},
        {"num": "2", "q": "Simon is a...", "opts": ["contractor.", "gardener.", "teacher."], "correct": "gardener."},
        {"num": "3", "q": "Sue is a...", "opts": ["nurse.", "chef.", "teacher."], "correct": "nurse."},
        {"num": "4", "q": "John is a...", "opts": ["scientist.", "businessman.", "doctor."], "correct": "businessman."},
        {"num": "5", "q": "Alberto is a...", "opts": ["waiter.", "chef.", "actor."], "correct": "chef."},
        {"num": "6", "q": "Susan and Pam are...", "opts": ["chefs.", "hairdressers.", "gardeners."], "correct": "hairdressers."},
        {"num": "7", "q": "Douglas is an...", "opts": ["actor.", "farmer.", "police officer."], "correct": "actor."},
        {"num": "8", "q": "Danny is a...", "opts": ["contractor.", "architect.", "farmer."], "correct": "contractor."}
    ]
    
    cards = []
    for idx, it in enumerate(questions):
        correct = it["correct"]
        opt_btns = []
        for o in it["opts"]:
            opt_btns.append(f'''
            <button type="button" class="ghibli-option" data-value="{o}" style="display:flex; align-items:center; gap:10px; padding:10px 14px; border-radius:12px; border:2px solid #cbd5e1; background:#fff; font-weight:600; cursor:pointer; text-align:left; color:#2b261f;">
              <span class="mc-radio-box" style="width:18px; height:18px; border-radius:50%; border:2px solid #94a3b8; display:inline-block; flex-shrink:0;"></span>
              <span>{o}</span>
            </button>
            ''')
            
        cards.append(f'''
        <div class="ghibli-char-card" style="display:flex; flex-direction:column; padding:18px; background:rgba(255,255,255,0.92); border-radius:20px; border:1.5px solid #e2d7c3; box-shadow:0 6px 18px rgba(0,0,0,0.06);">
          <div style="font-weight:800; color:#2d5a27; font-size:1.05rem; margin-bottom:12px;">{it["num"]}. {it["q"]}</div>
          <div class="mc-options-grid" style="display:flex; flex-direction:column; gap:8px; width:100%;">
            {'\n'.join(opt_btns)}
          </div>
          <input type="hidden" class="ghibli-input" data-correct="{correct}" />
        </div>
        ''')
        
    return f'''
    <section class="ghibli-section">
      <div class="exercise-header" style="display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:12px; margin-bottom:20px;">
        <div>
          <span class="exercise-num" style="background:var(--ghibli-accent-green); color:#fff; padding:4px 12px; border-radius:20px; font-weight:700; font-size:0.85rem;"><i class="fa-solid fa-headphones"></i> Exercise {ex_id}</span>
          <h3 class="exercise-instruction" style="font-family:var(--font-heading); margin-top:8px; color:var(--ghibli-text-main); font-size:1.15rem;">{instruction}</h3>
          <p style="font-size:0.88rem; color:var(--ghibli-text-muted); margin-top:2px;">Listen to each description and click the correct occupation for each person!</p>
        </div>
        <button class="ghibli-audio-play-btn" data-audio="audio/10/10_6_1.mp3" style="padding:10px 18px; font-size:0.9rem;"><i class="fa-solid fa-play"></i> Play Listening Audio</button>
      </div>
      <div style="display:grid; grid-template-columns:repeat(auto-fill, minmax(280px, 1fr)); gap:20px;">
        {'\n'.join(cards)}
      </div>
    </section>
    '''

def render_telling_time_11_1(ex, ex_idx, page_num):
    """Page 36 Ex 11.1: Match analog & digital clocks to written times."""
    ex_id = "11.1"
    instruction = "MATCH THE PICTURES TO THE CORRECT TIMES"
    
    clocks = [
        {"num": "1", "time_str": "07:15", "type": "digital", "ans": "It's seven fifteen.", "audio": "audio/11/11_1_eg.mp3", "is_eg": True},
        {"num": "2", "time_str": "08:30", "type": "analog", "svg": "images/clocks/clock_08_30.svg", "ans": "It's half past eight.", "audio": "audio/11/11_1_1.mp3", "is_eg": False},
        {"num": "3", "time_str": "07:50", "type": "digital", "ans": "It's seven fifty.", "audio": "audio/11/11_1_2.mp3", "is_eg": False},
        {"num": "4", "time_str": "12:00", "type": "analog", "svg": "images/clocks/clock_12_00.svg", "ans": "It's midnight.", "audio": "audio/11/11_1_3.mp3", "is_eg": False},
        {"num": "5", "time_str": "06:15", "type": "digital", "ans": "It's a quarter after six.", "audio": "audio/11/11_1_4.mp3", "is_eg": False},
        {"num": "6", "time_str": "04:30", "type": "analog", "svg": "images/clocks/clock_04_30.svg", "ans": "It's four thirty.", "audio": "audio/11/11_1_5.mp3", "is_eg": False},
        {"num": "7", "time_str": "03:30", "type": "digital", "ans": "It's three thirty.", "audio": "audio/11/11_1_6.mp3", "is_eg": False},
        {"num": "8", "time_str": "08:45", "type": "analog", "svg": "images/clocks/clock_08_45.svg", "ans": "It's a quarter to nine.", "audio": "audio/11/11_1_7.mp3", "is_eg": False},
        {"num": "9", "time_str": "05:45", "type": "digital", "ans": "It's five forty-five.", "audio": "audio/11/11_1_8.mp3", "is_eg": False}
    ]
    
    time_options = [
        "It's half past eight.", "It's seven fifteen.", "It's four thirty.", "It's a quarter after six.",
        "It's midnight.", "It's a quarter to nine.", "It's seven fifty.", "It's five forty-five.", "It's three thirty."
    ]
    
    cards = []
    for idx, it in enumerate(clocks):
        correct = it["ans"]
        
        if it["type"] == "analog":
            dial_content = f'<img src="{it["svg"]}" alt="Clock {it["time_str"]}" style="width:130px; height:130px; display:block; filter:drop-shadow(0 4px 8px rgba(0,0,0,0.12));">'
        else:
            dial_content = f'<div style="background:#221a16; color:#7ec8e3; font-family:Courier, monospace; font-size:2rem; font-weight:800; padding:12px 24px; border-radius:14px; border:2px solid #5c4d3c; box-shadow:inset 0 2px 6px rgba(0,0,0,0.6);">{it["time_str"]}</div>'
            
        if it["is_eg"]:
            cards.append(f'''
            <div class="ghibli-char-card example-card" style="display:flex; flex-direction:column; align-items:center; text-align:center; padding:18px 16px; background:rgba(255,255,255,0.95); border-radius:20px; border:2px solid #2d5a27; box-shadow:0 6px 18px rgba(45,90,39,0.12); box-sizing:border-box;">
              <div style="display:flex; justify-content:space-between; align-items:center; width:100%; margin-bottom:12px;">
                <div style="display:flex; align-items:center; gap:8px;">
                  <span class="item-index" style="font-weight:800; color:#2d5a27; font-size:1.1rem;">{it["num"]}.</span>
                  <span class="ghibli-example-badge" style="background:#2d5a27; color:#fff; padding:3px 10px; border-radius:12px; font-weight:700; font-size:0.75rem; text-transform:uppercase;">Example</span>
                </div>
                <button class="ghibli-audio-play-btn" data-audio="{it["audio"]}" title="Play Audio"><i class="fa-solid fa-play"></i></button>
              </div>
              <div style="width:100%; height:140px; display:flex; align-items:center; justify-content:center; margin-bottom:14px;">
                {dial_content}
              </div>
              <div style="width:100%;">
                <input type="text" class="ghibli-input example-input" data-correct="{correct}" value="{correct}" readonly style="width:100%; text-align:center; font-weight:700; border-color:#2d5a27; background:rgba(45,90,39,0.12); color:#2d5a27;">
              </div>
            </div>
            ''')
        else:
            opt_tags = [f'<option value="{opt}">{opt}</option>' for opt in time_options]
            cards.append(f'''
            <div class="ghibli-char-card" style="display:flex; flex-direction:column; align-items:center; text-align:center; padding:18px 16px; background:rgba(255,255,255,0.92); border-radius:20px; border:1.5px solid #e2d7c3; box-shadow:0 6px 18px rgba(0,0,0,0.06); box-sizing:border-box;">
              <div style="display:flex; justify-content:space-between; align-items:center; width:100%; margin-bottom:12px;">
                <span class="item-index" style="font-weight:800; color:#2d5a27; font-size:1.1rem;">{it["num"]}.</span>
                <div style="display:flex; align-items:center; gap:6px;">
                  <button class="ghibli-audio-play-btn" data-audio="{it["audio"]}" title="Play Audio"><i class="fa-solid fa-play"></i></button>
                  <div class="voice-recorder-controls">
                    <button class="voice-btn rec-btn" data-id="p36_ex1_i{idx+1}"><i class="fa-solid fa-microphone"></i> Rec</button>
                    <button class="voice-btn play-rec-btn hidden" data-id="p36_ex1_i{idx+1}"><i class="fa-solid fa-play"></i> My Voice</button>
                  </div>
                </div>
              </div>
              <div style="width:100%; height:140px; display:flex; align-items:center; justify-content:center; margin-bottom:14px;">
                {dial_content}
              </div>
              <div style="width:100%;">
                <select class="ghibli-input ghibli-matching-select" data-correct="{correct}" style="width:100%; padding:10px 12px; border-radius:12px; border:1.5px solid #d4c5a9; background:#fff; font-weight:600; text-align:center; cursor:pointer;">
                  <option value="">-- Choose time phrase --</option>
                  {'\n'.join(opt_tags)}
                </select>
              </div>
            </div>
            ''')
            
    return f'''
    <section class="ghibli-section">
      <div class="ghibli-section-header">
        <div class="ghibli-ex-num">{ex_id}</div>
        <div>
          <h3 class="ghibli-ex-instruction">{instruction}</h3>
          <p class="ghibli-ex-subtext">Look at each analog clock or digital display, listen to the pronunciation, and match the time!</p>
        </div>
      </div>
      <div style="display:grid; grid-template-columns:repeat(auto-fill, minmax(230px, 1fr)); gap:20px;">
        {'\n'.join(cards)}
      </div>
    </section>
    '''

def render_audio_clocks_11_2(ex, ex_idx, page_num):
    """Page 36 Ex 11.2: Listen to audio and mark the correct clock."""
    ex_id = "11.2"
    instruction = "LISTEN TO THE AUDIO AND MARK THE CORRECT TIMES"
    
    pairs = [
        {"num": "1", "optA": "05:45", "optB": "06:15", "correct": "05:45", "audio": "audio/11/11_2_eg_usuk.mp3", "is_eg": True},
        {"num": "2", "optA": "07:45", "optB": "08:15", "correct": "07:45", "audio": "audio/11/11_2_1_usuk.mp3", "is_eg": False},
        {"num": "3", "optA": "07:30", "optB": "08:30", "correct": "08:30", "audio": "audio/11/11_2_2.mp3", "is_eg": False},
        {"num": "4", "optA": "11:15", "optB": "10:45", "correct": "11:15", "audio": "audio/11/11_2_3_usuk.mp3", "is_eg": False},
        {"num": "5", "optA": "09:30", "optB": "09:20", "correct": "09:20", "audio": "audio/11/11_2_4.mp3", "is_eg": False},
        {"num": "6", "optA": "11:00", "optB": "10:00", "correct": "11:00", "audio": "audio/11/11_2_5_usuk.mp3", "is_eg": False},
        {"num": "7", "optA": "07:45", "optB": "07:15", "correct": "07:15", "audio": "audio/11/11_2_6.mp3", "is_eg": False},
        {"num": "8", "optA": "03:35", "optB": "03:25", "correct": "03:25", "audio": "audio/11/11_2_7.mp3", "is_eg": False},
        {"num": "9", "optA": "09:45", "optB": "10:45", "correct": "09:45", "audio": "audio/11/11_2_8.mp3", "is_eg": False},
        {"num": "10", "optA": "06:38", "optB": "06:28", "correct": "06:38", "audio": "audio/11/11_2_9.mp3", "is_eg": False},
        {"num": "11", "optA": "05:05", "optB": "05:30", "correct": "05:05", "audio": "audio/11/11_2_10.mp3", "is_eg": False},
        {"num": "12", "optA": "10:00", "optB": "10:10", "correct": "10:10", "audio": "audio/11/11_2_11.mp3", "is_eg": False},
        {"num": "13", "optA": "02:13", "optB": "02:30", "correct": "02:13", "audio": "audio/11/11_2_12.mp3", "is_eg": False},
        {"num": "14", "optA": "08:15", "optB": "07:45", "correct": "07:45", "audio": "audio/11/11_2_13.mp3", "is_eg": False}
    ]
    
    cards = []
    for idx, it in enumerate(pairs):
        hA, mA = [int(x) for x in it["optA"].split(":")]
        hB, mB = [int(x) for x in it["optB"].split(":")]
        svgA = f"images/clocks/clock_{hA:02d}_{mA:02d}.svg"
        svgB = f"images/clocks/clock_{hB:02d}_{mB:02d}.svg"
        correct = it["correct"]
        
        cards.append(f'''
        <div class="ghibli-char-card" style="display:flex; flex-direction:column; align-items:center; padding:18px; background:rgba(255,255,255,0.92); border-radius:20px; border:1.5px solid #e2d7c3; box-shadow:0 6px 18px rgba(0,0,0,0.06);">
          <div style="display:flex; justify-content:space-between; align-items:center; width:100%; margin-bottom:14px;">
            <span class="item-index" style="font-weight:800; color:#2d5a27; font-size:1.1rem;">{it["num"]}.</span>
            <button class="ghibli-audio-play-btn" data-audio="{it["audio"]}" title="Listen to time"><i class="fa-solid fa-play"></i></button>
          </div>
          <div class="mc-options-grid" style="display:flex; gap:16px; width:100%; justify-content:center;">
            <button type="button" class="ghibli-option" data-value="{it["optA"]}" style="flex:1; display:flex; flex-direction:column; align-items:center; gap:8px; padding:12px; border-radius:16px; border:2px solid #cbd5e1; background:#fff; cursor:pointer;">
              <img src="{svgA}" alt="{it["optA"]}" style="width:100px; height:100px;">
              <span style="font-weight:700; color:#2b261f;">{it["optA"]}</span>
            </button>
            <button type="button" class="ghibli-option" data-value="{it["optB"]}" style="flex:1; display:flex; flex-direction:column; align-items:center; gap:8px; padding:12px; border-radius:16px; border:2px solid #cbd5e1; background:#fff; cursor:pointer;">
              <img src="{svgB}" alt="{it["optB"]}" style="width:100px; height:100px;">
              <span style="font-weight:700; color:#2b261f;">{it["optB"]}</span>
            </button>
          </div>
          <input type="hidden" class="ghibli-input" data-correct="{correct}" />
        </div>
        ''')
        
    return f'''
    <section class="ghibli-section">
      <div class="ghibli-section-header">
        <div class="ghibli-ex-num">{ex_id}</div>
        <div>
          <h3 class="ghibli-ex-instruction">{instruction}</h3>
          <p class="ghibli-ex-subtext">Click the play button to hear the time, then click the correct clock face!</p>
        </div>
      </div>
      <div style="display:grid; grid-template-columns:repeat(auto-fill, minmax(280px, 1fr)); gap:20px;">
        {'\n'.join(cards)}
      </div>
    </section>
    '''

def render_spoken_time_11_4(ex, ex_idx, page_num):
    """Page 37 Ex 11.4: Look at clock, say time out loud, listen and verify."""
    ex_id = "11.4"
    instruction = "LOOK AT THE PICTURES, THEN SAY EACH TIME OUT LOUD"
    
    clocks = [
        {"num": "1", "time": "09:15", "ans": "It's a quarter past nine.", "audio": "audio/11/11_4_eg.mp3", "is_eg": True},
        {"num": "2", "time": "09:45", "ans": "It's a quarter to ten.", "audio": "audio/11/11_4_1.mp3", "is_eg": False},
        {"num": "3", "time": "04:00", "ans": "It's four o'clock.", "audio": "audio/11/11_4_2.mp3", "is_eg": False},
        {"num": "4", "time": "10:20", "ans": "It's ten twenty.", "audio": "audio/11/11_4_3.mp3", "is_eg": False},
        {"num": "5", "time": "11:30", "ans": "It's half past eleven.", "audio": "audio/11/11_4_4.mp3", "is_eg": False},
        {"num": "6", "time": "03:47", "ans": "It's three forty-seven.", "audio": "audio/11/11_4_5.mp3", "is_eg": False},
        {"num": "7", "time": "03:15", "ans": "It's a quarter past three.", "audio": "audio/11/11_4_6.mp3", "is_eg": False},
        {"num": "8", "time": "06:30", "ans": "It's half past six.", "audio": "audio/11/11_4_7.mp3", "is_eg": False},
        {"num": "9", "time": "08:22", "ans": "It's eight twenty-two.", "audio": "audio/11/11_4_8.mp3", "is_eg": False},
        {"num": "10", "time": "01:25", "ans": "It's one twenty-five.", "audio": "audio/11/11_4_9.mp3", "is_eg": False}
    ]
    
    cards = []
    for idx, it in enumerate(clocks):
        h, m = [int(x) for x in it["time"].split(":")]
        svg_path = f"images/clocks/clock_{h:02d}_{m:02d}.svg"
        correct = it["ans"]
        item_id = f"p37_ex2_i{idx+1}"
        
        cards.append(f'''
        <div class="ghibli-char-card" style="display:flex; flex-direction:column; align-items:center; text-align:center; padding:18px 16px; background:rgba(255,255,255,0.92); border-radius:20px; border:1.5px solid #e2d7c3; box-shadow:0 6px 18px rgba(0,0,0,0.06);">
          <div style="display:flex; justify-content:space-between; align-items:center; width:100%; margin-bottom:12px;">
            <span class="item-index" style="font-weight:800; color:#2d5a27; font-size:1.1rem;">{it["num"]}.</span>
            <div style="display:flex; align-items:center; gap:6px;">
              <button class="ghibli-audio-play-btn" data-audio="{it["audio"]}" title="Listen to Native Audio"><i class="fa-solid fa-play"></i></button>
              <div class="voice-recorder-controls">
                <button class="voice-btn rec-btn" data-id="{item_id}"><i class="fa-solid fa-microphone"></i> Rec</button>
                <button class="voice-btn play-rec-btn hidden" data-id="{item_id}"><i class="fa-solid fa-play"></i> My Voice</button>
              </div>
            </div>
          </div>
          <div style="width:100%; height:130px; display:flex; align-items:center; justify-content:center; margin-bottom:12px;">
            <img src="{svg_path}" alt="{it["time"]}" style="width:120px; height:120px;">
          </div>
          <div style="font-weight:800; color:#2d5a27; font-size:1.2rem; margin-bottom:10px;">{it["time"]}</div>
          <div style="width:100%;">
            <input type="text" class="ghibli-input" data-correct="{correct}" placeholder="Say or type time..." style="width:100%; text-align:center; font-weight:600; font-size:0.95rem;">
          </div>
        </div>
        ''')
        
    return f'''
    <section class="ghibli-section">
      <div class="ghibli-section-header">
        <div class="ghibli-ex-num">{ex_id}</div>
        <div>
          <h3 class="ghibli-ex-instruction">{instruction}</h3>
          <p class="ghibli-ex-subtext">Look at each clock, say the time out loud into the microphone, and listen to compare!</p>
        </div>
      </div>
      <div style="display:grid; grid-template-columns:repeat(auto-fill, minmax(230px, 1fr)); gap:20px;">
        {'\n'.join(cards)}
      </div>
    </section>
    '''

def render_routines_12_1(ex, ex_idx, page_num):
    """Pages 38-39 Ex 12.1: Daily routines vocabulary picture cards."""
    config_path = 'images/routines/routines_config.json'
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
    else:
        config = {}

    p_key = f"p{page_num}"
    p_items = config.get(p_key, [])
    
    p38_words = [
        'go to work', 'buy groceries', 'take a bath', 'eat lunch', 'wake up', 'cook dinner',
        'brush hair', 'start work', 'eat dinner', 'go to school', 'get dressed', 'go to bed',
        'morning', 'afternoon', 'evening', 'night'
    ]
    p39_words = [
        'clear the table', 'leave work', 'wash your face', 'finish work', 'brush your teeth',
        'go home', 'take a shower', 'get up', 'iron a shirt', 'do the dishes',
        'have breakfast', 'walk the dog'
    ]
    words_list = p38_words if page_num == 38 else p39_words

    chips_html = ' '.join([f'<span class="word-chip word-panel-tag" style="background:#fff; padding:6px 14px; border-radius:12px; font-weight:600; font-size:0.95rem; color:#2b261f; border:1.5px solid #dcd1be; box-shadow:0 2px 4px rgba(0,0,0,0.04); display:inline-block; margin:4px; cursor:default;">{w}</span>' for w in words_list])

    cards = []
    if p_items:
        for it in p_items:
            img_url = it.get('img', '')
            img_src = get_mtime_src(img_url)
            num_label = it.get('num', '')
            correct_val = it.get('correct', '')
            audio_path = it.get('audio', '')
            rec_id = it.get('rec_id', '')
            is_eg = it.get('is_example', False)

            if is_eg:
                cards.append(f'''
                <div class="ghibli-char-card example-card" style="display:flex; flex-direction:column; align-items:center; text-align:center; padding:18px 16px; background:rgba(255,255,255,0.95); border-radius:20px; border:2px solid #2d5a27; box-shadow:0 6px 18px rgba(45,90,39,0.12); box-sizing:border-box;">
                  <div style="display:flex; justify-content:space-between; align-items:center; width:100%; margin-bottom:12px;">
                    <div style="display:flex; align-items:center; gap:8px;">
                      <span class="item-index" style="font-weight:800; color:#2d5a27; font-size:1.1rem;">{num_label}</span>
                      <span class="ghibli-example-badge" style="background:#2d5a27; color:#fff; padding:3px 10px; border-radius:12px; font-weight:700; font-size:0.75rem; text-transform:uppercase;">Example</span>
                    </div>
                    <div style="display:flex; align-items:center; gap:6px;">
                      <button class="ghibli-audio-play-btn" data-audio="{audio_path}" title="Play Audio"><i class="fa-solid fa-play"></i></button>
                      <div class="voice-recorder-controls">
                        <button class="voice-btn rec-btn" data-id="{rec_id}"><i class="fa-solid fa-microphone"></i> Rec</button>
                        <button class="voice-btn play-rec-btn hidden" data-id="{rec_id}"><i class="fa-solid fa-play"></i> My Voice</button>
                      </div>
                    </div>
                  </div>
                  <div style="width:100%; height:130px; display:flex; align-items:center; justify-content:center; background:#fff; border-radius:14px; border:1px solid #ebdcc5; margin-bottom:14px; padding:6px; box-sizing:border-box;">
                    <img src="{img_src}" alt="{correct_val}" style="max-width:100%; max-height:100%; object-fit:contain; filter:drop-shadow(0 4px 6px rgba(0,0,0,0.10));" loading="eager" decoding="async">
                  </div>
                  <div style="width:100%;">
                    <input type="text" class="ghibli-input example-input" data-correct="{correct_val}" value="{correct_val}" readonly style="width:100%; text-align:center; font-size:1.02rem; font-weight:700; padding:10px 12px; border-radius:12px; border-color:#2d5a27; background:rgba(45,90,39,0.12); color:#2d5a27;">
                  </div>
                </div>
                ''')
            else:
                cards.append(f'''
                <div class="ghibli-char-card" style="display:flex; flex-direction:column; align-items:center; text-align:center; padding:18px 16px; background:rgba(255,255,255,0.92); border-radius:20px; border:1.5px solid #e2d7c3; box-shadow:0 6px 18px rgba(0,0,0,0.06); box-sizing:border-box;">
                  <div style="display:flex; justify-content:space-between; align-items:center; width:100%; margin-bottom:12px;">
                    <span class="item-index" style="font-weight:800; color:#2d5a27; font-size:1.1rem;">{num_label}</span>
                    <div style="display:flex; align-items:center; gap:6px;">
                      <button class="ghibli-audio-play-btn" data-audio="{audio_path}" title="Play Audio"><i class="fa-solid fa-play"></i></button>
                      <div class="voice-recorder-controls">
                        <button class="voice-btn rec-btn" data-id="{rec_id}"><i class="fa-solid fa-microphone"></i> Rec</button>
                        <button class="voice-btn play-rec-btn hidden" data-id="{rec_id}"><i class="fa-solid fa-play"></i> My Voice</button>
                      </div>
                    </div>
                  </div>
                  <div style="width:100%; height:130px; display:flex; align-items:center; justify-content:center; background:#fff; border-radius:14px; border:1px solid #ebdcc5; margin-bottom:14px; padding:6px; box-sizing:border-box;">
                    <img src="{img_src}" alt="Routine Activity" style="max-width:100%; max-height:100%; object-fit:contain; filter:drop-shadow(0 4px 6px rgba(0,0,0,0.10));" loading="eager" decoding="async">
                  </div>
                  <div style="width:100%;">
                    <input type="text" class="ghibli-input" data-correct="{correct_val}" placeholder="Type phrase..." autocomplete="off" style="width:100%; text-align:center; font-size:1.02rem; font-weight:600; padding:10px 12px; border-radius:12px; border:1.5px solid #d4c5a9; background:#fff;">
                  </div>
                </div>
                ''')

    ex_id = "12.1"
    instruction = "DAILY ROUTINES • WRITE THE WORDS FROM THE PANEL UNDER THE CORRECT PICTURES"
    
    return f'''
    <section class="ghibli-section">
      <div class="ghibli-section-header">
        <div class="ghibli-ex-num">{ex_id}</div>
        <div>
          <h3 class="ghibli-ex-instruction">{instruction}</h3>
          <p class="ghibli-ex-subtext">Look at each daily routine activity, listen to the pronunciation, and enter the correct phrase!</p>
        </div>
      </div>
      <div class="ghibli-word-bank-panel" style="background:rgba(255,255,255,0.75); backdrop-filter:blur(10px); border-radius:18px; padding:18px 22px; margin-bottom:28px; border:1.5px solid #d4c5a9; box-shadow:0 4px 14px rgba(0,0,0,0.05);">
        <div style="display:flex; align-items:center; gap:8px; margin-bottom:12px; font-weight:800; color:#2d5a27; font-size:1rem;"><i class="fa-solid fa-calendar-day"></i> <span>Routine Word Panel</span></div>
        <div style="display:flex; flex-wrap:wrap; gap:8px;">{chips_html}</div>
      </div>
      <div style="display:grid; grid-template-columns:repeat(auto-fill, minmax(210px, 1fr)); gap:20px;">
        {'\n'.join(cards)}
      </div>
    </section>
    '''

def render_marion_timeline_13_1(ex, ex_idx, page_num):
    """Page 40 Ex 13.1: Match pictures to sentences for Marion's day."""
    ex_id = "13.1"
    instruction = "MATCH THE PICTURES TO THE CORRECT SENTENCES"
    
    timeline = [
        {"num": "1", "time": "6:45am", "ans": "Marion has a shower at 6:45am.", "img": "images/routines/marion_shower_645.png", "audio": "audio/13/13_1_eg.mp3", "is_eg": True},
        {"num": "2", "time": "7am", "ans": "Marion has breakfast at 7am.", "img": "images/routines/marion_breakfast_700.png", "audio": "audio/13/13_1_1.mp3", "is_eg": False},
        {"num": "3", "time": "7:20am", "ans": "Marion brushes her teeth at 7:20am.", "img": "images/routines/marion_teeth_720.png", "audio": "audio/13/13_1_2.mp3", "is_eg": False},
        {"num": "4", "time": "7:30am", "ans": "Marion goes to work at 7:30am.", "img": "images/routines/marion_leave_730.png", "audio": "audio/13/13_1_3.mp3", "is_eg": False},
        {"num": "5", "time": "7:45am", "ans": "Marion gets the bus at 7:45am.", "img": "images/routines/marion_bus_745.png", "audio": "audio/13/13_1_4.mp3", "is_eg": False},
        {"num": "6", "time": "8:30am", "ans": "Marion gets to work at 8:30am.", "img": "images/routines/marion_arrive_830.png", "audio": "audio/13/13_1_5.mp3", "is_eg": False},
        {"num": "7", "time": "5pm", "ans": "Marion leaves work at 5pm.", "img": "images/routines/marion_leave_500.png", "audio": "audio/13/13_1_6.mp3", "is_eg": False}
    ]
    
    sentence_options = [
        "Marion brushes her teeth at 7:20am.", "Marion gets up at 6:30am.", "Marion gets the bus at 7:45am.",
        "Marion leaves work at 5pm.", "Marion has a shower at 6:45am.", "Marion has breakfast at 7am.",
        "Marion goes to work at 7:30am.", "Marion gets to work at 8:30am."
    ]
    
    cards = []
    for idx, it in enumerate(timeline):
        img_src = get_mtime_src(it["img"])
        correct = it["ans"]
        
        if it["is_eg"]:
            cards.append(f'''
            <div class="ghibli-char-card example-card" style="display:flex; flex-direction:column; align-items:center; text-align:center; padding:18px 16px; background:rgba(255,255,255,0.95); border-radius:20px; border:2px solid #2d5a27; box-shadow:0 6px 18px rgba(45,90,39,0.12);">
              <div style="display:flex; justify-content:space-between; align-items:center; width:100%; margin-bottom:12px;">
                <div style="display:flex; align-items:center; gap:8px;">
                  <span class="item-index" style="font-weight:800; color:#2d5a27; font-size:1.1rem;">{it["num"]}.</span>
                  <span class="ghibli-example-badge" style="background:#2d5a27; color:#fff; padding:3px 10px; border-radius:12px; font-weight:700; font-size:0.75rem; text-transform:uppercase;">Example</span>
                </div>
                <button class="ghibli-audio-play-btn" data-audio="{it["audio"]}" title="Play Audio"><i class="fa-solid fa-play"></i></button>
              </div>
              <div style="width:100%; height:140px; display:flex; align-items:center; justify-content:center; margin-bottom:12px;">
                <img src="{img_src}" alt="Timeline {it["time"]}" style="max-width:100%; max-height:100%; object-fit:contain; border-radius:12px;">
              </div>
              <div style="width:100%;">
                <input type="text" class="ghibli-input example-input" data-correct="{correct}" value="{correct}" readonly style="width:100%; text-align:center; font-weight:700; border-color:#2d5a27; background:rgba(45,90,39,0.12); color:#2d5a27;">
              </div>
            </div>
            ''')
        else:
            opt_tags = [f'<option value="{opt}">{opt}</option>' for opt in sentence_options]
            cards.append(f'''
            <div class="ghibli-char-card" style="display:flex; flex-direction:column; align-items:center; text-align:center; padding:18px 16px; background:rgba(255,255,255,0.92); border-radius:20px; border:1.5px solid #e2d7c3; box-shadow:0 6px 18px rgba(0,0,0,0.06);">
              <div style="display:flex; justify-content:space-between; align-items:center; width:100%; margin-bottom:12px;">
                <span class="item-index" style="font-weight:800; color:#2d5a27; font-size:1.1rem;">{it["num"]}.</span>
                <button class="ghibli-audio-play-btn" data-audio="{it["audio"]}" title="Play Audio"><i class="fa-solid fa-play"></i></button>
              </div>
              <div style="width:100%; height:140px; display:flex; align-items:center; justify-content:center; margin-bottom:12px;">
                <img src="{img_src}" alt="Timeline {it["time"]}" style="max-width:100%; max-height:100%; object-fit:contain; border-radius:12px;">
              </div>
              <div style="width:100%;">
                <select class="ghibli-input ghibli-matching-select" data-correct="{correct}" style="width:100%; padding:10px 12px; border-radius:12px; border:1.5px solid #d4c5a9; background:#fff; font-weight:600; text-align:center; cursor:pointer;">
                  <option value="">-- Choose sentence --</option>
                  {'\n'.join(opt_tags)}
                </select>
              </div>
            </div>
            ''')
            
    return f'''
    <section class="ghibli-section">
      <div class="ghibli-section-header">
        <div class="ghibli-ex-num">{ex_id}</div>
        <div>
          <h3 class="ghibli-ex-instruction">{instruction}</h3>
          <p class="ghibli-ex-subtext">Look at each picture in Marion's morning routine, listen to the audio, and match the sentence!</p>
        </div>
      </div>
      <div style="display:grid; grid-template-columns:repeat(auto-fill, minmax(260px, 1fr)); gap:20px;">
        {'\n'.join(cards)}
      </div>
    </section>
    '''

def render_pronunciation_verbs_13_5(ex, ex_idx, page_num):
    """Page 41 Ex 13.5: Pronunciation drill for verb endings (-s, -z, -iz)."""
    ex_id = "13.5"
    instruction = "SAY THESE VERBS OUT LOUD"
    
    verbs = [
        {"num": "1", "verb": "starts", "ending": "/s/", "audio": "audio/13/13_5_eg.mp3", "is_eg": True},
        {"num": "2", "verb": "goes", "ending": "/z/", "audio": "audio/13/13_5_1.mp3", "is_eg": False},
        {"num": "3", "verb": "washes", "ending": "/ɪz/", "audio": "audio/13/13_5_2.mp3", "is_eg": False},
        {"num": "4", "verb": "wakes", "ending": "/s/", "audio": "audio/13/13_5_3.mp3", "is_eg": False},
        {"num": "5", "verb": "gets", "ending": "/s/", "audio": "audio/13/13_5_4.mp3", "is_eg": False},
        {"num": "6", "verb": "watches", "ending": "/ɪz/", "audio": "audio/13/13_5_5.mp3", "is_eg": False},
        {"num": "7", "verb": "leaves", "ending": "/z/", "audio": "audio/13/13_5_6.mp3", "is_eg": False},
        {"num": "8", "verb": "has", "ending": "/z/", "audio": "audio/13/13_5_7.mp3", "is_eg": False},
        {"num": "9", "verb": "finishes", "ending": "/ɪz/", "audio": "audio/13/13_5_8.mp3", "is_eg": False}
    ]
    
    cards = []
    for idx, it in enumerate(verbs):
        item_id = f"p41_ex3_i{idx+1}"
        cards.append(f'''
        <div class="ghibli-char-card" style="display:flex; flex-direction:column; align-items:center; text-align:center; padding:18px 14px; background:rgba(255,255,255,0.92); border-radius:20px; border:1.5px solid #e2d7c3; box-shadow:0 6px 18px rgba(0,0,0,0.06);">
          <div style="display:flex; justify-content:space-between; align-items:center; width:100%; margin-bottom:8px;">
            <span class="item-index" style="font-weight:800; color:#2d5a27; font-size:1.1rem;">{it["num"]}.</span>
            <span style="background:rgba(45,90,39,0.12); color:#2d5a27; font-weight:800; padding:2px 10px; border-radius:10px; font-size:0.8rem;">Ending: {it["ending"]}</span>
          </div>
          <div style="font-family:'Outfit', sans-serif; font-weight:800; color:#2b261f; font-size:1.4rem; margin:12px 0 16px 0;">{it["verb"]}</div>
          <div style="display:flex; gap:8px; align-items:center; justify-content:center; width:100%;">
            <button class="ghibli-audio-play-btn" data-audio="{it["audio"]}" title="Play Pronunciation"><i class="fa-solid fa-play"></i></button>
            <div class="voice-recorder-controls">
              <button class="voice-btn rec-btn" data-id="{item_id}"><i class="fa-solid fa-microphone"></i> Rec</button>
              <button class="voice-btn play-rec-btn hidden" data-id="{item_id}"><i class="fa-solid fa-play"></i> My Voice</button>
            </div>
          </div>
        </div>
        ''')
        
    return f'''
    <section class="ghibli-section">
      <div class="ghibli-section-header">
        <div class="ghibli-ex-num">{ex_id}</div>
        <div>
          <h3 class="ghibli-ex-instruction">{instruction}</h3>
          <p class="ghibli-ex-subtext">Listen to the native pronunciation of each verb, note the ending sound (/s/, /z/, /ɪz/), and record yourself!</p>
        </div>
      </div>
      <div style="display:grid; grid-template-columns:repeat(auto-fill, minmax(180px, 1fr)); gap:16px;">
        {'\n'.join(cards)}
      </div>
    </section>
    '''

def render_sentence_choice_pairs_14_2(ex, ex_idx, page_num):
    """Page 42 Ex 14.2: Mark the sentences that are correct."""
    ex_id = "14.2"
    instruction = "MARK THE SENTENCES THAT ARE CORRECT"
    
    pairs = [
        {"num": "1", "optA": "I play soccer on Mondays.", "optB": "I play soccer at Mondays.", "correct": "I play soccer on Mondays."},
        {"num": "2", "optA": "I work from Monday to Thursday.", "optB": "I work of Monday to Thursday.", "correct": "I work from Monday to Thursday."},
        {"num": "3", "optA": "My sister go swimming every day.", "optB": "My sister goes swimming every day.", "correct": "My sister goes swimming every day."},
        {"num": "4", "optA": "We go to the gym on Saturdays.", "optB": "We go to the gym at Saturdays.", "correct": "We go to the gym on Saturdays."},
        {"num": "5", "optA": "You read the newspaper in Sundays.", "optB": "You read the newspaper on Sundays.", "correct": "You read the newspaper on Sundays."},
        {"num": "6", "optA": "Peter goes to work on the weekend.", "optB": "Peter goes to work from the weekend.", "correct": "Peter goes to work on the weekend."},
        {"num": "7", "optA": "Jennifer goes to a café for Fridays.", "optB": "Jennifer goes to a café on Fridays.", "correct": "Jennifer goes to a café on Fridays."},
        {"num": "8", "optA": "Sam and Pete work to 9am from 5pm.", "optB": "Sam and Pete work from 9am to 5pm.", "correct": "Sam and Pete work from 9am to 5pm."}
    ]
    
    cards = []
    for idx, it in enumerate(pairs):
        correct = it["correct"]
        cards.append(f'''
        <div class="ghibli-char-card" style="display:flex; flex-direction:column; padding:18px; background:rgba(255,255,255,0.92); border-radius:20px; border:1.5px solid #e2d7c3; box-shadow:0 6px 18px rgba(0,0,0,0.06);">
          <div style="font-weight:800; color:#2d5a27; font-size:1.05rem; margin-bottom:12px;">Pair {it["num"]}</div>
          <div class="mc-options-grid" style="display:flex; flex-direction:column; gap:10px; width:100%;">
            <button type="button" class="ghibli-option" data-value="{it["optA"]}" style="display:flex; align-items:center; gap:12px; padding:12px 16px; border-radius:14px; border:2px solid #cbd5e1; background:#fff; cursor:pointer; text-align:left; font-size:0.98rem; font-weight:600; color:#2b261f;">
              <span class="mc-radio-box" style="width:20px; height:20px; border-radius:50%; border:2px solid #94a3b8; display:flex; align-items:center; justify-content:center; flex-shrink:0;"></span>
              <span>{it["optA"]}</span>
            </button>
            <button type="button" class="ghibli-option" data-value="{it["optB"]}" style="display:flex; align-items:center; gap:12px; padding:12px 16px; border-radius:14px; border:2px solid #cbd5e1; background:#fff; cursor:pointer; text-align:left; font-size:0.98rem; font-weight:600; color:#2b261f;">
              <span class="mc-radio-box" style="width:20px; height:20px; border-radius:50%; border:2px solid #94a3b8; display:flex; align-items:center; justify-content:center; flex-shrink:0;"></span>
              <span>{it["optB"]}</span>
            </button>
          </div>
          <input type="hidden" class="ghibli-input" data-correct="{correct}" />
        </div>
        ''')
        
    return f'''
    <section class="ghibli-section">
      <div class="ghibli-section-header">
        <div class="ghibli-ex-num">{ex_id}</div>
        <div>
          <h3 class="ghibli-ex-instruction">{instruction}</h3>
          <p class="ghibli-ex-subtext">Click the correct sentence in each pair to mark it!</p>
        </div>
      </div>
      <div style="display:grid; grid-template-columns:repeat(auto-fill, minmax(320px, 1fr)); gap:20px;">
        {'\n'.join(cards)}
      </div>
    </section>
    '''

def render_reading_email_14_6(ex, ex_idx, page_num):
    """Page 44 Ex 14.6: Read Jim's email and answer True/False questions."""
    ex_id = "14.6"
    instruction = "READ THE EMAIL AND ANSWER THE QUESTIONS"
    
    email_html = '''
    <div class="email-envelope-card" style="background:rgba(255,255,255,0.95); border-radius:20px; border:2px solid #c89d56; padding:24px; box-shadow:0 8px 24px rgba(0,0,0,0.08); margin-bottom:28px;">
      <div style="display:flex; align-items:center; gap:12px; border-bottom:1.5px solid #ebdcc5; padding-bottom:14px; margin-bottom:16px;">
        <i class="fa-solid fa-envelope" style="font-size:1.6rem; color:#2d5a27;"></i>
        <div>
          <div style="font-weight:800; color:#2d5a27; font-size:1.1rem;">From: Jim &lt;jim.miller@ghiblimail.com&gt;</div>
          <div style="font-size:0.88rem; color:#666;">Subject: My Weekly Routine</div>
        </div>
      </div>
      <div style="font-family:'Outfit', serif; font-size:1.05rem; line-height:1.7; color:#2b261f;">
        <p style="margin-bottom:12px;">Hi Everyone,</p>
        <p style="margin-bottom:12px;">I have a very busy weekly routine! From Monday to Friday, I get up at 6:30am and start work at 8am. On Mondays and Tuesdays, I go to the gym after work at 6pm.</p>
        <p style="margin-bottom:12px;">On Wednesdays and Thursdays, I play tennis with my friend Tom. On Fridays, I usually go to the cinema with my wife.</p>
        <p style="margin-bottom:12px;">On the weekend, we wake up late at 10am. We go to a restaurant for dinner on Sundays, and we relax at home on Saturdays!</p>
        <p>Best regards,<br><strong>Jim</strong></p>
      </div>
    </div>
    '''
    
    questions = [
        {"num": "1", "q": "Jim goes to the gym three times a week.", "ans": "False"},
        {"num": "2", "q": "Jim goes to work at 6am.", "ans": "False"},
        {"num": "3", "q": "Jim goes to the gym on Mondays and Tuesdays.", "ans": "True"},
        {"num": "4", "q": "He plays soccer on Fridays.", "ans": "False"},
        {"num": "5", "q": "Jim and his wife get up at 10am on the weekend.", "ans": "True"},
        {"num": "6", "q": "They go to the theater on Saturdays.", "ans": "False"},
        {"num": "7", "q": "They go to a restaurant on Sundays.", "ans": "True"}
    ]
    
    cards = []
    for it in questions:
        correct = it["ans"]
        cards.append(f'''
        <div class="tf-question-card" style="display:flex; justify-content:space-between; align-items:center; gap:16px; padding:16px 20px; background:rgba(255,255,255,0.9); border-radius:16px; border:1.5px solid #e2d7c3; margin-bottom:12px; flex-wrap:wrap;">
          <div style="font-weight:700; color:#2b261f; font-size:1rem; flex:1; min-width:240px;">
            <span style="color:#2d5a27; font-weight:800; margin-right:6px;">{it["num"]}.</span> {it["q"]}
          </div>
          <div class="tf-btn-group" style="display:flex; gap:10px;">
            <button type="button" class="tf-btn" data-value="True" style="padding:8px 20px; border-radius:12px; border:2px solid #cbd5e1; background:#fff; font-weight:700; cursor:pointer; color:#2b261f;">True</button>
            <button type="button" class="tf-btn" data-value="False" style="padding:8px 20px; border-radius:12px; border:2px solid #cbd5e1; background:#fff; font-weight:700; cursor:pointer; color:#2b261f;">False</button>
          </div>
          <input type="hidden" class="ghibli-input" data-correct="{correct}" />
        </div>
        ''')
        
    return f'''
    <section class="ghibli-section">
      <div class="ghibli-section-header">
        <div class="ghibli-ex-num">{ex_id}</div>
        <div>
          <h3 class="ghibli-ex-instruction">{instruction}</h3>
          <p class="ghibli-ex-subtext">Read Jim's email message, then click True or False for each statement!</p>
        </div>
      </div>
      {email_html}
      <div class="tf-questions-list">
        {'\n'.join(cards)}
      </div>
    </section>
    '''

def render_audio_listen_numbered_slots_14_7(ex, ex_idx, page_num):
    """Page 45 Ex 14.7: Numbered drop slots 1-6 on top with lifestyle scene cards below."""
    ex_id = "14.7"
    instruction = "LISTEN TO THE AUDIO, THEN NUMBER THE PICTURES IN THE ORDER THEY ARE DESCRIBED"
    
    # 6 scene cards (A to F)
    # Order described in audio: E (1: 6am wake up), A (2: gym), C (3: nurse), D (4: swim), F (5: restaurant), B (6: farm)
    cards_data = [
        {"letter": "E", "name": "Sally waking up at 6am", "img": "images/p45_card_e.jpg", "correct_slot": "1", "is_eg": True},
        {"letter": "A", "name": "Kate working out at the gym", "img": "images/p45_card_a.jpg", "correct_slot": "2", "is_eg": False},
        {"letter": "C", "name": "Jane working as a nurse", "img": "images/p45_card_c.jpg", "correct_slot": "3", "is_eg": False},
        {"letter": "D", "name": "Sally swimming in pool", "img": "images/p45_card_d.jpg", "correct_slot": "4", "is_eg": False},
        {"letter": "F", "name": "Jane dining at restaurant", "img": "images/p45_card_f.jpg", "correct_slot": "5", "is_eg": False},
        {"letter": "B", "name": "Paul working on the farm", "img": "images/p45_card_b.jpg", "correct_slot": "6", "is_eg": False}
    ]
    
    slots_html = []
    for s in range(1, 7):
        if s == 1:
            slots_html.append('''
            <div class="ghibli-drop-slot has-card" data-slot="1" data-correct-letter="E" style="min-height:160px; background:rgba(45,90,39,0.08); border:2px solid #2d5a27; border-radius:18px; padding:12px; display:flex; flex-direction:column; align-items:center; text-align:center;">
              <div class="slot-header" style="margin-bottom:8px;"><span class="slot-badge" style="background:#2d5a27; color:#fff; padding:3px 12px; border-radius:12px; font-weight:800;">Slot 1 (Example)</span></div>
              <div class="ghibli-scene-card" style="width:100%; display:flex; flex-direction:column; align-items:center;">
                <img src="images/p45_card_e.jpg" alt="Picture E" style="width:90px; height:90px; object-fit:cover; border-radius:12px; margin-bottom:4px;">
                <span style="font-weight:700; color:#2d5a27;">Picture E</span>
              </div>
            </div>
            ''')
        else:
            slots_html.append(f'''
            <div class="ghibli-drop-slot" data-slot="{s}" style="min-height:160px; background:rgba(255,255,255,0.7); border:2px dashed #cbd5e1; border-radius:18px; padding:12px; display:flex; flex-direction:column; align-items:center; justify-content:center; text-align:center;">
              <div class="slot-header" style="margin-bottom:8px;"><span class="slot-badge" style="background:#4a69bd; color:#fff; padding:3px 12px; border-radius:12px; font-weight:800;">Slot {s}</span></div>
              <div class="drop-placeholder" style="color:#888; font-size:0.85rem;"><i class="fa-regular fa-hand-pointer"></i> Drop card here</div>
            </div>
            ''')
            
    cards_pool_html = []
    for it in cards_data:
        if it["is_eg"]:
            continue
        cards_pool_html.append(f'''
        <div class="ghibli-draggable-card scene-card" draggable="true" data-letter="{it["letter"]}" data-target-slot="{it["correct_slot"]}" style="display:flex; flex-direction:column; align-items:center; padding:12px; background:#fff; border-radius:16px; border:1.5px solid #e2d7c3; box-shadow:0 4px 12px rgba(0,0,0,0.06); cursor:grab; min-width:130px; text-align:center;">
          <img src="{it["img"]}" alt="Picture {it["letter"]}" style="width:100px; height:100px; object-fit:cover; border-radius:12px; margin-bottom:8px; pointer-events:none;">
          <span style="font-weight:800; color:#2b261f; font-size:1rem;">Picture {it["letter"]}</span>
          <span style="font-size:0.75rem; color:#666; margin-top:2px;">{it["name"]}</span>
        </div>
        ''')
        
    return f'''
    <section class="ghibli-section ex-14-7-section">
      <div class="exercise-header" style="display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:12px; margin-bottom:20px;">
        <div>
          <span class="exercise-num" style="background:var(--ghibli-accent-green); color:#fff; padding:4px 12px; border-radius:20px; font-weight:700; font-size:0.85rem;"><i class="fa-solid fa-headphones"></i> Exercise {ex_id}</span>
          <h3 class="exercise-instruction" style="font-family:var(--font-heading); margin-top:8px; color:var(--ghibli-text-main); font-size:1.15rem;">{instruction}</h3>
          <p style="font-size:0.88rem; color:var(--ghibli-text-muted); margin-top:2px;">Click or drag the scene cards below into the numbered order slots (1 to 6) above!</p>
        </div>
        <button class="ghibli-btn ghibli-btn-gold" id="playFullEx14_7Btn" style="padding:10px 18px; font-size:0.9rem;"><i class="fa-solid fa-headphones"></i> Play Listening Audio Track</button>
      </div>
      
      <!-- 6 Numbered Drop Slots (ON TOP) -->
      <div class="slots-section-wrap" style="margin-bottom:24px;">
        <div class="ghibli-slots-grid" id="slotsGrid14_7" style="display:grid; grid-template-columns:repeat(auto-fit, minmax(140px, 1fr)); gap:14px;">
          {'\n'.join(slots_html)}
        </div>
      </div>
      
      <!-- Scene Cards Pool (BELOW) -->
      <div class="pool-section-wrap" style="background:rgba(255,255,255,0.6); padding:20px; border-radius:20px; border:1.5px solid #d4c5a9;">
        <div style="font-weight:800; color:#2d5a27; font-size:0.95rem; margin-bottom:14px;"><i class="fa-solid fa-images"></i> Available Scene Cards:</div>
        <div class="ghibli-speaker-pool" id="sceneCardsPool" style="display:flex; flex-wrap:wrap; gap:16px; justify-content:center;">
          {'\n'.join(cards_pool_html)}
        </div>
      </div>
    </section>
    '''

def render_multiple_choice_14_8(ex, ex_idx, page_num):
    """Page 45 Ex 14.8: Listen to 14.7 again and answer multiple choice questions."""
    ex_id = "14.8"
    instruction = "LISTEN TO 14.7 AGAIN AND ANSWER THE QUESTIONS"
    
    questions = [
        {"num": "1", "q": "Kate goes to the gym on...", "opts": ["Monday", "Tuesday", "Friday"], "correct": "Friday"},
        {"num": "2", "q": "Paul is a...", "opts": ["farmer", "teacher", "doctor"], "correct": "farmer"},
        {"num": "3", "q": "Jane is a...", "opts": ["nurse", "doctor", "teacher"], "correct": "nurse"},
        {"num": "4", "q": "On the weekend, Jane goes to...", "opts": ["a restaurant", "the movies", "a gym"], "correct": "a restaurant"},
        {"num": "5", "q": "Sally gets up at...", "opts": ["6am", "7am", "8am"], "correct": "6am"},
        {"num": "6", "q": "Sally goes swimming on...", "opts": ["Saturday", "Sunday", "Thursday"], "correct": "Saturday"},
        {"num": "7", "q": "Eric works at the...", "opts": ["school", "theater", "restaurant"], "correct": "theater"},
        {"num": "8", "q": "Eric works...", "opts": ["twice a week", "three days a week", "four days a week"], "correct": "four days a week"},
        {"num": "9", "q": "Claire is a...", "opts": ["waitress", "carpenter", "farmer"], "correct": "waitress"},
        {"num": "10", "q": "Claire starts work at...", "opts": ["6am", "4pm", "6pm"], "correct": "4pm"}
    ]
    
    cards = []
    for idx, it in enumerate(questions):
        correct = it["correct"]
        opt_btns = []
        for o in it["opts"]:
            opt_btns.append(f'''
            <button type="button" class="ghibli-option" data-value="{o}" style="display:flex; align-items:center; gap:10px; padding:10px 14px; border-radius:12px; border:2px solid #cbd5e1; background:#fff; font-weight:600; cursor:pointer; text-align:left; color:#2b261f;">
              <span class="mc-radio-box" style="width:18px; height:18px; border-radius:50%; border:2px solid #94a3b8; display:inline-block; flex-shrink:0;"></span>
              <span>{o}</span>
            </button>
            ''')
            
        cards.append(f'''
        <div class="ghibli-char-card" style="display:flex; flex-direction:column; padding:18px; background:rgba(255,255,255,0.92); border-radius:20px; border:1.5px solid #e2d7c3; box-shadow:0 6px 18px rgba(0,0,0,0.06);">
          <div style="font-weight:800; color:#2d5a27; font-size:1.05rem; margin-bottom:12px;">{it["num"]}. {it["q"]}</div>
          <div class="mc-options-grid" style="display:flex; flex-direction:column; gap:8px; width:100%;">
            {'\n'.join(opt_btns)}
          </div>
          <input type="hidden" class="ghibli-input" data-correct="{correct}" />
        </div>
        ''')
        
    return f'''
    <section class="ghibli-section">
      <div class="ghibli-section-header">
        <div class="ghibli-ex-num">{ex_id}</div>
        <div>
          <h3 class="ghibli-ex-instruction">{instruction}</h3>
          <p class="ghibli-ex-subtext">Listen to audio track 14.7 again and select the correct option for each question!</p>
        </div>
      </div>
      <div style="display:grid; grid-template-columns:repeat(auto-fill, minmax(280px, 1fr)); gap:20px;">
        {'\n'.join(cards)}
      </div>
    </section>
    '''
