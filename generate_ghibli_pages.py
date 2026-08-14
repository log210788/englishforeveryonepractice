#!/usr/bin/env python3
"""
generate_ghibli_pages.py - Studio Ghibli Interactive Page-by-Page Generator (v4.0)
Generates ghibli_page012.html through ghibli_page176.html using ghibli_page12.css.
Includes interactive Click & Drag / Tap word ordering chips, Ghibli character cards, flag badges, audio, and voice recorder buttons.
"""

import json
import os
import re
import html
import random

CONSOLIDATED_JSON_PATH = "output_json/all_pages_consolidated.json"
OUTPUT_DIR = "."

COUNTRY_FLAGS = {
    "turkey": "🇹🇷", "south korea": "🇰🇷", "thailand": "🇹🇭", "greece": "🇬🇷", "china": "🇨🇳",
    "portugal": "🇵🇹", "singapore": "🇸🇬", "egypt": "🇪🇬", "mongolia": "🇲🇳", "united kingdom": "🇬🇧",
    "france": "🇫🇷", "united arab emirates": "🇦🇪", "new zealand": "🇳🇿", "germany": "🇩🇪", "austria": "🇦🇹",
    "switzerland": "🇨🇭", "argentina": "🇦🇷", "russia": "🇷🇺", "australia": "🇦🇺", "canada": "🇨🇦",
    "philippines": "🇵🇭", "south africa": "🇿🇦", "brazil": "🇧🇷", "netherlands": "🇳🇱", "spain": "🇪🇸",
    "czech republic": "🇨🇿", "mexico": "🇲🇽", "india": "🇮🇳", "united states of america": "🇺🇸",
    "united states": "🇺🇸", "usa": "🇺🇸", "japan": "🇯🇵", "indonesia": "🇮🇩", "italy": "🇮🇹",
    "poland": "🇵🇱", "pakistan": "🇵🇰", "slovakia": "🇸🇰", "ireland": "🇮🇪"
}

COUNTRY_ISO = {
    "turkey": "tr", "south korea": "kr", "thailand": "th", "greece": "gr", "china": "cn",
    "portugal": "pt", "singapore": "sg", "egypt": "eg", "mongolia": "mn", "united kingdom": "gb",
    "france": "fr", "united arab emirates": "ae", "new zealand": "nz", "germany": "de", "austria": "at",
    "switzerland": "ch", "argentina": "ar", "russia": "ru", "australia": "au", "canada": "ca",
    "philippines": "ph", "south africa": "za", "brazil": "br", "netherlands": "nl", "spain": "es",
    "czech republic": "cz", "mexico": "mx", "india": "in", "united states of america": "us",
    "united states": "us", "usa": "us", "japan": "jp", "indonesia": "id", "italy": "it",
    "poland": "pl", "pakistan": "pk", "slovakia": "sk", "ireland": "ie"
}

NATIONALITY_ISO_MAP = {
    "spanish": "es", "spain": "es",
    "japanese": "jp", "japan": "jp",
    "italy": "it", "italian": "it",
    "french": "fr", "france": "fr",
    "pakistan": "pk", "pakistani": "pk",
    "irish": "ie", "ireland": "ie",
    "german": "de", "germany": "de",
    "new zealand": "nz",
    "canada": "ca", "canadian": "ca"
}

GHIBLI_AVATARS = [
    "images/ghibli/gary.jpg",
    "images/ghibli/natalie.jpg",
    "images/ghibli/sue.jpg",
    "images/ghibli/ryan.jpg",
    "images/ghibli/mia.jpg",
    "images/ghibli/amelia.jpg",
    "images/ghibli/avatar_boy.jpg",
    "images/ghibli/avatar_girl.jpg",
    "images/ghibli/avatar_man.jpg",
    "images/ghibli/avatar_woman.jpg"
]

PEOPLE_KEYWORDS = {
    "name", "i", "me", "my", "you", "your", "he", "him", "his", "she", "her", "we", "us", "our", "they", "them", "their",
    "who", "man", "men", "woman", "women", "boy", "girl", "child", "children", "kid", "kids", "person", "people",
    "teacher", "doctor", "student", "actor", "actress", "nurse", "hairdresser", "engineer", "chef", "waiter", "waitress",
    "brother", "sister", "mother", "father", "parent", "parents", "son", "daughter", "grandfather", "grandmother",
    "granddaughter", "granddaughters", "grandson", "grandsons", "husband", "wife", "pet", "dog", "cat",
    "uncle", "aunt", "cousin", "friend", "friends", "rachel", "noah", "marina", "james", "sophia", "alexander", "emily",
    "daniel", "olivia", "matthew", "kirsty", "kim", "dan", "lewis", "john", "sarah", "tom", "ben", "lisa",
    "christopher", "joe", "greg", "dolly", "sam"
}

def is_person_context(text, instruction=""):
    combined = f"{text or ''} {instruction or ''}".lower()
    words = set(re.findall(r'\b[a-zA-Z]+\b', combined))
    if words.intersection(PEOPLE_KEYWORDS):
        return True
    if any(k in combined for k in ["apostrophe", "belong", "family", "relative", "people"]):
        return True
    return False


EX1_4_DEFAULT_NAMES = {
    0: "Rachel Harper",
    1: "Noah Anderson",
    2: "Noah Anderson",
    3: "Marina Davis",
    4: "James Wilson",
    5: "Sophia Taylor",
    6: "Alexander White",
    7: "Emily Martin",
    8: "Daniel Thomas",
    9: "Olivia Jackson",
    10: "Matthew Harris"
}

UNIT_METADATA = [
    (8, 11, "Starter", "Reference & Warm-up", 
     "Reference overview of the English alphabet, numbers, and introductory language structures.", 
     "English alphabet & numbers", "Basic words & numbers", "Basic English literacy"),
    
    (12, 13, 1, "Introducing yourself", 
     'You can greet people by saying "Hello!" or "Hi!" Introduce yourself using "I am." You may also need to spell out the letters of your name.', 
     'Using "to be" with names', "Names and letters", "Saying your name"),
    
    (14, 15, 2, "Countries & Flags", 
     "Vocabulary module focused on country names, national flags, and spelling international locations.", 
     "Country names and flags", "Countries & Flags", "Identifying countries"),
    
    (16, 17, 3, "Talking about yourself", 
     'It\'s useful to know how to say your age and where you come from. You can use the verb "to be" to talk about these topics.', 
     '"To be" with ages and nationalities', "Numbers and nationalities", "Talking about yourself"),
    
    (18, 19, 4, "Family & Relatives", 
     "Vocabulary module for family relationships, family trees, and describing relatives.", 
     "Family terms & relationships", "Family & Relatives", "Describing your family"),
    
    (20, 21, 5, "Things you have", 
     'Use possessive adjectives to show who something belongs to. Use "this" for something near you and "that" for something further away.', 
     'Possessive adjectives; "this" and "that"', "Animals and family", "Talking about who things belong to"),
    
    (22, 22, 6, "Using apostrophes ('s)", 
     "Use the possessive apostrophe to show that something belongs to a person or animal.", 
     "Possessive apostrophe", "Family and pets", "Talking about belonging"),
    
    (23, 23, 12, "Entertainment", 
     "Vocabulary module covering hobbies, entertainment, and leisure activities.", 
     "Entertainment & leisure", "Entertainment", "Talking about entertainment"),
    
    (24, 25, 7, "Everyday Things", 
     "Vocabulary module covering common objects, personal possessions, and household items.", 
     "Everyday objects", "Everyday Things", "Naming common objects"),
    
    (26, 29, 8, "Talking about your things", 
     'Use demonstrative pronouns "these" and "those" to point to multiple things near or far from you.', 
     '"These" and "those"', "Possessions", "Using determiners and pronouns"),
    
    (30, 31, 9, "Occupations & Jobs", 
     "Vocabulary module covering professions, workplaces, and common occupations.", 
     "Job titles & occupations", "Jobs & Workplaces", "Identifying occupations"),
    
    (32, 35, 10, "Talking about your job", 
     'You can use "I am" followed by "a" or "an" to state your job or profession.', 
     'Using "I am" for your job', "Jobs and workplaces", "Describing your job"),
    
    (36, 37, 11, "Telling the time", 
     "Learn how to ask for and tell the time using hours, minutes, o'clock, past, and to.", 
     "Times of the day", "Words for time", "Saying what the time is"),
    
    (38, 39, 12, "Daily routines", 
     "Talk about regular daily activities using the present simple tense.", 
     "The present simple", "Routine activities", "Describing daily routines"),
    
    (40, 41, 13, "Describing your day", 
     "Use time expressions and simple present verbs to describe your daily schedule.", 
     "Present simple habits", "Daily habits & times", "Talking about your daily routine"),
    
    (42, 45, 14, "Describing your week", 
     'Use prepositions of time like "on" with days of the week to talk about weekly schedules.', 
     "Days and prepositions", "Days of the week", "Talking about your weekly routine"),
    
    (46, 49, 15, "Negatives with 'to be'", 
     'To make a sentence with the verb "to be" negative, add "not" after the verb.', 
     'Negatives with "to be"', '"Not"', "Saying what things are not"),
    
    (50, 53, 16, "More negatives", 
     'To make present simple sentences negative, use "do not" (don\'t) or "does not" (doesn\'t).', 
     "Present simple negative", "Daily activities", "Saying what you don't do"),
    
    (54, 57, 17, "Simple questions", 
     'Form simple questions in the present tense by placing "do" or "does" before the subject.', 
     "Simple questions", "Jobs and routine activities", "Asking simple questions"),
    
    (58, 59, 18, "Answering questions", 
     "Give short, natural answers to simple questions using subject pronouns and auxiliary verbs.", 
     "Simple answers", "Jobs and routines", "Answering spoken questions"),
    
    (60, 63, 19, "Asking questions", 
     'Use question words like "what," "where," "when," "who," and "why" to ask for specific information.', 
     "Open questions", "Question words", "Asking for details"),
    
    (64, 65, 20, "Town Places", 
     "Vocabulary module covering places around town, buildings, shops, and public spaces.", 
     "Places in town", "Towns & Buildings", "Naming places in town"),
    
    (66, 69, 21, "Talking about your town", 
     'Use "there is" for singular nouns and "there are" for plural nouns to describe what a town contains.', 
     '"There is" and "there are"', "Towns and buildings", "Describing a town"),
    
    (70, 73, 22, "Using 'a' and 'the'", 
     'Use "a" or "an" when mentioning something for the first time, and "the" when referring to a specific thing.', 
     "Definite and indefinite articles", "Places in town", "Using articles"),
    
    (74, 77, 23, "Orders and directions", 
     "Use imperatives to tell someone to do something, give instructions, warnings, or directions.", 
     "Imperatives", "Directions", "Finding your way"),
    
    (78, 80, 24, "Joining sentences", 
     'Use conjunctions like "and" to add information and "but" to show contrast between ideas.', 
     'Using "and" and "but"', "Town, jobs, and family", "Joining sentences"),
    
    (81, 83, 25, "Describing places", 
     'Use adjectives before nouns or after the verb "to be" to describe towns, places, and buildings.', 
     "Adjectives", "Place adjectives and nouns", "Describing places"),
    
    (84, 85, 26, "Giving reasons", 
     'Use the conjunction "because" to give reasons and answer questions beginning with "why".', 
     '"Because"', "Places and jobs", "Giving reasons"),
    
    (86, 87, 27, "Around the house", 
     "Vocabulary module covering household objects, rooms, furniture, and appliances.", 
     "House & furniture", "Household objects", "Naming house items"),
    
    (88, 91, 28, "Accommodation & House", 
     'When you talk about things you own, such as furniture or pets, you can use the verb "have."', 
     'Using "have"', "Household objects", "Talking about possessions"),
    
    (92, 95, 29, "What do you have?", 
     'Use questions with "have" to ask someone about the things they own. "Do" or "does" helps to form the question.', 
     '"Have" questions', "House and furniture", "Asking about household objects"),
    
    (96, 97, 30, "Food and drink", 
     "Vocabulary module covering food, drinks, containers, and kitchen items.", 
     "Food & Drink terms", "Food & Drink", "Identifying food items"),
    
    (98, 101, 31, "Counting", 
     "Learn how to count countable objects and talk about singular and plural food items.", 
     "Countable & Uncountable", "Food & Quantities", "Counting food & drinks"),
    
    (102, 105, 32, "Measuring", 
     'Use "enough" when you have the correct number or amount of something. Use "too many" or "too much" if you have more than enough.', 
     "Measurements", "Ingredients and quantities", "Talking about amounts"),
    
    (106, 107, 33, "Clothes & Accessories", 
     "Vocabulary module covering clothes, accessories, and colors.", 
     "Clothing & Accessories", "Clothes & Colors", "Naming clothing items"),
    
    (108, 111, 34, "At the shops", 
     'You can use many different verbs to talk about what happens when you are shopping. Use "too" and "enough" to describe how well clothes fit you.', 
     'Using "too" and "fit"', "Shopping and clothes", "Describing clothes"),
    
    (112, 115, 35, "Describing things", 
     "You can use adjectives to give your opinion about things as well as to give factual information. You can use more than one adjective before a noun.", 
     "Opinion adjectives", "Shopping and materials", "Giving opinions"),
    
    (116, 117, 36, "Sports Vocabulary", 
     "Vocabulary module covering sports equipment, games, and sports venues.", 
     "Sports & Equipment", "Sports equipment", "Naming sports items"),
    
    (118, 121, 37, "Talking about sports", 
     'To describe taking part in some sports, you use the verb "go" plus the gerund. For other sports, you use "play" plus the noun.', 
     '"Go" and "play"', "Sports", "Talking about sports"),
    
    (122, 123, 38, "Hobbies & Pastimes", 
     "Vocabulary module covering common hobbies, pastimes, and weekend activities.", 
     "Hobbies & Pastimes", "Free time activities", "Naming hobbies"),
    
    (124, 127, 39, "Free time activities", 
     'Adverbs of frequency show how often you do something, from something you do very frequently ("always") to something you don\'t do at all ("never").', 
     "Adverbs of frequency", "Pastimes", "Talking about your free time"),
    
    (128, 131, 40, "Likes and dislikes", 
     'Verbs such as "love," "like," and "hate" express your feelings about things. You can use these verbs with nouns or gerunds.', 
     '"Love," "like," and "hate"', "Food, sports, and pastimes", "Talking about what you like"),
    
    (132, 133, 41, "Music Vocabulary", 
     "Vocabulary module covering musical instruments, genres, and entertainment terms.", 
     "Music & Instruments", "Music & Instruments", "Naming musical terms"),
    
    (134, 137, 42, "Expressing preference", 
     'You use "like" and "love" to show how much you enjoy something. "Favorite" is used to identify the thing you love most in a group.', 
     'Using "favorite"', "Food and music", "Talking about your favorite things"),
    
    (138, 139, 43, "Abilities Vocabulary", 
     "Vocabulary module covering talents, physical skills, and artistic abilities.", 
     "Abilities & Skills", "Talents & Skills", "Naming abilities"),
    
    (140, 143, 44, "What you can and can't do", 
     'Use "can" to talk about the things you are able to do, such as ride a bicycle or play the guitar. Use "cannot" or "can\'t" for things you are not able to do.', 
     '"Can," "can\'t," and "cannot"', "Talents and abilities", "Say what you can and can't do"),
    
    (144, 145, 45, "Describing actions", 
     'Words such as "quietly" and "loudly" are called adverbs. They give more information about verbs, so you can use them to describe how you do something.', 
     "Regular and irregular adverbs", "Hobbies and activities", "Describing activities"),
    
    (146, 147, 46, "Describing ability", 
     'Words such as "quite" and "very" are modifying adverbs. You can use them before other adverbs to give more information about how you do something.', 
     "Modifying adverbs", "Skills and abilities", "Saying how well you do things"),
    
    (148, 151, 47, "Wishes and desires", 
     'You can use "I want" and "I would like" to talk about things you want to do. You can also use their negative form to say what you would not like to do.', 
     '"Would" and "want"', "Leisure activities", "Talking about ambitions"),
    
    (152, 155, 48, "Studying", 
     'When talking about your studies you can use "I would" and "I want" to say which subjects you would like to learn. Use adverbs to say how much you want to do them.', 
     "Adverbs and articles", "Academic subjects", "Talking about your studies"),
    
    (156, 176, 49, "Review & Practice Modules", 
     "Comprehensive review modules, grammar reference summaries, and final practice exercises across all Level 1 units.", 
     "Level 1 Grammar Review", "Comprehensive Level 1 Vocab", "Consolidating Level 1 Skills")
]

def get_unit_info(page_num):
    for start_p, end_p, u_num, u_title, u_desc, new_lang, vocab, new_skill in UNIT_METADATA:
        if start_p <= page_num <= end_p:
            return u_num, u_title, u_desc, new_lang, vocab, new_skill
    return "", "English Practice", "Interactive Ghibli Edition practice page.", "English Grammar & Vocabulary", "Level 1 Vocabulary", "Practicing English Skills"

def escape(text):
    if text is None:
        return ""
    return html.escape(str(text))

def load_pages():
    with open(CONSOLIDATED_JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    raw_pages = data.get("pages", [])
    filtered_pages = []
    seen = set()

    for idx, page in enumerate(raw_pages):
        p_num = page.get("page_number")
        if p_num is not None and 8 <= p_num <= 176:
            if idx == 12:  # Skip raw Page 12 OCR duplicate
                continue
            if p_num not in seen:
                seen.add(p_num)
                filtered_pages.append(page)

    filtered_pages.sort(key=lambda x: x.get("page_number", 0))
    return filtered_pages

def compute_navigation(pages):
    nav_map = {}
    total = len(pages)
    for i, page in enumerate(pages):
        p_num = page["page_number"]
        filename = f"ghibli_page{p_num:03d}.html" if p_num != 12 else "ghibli_page12.html"
        
        prev_p = pages[i-1]['page_number'] if i > 0 else None
        next_p = pages[i+1]['page_number'] if i < total - 1 else None
        
        prev_fn = (f"ghibli_page{prev_p:03d}.html" if prev_p != 12 else "ghibli_page12.html") if prev_p else None
        next_fn = (f"ghibli_page{next_p:03d}.html" if next_p != 12 else "ghibli_page12.html") if next_p else None

        nav_map[p_num] = {
            "filename": filename,
            "prev": prev_fn,
            "next": next_fn,
            "page_index": i + 1,
            "total_pages": total
        }
    return nav_map

def clean_spelled_text(text):
    if not text:
        return ""
    s = str(text).strip()
    if re.search(r'\b[A-Za-z](-[A-Za-z])+\b', s):
        # Unhyphenate: M-A-R-I-N-A -> Marina
        unhyphenated = re.sub(r'(?<=\b[A-Za-z])-(?=[A-Za-z]\b)', '', s)
        return unhyphenated.title()
    return s

def format_correct_answer(val):
    if val is None:
        return ""
    if isinstance(val, list):
        return "|".join(format_correct_answer(x) for x in val)
    s = str(val).strip()
    if re.search(r'\b[A-Za-z](-[A-Za-z])+\b', s):
        unhyphenated = re.sub(r'(?<=\b[A-Za-z])-(?=[A-Za-z]\b)', '', s)
        return f"{unhyphenated.title()}|{unhyphenated}|{s}"
    return s

def render_audio_btn(item):
    audio_path = item.get("audio_file_path")
    if audio_path:
        return f'<button class="ghibli-audio-play-btn" data-audio="{escape(audio_path)}" title="Play Audio"><i class="fa-solid fa-play"></i></button>'
    return ""

def render_rec_btn(item_id):
    return f'''
    <div class="voice-recorder-controls">
      <button class="voice-btn rec-btn" data-id="{escape(item_id)}"><i class="fa-solid fa-microphone"></i> Rec</button>
      <button class="voice-btn play-rec-btn hidden" data-id="{escape(item_id)}"><i class="fa-solid fa-play"></i> My Voice</button>
    </div>
    '''

def render_flag_badge(correct_ans):
    if not correct_ans:
        return ""
    ans_first = correct_ans.split('|')[0].strip().lower()
    emoji = COUNTRY_FLAGS.get(ans_first, "🏳️")
    if ans_first in COUNTRY_ISO:
        iso = COUNTRY_ISO[ans_first]
        return f'<img src="images/flags/{iso}.svg" alt="{html.escape(ans_first)} flag" class="ghibli-flag-img" style="width: 52px; height: 35px; object-fit: cover; border-radius: 6px; border: 1px solid rgba(0,0,0,0.15); box-shadow: 0 2px 6px rgba(0,0,0,0.12); vertical-align: middle; margin-right: 8px;" onerror="this.onerror=null; this.replaceWith(document.createTextNode(\'{emoji}\'));">'
    elif ans_first in COUNTRY_FLAGS:
        return f'<span class="ghibli-flag-badge" style="font-size: 2.2rem; margin-right: 8px; vertical-align: middle;">{emoji}</span>'
    return ""

EX34_AVATARS = [
    "images/ghibli/gary.jpg",          # 0: Alfonso (87, Spain, male)
    "images/ghibli/avatar_woman.jpg",  # 1: Abe (72, Japan, female)
    "images/ghibli/avatar_boy.jpg",    # 2: Mia and Leo (12, Italy)
    "images/ghibli/natalie.jpg",       # 3: Chantal (66, France, female)
    "images/ghibli/ryan.jpg",          # 4: Amir and Aamna (90, Pakistan)
    "images/ghibli/sue.jpg",           # 5: I (24, Ireland)
    "images/ghibli/avatar_man.jpg",    # 6: Max (47, Germany, male)
    "images/ghibli/amelia.jpg",        # 7: We (38, New Zealand)
    "images/ghibli/avatar_girl.jpg"    # 8: My sister (4, Canada, little girl)
]

def render_ghibli_family_tree(ex, ex_idx, page_num):
    ex_id = escape(ex.get("exercise_id") or "4.1")
    instruction = escape(ex.get("instruction") or "PABLO'S FAMILY WRITE THE WORDS FROM THE PANEL IN THE CORRECT PLACES ON PABLO'S FAMILY TREE")
    
    words = [
        "grandmother", "grandfather", "father", "mother", "sister", 
        "uncle", "aunt", "Pablo", "wife", "son", "daughter", "grandson", "granddaughter"
    ]
    
    chips_html = "".join([
        f'<span class="family-word-chip {"example-chip" if w == "grandmother" else ""}">{w}</span>'
        for w in words
    ])
    
    word_panel_html = f'''
    <div class="ghibli-word-panel ghibli-family-word-bank">
      <div style="font-family: var(--font-heading, 'Outfit', sans-serif); font-weight: 700; color: var(--ghibli-text-main, #2b261f); font-size: 1.05rem; margin-bottom: 12px; display: flex; align-items: center; justify-content: center; gap: 8px;">
        <i class="fa-solid fa-leaf" style="color: #2d5a27;"></i> <span>Family Vocabulary Panel</span> <i class="fa-solid fa-seedling" style="color: #2d5a27;"></i>
      </div>
      <div class="family-chips-container" style="display: flex; flex-wrap: wrap; justify-content: center; gap: 10px;">
        {chips_html}
      </div>
    </div>
    '''
    
    tree_html = f'''
    <section class="ghibli-section">
      <div class="ghibli-section-header">
        <div class="ghibli-ex-num">{ex_id}</div>
        <div>
          <h3 class="ghibli-ex-instruction">{instruction}</h3>
          <p class="ghibli-ex-subtext">Click play to listen or use Rec to practice speaking out loud!</p>
        </div>
      </div>
      
      {word_panel_html}

      <div class="ghibli-family-tree-canvas">
        
        <!-- GENERATION 1: GRANDPARENTS (TOP TIER) -->
        <div class="tree-gen-group">
          <div class="tree-couple-row" style="display:flex; align-items:center; gap:20px;">
            
            <!-- Grandmother (Example - Silhouette Woman, ONLY ONE IN A BOX) -->
            <div class="tree-node example-card" style="background:rgba(45,90,39,0.08); border:2px solid #2d5a27; border-radius:20px; padding:12px;">
              <div class="tree-avatar-container">
                <img src="images/people/womanNoDetail.png" alt="Grandmother" class="tree-avatar">
                <div class="tree-audio-btn-wrap">
                  <button class="ghibli-audio-play-btn" data-audio="audio/4/4_1_eg.mp3" title="Play Audio"><i class="fa-solid fa-play"></i></button>
                </div>
              </div>
              <div style="font-size:0.75rem; font-weight:700; color:#2d5a27; text-transform:uppercase; margin-bottom:4px;">
                <span class="ghibli-example-badge" style="background:#2d5a27; color:#fff; padding:2px 6px; border-radius:10px; font-size:0.7rem;">Example</span>
              </div>
              <div class="ghibli-input-wrap" style="width:100%;">
                <input type="text" class="ghibli-input example-input tree-node-input" data-correct="grandmother" value="grandmother" readonly style="border-color:#2d5a27; background:rgba(45,90,39,0.12); font-weight:700; color:#2d5a27; text-align:center;" placeholder="grandmother">
              </div>
            </div>

            <div class="marriage-badge-wrap">
              <span class="marriage-badge"><i class="fa-solid fa-ring"></i> Married <i class="fa-solid fa-heart" style="color:#e63946;"></i></span>
            </div>

            <!-- Grandfather (Blank 1 - Silhouette Man, NO BOX) -->
            <div class="tree-node">
              <div class="tree-avatar-container">
                <img src="images/people/manNoDetail.png" alt="Grandfather" class="tree-avatar">
                <div class="tree-audio-btn-wrap">
                  <button class="ghibli-audio-play-btn" data-audio="audio/4/4_1_1.mp3" title="Play Audio"><i class="fa-solid fa-play"></i></button>
                </div>
              </div>
              <div class="ghibli-input-wrap" style="width:100%;">
                <input type="text" class="ghibli-input tree-node-input" data-correct="grandfather" placeholder="Type answer...">
              </div>
            </div>

          </div>
        </div>

        <!-- DESCENT CONNECTOR: GRANDPARENTS -> TWO BROTHERS ONLY (FATHER & UNCLE - BYPASSING MOTHER) -->
        <div class="tree-descent-connector gen1-to-gen2">
          <div class="descent-stem-top"></div>
          <div class="descent-fork-bar bar-gen1-to-gen2"></div>
          <div class="descent-stems-pair pair-gen1-to-gen2">
            <div class="stem-down"></div>
            <div class="stem-down"></div>
          </div>
        </div>

        <!-- GENERATION 2: TWO BROTHERS (FATHER & UNCLE) - NO BOXES -->
        <div class="tree-gen-group">
          <div class="gen2-wide-row" style="display:flex; justify-content:center; align-items:center; gap:24px; flex-wrap:wrap; width:100%;">
            
            <!-- LEFT: FATHER + MOTHER (NO BOX CARDS) -->
            <div class="couple-unboxed-wrap" style="display:flex; align-items:center; gap:12px;">
              <!-- Mother (Given In-law Spouse from outside family) -->
              <div class="tree-node in-law-node">
                <div class="tree-avatar-container">
                  <img src="images/people/womanNoDetail.png" alt="Mother" class="tree-avatar">
                </div>
                <span class="given-role-badge">mother</span>
              </div>

              <div class="marriage-mini-link" title="Married"><i class="fa-solid fa-heart"></i></div>

              <!-- Father (Blank 2 - Brother 1 / Blood Son) -->
              <div class="tree-node blood-node">
                <div class="tree-avatar-container">
                  <img src="images/people/manNoDetail.png" alt="Father" class="tree-avatar">
                  <div class="tree-audio-btn-wrap">
                    <button class="ghibli-audio-play-btn" data-audio="audio/4/4_1_2.mp3" title="Play Audio"><i class="fa-solid fa-play"></i></button>
                  </div>
                </div>
                <div class="ghibli-input-wrap" style="width:100%;">
                  <input type="text" class="ghibli-input tree-node-input" data-correct="father" placeholder="Type answer...">
                </div>
              </div>
            </div>

            <!-- RIGHT: UNCLE (SINGLE MALE SILHOUETTE - NO BOX) -->
            <div class="tree-node blood-node">
              <div class="tree-avatar-container">
                <img src="images/people/manNoDetail.png" alt="Uncle" class="tree-avatar">
                <div class="tree-audio-btn-wrap">
                  <button class="ghibli-audio-play-btn" data-audio="audio/4/4_1_4.mp3" title="Play Audio"><i class="fa-solid fa-play"></i></button>
                </div>
              </div>
              <div class="ghibli-input-wrap" style="width:100%;">
                <input type="text" class="ghibli-input tree-node-input" data-correct="uncle" placeholder="Type answer...">
              </div>
            </div>

          </div>
        </div>

        <!-- DESCENT CONNECTOR: FATHER & MOTHER -> SISTER, BROTHER & PABLO -->
        <div class="tree-descent-connector align-parents-branch">
          <div class="descent-stem-top"></div>
          <div class="descent-fork-bar bar-mid"></div>
          <div class="descent-stems-pair pair-mid">
            <div class="stem-down"></div>
            <div class="stem-down"></div>
          </div>
        </div>

        <!-- GENERATION 3: SISTER, BROTHER, PABLO (BLOOD SIBLINGS) + WIFE (IN-LAW) - NO BOXES -->
        <div class="tree-gen-group">
          <div class="gen3-row" style="display:flex; justify-content:center; align-items:center; gap:20px; flex-wrap:wrap; width:100%;">
            <!-- Sister (Blank 3 - Blood Daughter of Parents) -->
            <div class="tree-node blood-node">
              <div class="tree-avatar-container">
                <img src="images/people/womanNoDetail.png" alt="Sister" class="tree-avatar">
                <div class="tree-audio-btn-wrap">
                  <button class="ghibli-audio-play-btn" data-audio="audio/4/4_1_3.mp3" title="Play Audio"><i class="fa-solid fa-play"></i></button>
                </div>
              </div>
              <div class="ghibli-input-wrap" style="width:100%;">
                <input type="text" class="ghibli-input tree-node-input" data-correct="sister" placeholder="Type answer...">
              </div>
            </div>

            <!-- Brother (Given Blood Brother of Pablo & Sister - NO BOX) -->
            <div class="tree-node blood-node">
              <div class="tree-avatar-container">
                <img src="images/people/manNoDetail.png" alt="Brother" class="tree-avatar">
              </div>
              <span class="given-role-badge">brother</span>
            </div>

            <!-- Pablo & Wife Couple (NO BOX CARD) -->
            <div class="couple-unboxed-wrap" style="display:flex; align-items:center; gap:12px;">
              <!-- Pablo (Given Hero - Blood Son of Parents) -->
              <div class="tree-node hero-node">
                <div class="tree-avatar-container">
                  <img src="images/people/manNoDetail.png" alt="Pablo" class="tree-avatar">
                </div>
                <span class="given-role-badge hero-badge">Pablo</span>
              </div>

              <div class="marriage-mini-link" title="Married"><i class="fa-solid fa-heart"></i></div>

              <!-- Wife (Given In-Law) -->
              <div class="tree-node in-law-node">
                <div class="tree-avatar-container">
                  <img src="images/people/womanNoDetail.png" alt="Wife" class="tree-avatar">
                </div>
                <span class="given-role-badge">wife</span>
              </div>
            </div>

          </div>
        </div>

        <!-- DESCENT CONNECTOR: PABLO & WIFE -> SON & DAUGHTER -->
        <div class="tree-descent-connector align-pablo-branch">
          <div class="descent-stem-top"></div>
          <div class="descent-fork-bar bar-narrow"></div>
          <div class="descent-stems-pair pair-narrow">
            <div class="stem-down"></div>
            <div class="stem-down"></div>
          </div>
        </div>

        <!-- GENERATION 4: DAUGHTER & SON-IN-LAW + SON (NO BOXES) -->
        <div class="tree-gen-group">
          <div class="gen4-row" style="display:flex; justify-content:center; align-items:center; gap:24px; flex-wrap:wrap; width:100%;">
            
            <!-- Daughter & Son-in-Law Married Couple (NO BOX CARD) -->
            <div class="couple-unboxed-wrap" style="display:flex; align-items:center; gap:12px;">
              <!-- Son-in-Law (Given In-Law Spouse - Adult Male Silhouette) -->
              <div class="tree-node in-law-node">
                <div class="tree-avatar-container">
                  <img src="images/people/manNoDetail.png" alt="Son-in-Law" class="tree-avatar">
                </div>
                <span class="given-role-badge">son-in-law</span>
              </div>

              <div class="marriage-mini-link" title="Married"><i class="fa-solid fa-heart"></i></div>

              <!-- Daughter (Blank 6 - Adult Silhouette Woman) -->
              <div class="tree-node blood-node daughter-node">
                <div class="tree-avatar-container">
                  <img src="images/people/womanNoDetail.png" alt="Daughter" class="tree-avatar">
                  <div class="tree-audio-btn-wrap">
                    <button class="ghibli-audio-play-btn" data-audio="audio/4/4_1_6.mp3" title="Play Audio"><i class="fa-solid fa-play"></i></button>
                  </div>
                </div>
                <div class="ghibli-input-wrap" style="width:100%;">
                  <input type="text" class="ghibli-input tree-node-input" data-correct="daughter" placeholder="Type answer...">
                </div>
              </div>
            </div>

            <!-- Son (Blank 5 - Adult Silhouette Man) -->
            <div class="tree-node blood-node">
              <div class="tree-avatar-container">
                <img src="images/people/manNoDetail.png" alt="Son" class="tree-avatar">
                <div class="tree-audio-btn-wrap">
                  <button class="ghibli-audio-play-btn" data-audio="audio/4/4_1_5.mp3" title="Play Audio"><i class="fa-solid fa-play"></i></button>
                </div>
              </div>
              <div class="ghibli-input-wrap" style="width:100%;">
                <input type="text" class="ghibli-input tree-node-input" data-correct="son" placeholder="Type answer...">
              </div>
            </div>

          </div>
        </div>

        <!-- DESCENT CONNECTOR: DAUGHTER -> GRANDCHILDREN -->
        <div class="tree-descent-connector align-daughter-branch">
          <div class="descent-stem-top"></div>
          <div class="descent-fork-bar bar-narrow"></div>
          <div class="descent-stems-pair pair-narrow">
            <div class="stem-down"></div>
            <div class="stem-down"></div>
          </div>
        </div>

        <!-- GENERATION 5: GRANDCHILDREN (RIGHT AT THE BOTTOM) - NO BOXES -->
        <div class="tree-gen-group">
          <div class="gen5-row" style="display:flex; justify-content:center; align-items:center; gap:24px; flex-wrap:wrap; width:100%;">
            <!-- Grandson (Blank 7 - Child Silhouette Boy) -->
            <div class="tree-node blood-node">
              <div class="tree-avatar-container">
                <img src="images/people/boyNoDetail.png" alt="Grandson" class="tree-avatar">
                <div class="tree-audio-btn-wrap">
                  <button class="ghibli-audio-play-btn" data-audio="audio/4/4_1_7.mp3" title="Play Audio"><i class="fa-solid fa-play"></i></button>
                </div>
              </div>
              <div class="ghibli-input-wrap" style="width:100%;">
                <input type="text" class="ghibli-input tree-node-input" data-correct="grandson" placeholder="Type answer...">
              </div>
            </div>

            <!-- Granddaughter (Blank 8 - Child Silhouette Girl) -->
            <div class="tree-node blood-node">
              <div class="tree-avatar-container">
                <img src="images/people/girlNoDetail.png" alt="Granddaughter" class="tree-avatar">
                <div class="tree-audio-btn-wrap">
                  <button class="ghibli-audio-play-btn" data-audio="audio/4/4_1_8.mp3" title="Play Audio"><i class="fa-solid fa-play"></i></button>
                </div>
              </div>
              <div class="ghibli-input-wrap" style="width:100%;">
                <input type="text" class="ghibli-input tree-node-input" data-correct="granddaughter" placeholder="Type answer...">
              </div>
            </div>

          </div>
        </div>

      </div>
    </section>
    '''
    return tree_html


def render_ghibli_animals_exercise(ex, ex_idx, page_num):
    ex_id = str(ex.get("exercise_id") or "4.2")
    instruction = str(ex.get("instruction") or "PETS AND DOMESTIC ANIMALS: WRITE THE WORDS FROM THE PANEL UNDER THE CORRECT PICTURES")

    # Word panel items (matching original book order)
    words = [
        ("guinea pig", False),
        ("parrot", False),
        ("dog", False),
        ("chicken", False),
        ("snake", False),
        ("hamster", True),  # Example (crossed out)
        ("cat", False),
        ("rabbit", False),
        ("fish", False),
        ("tortoise", False),
        ("pig", False),
        ("horse", False)
    ]

    word_chips = []
    for w, is_eg in words:
        if is_eg:
            word_chips.append(f'<li class="animal-word-item example-item" data-word="{w}" style="padding: 6px 12px; background: rgba(45,90,39,0.1); color: #2d5a27; font-weight: 700; border-radius: 8px; text-decoration: line-through; opacity: 0.75; font-size: 0.95rem;">{w}</li>')
        else:
            word_chips.append(f'<li class="animal-word-item" data-word="{w}" style="padding: 6px 12px; background: #ffffff; color: #2b261f; font-weight: 600; border-radius: 8px; border: 1px solid rgba(45,90,39,0.18); font-size: 0.95rem; box-shadow: 0 1px 3px rgba(0,0,0,0.03);">{w}</li>')

    sidebar_word_panel = f'''
    <div class="animal-sidebar-panel" style="flex: 0 0 220px; background: rgba(255,255,255,0.7); border: 2px solid rgba(45,90,39,0.2); border-radius: 20px; padding: 18px; backdrop-filter: blur(8px); box-shadow: 0 6px 20px rgba(0,0,0,0.05); align-self: flex-start;">
      <div style="font-family: var(--font-heading, 'Outfit', sans-serif); font-weight: 800; color: #2d5a27; font-size: 1.05rem; margin-bottom: 14px; text-align: center; display: flex; align-items: center; justify-content: center; gap: 8px;">
        <i class="fa-solid fa-paw"></i> <span>Word Panel</span>
      </div>
      <ul style="list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 8px;">
        {"".join(word_chips)}
      </ul>
    </div>
    '''

    # 12 animal items matching the book's 3x4 grid order
    animal_items = [
        {"num": 0, "name": "hamster", "correct": "hamster", "is_example": True, "img": "images/animals/clean/hamster.png", "audio": "audio/4/4_2_eg.mp3"},
        {"num": 1, "name": "cat", "correct": "cat", "is_example": False, "img": "images/animals/clean/cat.png", "audio": "audio/4/4_2_1.mp3"},
        {"num": 2, "name": "chicken", "correct": "chicken", "is_example": False, "img": "images/animals/clean/chicken.png", "audio": "audio/4/4_2_2.mp3"},
        {"num": 3, "name": "rabbit", "correct": "rabbit", "is_example": False, "img": "images/animals/clean/rabbit.png", "audio": "audio/4/4_2_3.mp3"},
        {"num": 4, "name": "tortoise", "correct": "tortoise", "is_example": False, "img": "images/animals/clean/tortoise.png", "audio": "audio/4/4_2_4.mp3"},
        {"num": 5, "name": "parrot", "correct": "parrot", "is_example": False, "img": "images/animals/clean/parrot.png", "audio": "audio/4/4_2_5.mp3"},
        {"num": 6, "name": "dog", "correct": "dog", "is_example": False, "img": "images/animals/clean/dog.png", "audio": "audio/4/4_2_6.mp3"},
        {"num": 7, "name": "fish", "correct": "fish", "is_example": False, "img": "images/animals/clean/fish.png", "audio": "audio/4/4_2_7.mp3"},
        {"num": 8, "name": "snake", "correct": "snake", "is_example": False, "img": "images/animals/clean/snake.png", "audio": "audio/4/4_2_8.mp3"},
        {"num": 9, "name": "pig", "correct": "pig", "is_example": False, "img": "images/animals/clean/pig.png", "audio": "audio/4/4_2_9.mp3"},
        {"num": 10, "name": "horse", "correct": "horse", "is_example": False, "img": "images/animals/clean/horse.png", "audio": "audio/4/4_2_10.mp3"},
        {"num": 11, "name": "guinea pig", "correct": "guinea pig", "is_example": False, "img": "images/animals/clean/guinea_pig.png", "audio": "audio/4/4_2_11.mp3"},
    ]

    cards_html = []
    for item in animal_items:
        num = item["num"]
        name = item["name"]
        correct = item["correct"]
        is_eg = item["is_example"]
        img_path = item["img"]
        audio_path = item["audio"]
        item_id = f"p19_ex1_i{num}" if not is_eg else "p19_ex1_eg"

        if is_eg:
            cards_html.append(f'''
            <div class="animal-card example-card" style="background: rgba(45,90,39,0.06); border: 2px solid #2d5a27; border-radius: 18px; padding: 14px; display: flex; flex-direction: column; align-items: center; position: relative;">
              <div class="animal-img-container" style="width: 100%; height: 140px; background: #ffffff; border-radius: 12px; border: 1.5px solid rgba(45,90,39,0.15); display: flex; align-items: center; justify-content: center; margin-bottom: 10px; padding: 8px;">
                <img src="{img_path}" alt="{name}" style="max-width: 90%; max-height: 90%; object-fit: contain;">
              </div>
              <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 8px;">
                <span class="ghibli-example-badge" style="background:#2d5a27; color:#fff; padding:2px 8px; border-radius:10px; font-size:0.75rem; font-weight:700; text-transform:uppercase;">Example</span>
              </div>
              <div style="display: flex; align-items: center; gap: 8px; width: 100%;">
                <button class="ghibli-audio-play-btn" data-audio="{audio_path}" title="Play Audio"><i class="fa-solid fa-play"></i></button>
                <input type="text" class="ghibli-input example-input" data-correct="{correct}" value="{correct}" readonly style="flex: 1; border-color:#2d5a27; background:rgba(45,90,39,0.12); font-weight:700; color:#2d5a27; text-align:center;" placeholder="{correct}">
              </div>
              <div class="voice-recorder-controls" style="margin-top: 8px; width: 100%; display: flex; justify-content: center;">
                <button class="voice-btn rec-btn" data-id="{item_id}"><i class="fa-solid fa-microphone"></i> Rec</button>
                <button class="voice-btn play-rec-btn hidden" data-id="{item_id}"><i class="fa-solid fa-play"></i> My Voice</button>
              </div>
            </div>
            ''')
        else:
            cards_html.append(f'''
            <div class="animal-card" style="background: var(--ghibli-card-bg, #ffffff); border: 2px solid var(--ghibli-border, rgba(0,0,0,0.08)); border-radius: 18px; padding: 14px; display: flex; flex-direction: column; align-items: center; position: relative;">
              <div class="animal-img-container" style="width: 100%; height: 140px; background: rgba(245,248,245,0.7); border-radius: 12px; border: 1.5px solid rgba(45,90,39,0.12); display: flex; align-items: center; justify-content: center; margin-bottom: 10px; padding: 8px; position: relative;">
                <img src="{img_path}" alt="{name}" style="max-width: 90%; max-height: 90%; object-fit: contain;">
                <span style="position: absolute; bottom: 6px; left: 6px; background: rgba(45,90,39,0.85); color: #ffffff; font-weight: 800; font-size: 0.8rem; border-radius: 50%; width: 24px; height: 24px; display: flex; align-items: center; justify-content: center;">{num}</span>
              </div>
              <div style="display: flex; align-items: center; gap: 8px; width: 100%;">
                <button class="ghibli-audio-play-btn" data-audio="{audio_path}" title="Play Audio"><i class="fa-solid fa-play"></i></button>
                <input type="text" class="ghibli-input" data-correct="{correct}" placeholder="Type animal name..." style="flex: 1; text-align: center;">
              </div>
              <div class="voice-recorder-controls" style="margin-top: 8px; width: 100%; display: flex; justify-content: center;">
                <button class="voice-btn rec-btn" data-id="{item_id}"><i class="fa-solid fa-microphone"></i> Rec</button>
                <button class="voice-btn play-rec-btn hidden" data-id="{item_id}"><i class="fa-solid fa-play"></i> My Voice</button>
              </div>
            </div>
            ''')

    grid_items_str = "".join(cards_html)
    grid_container_html = f'''
    <div class="animal-cards-grid" style="flex: 1; display: grid; grid-template-columns: repeat(3, 1fr); gap: 18px;">
      {grid_items_str}
    </div>
    '''

    section_html = f'''
    <section class="ghibli-section">
      <div class="ghibli-section-header">
        <div class="ghibli-ex-num">{ex_id}</div>
        <div>
          <h3 class="ghibli-ex-instruction">{instruction}</h3>
          <p class="ghibli-ex-subtext">Look at each animal picture, click play to listen, write the correct animal name, and practice speaking out loud!</p>
        </div>
      </div>
      
      <div class="animal-exercise-wrapper" style="display: flex; gap: 24px; margin-top: 20px; flex-wrap: wrap;">
        {grid_container_html}
        {sidebar_word_panel}
      </div>
    </section>
    '''
    return section_html


def render_fill_in_blank(ex, ex_idx, page_num):
    ex_id = escape(ex.get("exercise_id") or f"{page_num}.{ex_idx+1}")
    if page_num == 18 or ex_id == "4.1":
        return render_ghibli_family_tree(ex, ex_idx, page_num)

    instruction = escape(ex.get("instruction") or "Fill in the blanks with the correct words.")
    items = ex.get("items", [])

    is_pure_listening = any(term in instruction.upper() for term in ["LISTEN TO THE AUDIO AND SPELL", "SPELL OUT THE NAMES YOU HEAR", "LISTEN AND WRITE"])
    is_flags_exercise = ex_id in ["2.1", "A"] or "WRITE THE COUNTRY NAME" in instruction.upper() or "LOOK AT THE FLAGS" in instruction.upper() or "IDENTIFY THE COUNTRY FROM THE FLAG" in instruction.upper() or page_num in [14, 15]

    word_panel_html = ""
    if is_flags_exercise:
        if page_num == 14:
            country_list_str = "Turkey &bull; South Korea &bull; Thailand &bull; Greece &bull; Poland &bull; Pakistan &bull; Slovakia &bull; Ireland &bull; China &bull; Portugal &bull; Singapore &bull; Egypt &bull; Mongolia &bull; United Kingdom &bull; France &bull; United Arab Emirates &bull; New Zealand &bull; Germany &bull; Austria &bull; Switzerland"
        else:
            country_list_str = "Argentina &bull; Russia &bull; Australia &bull; Canada &bull; Philippines &bull; South Africa &bull; Brazil &bull; Netherlands &bull; Spain &bull; Czech Republic &bull; Mexico &bull; India &bull; United States of America &bull; Japan &bull; Indonesia"

        word_panel_html = f'''
        <div class="ghibli-word-panel" style="background: rgba(255, 255, 255, 0.9); border: 1.5px dashed #2d5a27; border-radius: 16px; padding: 14px 20px; margin-bottom: 20px; text-align: center;">
          <div style="font-family: var(--font-heading, 'Outfit', sans-serif); font-weight: 600; color: #2b261f; font-size: 0.95rem; line-height: 1.6;">
            {country_list_str}
          </div>
        </div>
        '''

    items_html = []
    for idx, item in enumerate(items):
        item_id = f"p{page_num}_ex{ex_idx+1}_i{idx+1}"
        correct_ans = format_correct_answer(item.get("correct_answer"))
        question = item.get("question") or item.get("prompt_text") or ""
        audio_btn = render_audio_btn(item)
        rec_btn = render_rec_btn(item_id)
        flag_badge = render_flag_badge(correct_ans)
        
        if page_num == 17 and ex_id == "3.4":
            avatar_img = EX34_AVATARS[idx % len(EX34_AVATARS)]
        else:
            avatar_img = GHIBLI_AVATARS[(idx + page_num) % len(GHIBLI_AVATARS)]

        if is_flags_exercise:
            item_num_label = item.get("item_number") if (item.get("item_number") and page_num == 15) else (idx + 1)
            if idx == 0 and page_num == 14:
                # Example item: NO avatar picture of people!
                items_html.append(f'''
                  <div class="ghibli-char-card example-card" style="border: 2px solid #2d5a27; background: rgba(45,90,39,0.06); padding: 16px;">
                    <div class="ghibli-card-body" style="width: 100%;">
                      <div class="ghibli-prompt-text" style="align-items: center; gap: 12px; margin-bottom: 12px;">
                        <span class="item-index" style="font-weight: 800; color: #2d5a27; font-size: 1.1rem;">1.</span>
                        <span class="ghibli-example-badge" style="background:#2d5a27; color:#fff; padding:3px 8px; border-radius:12px; font-weight:700; font-size:0.75rem; text-transform:uppercase;">Example</span>
                        {flag_badge}
                        {audio_btn}
                      </div>
                      <div class="ghibli-input-wrap">
                        <input type="text" class="ghibli-input example-input" data-correct="{escape(correct_ans)}" value="Turkey" readonly style="border-color:#2d5a27; background:rgba(45,90,39,0.12); font-weight:700; color:#2d5a27;" placeholder="Turkey">
                      </div>
                      {rec_btn}
                    </div>
                  </div>
                ''')
            else:
                # Standard item: NO avatar picture of people! Just item number, flag image, audio play button, input field!
                items_html.append(f'''
                  <div class="ghibli-char-card" style="padding: 16px;">
                    <div class="ghibli-card-body" style="width: 100%;">
                      <div class="ghibli-prompt-text" style="align-items: center; gap: 12px; margin-bottom: 12px;">
                        <span class="item-index" style="font-weight: 800; color: #2d5a27; font-size: 1.1rem; min-width: 24px;">{item_num_label}.</span>
                        {flag_badge}
                        {audio_btn}
                      </div>
                      <div class="ghibli-input-wrap">
                        <input type="text" class="ghibli-input" data-correct="{escape(correct_ans)}" placeholder="Type country name...">
                      </div>
                      {rec_btn}
                    </div>
                  </div>
                ''')
            continue

        if is_pure_listening:
            if not correct_ans and ex_id == "1.4":
                correct_ans = EX1_4_DEFAULT_NAMES.get(idx, "")
            clean_display_prompt = escape(clean_spelled_text(question)) if question and not re.search(r'^[0-9]+$', question.strip()) else ""
            is_example = (idx == 0) and (
                item.get("item_number") == 0 or
                ex_id in ["1.4", "3.1", "2.1", "3.4"] or
                (item.get("audio_file_path") and "_eg" in item.get("audio_file_path"))
            )
            if is_example:
                example_val = clean_display_prompt or (EX1_4_DEFAULT_NAMES.get(0, "Rachel Harper") if ex_id == "1.4" else "")
                items_html.append(f'''
              <div class="ghibli-char-card pure-listen-card example-card" style="display:flex; align-items:center; gap:16px; padding:16px 20px; background:rgba(45,90,39,0.06); border-radius:18px; border:2px solid #2d5a27; margin-bottom:12px;">
                <span class="item-index" style="font-weight:800; color:#2d5a27; font-size:1.1rem;">{idx+1}.</span>
                {audio_btn}
                <div style="flex:1;">
                  <input type="text" class="ghibli-input example-input" value="{example_val}" data-correct="{escape(correct_ans)}" readonly placeholder="Listen & type name..." style="max-width:280px;" />
                </div>
              </div>
            ''')
            else:
                items_html.append(f'''
              <div class="ghibli-char-card pure-listen-card" style="display:flex; align-items:center; gap:16px; padding:16px 20px; background:var(--ghibli-card-bg); border-radius:18px; border:2px solid var(--ghibli-border); margin-bottom:12px;">
                <span class="item-index" style="font-weight:800; color:#2d5a27; font-size:1.1rem;">{idx+1}.</span>
                {audio_btn}
                <div style="flex:1;">
                  {f'<div style="font-size:0.9rem; font-weight:600; color:var(--ghibli-text-muted); margin-bottom:4px;">{clean_display_prompt}</div>' if clean_display_prompt else ''}
                  <input type="text" class="ghibli-input" data-correct="{escape(correct_ans)}" placeholder="Listen & type name..." style="max-width:280px;" />
                </div>
              </div>
            ''')
            continue

        is_example = (idx == 0) and (
            item.get("item_number") == 0 or
            ex_id in ["3.1", "2.1", "3.4"] or
            (item.get("audio_file_path") and "_eg" in item.get("audio_file_path"))
        )

        example_badge_html = '<span class="ghibli-example-badge" style="background:#2d5a27; color:#fff; padding:3px 8px; border-radius:12px; font-weight:700; font-size:0.75rem; text-transform:uppercase; margin-right:6px;">Example</span>' if is_example else ''
        card_style = 'border: 2px solid #2d5a27; background: rgba(45,90,39,0.06);' if is_example else ''
        card_class = 'ghibli-char-card example-card' if is_example else 'ghibli-char-card'
        question_text = escape(clean_spelled_text(question))

        prompt_text_val = item.get("prompt_text")
        if prompt_text_val and str(prompt_text_val).strip() and not str(prompt_text_val).endswith(('.jpg', '.png')):
            pt_clean = str(prompt_text_val).strip()
            if page_num == 20 or (ex_id == "5.1") or (len(pt_clean) <= 10 and pt_clean.lower() not in question_text.lower()):
                clue = "I" if pt_clean == "I" else pt_clean.lower()
                if f"({clue})" not in question_text and f"({pt_clean})" not in question_text:
                    question_text = f"{question_text} ({clue})"

        if not flag_badge:
            q_lower = question_text.lower()
            for nat_key, iso_code in NATIONALITY_ISO_MAP.items():
                if nat_key in q_lower:
                    flag_badge = f'<img src="images/flags/{iso_code}.svg" alt="{nat_key} flag" class="ghibli-flag-img" style="width: 52px; height: 35px; object-fit: cover; border-radius: 6px; border: 1px solid rgba(0,0,0,0.15); box-shadow: 0 2px 6px rgba(0,0,0,0.12); vertical-align: middle; margin-right: 8px;">'
                    break

        has_person = is_person_context(question_text, instruction) or page_num in [12, 13, 16, 17, 18, 30, 31, 32, 33, 46, 47, 50, 51, 54, 55]

        if "______" in question_text or "___" in question_text:
            ans_list = item.get("correct_answer")
            if isinstance(ans_list, list):
                blank_parts = re.split(r'_{3,}', question_text)
                reconstructed_parts = [blank_parts[0]]
                for i_part, ans_val in enumerate(ans_list):
                    ans_str = str(ans_val).strip()
                    if is_example:
                        inp_code = f'<input type="text" class="ghibli-input ghibli-inline-input example-input" data-correct="{escape(ans_str)}" value="{escape(ans_str)}" readonly style="max-width:110px; width:85px; display:inline-block; margin:0 4px; text-align:center; border-color:#2d5a27; background:rgba(45,90,39,0.12); font-weight:700; color:#2d5a27;" placeholder="{escape(ans_str)}" />'
                    else:
                        inp_code = f'<input type="text" class="ghibli-input ghibli-inline-input" data-correct="{escape(ans_str)}" placeholder="Type..." style="max-width:110px; width:85px; display:inline-block; margin:0 4px; text-align:center;" />'
                    reconstructed_parts.append(inp_code)
                    if i_part + 1 < len(blank_parts):
                        reconstructed_parts.append(blank_parts[i_part + 1])
                blank_question = "".join(reconstructed_parts)
            else:
                if is_example:
                    input_html = f'<input type="text" class="ghibli-input example-input" data-correct="{escape(correct_ans)}" value="{escape(correct_ans)}" readonly style="border-color:#2d5a27; background:rgba(45,90,39,0.12); font-weight:700; color:#2d5a27;" placeholder="{escape(correct_ans)}" />'
                else:
                    input_html = f'<input type="text" class="ghibli-input" data-correct="{escape(correct_ans)}" placeholder="Type answer..." />'
                blank_question = re.sub(r'_{3,}', input_html, question_text)

            if has_person:
                items_html.append(f'''
                  <div class="{card_class}" style="{card_style}">
                    <div class="ghibli-avatar-wrap">
                      <img src="{avatar_img}" alt="Avatar" class="ghibli-avatar-img">
                      {audio_btn}
                    </div>
                    <div class="ghibli-card-body">
                      <div class="ghibli-prompt-text">
                        {example_badge_html}
                        {flag_badge}
                        <span>{blank_question}</span>
                      </div>
                      {rec_btn}
                    </div>
                  </div>
                ''')
            else:
                items_html.append(f'''
                  <div class="{card_class}" style="{card_style}">
                    <div class="ghibli-card-body" style="width: 100%;">
                      <div class="ghibli-prompt-text" style="align-items: center; gap: 10px; margin-bottom: 10px;">
                        <span class="item-index" style="font-weight: 800; color: #2d5a27; font-size: 1.1rem; min-width: 24px;">{idx+1}.</span>
                        {example_badge_html}
                        {flag_badge}
                        {audio_btn}
                        <span>{blank_question}</span>
                      </div>
                      {rec_btn}
                    </div>
                  </div>
                ''')

        else:
            is_spelling_ex = ex_id == "1.5" or "SPELL OUT" in instruction.upper()
            if is_example:
                display_ex_val = correct_ans.split('|')[-1].strip() if '|' in correct_ans else correct_ans
                input_field_html = f'<input type="text" class="ghibli-input example-input" data-correct="{escape(correct_ans)}" value="{escape(display_ex_val)}" readonly style="border-color:#2d5a27; background:rgba(45,90,39,0.12); font-weight:700; color:#2d5a27;" placeholder="{escape(display_ex_val)}">'
                prompt_header_html = f'''
                  <div class="ghibli-prompt-text">
                    {example_badge_html}
                    {flag_badge}
                    <span>{question_text}</span>
                  </div>
                '''
            else:
                placeholder_str = "Listen & spell name..." if is_spelling_ex else "Type answer..."
                input_field_html = f'<input type="text" class="ghibli-input" data-correct="{escape(correct_ans)}" placeholder="{placeholder_str}">'
                if is_spelling_ex:
                    prompt_header_html = ""
                else:
                    prompt_header_html = f'''
                      <div class="ghibli-prompt-text">
                        {flag_badge}
                        <span>{question_text}</span>
                      </div>
                    '''

            if has_person:
                items_html.append(f'''
                  <div class="{card_class}" style="{card_style}">
                    <div class="ghibli-avatar-wrap">
                      <img src="{avatar_img}" alt="Avatar" class="ghibli-avatar-img">
                      {audio_btn}
                    </div>
                    <div class="ghibli-card-body">
                      {prompt_header_html}
                      <div class="ghibli-input-wrap">
                        {input_field_html}
                      </div>
                      {rec_btn}
                    </div>
                  </div>
                ''')
            else:
                items_html.append(f'''
                  <div class="{card_class}" style="{card_style}">
                    <div class="ghibli-card-body" style="width: 100%;">
                      <div class="ghibli-prompt-text" style="align-items: center; gap: 10px; margin-bottom: 10px;">
                        <span class="item-index" style="font-weight: 800; color: #2d5a27; font-size: 1.1rem; min-width: 24px;">{idx+1}.</span>
                        {example_badge_html}
                        {flag_badge}
                        {audio_btn}
                        <span>{question_text}</span>
                      </div>
                      <div class="ghibli-input-wrap">
                        {input_field_html}
                      </div>
                      {rec_btn}
                    </div>
                  </div>
                ''')


    return f'''
    <section class="ghibli-section">
      <div class="ghibli-section-header">
        <div class="ghibli-ex-num">{ex_id}</div>
        <div>
          <h3 class="ghibli-ex-instruction">{instruction}</h3>
          <p class="ghibli-ex-subtext">Click play to listen or use Rec to practice speaking out loud!</p>
        </div>
      </div>
      {word_panel_html}
      <div class="ghibli-char-grid">
        {"".join(items_html)}
      </div>
    </section>
    '''

def render_sentence_ordering(ex, ex_idx, page_num):
    ex_id = escape(ex.get("exercise_id") or f"{page_num}.{ex_idx+1}")
    instruction = escape(ex.get("instruction") or "REWRITE THE SENTENCES, PUTTING THE WORDS IN THE CORRECT ORDER")
    items = ex.get("items", [])

    chart_html = ""
    if ex_id == "3.3" or "USE THE CHART" in instruction.upper():
        chart_html = '''
      <div class="ghibli-chart-container" style="background: rgba(255, 255, 255, 0.95); border: 2px solid var(--border-color, #e2d7c3); border-radius: 20px; padding: 24px; margin-bottom: 24px; box-shadow: 0 8px 24px rgba(0,0,0,0.06);">
        <div style="font-weight: 700; color: #2d5a27; font-size: 0.9rem; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 16px; text-align: center;">
          <i class="fa-solid fa-diagram-project"></i> Exercise 3.3 Sentence Construction Chart
        </div>
        <div class="ghibli-chart-columns" style="display: flex; flex-wrap: wrap; gap: 16px; justify-content: center; margin-bottom: 20px;">
          
          <div class="ghibli-chart-col" style="flex: 1; min-width: 140px; background: rgba(45,90,39,0.04); padding: 14px; border-radius: 16px; border: 1.5px solid rgba(45,90,39,0.15);">
            <span class="ghibli-col-header" style="display: block; font-weight: 800; color: #2d5a27; font-size: 0.9rem; margin-bottom: 10px; text-align: center;">1. Subject</span>
            <button class="ghibli-block-btn selected" data-col="subject" data-value="I" style="width: 100%; padding: 10px; margin-bottom: 6px; border-radius: 12px; border: 2px solid #2d5a27; background: #2d5a27; color: #fff; font-weight: 700; cursor: pointer;">I</button>
            <button class="ghibli-block-btn" data-col="subject" data-value="Dan" style="width: 100%; padding: 10px; margin-bottom: 6px; border-radius: 12px; border: 2px solid #cbd5e1; background: #fff; font-weight: 600; cursor: pointer;">Dan</button>
            <button class="ghibli-block-btn" data-col="subject" data-value="You" style="width: 100%; padding: 10px; border-radius: 12px; border: 2px solid #cbd5e1; background: #fff; font-weight: 600; cursor: pointer;">You</button>
          </div>

          <div class="ghibli-chart-col" style="flex: 1; min-width: 140px; background: rgba(45,90,39,0.04); padding: 14px; border-radius: 16px; border: 1.5px solid rgba(45,90,39,0.15);">
            <span class="ghibli-col-header" style="display: block; font-weight: 800; color: #2d5a27; font-size: 0.9rem; margin-bottom: 10px; text-align: center;">2. Verb</span>
            <button class="ghibli-block-btn selected" data-col="verb" data-value="am" style="width: 100%; padding: 10px; margin-bottom: 6px; border-radius: 12px; border: 2px solid #2d5a27; background: #2d5a27; color: #fff; font-weight: 700; cursor: pointer;">am</button>
            <button class="ghibli-block-btn" data-col="verb" data-value="is" style="width: 100%; padding: 10px; margin-bottom: 6px; border-radius: 12px; border: 2px solid #cbd5e1; background: #fff; font-weight: 600; cursor: pointer;">is</button>
            <button class="ghibli-block-btn" data-col="verb" data-value="are" style="width: 100%; padding: 10px; border-radius: 12px; border: 2px solid #cbd5e1; background: #fff; font-weight: 600; cursor: pointer;">are</button>
          </div>

          <div class="ghibli-chart-col" style="flex: 1; min-width: 140px; background: rgba(45,90,39,0.04); padding: 14px; border-radius: 16px; border: 1.5px solid rgba(45,90,39,0.15);">
            <span class="ghibli-col-header" style="display: block; font-weight: 800; color: #2d5a27; font-size: 0.9rem; margin-bottom: 10px; text-align: center;">3. Age</span>
            <button class="ghibli-block-btn selected" data-col="age" data-value="twenty-three" style="width: 100%; padding: 10px; margin-bottom: 6px; border-radius: 12px; border: 2px solid #2d5a27; background: #2d5a27; color: #fff; font-weight: 700; cursor: pointer;">twenty-three</button>
            <button class="ghibli-block-btn" data-col="age" data-value="thirty-two" style="width: 100%; padding: 10px; margin-bottom: 6px; border-radius: 12px; border: 2px solid #cbd5e1; background: #fff; font-weight: 600; cursor: pointer;">thirty-two</button>
            <button class="ghibli-block-btn" data-col="age" data-value="sixty-eight" style="width: 100%; padding: 10px; border-radius: 12px; border: 2px solid #cbd5e1; background: #fff; font-weight: 600; cursor: pointer;">sixty-eight</button>
          </div>

          <div class="ghibli-chart-col" style="flex: 1; min-width: 140px; background: rgba(45,90,39,0.04); padding: 14px; border-radius: 16px; border: 1.5px solid rgba(45,90,39,0.15);">
            <span class="ghibli-col-header" style="display: block; font-weight: 800; color: #2d5a27; font-size: 0.9rem; margin-bottom: 10px; text-align: center;">4. Phrase</span>
            <button class="ghibli-block-btn selected" data-col="phrase" data-value="years old." style="width: 100%; padding: 10px; border-radius: 12px; border: 2px solid #2d5a27; background: #2d5a27; color: #fff; font-weight: 700; cursor: pointer;">years old.</button>
          </div>

        </div>

        <div class="ghibli-assembled-box" style="display: flex; flex-direction: column; align-items: center; gap: 12px; padding: 16px; background: rgba(45,90,39,0.08); border-radius: 16px; border: 1.5px solid #2d5a27;">
          <div class="ghibli-assembled-text" id="assembledGreetingText_ex3_3" style="font-family: var(--font-heading); font-size: 1.25rem; font-weight: 700; color: #2d5a27; text-align: center;">
            "I am twenty-three years old."
          </div>
          <div style="display: flex; gap: 10px; flex-wrap: wrap; justify-content: center;">
            <button class="ghibli-btn ghibli-btn-primary" id="playChartSentenceBtn_ex3_3" style="cursor: pointer;">
              <i class="fa-solid fa-volume-high"></i> Listen & Speak
            </button>
            <button class="voice-btn rec-btn" data-id="ex3_3_chart" style="padding: 8px 16px; border-radius: 12px; border: 1.5px solid #2d5a27; background: #fff; color: #2d5a27; font-weight: 700; cursor: pointer;">
              <i class="fa-solid fa-microphone"></i> Rec My Voice
            </button>
          </div>
        </div>

      </div>
        '''

    items_html = []
    if not chart_html:
        for idx, item in enumerate(items):
            item_id = f"p{page_num}_ex{ex_idx+1}_i{idx+1}"
            correct_ans = format_correct_answer(item.get("correct_answer")) or str(item.get("question") or "")
            prompt_text = str(item.get("prompt_text") or item.get("question") or "")
            audio_btn = render_audio_btn(item)
            rec_btn = render_rec_btn(item_id)
            avatar_img = GHIBLI_AVATARS[(idx + page_num) % len(GHIBLI_AVATARS)]

            has_person = is_person_context(prompt_text, instruction) or is_person_context(correct_ans)
            avatar_html = f'<img src="{avatar_img}" alt="Avatar" class="ghibli-avatar-img" style="width:44px; height:44px; border-radius:50%; object-fit:cover; border:2px solid #e5a93c;">' if has_person else ''

            if prompt_text and len(prompt_text.split()) > 1:
                raw_words = prompt_text.split()
            else:
                raw_words = correct_ans.split()
                random.seed(idx + page_num)
                random.shuffle(raw_words)

            chips_html = "".join([f'<span class="word-chip" draggable="true" style="background:#eef2ff; color:#3730a3; padding:8px 14px; border-radius:14px; font-weight:700; font-size:0.95rem; border:1.5px solid #c7d2fe; cursor:pointer; user-select:none; transition:all 0.2s;">{escape(w)}</span>' for w in raw_words])

            items_html.append(f'''
              <div class="ghibli-ordering-container ghibli-char-card" data-correct="{escape(correct_ans)}" style="padding:20px; margin-bottom:16px; background:var(--ghibli-card-bg); border-radius:18px; border:2px solid var(--ghibli-border);">
                <div style="display:flex; align-items:center; gap:12px; margin-bottom:12px;">
                  {avatar_html}
                  <span class="item-index" style="font-weight:800; color:#2d5a27; font-size:1.1rem; min-width:24px;">{idx+1}.</span>
                  {audio_btn}
                  <span style="font-weight:600; color:var(--ghibli-text-muted);">Click/drag words to build sentence:</span>
                  {rec_btn}
                </div>
                <div class="word-pool" style="display:flex; flex-wrap:wrap; gap:8px; padding:12px; background:rgba(0,0,0,0.03); border-radius:14px; min-height:50px; align-items:center; margin-bottom:12px;">
                  {chips_html}
                </div>
                <div class="ghibli-drop-slot" style="display:flex; flex-wrap:wrap; gap:8px; padding:14px; background:rgba(255,255,255,0.9); border:2px dashed #cbd5e1; border-radius:14px; min-height:56px; align-items:center;">
                </div>
                <input type="hidden" class="order-input" data-correct="{escape(correct_ans)}" />
              </div>
            ''')

    subtext = "Select words from each column to form sentences, then listen or record your voice!" if chart_html else "Click or drag the word chips into the box to form the correct sentence!"

    items_block = f'<div class="exercise-items-list">{"".join(items_html)}</div>' if items_html else ''

    return f'''
    <section class="ghibli-section">
      <div class="ghibli-section-header">
        <div class="ghibli-ex-num">{ex_id}</div>
        <div>
          <h3 class="ghibli-ex-instruction">{instruction}</h3>
          <p class="ghibli-ex-subtext">{subtext}</p>
        </div>
      </div>
      {chart_html}
      {items_block}
    </section>
    '''

def render_multiple_choice(ex, ex_idx, page_num):
    ex_id = escape(ex.get("exercise_id") or f"{page_num}.{ex_idx+1}")
    instruction = escape(ex.get("instruction") or "LOOK AT THE PICTURES AND CHOOSE THE CORRECT WORD")
    items = ex.get("items", [])

    items_html = []
    for idx, item in enumerate(items):
        item_id = f"p{page_num}_ex{ex_idx+1}_i{idx+1}"
        correct_ans = format_correct_answer(item.get("correct_answer"))
        question = item.get("question") or item.get("prompt_text") or f"Item {idx+1}"
        options = item.get("options") or []
        audio_btn = render_audio_btn(item)
        rec_btn = render_rec_btn(item_id)
        avatar_img = GHIBLI_AVATARS[(idx + page_num) % len(GHIBLI_AVATARS)]
        has_person = is_person_context(question, instruction)

        correct_answers_list = [c.lower() for c in correct_ans.split("|")]
        opts_html = []
        for opt in options:
            opt_str = str(opt).strip()
            is_correct = (opt_str.lower() in correct_answers_list)
            opts_html.append(f'<button class="ghibli-option" data-correct="{"true" if is_correct else "false"}" style="padding:10px 18px; border-radius:14px; border:2px solid #cbd5e1; background:#fff; font-weight:600; cursor:pointer; transition:all 0.2s;">{escape(opt_str)}</button>')

        if has_person:
            items_html.append(f'''
              <div class="ghibli-char-card" style="margin-bottom:16px;">
                <div class="ghibli-avatar-wrap">
                  <img src="{avatar_img}" alt="Avatar" class="ghibli-avatar-img">
                  {audio_btn}
                </div>
                <div class="ghibli-card-body">
                  <div class="ghibli-prompt-text">
                    <span>{escape(question)}</span>
                  </div>
                  <div class="mc-options-grid" style="display:flex; flex-wrap:wrap; gap:10px; margin-top:12px;">
                    {"".join(opts_html)}
                  </div>
                  {rec_btn}
                </div>
              </div>
            ''')
        else:
            items_html.append(f'''
              <div class="ghibli-char-card" style="margin-bottom:16px;">
                <div class="ghibli-card-body" style="width:100%;">
                  <div class="ghibli-prompt-text" style="align-items:center; gap:10px;">
                    <span class="item-index" style="font-weight:800; color:#2d5a27; font-size:1.1rem; min-width:24px;">{idx+1}.</span>
                    {audio_btn}
                    <span>{escape(question)}</span>
                  </div>
                  <div class="mc-options-grid" style="display:flex; flex-wrap:wrap; gap:10px; margin-top:12px;">
                    {"".join(opts_html)}
                  </div>
                  {rec_btn}
                </div>
              </div>
            ''')

    return f'''
    <section class="ghibli-section">
      <div class="ghibli-section-header">
        <div class="ghibli-ex-num">{ex_id}</div>
        <div>
          <h3 class="ghibli-ex-instruction">{instruction}</h3>
        </div>
      </div>
      <div class="ghibli-char-grid">
        {"".join(items_html)}
      </div>
    </section>
    '''

def render_matching(ex, ex_idx, page_num):
    ex_id = escape(ex.get("exercise_id") or f"{page_num}.{ex_idx+1}")
    instruction = escape(ex.get("instruction") or "LISTEN TO THE AUDIO AND MATCH THE PAIRS")
    items = ex.get("items", [])
    ex_audio = ex.get("audio_file_path") or (items[0].get("audio_file_path") if items else None)

    ex_audio_btn = ""
    if ex_audio:
        ex_audio_btn = f'''
        <div style="margin-top:12px; margin-bottom:16px;">
          <button class="ghibli-audio-btn ghibli-btn ghibli-btn-primary" data-audio="{escape(ex_audio)}" style="padding:10px 20px; font-weight:700;">
            <i class="fa-solid fa-volume-high"></i> Play Exercise Audio (Track {ex_id})
          </button>
        </div>
        '''

    items_html = []
    for idx, item in enumerate(items):
        question = item.get("question") or ""
        correct_ans = item.get("correct_answer") or ""
        options = item.get("options") or []

        options_html_list = ['<option value="">-- Choose matching relationship --</option>']
        for opt in options:
            selected_str = ' selected' if opt == correct_ans and item.get("is_example") else ''
            options_html_list.append(f'<option value="{escape(opt)}"{selected_str}>{escape(opt)}</option>')

        avatar_img = GHIBLI_AVATARS[idx % len(GHIBLI_AVATARS)]
        
        rec_id = f"p{page_num}_ex{ex_idx+1}_i{idx+1}"
        rec_btn = f'''
        <div class="voice-recorder-controls" style="margin-left:auto;">
          <button class="voice-btn rec-btn" data-id="{rec_id}"><i class="fa-solid fa-microphone"></i> Rec</button>
          <button class="voice-btn play-rec-btn hidden" data-id="{rec_id}"><i class="fa-solid fa-play"></i> My Voice</button>
        </div>
        '''

        select_html = f'''
        <select class="ghibli-input ghibli-select-matching" data-correct="{escape(correct_ans)}" style="width:100%; max-width:280px; padding:10px 14px; border-radius:12px; border:2px solid #2d5a27; background:#ffffff; font-size:1rem; font-weight:600; color:#2d5a27; cursor:pointer;">
          {"".join(options_html_list)}
        </select>
        '''

        items_html.append(f'''
          <div class="ghibli-char-card" style="display:flex; align-items:center; gap:16px; padding:16px; margin-bottom:14px; background:rgba(255,255,255,0.95); border-radius:16px; border:1px solid #e2d7c3; flex-wrap:wrap;">
            <div class="ghibli-avatar-wrap" style="flex-shrink:0;">
              <img src="{avatar_img}" alt="Avatar" class="ghibli-avatar-img" style="width:48px; height:48px; border-radius:50%; object-fit:cover; border:2px solid #e5a93c;">
            </div>
            <span class="item-index" style="font-weight:800; color:#2d5a27; font-size:1.1rem; min-width:24px;">{idx+1}.</span>
            <div class="ghibli-prompt-text" style="font-weight:700; color:#2b261f; font-size:1.05rem; min-width:120px;">
              <span>{escape(question)}</span>
            </div>
            <div class="ghibli-input-wrap" style="flex:1; min-width:200px;">
              {select_html}
            </div>
            {rec_btn}
          </div>
        ''')

    return f'''
    <section class="ghibli-section">
      <div class="ghibli-section-header">
        <div class="ghibli-ex-num">{ex_id}</div>
        <div>
          <h3 class="ghibli-ex-instruction">{instruction}</h3>
          <p class="ghibli-ex-subtext">Listen to the audio, then select the matching relationship for each person!</p>
          {ex_audio_btn}
        </div>
      </div>
      <div class="ghibli-matching-grid" style="display:flex; flex-direction:column; gap:10px;">
        {"".join(items_html)}
      </div>
    </section>
    '''

def render_exercise(ex, ex_idx, page_num):
    ex_id = str(ex.get("exercise_id") or "")
    if page_num == 18 or ex_id == "4.1":
        return render_ghibli_family_tree(ex, ex_idx, page_num)
    elif page_num == 19 or ex_id == "4.2":
        return render_ghibli_animals_exercise(ex, ex_idx, page_num)
    ex_type = ex.get("exercise_type")
    if ex_type == "sentence_ordering":
        return render_sentence_ordering(ex, ex_idx, page_num)
    elif ex_type == "multiple_choice":
        return render_multiple_choice(ex, ex_idx, page_num)
    elif ex_type == "matching":
        return render_matching(ex, ex_idx, page_num)
    else:
        return render_fill_in_blank(ex, ex_idx, page_num)

def count_total_items(exercises):
    total = 0
    for ex in exercises:
        items = ex.get("items", [])
        total += len(items)
    return total

def generate_page_html(page_data, nav_info):
    page_num = page_data["page_number"]
    unit_num, unit_title, unit_desc, new_lang, vocab, new_skill = get_unit_info(page_num)
    exercises = page_data.get("exercises", [])

    total_items = count_total_items(exercises)

    rendered_exercises = []
    for idx, ex in enumerate(exercises):
        rendered_exercises.append(render_exercise(ex, idx, page_num))

    exercises_html = "\n".join(rendered_exercises)

    prev_file = nav_info["prev"]
    next_file = nav_info["next"]
    total_pages = nav_info["total_pages"]

    prev_btn_html = f'<a href="{prev_file}" class="ghibli-btn ghibli-btn-secondary"><i class="fa-solid fa-arrow-left"></i> Previous Page (Page {page_num-1})</a>' if prev_file else '<span class="ghibli-btn ghibli-btn-secondary disabled"><i class="fa-solid fa-arrow-left"></i> Previous Page</span>'
    next_btn_html = f'<a href="{next_file}" class="ghibli-btn ghibli-btn-primary">Next Page (Page {page_num+1}) <i class="fa-solid fa-arrow-right"></i></a>' if next_file else '<span class="ghibli-btn ghibli-btn-primary disabled">Next Page <i class="fa-solid fa-arrow-right"></i></span>'

    unit_tag_str = f'Unit {unit_num}' if unit_num else 'Practice Book'

    bottom_check_bar = ""
    if total_items > 0 or len(exercises) > 0:
        bottom_check_bar = '''
    <!-- Bottom Check Answers Bar -->
    <div class="bottom-action-bar" style="display: flex; align-items: center; justify-content: center; gap: 16px; margin: 32px 0 20px 0; padding: 20px; background: rgba(255, 255, 255, 0.4); backdrop-filter: blur(8px); border-radius: 20px; border: 1.5px solid rgba(255, 255, 255, 0.5);">
      <button class="ghibli-btn ghibli-btn-primary ghibli-check-btn-bottom" style="font-size: 1.05rem; padding: 12px 28px; box-shadow: 0 4px 14px rgba(45,90,39,0.3); cursor: pointer;"><i class="fa-solid fa-circle-check"></i> Check Answers</button>
      <button class="ghibli-btn ghibli-btn-secondary ghibli-reset-btn-bottom" style="font-size: 1rem; padding: 12px 24px; cursor: pointer;"><i class="fa-solid fa-rotate-left"></i> Reset Answers</button>
    </div>
        '''

    html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Teacher Lewis's Practice Book • Unit {unit_num}: {unit_title} • Page {page_num} | Studio Ghibli Edition</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Outfit:wght@500;600;700;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  <link rel="stylesheet" href="ghibli_page12.css">
  <style>
    .page-turn-bar {{ display: flex; align-items: center; justify-content: space-between; gap: 12px; padding: 12px 24px; background: rgba(255,255,255,0.18); backdrop-filter: blur(10px); border-radius: 40px; margin: 0 auto 20px auto; max-width: 800px; border: 1.5px solid rgba(255,255,255,0.3); }}
    .page-turn-badge {{ font-family: var(--font-heading); font-weight: 800; color: #fff; font-size: 1rem; text-shadow: 0 2px 4px rgba(0,0,0,0.3); }}
  </style>
</head>
<body class="theme-day">
  <div class="ghibli-bg-overlay"></div>
  <div class="ghibli-vignette"></div>
  <div id="firefliesContainer"></div>

  <div class="ghibli-container">
    <header class="ghibli-header">
      <a href="index.html" class="ghibli-brand" style="text-decoration:none; color:inherit;">
        <div class="ghibli-logo-badge"><i class="fa-solid fa-seedling"></i></div>
        <div class="ghibli-title-wrap">
          <h1>Teacher Lewis's Practice Book</h1>
          <span class="ghibli-subtitle">🌿 Unit {unit_num}: {unit_title} • Page {page_num}</span>
        </div>
      </a>
      <div class="ghibli-header-actions">
        <a href="index.html" class="ghibli-btn ghibli-btn-secondary"><i class="fa-solid fa-house"></i> Home Hub</a>
        <a href="ghibli_reader.html" class="ghibli-btn ghibli-btn-gold" title="Continuous Music Reader Mode"><i class="fa-solid fa-headphones"></i> Reader Mode</a>
        <button class="ghibli-btn ghibli-btn-secondary" id="toggleAmbientBtn" title="Toggle Background Music"><i class="fa-solid fa-music"></i> <span class="bgm-btn-text">Music: Off</span></button>
        <div class="tod-group">
          <button class="tod-btn active" data-theme="day">☀️ Day</button>
          <button class="tod-btn" data-theme="sunset">🌅 Sunset</button>
          <button class="tod-btn" data-theme="night">🌙 Night</button>
        </div>
        <div class="ghibli-score-badge" id="ghibliScoreBadge"><i class="fa-solid fa-star"></i> <span id="ghibliScoreText">Score: 0 / {total_items}</span></div>
        <button class="ghibli-btn ghibli-btn-primary" id="ghibliCheckAnswersBtn" style="cursor:pointer;"><i class="fa-solid fa-circle-check"></i> Check Answers</button>
        <button class="ghibli-btn ghibli-btn-secondary" id="ghibliResetBtn"><i class="fa-solid fa-rotate-left"></i> Reset</button>
      </div>
    </header>

    <!-- Page Turning Navigation Bar Top -->
    <div class="chapter-nav-bar page-turn-bar">
      {prev_btn_html}
      <span class="page-turn-badge">📖 Page {page_num} of {total_pages}</span>
      {next_btn_html}
    </div>

    <!-- Unit Hero Card -->
    <div class="ghibli-hero-card">
      <div class="ghibli-hero-main">
        <span class="ghibli-unit-tag"><i class="fa-solid fa-feather"></i> {unit_tag_str}</span>
        <h2 class="ghibli-hero-title">{escape(unit_title)}</h2>
        <p class="ghibli-hero-desc">{escape(unit_desc)}</p>
      </div>
      <div class="ghibli-unit-key-box">
        <div class="key-item">
          <span class="key-label"><i class="fa-solid fa-comments"></i> New language</span>
          <span class="key-value">{escape(new_lang)}</span>
        </div>
        <div class="key-item">
          <span class="key-label"><i class="fa-solid fa-book-open"></i> Vocabulary</span>
          <span class="key-value">{escape(vocab)}</span>
        </div>
        <div class="key-item">
          <span class="key-label"><i class="fa-solid fa-bullseye"></i> New skill</span>
          <span class="key-value">{escape(new_skill)}</span>
        </div>
      </div>
    </div>

    <!-- Exercises Container -->
    {exercises_html}

    {bottom_check_bar}

    <!-- Page Turning Navigation Bar Bottom -->
    <div style="display:flex; justify-content:center; align-items:center; gap:16px; margin-top:32px; padding-bottom:40px;">
      {prev_btn_html}
      {next_btn_html}
    </div>
  </div>

  <!-- Floating Check Answers Button (Fixed Bottom-Left) -->
  <button class="ghibli-floating-check-btn" id="ghibliCheckAnswersBtn" title="Check Answers">
    <i class="fa-solid fa-circle-check"></i> Check Answers
  </button>

  <!-- Kodama Mascot Widget -->
  <div class="ghibli-mascot-container" id="ghibliMascotWidget">
    <div class="mascot-bubble-wrap">
      <div class="mascot-min-bar">
        <div class="story-chip"><i class="fa-solid fa-book-bookmark"></i> <span>Page {page_num}</span></div>
        <div class="pomo-min-pill">
          <button class="pomo-toggle-btn" id="pomoToggleBtn"><i class="fa-solid fa-play" id="pomoIcon"></i></button>
          <span class="pomo-min-time" id="pomoMinTime">25:00</span>
          <button class="pomo-opt-btn" id="pomoOptBtn"><i class="fa-solid fa-sliders"></i></button>
        </div>
      </div>
      <div class="mascot-bubble" id="mascotBubble">
        <div class="mascot-action-chip"><i class="fa-solid fa-paw"></i> Kodama on Page {page_num}</div>
        <div class="mascot-text" id="mascotTextContent">"Welcome to Page {page_num}! Complete exercises and turn the page when ready!"</div>
      </div>
    </div>
    <div class="mascot-avatar-wrap" id="mascotAvatarWrap">
      <img src="images/ghibli/mascot.jpg" alt="Kodama Mascot" class="mascot-avatar" id="mascotAvatarImg">
    </div>
  </div>

  <script src="ghibli_audio.js"></script>
  <script src="ghibli_page_engine.js"></script>
</body>
</html>
'''
    return html_content

def main():
    print("Loading pages from consolidated JSON...")
    pages = load_pages()
    print(f"Loaded {len(pages)} exercise pages.")

    nav_map = compute_navigation(pages)

    # Note: ghibli_page12.html is our handwritten prototype page for page 12
    for page in pages:
        p_num = page["page_number"]
        if p_num == 12:
            continue
        nav_info = nav_map[p_num]
        html_code = generate_page_html(page, nav_info)

        out_path1 = os.path.join(OUTPUT_DIR, nav_info["filename"])
        out_path2 = os.path.join(OUTPUT_DIR, f"ghibli_p{p_num:03d}.html")
        with open(out_path1, "w", encoding="utf-8") as f:
            f.write(html_code)
        with open(out_path2, "w", encoding="utf-8") as f:
            f.write(html_code)

    print(f"SUCCESS: Generated all page-by-page HTML files matching ghibli_page12.css styling!")

if __name__ == "__main__":
    main()
