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
import time
try:
    import unit2_builders as u2
except ImportError:
    u2 = None

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
    "images/ghibli/gary.webp",
    "images/ghibli/natalie.webp",
    "images/ghibli/sue.webp",
    "images/ghibli/ryan.webp",
    "images/ghibli/mia.webp",
    "images/ghibli/amelia.webp",
    "images/ghibli/avatar_boy.webp",
    "images/ghibli/avatar_girl.webp",
    "images/ghibli/avatar_man.webp",
    "images/ghibli/avatar_woman.webp"
]

PEOPLE_KEYWORDS = {
    "name", "i", "me", "my", "you", "your", "he", "him", "his", "she", "her", "it", "its", "we", "us", "our", "they", "them", "their",
    "who", "man", "men", "woman", "women", "boy", "girl", "child", "children", "kid", "kids", "person", "people",
    "teacher", "doctor", "student", "actor", "actress", "nurse", "hairdresser", "engineer", "chef", "waiter", "waitress",
    "brother", "sister", "mother", "father", "parent", "parents", "son", "daughter", "grandfather", "grandmother",
    "granddaughter", "granddaughters", "grandson", "grandsons", "husband", "wife", "pet", "pets", "dog", "cat",
    "rabbit", "snake", "horse", "parrot", "cow", "monkey", "fish", "sheep", "bird", "animal", "animals", "ball",
    "uncle", "aunt", "cousin", "friend", "friends", "rachel", "noah", "marina", "james", "sophia", "alexander", "emily",
    "daniel", "olivia", "matthew", "kirsty", "kim", "dan", "lewis", "john", "sarah", "tom", "ben", "lisa",
    "christopher", "joe", "greg", "dolly", "sam", "this", "that", "these", "those"
}

def is_person_context(text, instruction=""):
    combined = f"{text or ''} {instruction or ''}".lower()
    words = set(re.findall(r'\b[a-zA-Z]+\b', combined))
    if words.intersection(PEOPLE_KEYWORDS):
        return True
    if any(k in combined for k in ["apostrophe", "belong", "family", "relative", "people", "possessive", "this", "that"]):
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
    
    (22, 23, 6, "Using apostrophes ('s)", 
     "Use the possessive apostrophe to show that something belongs to a person or animal.", 
     "Possessive apostrophe", "Family and pets", "Talking about belonging"),
    
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

def get_parent_unit(page_num):
    if 12 <= page_num <= 29:
        return 1, "Introducing Yourself & Belongings", "1.1 – 8.10"
    elif 30 <= page_num <= 45:
        return 2, "Jobs, Time & Daily Life", "9.1 – 14.8"
    elif 46 <= page_num <= 63:
        return 3, "Negatives & Questions", "15.1 – 19.9"
    elif 64 <= page_num <= 85:
        return 4, "Towns, Places & Giving Directions", "20.1 – 26.4"
    elif 86 <= page_num <= 115:
        return 5, "Around the House, Food & Shopping", "27.1 – 35.6"
    elif 116 <= page_num <= 137:
        return 6, "Sports, Free Time & Preferences", "36.1 – 42.6"
    elif 138 <= page_num <= 155:
        return 7, "Abilities, Actions & Studying", "43.1 – 48.8"
    elif page_num >= 156:
        return "Answers", "Answer Keys & Solutions", "1.1 – 48.8"
    else:
        return "Starter", "Reference & Warm-up", "Reference"

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
        filename = f"ghibli_p{p_num:03d}.html"
        
        prev_p = pages[i-1]['page_number'] if i > 0 else None
        next_p = pages[i+1]['page_number'] if i < total - 1 else None
        
        prev_fn = f"ghibli_p{prev_p:03d}.html" if prev_p else None
        next_fn = f"ghibli_p{next_p:03d}.html" if next_p else None

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
                <img src="images/people/womanNoDetail.png" alt="Grandmother" class="tree-avatar" width="100" height="125" loading="eager" decoding="async">
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
                <img src="images/people/manNoDetail.png" alt="Grandfather" class="tree-avatar" width="100" height="125" loading="eager" decoding="async">
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
                  <img src="images/people/womanNoDetail.png" alt="Mother" class="tree-avatar" width="100" height="125" loading="eager" decoding="async">
                </div>
                <span class="given-role-badge">mother</span>
              </div>

              <div class="marriage-mini-link" title="Married"><i class="fa-solid fa-heart"></i></div>

              <!-- Father (Blank 2 - Brother 1 / Blood Son) -->
              <div class="tree-node blood-node">
                <div class="tree-avatar-container">
                  <img src="images/people/manNoDetail.png" alt="Father" class="tree-avatar" width="100" height="125" loading="eager" decoding="async">
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
                <img src="images/people/manNoDetail.png" alt="Uncle" class="tree-avatar" width="100" height="125" loading="eager" decoding="async">
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
                <img src="images/people/womanNoDetail.png" alt="Sister" class="tree-avatar" width="100" height="125" loading="eager" decoding="async">
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
                <img src="images/people/manNoDetail.png" alt="Brother" class="tree-avatar" width="100" height="125" loading="eager" decoding="async">
              </div>
              <span class="given-role-badge">brother</span>
            </div>

            <!-- Pablo & Wife Couple (NO BOX CARD) -->
            <div class="couple-unboxed-wrap" style="display:flex; align-items:center; gap:12px;">
              <!-- Pablo (Given Hero - Blood Son of Parents) -->
              <div class="tree-node hero-node">
                <div class="tree-avatar-container">
                  <img src="images/people/manNoDetail.png" alt="Pablo" class="tree-avatar" width="100" height="125" loading="eager" decoding="async">
                </div>
                <span class="given-role-badge hero-badge">Pablo</span>
              </div>

              <div class="marriage-mini-link" title="Married"><i class="fa-solid fa-heart"></i></div>

              <!-- Wife (Given In-Law) -->
              <div class="tree-node in-law-node">
                <div class="tree-avatar-container">
                  <img src="images/people/womanNoDetail.png" alt="Wife" class="tree-avatar" width="100" height="125" loading="eager" decoding="async">
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
                  <img src="images/people/manNoDetail.png" alt="Son-in-Law" class="tree-avatar" width="100" height="125" loading="eager" decoding="async">
                </div>
                <span class="given-role-badge">son-in-law</span>
              </div>

              <div class="marriage-mini-link" title="Married"><i class="fa-solid fa-heart"></i></div>

              <!-- Daughter (Blank 6 - Adult Silhouette Woman) -->
              <div class="tree-node blood-node daughter-node">
                <div class="tree-avatar-container">
                  <img src="images/people/womanNoDetail.png" alt="Daughter" class="tree-avatar" width="100" height="125" loading="eager" decoding="async">
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
                <img src="images/people/manNoDetail.png" alt="Son" class="tree-avatar" width="100" height="125" loading="eager" decoding="async">
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
                <img src="images/people/boyNoDetail.png" alt="Grandson" class="tree-avatar" width="100" height="125" loading="eager" decoding="async">
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
                <img src="images/people/girlNoDetail.png" alt="Granddaughter" class="tree-avatar" width="100" height="125" loading="eager" decoding="async">
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

        example_badge_html = '<span class="ghibli-example-badge" style="background:#2d5a27; color:#fff; padding:3px 10px; border-radius:12px; font-weight:700; font-size:0.75rem; text-transform:uppercase;">Example</span>' if is_example else ''
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
                    flag_badge = f'<img src="images/flags/{iso_code}.svg" alt="{nat_key} flag" class="ghibli-flag-img" style="width: 42px; height: 28px; object-fit: cover; border-radius: 4px; border: 1px solid rgba(0,0,0,0.15); box-shadow: 0 2px 4px rgba(0,0,0,0.1); vertical-align: middle;">'
                    break

        has_person = is_person_context(question_text, instruction) or page_num in [12, 13, 16, 17, 18, 20, 21, 22, 23, 30, 31, 32, 33, 46, 47, 50, 51, 54, 55]

        if "______" in question_text or "___" in question_text:
            ans_list = item.get("correct_answer")
            if isinstance(ans_list, list):
                blank_parts = re.split(r'_{3,}', question_text)
                reconstructed_parts = [blank_parts[0]]
                for i_part, ans_val in enumerate(ans_list):
                    ans_str = str(ans_val).strip()
                    is_short = len(ans_str) <= 4
                    short_cls = " short-gap" if is_short else ""
                    short_style = "max-width:90px; min-width:60px; width:72px;" if is_short else "max-width:240px; min-width:130px; width:auto;"
                    if is_example:
                        inp_code = f'<input type="text" class="ghibli-input ghibli-inline-input example-input{short_cls}" data-correct="{escape(ans_str)}" value="{escape(ans_str)}" readonly style="{short_style} display:inline-block; margin:0 4px; text-align:center; border-color:#2d5a27; background:rgba(45,90,39,0.12); font-weight:700; color:#2d5a27;" placeholder="{escape(ans_str)}" />'
                    else:
                        placeholder_val = escape(ans_str) if is_example else ("..." if is_short else "Type answer...")
                        inp_code = f'<input type="text" class="ghibli-input ghibli-inline-input{short_cls}" data-correct="{escape(ans_str)}" placeholder="{placeholder_val}" style="{short_style} display:inline-block; margin:0 4px; text-align:center;" />'
                    reconstructed_parts.append(inp_code)
                    if i_part + 1 < len(blank_parts):
                        reconstructed_parts.append(blank_parts[i_part + 1])
                blank_question = "".join(reconstructed_parts)
            else:
                ans_str = str(correct_ans).strip()
                is_short = len(ans_str) <= 4
                short_cls = " short-gap" if is_short else ""
                short_style = "max-width:90px; min-width:60px; width:72px;" if is_short else "max-width:240px; min-width:130px; width:auto;"
                if is_example:
                    input_html = f'<input type="text" class="ghibli-input ghibli-inline-input example-input{short_cls}" data-correct="{escape(correct_ans)}" value="{escape(correct_ans)}" readonly style="{short_style} display:inline-block; margin:0 4px; text-align:center; border-color:#2d5a27; background:rgba(45,90,39,0.12); font-weight:700; color:#2d5a27;" placeholder="{escape(correct_ans)}" />'
                else:
                    placeholder_val = "..." if is_short else "Type answer..."
                    input_html = f'<input type="text" class="ghibli-input ghibli-inline-input{short_cls}" data-correct="{escape(correct_ans)}" placeholder="{placeholder_val}" style="{short_style} display:inline-block; margin:0 4px; text-align:center;" />'
                blank_question = re.sub(r'_{3,}', input_html, question_text)

            item_num_badge = f'<span class="item-index" style="font-weight: 800; color: #2d5a27; font-size: 1.05rem; min-width: 20px;">{idx}.</span>' if (idx > 0 and not is_example) else ''
            meta_header_html = ""
            if example_badge_html or flag_badge or item_num_badge:
                meta_header_html = f'''<div class="ghibli-card-meta-row" style="display:flex; align-items:center; gap:8px; margin-bottom:8px;">
                        {example_badge_html}
                        {item_num_badge}
                        {flag_badge}
                      </div>'''

            if has_person:
                items_html.append(f'''
                  <div class="{card_class}" style="{card_style}">
                    <div class="ghibli-avatar-wrap">
                      <img src="{avatar_img}" alt="Avatar" class="ghibli-avatar-img" width="76" height="76" loading="eager" decoding="async">
                      {audio_btn}
                    </div>
                    <div class="ghibli-card-body" style="flex:1; min-width:0;">
                      {meta_header_html}
                      <div class="ghibli-sentence-text" style="font-size:1.05rem; font-weight:600; color:var(--ghibli-text-main, #2b261f); line-height:2.2; margin-bottom:8px;">
                        {blank_question}
                      </div>
                      {rec_btn}
                    </div>
                  </div>
                ''')
            else:
                items_html.append(f'''
                  <div class="{card_class}" style="{card_style}">
                    <div class="ghibli-card-body" style="width: 100%;">
                      {meta_header_html}
                      <div class="ghibli-sentence-text" style="display:flex; align-items:center; flex-wrap:wrap; gap:8px; font-size:1.05rem; font-weight:600; color:var(--ghibli-text-main, #2b261f); line-height:2.2; margin-bottom:8px;">
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
                      <img src="{avatar_img}" alt="Avatar" class="ghibli-avatar-img" width="76" height="76" loading="eager" decoding="async">
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
            prompt_text = str(item.get("prompt_text") or item.get("question") or "").strip()
            options = item.get("options")
            audio_btn = render_audio_btn(item)
            rec_btn = render_rec_btn(item_id)
            avatar_img = GHIBLI_AVATARS[(idx + page_num) % len(GHIBLI_AVATARS)]

            has_person = is_person_context(prompt_text, instruction) or is_person_context(correct_ans)
            avatar_html = f'<img src="{avatar_img}" alt="Avatar" class="ghibli-avatar-img" width="44" height="44" style="width:44px; height:44px; border-radius:50%; object-fit:cover; border:2px solid #e5a93c;" loading="eager" decoding="async">' if has_person else ''

            if options and isinstance(options, list) and len(options) > 0:
                raw_words = [str(w).strip() for w in options if str(w).strip() and str(w).strip() != '/']
            elif prompt_text:
                clean_p = prompt_text.replace('/', ' ')
                raw_words = [w.strip() for w in clean_p.split() if w.strip() and w.strip() != '/']
                if ' '.join(raw_words).lower() == correct_ans.lower():
                    random.seed(idx + page_num)
                    random.shuffle(raw_words)
            else:
                clean_c = correct_ans.replace('/', ' ')
                raw_words = [w.strip() for w in clean_c.split() if w.strip() and w.strip() != '/']
                random.seed(idx + page_num)
                random.shuffle(raw_words)

            chips_html = "".join([
                f'<span class="word-chip" draggable="true" data-word="{escape(w)}" title="Click to move or drag to place">{escape(w)}</span>'
                for w in raw_words
            ])

            items_html.append(f'''
              <div class="ghibli-ordering-container ghibli-char-card" data-correct="{escape(correct_ans)}">
                <div style="display:flex; align-items:center; justify-content:space-between; gap:12px; margin-bottom:12px; flex-wrap:wrap;">
                  <div style="display:flex; align-items:center; gap:10px;">
                    {avatar_html}
                    <span class="item-index" style="font-weight:800; color:#2d5a27; font-size:1.1rem; min-width:24px;">{idx+1}.</span>
                    {audio_btn}
                    <span style="font-weight:700; color:var(--ghibli-text-main); font-size:0.95rem;">Build the sentence:</span>
                  </div>
                  <div style="display:flex; align-items:center; gap:8px;">
                    {rec_btn}
                    <button class="ghibli-order-reset-btn" title="Reset this sentence"><i class="fa-solid fa-rotate-left"></i> Reset</button>
                  </div>
                </div>

                <div class="ordering-zone-wrap word-pool-wrap">
                  <div class="ordering-zone-label">
                    <i class="fa-solid fa-layer-group"></i> <span>Word Bank</span> <span class="zone-hint">(click or drag words)</span>
                  </div>
                  <div class="word-pool" style="display:flex; flex-direction:row; flex-wrap:wrap; gap:10px; padding:14px 16px; min-height:58px; align-items:center; justify-content:flex-start;">
                    {chips_html}
                  </div>
                </div>

                <div class="ordering-zone-wrap drop-slot-wrap">
                  <div class="ordering-zone-label drop-label">
                    <i class="fa-solid fa-arrow-right-to-bracket"></i> <span>Your Sentence</span> <span class="zone-hint">(drop words here in order)</span>
                  </div>
                  <div class="ghibli-drop-slot sentence-slot" style="display:flex; flex-direction:row; flex-wrap:wrap; gap:10px; padding:14px 16px; min-height:60px; align-items:center; justify-content:flex-start;">
                    <div class="drop-placeholder"><i class="fa-regular fa-hand-pointer"></i> Drag words here or click chips above</div>
                  </div>
                </div>
                <input type="hidden" class="order-input" data-correct="{escape(correct_ans)}" />
              </div>
            ''')

    subtext = "Select words from each column to form sentences, then listen or record your voice!" if chart_html else "Click or drag the word chips into the sentence box to form the correct order!"

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
                  <img src="{avatar_img}" alt="Avatar" class="ghibli-avatar-img" width="76" height="76" loading="eager" decoding="async">
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

def render_cross_out(ex, ex_idx, page_num):
    ex_id = escape(ex.get("exercise_id") or f"{page_num}.{ex_idx+1}")
    instruction = escape(ex.get("instruction") or "CROSS OUT THE INCORRECT WORD IN EACH SENTENCE")
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

        correct_answers_list = [c.lower() for c in correct_ans.split("|")]

        choice_btns = []
        for opt in options:
            opt_str = str(opt).strip()
            # For cross-out exercises, crossing out the INCORRECT word is the correct answer!
            is_target_to_cross = (opt_str.lower() not in correct_answers_list)
            choice_btns.append(f'<button type="button" class="ghibli-crossout-btn" data-word="{escape(opt_str)}" data-correct="{"true" if is_target_to_cross else "false"}">{escape(opt_str)}</button>')

        group_html = f'<span class="ghibli-crossout-group" data-item-id="{item_id}">{"<span class=\"crossout-slash\">/</span>".join(choice_btns)}</span>'

        # Match slash pattern in raw question string
        match = None
        if len(options) >= 2:
            opt1, opt2 = str(options[0]).strip(), str(options[1]).strip()
            pattern = re.compile(re.escape(opt1) + r'\s*/\s*' + re.escape(opt2), re.IGNORECASE)
            match = pattern.search(question)
        if not match:
            match = re.search(r'([A-Za-z0-9\']+)\s*/\s*([A-Za-z0-9\']+)', question)

        if match:
            prefix = escape(question[:match.start()])
            suffix = escape(question[match.end():])
            rendered_sentence = f"{prefix}{group_html}{suffix}"
        else:
            rendered_sentence = f"{group_html} {escape(question)}"

        items_html.append(f'''
          <div class="ghibli-char-card crossout-card" style="margin-bottom:16px;">
            <div class="ghibli-avatar-wrap">
              <img src="{avatar_img}" alt="Avatar" class="ghibli-avatar-img" width="76" height="76" loading="eager" decoding="async">
              {audio_btn}
            </div>
            <div class="ghibli-card-body">
              <div class="ghibli-prompt-text ghibli-crossout-sentence">
                <span class="item-index" style="font-weight:800; color:#2d5a27; font-size:1.1rem; margin-right:4px;">{idx+1}.</span>
                {rendered_sentence}
              </div>
              {rec_btn}
            </div>
          </div>
        ''')

    return f'''
    <section class="ghibli-section crossout-exercise-section">
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
        correct_ans = format_correct_answer(item.get("correct_answer")) or ""
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
        <select class="ghibli-input ghibli-select-matching" data-correct="{escape(correct_ans)}" style="width:100%; max-width:280px; padding:10px 14px; border-radius:12px; font-size:1rem; font-weight:600; cursor:pointer;">
          {"".join(options_html_list)}
        </select>
        '''

        items_html.append(f'''
          <div class="ghibli-char-card" style="display:flex; align-items:center; gap:16px; padding:16px; margin-bottom:14px; background:rgba(255,255,255,0.95); border-radius:16px; border:1px solid #e2d7c3; flex-wrap:wrap;">
            <div class="ghibli-avatar-wrap" style="flex-shrink:0;">
              <img src="{avatar_img}" alt="Avatar" class="ghibli-avatar-img" width="48" height="48" style="width:48px; height:48px; border-radius:50%; object-fit:cover; border:2px solid #e5a93c;" loading="eager" decoding="async">
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

def render_matching_exercise_8_6(ex, ex_idx, page_num):
    ex_id = escape(ex.get("exercise_id") or "8.6")
    instruction = escape(ex.get("instruction") or "MATCH THE DETERMINERS TO THE PRONOUNS")
    
    # Left column: Determiners
    # Example: my -> mine (audio: audio/8/8_6_eg.mp3)
    # 1. his -> his (audio: audio/8/8_6_1.mp3)
    # 2. its -> its (audio/8/8_6_2.mp3)
    # 3. her -> hers (audio/8/8_6_3.mp3)
    # 4. your -> yours (audio/8/8_6_4.mp3)
    # 5. their -> theirs (audio/8/8_6_5.mp3)
    # 6. our -> ours (audio/8/8_6_6.mp3)
    
    left_items = [
        {"num": 1, "determiner": "his", "correct": "his", "audio": "audio/8/8_6_1.mp3", "rec_id": "p28_ex1_i1"},
        {"num": 2, "determiner": "its", "correct": "its", "audio": "audio/8/8_6_2.mp3", "rec_id": "p28_ex1_i2"},
        {"num": 3, "determiner": "her", "correct": "hers", "audio": "audio/8/8_6_3.mp3", "rec_id": "p28_ex1_i3"},
        {"num": 4, "determiner": "your", "correct": "yours", "audio": "audio/8/8_6_4.mp3", "rec_id": "p28_ex1_i4"},
        {"num": 5, "determiner": "their", "correct": "theirs", "audio": "audio/8/8_6_5.mp3", "rec_id": "p28_ex1_i5"},
        {"num": 6, "determiner": "our", "correct": "ours", "audio": "audio/8/8_6_6.mp3", "rec_id": "p28_ex1_i6"},
    ]
    
    # Right column: Pronouns in textbook order: yours, mine, his, ours, theirs, hers, its
    right_items = [
        {"pronoun": "yours", "is_example": False},
        {"pronoun": "mine", "is_example": True},
        {"pronoun": "his", "is_example": False},
        {"pronoun": "ours", "is_example": False},
        {"pronoun": "theirs", "is_example": False},
        {"pronoun": "hers", "is_example": False},
        {"pronoun": "its", "is_example": False},
    ]

    left_html = []
    # Add example item 'my'
    left_html.append('''
        <div class="connecting-card example-card is-connected" data-source-id="my" title="Example: 'my' is matched to 'mine'">
          <button class="ghibli-audio-play-btn" data-audio="audio/8/8_6_eg.mp3" title="Play 'my' audio"><i class="fa-solid fa-play"></i></button>
          <span class="example-badge"><i class="fa-solid fa-star"></i> Example</span>
          <span class="word-text">my</span>
          <div class="anchor-dot right-dot" title="Connected to 'mine'"></div>
        </div>
    ''')

    for item in left_items:
        rec_btn = f'''
        <div class="voice-recorder-controls" style="margin-left:auto; margin-right:8px;">
          <button class="voice-btn rec-btn" data-id="{item['rec_id']}" title="Record your voice"><i class="fa-solid fa-microphone"></i> Rec</button>
          <button class="voice-btn play-rec-btn hidden" data-id="{item['rec_id']}" title="Play your recording"><i class="fa-solid fa-play"></i> My Voice</button>
        </div>
        '''
        left_html.append(f'''
        <div class="connecting-card source-card" data-source-id="item-{item['num']}" data-correct="{item['correct']}" data-item="{item['num']}" title="Click to select '{item['determiner']}' and connect to a pronoun">
          <button class="ghibli-audio-play-btn" data-audio="{item['audio']}" title="Play '{item['determiner']}' audio"><i class="fa-solid fa-play"></i></button>
          <span class="word-text">{item['determiner']}</span>
          {rec_btn}
          <input type="hidden" class="ghibli-input ghibli-connecting-input" data-correct="{item['correct']}" data-item="{item['num']}" value="" />
          <div class="anchor-dot right-dot" title="Click or drag to connect"></div>
        </div>
        ''')

    right_html = []
    for item in right_items:
        p = item["pronoun"]
        if item["is_example"]:
            right_html.append(f'''
        <div class="connecting-card target-card example-card is-connected" data-target-id="{p}" data-value="{p}" title="Example: connected to 'my'">
          <div class="anchor-dot left-dot" title="Connected to 'my'"></div>
          <span class="word-text">{p}</span>
          <span class="example-badge" style="margin-left:auto;"><i class="fa-solid fa-check"></i> Example</span>
        </div>
            ''')
        else:
            right_html.append(f'''
        <div class="connecting-card target-card" data-target-id="{p}" data-value="{p}" title="Click to connect selected determiner to '{p}'">
          <div class="anchor-dot left-dot" title="Connect here"></div>
          <span class="word-text">{p}</span>
        </div>
            ''')

    return f'''
    <section class="ghibli-section ghibli-connecting-section">
      <div class="ghibli-section-header">
        <div class="ghibli-ex-num">{ex_id}</div>
        <div>
          <h3 class="ghibli-ex-instruction">{instruction}</h3>
          <p class="ghibli-ex-subtext">Click or tap a determiner on the left, then click its matching pronoun on the right to connect them! Listen to the audio for each determiner.</p>
        </div>
      </div>

      <div class="ghibli-connecting-container" id="connecting_ex_8_6" data-exercise-id="8.6">
        <svg class="ghibli-connecting-svg" aria-hidden="true">
          <defs>
            <marker id="arrow-example" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
              <path d="M 0 1 L 8 5 L 0 9 z" fill="#3d7ea6" />
            </marker>
            <marker id="arrow-user" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
              <path d="M 0 1 L 8 5 L 0 9 z" fill="#e5a93c" />
            </marker>
            <marker id="arrow-correct" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
              <path d="M 0 1 L 8 5 L 0 9 z" fill="#2e7d32" />
            </marker>
            <marker id="arrow-incorrect" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
              <path d="M 0 1 L 8 5 L 0 9 z" fill="#c62828" />
            </marker>
          </defs>
          <path class="connecting-line example-line" data-source="my" data-target="mine" d="" marker-end="url(#arrow-example)" />
        </svg>

        <div class="connecting-columns-grid">
          <div class="connecting-column left-column">
            <div class="column-header">
              <span class="column-title"><i class="fa-solid fa-list-check"></i> Determiners</span>
            </div>
            {"".join(left_html)}
          </div>

          <div class="connecting-column right-column">
            <div class="column-header">
              <span class="column-title"><i class="fa-solid fa-arrow-right-arrow-left"></i> Pronouns</span>
            </div>
            {"".join(right_html)}
          </div>
        </div>
      </div>
    </section>
    '''

def render_ghibli_substitution_chart_5_5(ex, ex_idx, page_num):
    ex_id = str(ex.get("exercise_id") or "5.5")
    instruction = str(ex.get("instruction") or "USE THE CHART TO CREATE 12 CORRECT SENTENCES AND SAY THEM OUT LOUD")
    audio_ref = "audio/5/5_5_a.mp3"
    
    return f'''
    <!-- EXERCISE 5.5 (INTERACTIVE SUBSTITUTION CHART & SENTENCE BUILDER) -->
    <section class="ghibli-exercise-card ex5-5-card">
      <div class="exercise-header">
        <div class="exercise-badge-wrap" style="display:flex; align-items:center; gap:10px; flex-wrap:wrap;">
          <span class="exercise-num" style="background:var(--ghibli-accent-green, #48825c); color:#fff; padding:4px 12px; border-radius:20px; font-weight:700; font-size:0.85rem;">Exercise {ex_id}</span>
          <button class="ghibli-audio-btn ghibli-audio-play-btn" data-audio="{audio_ref}" title="Play Audio 5.5" style="background:var(--ghibli-accent-gold, #e5a93c); color:#fff; border:none; padding:4px 12px; border-radius:20px; font-weight:700; font-size:0.85rem; cursor:pointer; display:inline-flex; align-items:center; gap:5px;"><i class="fa-solid fa-volume-high"></i> Audio 5.5</button>
          <span class="ex5-5-progress-badge"><i class="fa-solid fa-trophy"></i> Discovered: <strong id="ex5_5_found_count">1</strong> / 12</span>
        </div>
        <h3 class="exercise-instruction" style="font-family:var(--font-heading); margin-top:8px; color:var(--ghibli-text-main); font-size:1.15rem;">{escape(instruction)}</h3>
        <p class="exercise-subtext">Click words in each column to build and experiment with valid English sentences. Speak them out loud or record your voice!</p>
      </div>

      <!-- Assembled Sentence Preview & Validation Bar -->
      <div class="ex5-5-preview-card">
        <div class="ex5-5-chips-wrap">
          <span class="ex5-5-chip chip-pointer" id="chip_pointer">This</span>
          <span class="ex5-5-chip chip-verb" id="chip_verb">is</span>
          <span class="ex5-5-chip chip-possessive" id="chip_possessive">her</span>
          <span class="ex5-5-chip chip-noun" id="chip_noun">cat.</span>
        </div>

        <div class="ex5-5-status-bar">
          <div class="ex5-5-validation-badge valid" id="ex5_5_val_badge">
            <i class="fa-solid fa-circle-check"></i> <span id="ex5_5_val_text">Valid Sentence!</span>
          </div>
          
          <div class="ex5-5-actions">
            <button class="ghibli-btn ghibli-btn-primary" id="playSentenceBtn" data-audio="{audio_ref}" style="padding:10px 18px; font-size:0.9rem;">
              <i class="fa-solid fa-volume-high"></i> Play Audio 5.5
            </button>
            <div class="voice-recorder-controls">
              <button class="voice-btn rec-btn" data-id="p21_ex3_sentence"><i class="fa-solid fa-microphone"></i> Rec</button>
              <button class="voice-btn play-rec-btn hidden" data-id="p21_ex3_sentence"><i class="fa-solid fa-play"></i> Voice</button>
            </div>
          </div>
        </div>
      </div>

      <!-- 4 Column Substitution Chart Grid -->
      <div class="ex5-5-chart-grid">
        <!-- Col 1: Pointer (This / That) -->
        <div class="ex5-5-col col-pointer">
          <div class="ex5-5-col-header"><i class="fa-solid fa-hand-pointer"></i> Pointer</div>
          <button class="ghibli-block-btn selected" data-col="pointer" data-value="This">This</button>
          <button class="ghibli-block-btn" data-col="pointer" data-value="That">That</button>
        </div>

        <!-- Col 2: Verb (is / are) -->
        <div class="ex5-5-col col-verb">
          <div class="ex5-5-col-header"><i class="fa-solid fa-bolt"></i> Verb</div>
          <button class="ghibli-block-btn selected" data-col="verb" data-value="is">is</button>
          <button class="ghibli-block-btn" data-col="verb" data-value="are">are</button>
        </div>

        <!-- Col 3: Possessive (her / their / my) -->
        <div class="ex5-5-col col-possessive">
          <div class="ex5-5-col-header"><i class="fa-solid fa-user-tag"></i> Possessive</div>
          <button class="ghibli-block-btn selected" data-col="possessive" data-value="her">her</button>
          <button class="ghibli-block-btn" data-col="possessive" data-value="their">their</button>
          <button class="ghibli-block-btn" data-col="possessive" data-value="my">my</button>
        </div>

        <!-- Col 4: Pet / Noun (cat. / parrot.) -->
        <div class="ex5-5-col col-noun">
          <div class="ex5-5-col-header"><i class="fa-solid fa-paw"></i> Pet / Noun</div>
          <button class="ghibli-block-btn selected" data-col="noun" data-value="cat.">cat.</button>
          <button class="ghibli-block-btn" data-col="noun" data-value="parrot.">parrot.</button>
        </div>
      </div>

      <!-- Discovered Sentences Collection Tray -->
      <div class="ex5-5-discovery-tray">
        <div class="ex5-5-tray-header" id="toggleSentencesTray">
          <span><i class="fa-solid fa-wand-magic-sparkles" style="color:var(--ghibli-accent-gold);"></i> Discovered Sentences (<span id="tray_count_5_5">1</span>/12)</span>
          <i class="fa-solid fa-chevron-down tray-icon"></i>
        </div>
        <div class="ex5-5-tray-grid" id="ex5_5_tray_grid">
          <!-- 12 slots dynamically updated in JS -->
        </div>
      </div>
    </section>
    '''

def render_ghibli_reading_exercise_6_3(ex, ex_idx, page_num):
    ex_id = html.escape(str(ex.get("exercise_id") or "6.3"))
    instruction = html.escape(str(ex.get("instruction") or "READ THE ARTICLE AND ANSWER THE QUESTIONS"))
    
    article_data = ex.get("article", {})
    article_img = article_data.get("image", "images/ai/Gemini_Generated_Image_ (2).png")
    
    # Items rendering
    items = ex.get("items", [])
    questions_html = []
    
    # Example card (Reading: clean left alignment, no audio/rec)
    example_card_html = f'''
    <div class="ghibli-char-card example-card" style="margin-bottom: 12px; background: rgba(45, 90, 39, 0.06); border: 2px dashed #2d5a27; border-radius: 16px; padding: 12px 18px; display: flex; justify-content: space-between; align-items: center; gap: 14px;">
      <div class="tf-question-left" style="display: flex; align-items: center; gap: 10px; flex: 1;">
        <span style="font-size: 0.72rem; font-weight: 800; color: #2d5a27; text-transform: uppercase; background: rgba(45,90,39,0.15); padding: 4px 8px; border-radius: 8px; letter-spacing: 0.5px; flex-shrink: 0;"><i class="fa-solid fa-circle-check"></i> Example</span>
        <span class="tf-sentence-text" style="font-family: var(--font-heading, 'Outfit', sans-serif); font-size: 1rem; font-weight: 600; color: #2b261f;">Sam lives with seven people.</span>
      </div>
      <div class="tf-btn-group" style="pointer-events: none; opacity: 0.95;">
        <span class="tf-btn tf-btn-true selected" style="padding: 6px 14px; min-width: 76px; font-size: 0.88rem;"><i class="fa-solid fa-check"></i> True</span>
        <span class="tf-btn tf-btn-false" style="padding: 6px 14px; min-width: 76px; font-size: 0.88rem; opacity: 0.4;"><i class="fa-solid fa-xmark"></i> False</span>
      </div>
    </div>
    '''
    
    for idx, item in enumerate(items):
        item_id = f"p23_ex1_i{idx+1}"
        item_num = item.get("item_number", idx+1)
        question_text = html.escape(item.get("question") or item.get("prompt_text") or "")
        correct_ans = item.get("correct_answer", "True")
        
        is_true_correct = (str(correct_ans).lower() == "true")
        
        card_html = f'''
        <div class="ghibli-char-card tf-question-card" style="margin-bottom: 10px; background: rgba(255,255,255,0.92); border-radius: 16px; padding: 12px 18px; border: 1.5px solid var(--border-color, #e2d7c3); display: flex; justify-content: space-between; align-items: center; gap: 14px; box-shadow: 0 3px 10px rgba(0,0,0,0.03);">
          <div class="tf-question-left" style="display: flex; align-items: center; gap: 12px; flex: 1;">
            <span class="item-index" style="font-weight: 800; color: #2d5a27; font-size: 1.05rem; min-width: 22px;">{item_num}.</span>
            <span class="tf-sentence-text" style="font-family: var(--font-heading, 'Outfit', sans-serif); font-size: 1rem; font-weight: 600; color: #2b261f; line-height: 1.4;">{question_text}</span>
          </div>
          
          <div class="tf-btn-group">
            <button type="button" class="ghibli-option tf-btn tf-btn-true" data-value="True" data-correct="{'true' if is_true_correct else 'false'}"><i class="fa-solid fa-check"></i> True</button>
            <button type="button" class="ghibli-option tf-btn tf-btn-false" data-value="False" data-correct="{'true' if not is_true_correct else 'false'}"><i class="fa-solid fa-xmark"></i> False</button>
          </div>
        </div>
        '''
        questions_html.append(card_html)
    
    questions_block = "\n".join(questions_html)
    
    return f'''
    <section class="ghibli-section reading-exercise-container">
      <div class="ghibli-section-header">
        <div class="ghibli-ex-num">{ex_id}</div>
        <div>
          <h3 class="ghibli-ex-instruction">{instruction}</h3>
          <p class="ghibli-ex-subtext">Read the article about Sam and his family, then select True or False for each question below!</p>
        </div>
      </div>
      
      <div class="ghibli-reading-layout" style="display: grid; grid-template-columns: 1.15fr 1fr; gap: 24px; align-items: start; margin-top: 16px;">
        <!-- Left: News Article Card with High-Res Ghibli Image -->
        <div class="reading-article-card" style="border-radius: 16px; overflow: hidden; border: 1.5px solid rgba(226, 215, 195, 0.8); box-shadow: 0 6px 20px rgba(45, 90, 39, 0.08); background: #ffffff;">
          <img src="{html.escape(article_img)}" alt="Television - The Douglas family article" style="width: 100%; height: auto; display: block; object-fit: contain;" loading="eager">
        </div>
        
        <!-- Right: Questions and Worked Example -->
        <div class="reading-questions-column" style="display: flex; flex-direction: column; gap: 4px;">
          {example_card_html}
          {questions_block}
        </div>
      </div>
    </section>
    '''

def render_everyday_things_7_1(ex, ex_idx, page_num):
    config_path = 'images/everyDayThings/items_config.json'
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
    else:
        config = {}

    p_key = f"p{page_num}"
    p_items = config.get(p_key, [])
    
    p24_words = [
        'wallet', 'notepad', 'sunglasses', 'keys', 'ID card', 'letter',
        'toothbrush', 'hairbrush', 'pencil', 'dictionary', 'apple', 'book',
        'passport', 'magazine', 'camera', 'glasses'
    ]
    p25_words = [
        'pen', 'necklace', 'newspaper', 'bottle of water', 'laptop', 'earphones',
        'tablet', 'mirror', 'coins', 'map', 'umbrella', 'sandwich'
    ]
    words_list = p24_words if page_num == 24 else p25_words

    chips_html = ' '.join([f'<span class="word-chip word-panel-tag" style="background:#fff; padding:6px 14px; border-radius:12px; font-weight:600; font-size:0.95rem; color:#2b261f; border:1.5px solid #dcd1be; box-shadow:0 2px 4px rgba(0,0,0,0.04); display:inline-block; margin:4px; cursor:default;">{w}</span>' for w in words_list])

    cards = []
    if p_items:
        for it in p_items:
            img_url = it.get('img', '')
            if os.path.exists(img_url):
                mtime = int(os.path.getmtime(img_url))
                img_src = f"{img_url}?v={mtime}"
            else:
                img_src = img_url
            
            num_label = it.get('num', '')
            correct_val = it.get('correct', '')
            audio_path = it.get('audio', '')
            rec_id = it.get('rec_id', '')
            is_eg = it.get('is_example', False)

            if is_eg:
                cards.append(f'''          <div class="ghibli-char-card example-card" style="display:flex; flex-direction:column; align-items:center; text-align:center; padding:18px 16px; background:rgba(255,255,255,0.95); border-radius:20px; border:2px solid #2d5a27; box-shadow:0 6px 18px rgba(45,90,39,0.12); box-sizing:border-box; width:100%;">
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
            <div class="everyday-obj-img-wrap" style="width:100%; height:130px; display:flex; align-items:center; justify-content:center; background:#fbf8f2; border-radius:14px; border:1px solid #ebdcc5; margin-bottom:14px; padding:8px; box-sizing:border-box;">
              <img src="{img_src}" alt="{correct_val}" style="max-width:100%; max-height:100%; object-fit:contain; filter:drop-shadow(0 4px 6px rgba(0,0,0,0.12));" loading="eager" decoding="async">
            </div>
            <div class="ghibli-input-wrap" style="width:100%; box-sizing:border-box;">
              <input type="text" class="ghibli-input example-input" data-correct="{correct_val}" value="{correct_val}" readonly style="width:100%; min-width:0; max-width:100%; box-sizing:border-box; text-align:center; font-size:1.02rem; font-weight:700; padding:10px 12px; border-radius:12px; border-color:#2d5a27; background:rgba(45,90,39,0.12); color:#2d5a27;">
            </div>
          </div>''')
            else:
                cards.append(f'''          <div class="ghibli-char-card" style="display:flex; flex-direction:column; align-items:center; text-align:center; padding:18px 16px; background:rgba(255,255,255,0.92); border-radius:20px; border:1.5px solid #e2d7c3; box-shadow:0 6px 18px rgba(0,0,0,0.06); box-sizing:border-box; width:100%;">
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
            <div class="everyday-obj-img-wrap" style="width:100%; height:130px; display:flex; align-items:center; justify-content:center; background:#fbf8f2; border-radius:14px; border:1px solid #ebdcc5; margin-bottom:14px; padding:8px; box-sizing:border-box;">
              <img src="{img_src}" alt="Everyday Object" style="max-width:100%; max-height:100%; object-fit:contain; filter:drop-shadow(0 4px 6px rgba(0,0,0,0.12));" loading="eager" decoding="async">
            </div>
            <div class="ghibli-input-wrap" style="width:100%; box-sizing:border-box;">
              <input type="text" class="ghibli-input" data-correct="{correct_val}" placeholder="Type answer..." autocomplete="off" style="width:100%; min-width:0; max-width:100%; box-sizing:border-box; text-align:center; font-size:1.02rem; font-weight:600; padding:10px 12px; border-radius:12px; border:1.5px solid #d4c5a9; background:#fff;">
            </div>
          </div>''')

    ex_id = escape(ex.get("exercise_id") or ("7.1" if page_num == 24 else "7.2"))
    instruction = escape(ex.get("instruction") or "EVERYDAY THINGS • WRITE THE WORDS FROM THE PANEL UNDER THE CORRECT PICTURES")
    
    return f'''
    <section class="ghibli-section">
      <div class="ghibli-section-header">
        <div class="ghibli-ex-num">{ex_id}</div>
        <div>
          <h3 class="ghibli-ex-instruction">{instruction}</h3>
          <p class="ghibli-ex-subtext">Look at each illustration, listen to the pronunciation, and type the correct word under each picture!</p>
        </div>
      </div>
      <div class="ghibli-word-bank-panel" style="background:rgba(255,255,255,0.75); backdrop-filter:blur(10px); border-radius:18px; padding:18px 22px; margin-bottom:28px; border:1.5px solid #d4c5a9; box-shadow:0 4px 14px rgba(0,0,0,0.05);">
        <div style="display:flex; align-items:center; gap:8px; margin-bottom:12px; font-weight:800; color:#2d5a27; font-size:1rem;"><i class="fa-solid fa-layer-group"></i> <span>Word Panel</span></div>
        <div style="display:flex; flex-wrap:wrap; gap:8px;">{chips_html}</div>
      </div>
      <div class="everyday-grid" style="display:grid; grid-template-columns:repeat(auto-fill, minmax(210px, 1fr)); gap:20px;">
        {chr(10).join(cards)}
      </div>
    </section>
    '''

def render_plurals_8_3(ex, ex_idx, page_num):
    ex_id = "8.3"
    instruction = "REWRITE THE SINGULAR NOUNS IN THE PLURAL"
    
    img_map = {
        "pencil": "images/everyDayThings/pencil.png",
        "fish": "images/animals/clean/fish.png",
        "brother": "images/people/boyDetail.png",
        "diary": "images/everyDayThings/diary.png",
        "necklace": "images/everyDayThings/necklace.png",
        "brush": "images/everyDayThings/hairbrush.png",
        "watch": "images/everyDayThings/watch.png",
        "box": "images/everyDayThings/box.png",
        "dictionary": "images/everyDayThings/dictionary.png",
        "sister": "images/people/girlDetail.png",
        "umbrella": "images/everyDayThings/umbrella.png",
        "laptop": "images/everyDayThings/laptop.png",
        "sandwich": "images/everyDayThings/sandwich.png",
        "cat": "images/animals/clean/cat.png",
        "apple": "images/everyDayThings/apple.png",
        "glass": "images/everyDayThings/glasses.png",
        "passport": "images/everyDayThings/passport.png",
        "magazine": "images/everyDayThings/magazine.png"
    }
    
    items = ex.get('items', [])
    cards = []
    for idx, it in enumerate(items):
        item_num = it.get('item_number', idx + 1)
        word = it.get('question', '') or it.get('prompt_text', '')
        correct = it.get('correct_answer', '')
        audio_file = it.get('audio_file_path', f'audio/8/8_3_{item_num}.mp3')
        rec_id = f"p27_ex1_i{item_num}"
        img_url = img_map.get(word.strip().lower(), "images/everyDayThings/pencil.png")
        if os.path.exists(img_url):
            mtime = int(os.path.getmtime(img_url))
            img_src = f"{img_url}?v={mtime}"
        else:
            img_src = img_url
            
        cards.append(f'''          <div class="ghibli-char-card" style="display:flex; align-items:center; gap:16px; padding:14px 18px; background:rgba(255,255,255,0.92); border-radius:18px; border:1.5px solid #e2d7c3; box-shadow:0 4px 12px rgba(0,0,0,0.05); box-sizing:border-box;">
            <div style="width:58px; height:58px; flex-shrink:0; display:flex; align-items:center; justify-content:center; background:#fff; border-radius:12px; border:1px solid #ebdcc5; padding:4px; box-sizing:border-box;">
              <img src="{img_src}" alt="{word}" style="max-width:100%; max-height:100%; object-fit:contain;" loading="eager" decoding="async">
            </div>
            <div style="flex-grow:1; display:flex; flex-direction:column; gap:8px;">
              <div style="display:flex; align-items:center; justify-content:space-between; gap:10px;">
                <div style="display:flex; align-items:center; gap:8px;">
                  <span class="item-index" style="font-weight:800; color:#2d5a27; font-size:1.05rem; min-width:22px;">{item_num}.</span>
                  <button class="ghibli-audio-play-btn" data-audio="{audio_file}" title="Play Audio" style="position:static; transform:none; width:28px; height:28px; font-size:0.75rem;"><i class="fa-solid fa-play"></i></button>
                  <span style="font-weight:700; color:#2b261f; font-size:1.05rem;">{word}</span>
                </div>
                <div class="voice-recorder-controls">
                  <button class="voice-btn rec-btn" data-id="{rec_id}"><i class="fa-solid fa-microphone"></i> Rec</button>
                  <button class="voice-btn play-rec-btn hidden" data-id="{rec_id}"><i class="fa-solid fa-play"></i> My Voice</button>
                </div>
              </div>
              <div class="ghibli-input-wrap" style="width:100%;">
                <input type="text" class="ghibli-input" data-correct="{correct}" placeholder="Type plural noun..." autocomplete="off" style="width:100%; font-size:0.98rem; font-weight:600; padding:8px 12px; border-radius:10px; border:1.5px solid #d4c5a9; background:#fff;">
              </div>
            </div>
          </div>''')
          
    return f'''
    <section class="ghibli-section">
      <div class="ghibli-section-header">
        <div class="ghibli-ex-num">{ex_id}</div>
        <div>
          <h3 class="ghibli-ex-instruction">{instruction}</h3>
          <p class="ghibli-ex-subtext">Click play to listen to each singular noun, then write its correct plural form!</p>
        </div>
      </div>
      <div style="display:grid; grid-template-columns:repeat(auto-fill, minmax(280px, 1fr)); gap:16px;">
        {chr(10).join(cards)}
      </div>
    </section>
    '''

def render_spelling_corrections_8_4(ex, ex_idx, page_num):
    ex_id = "8.4"
    instruction = "REWRITE THE WORDS, CORRECTING THE SPELLINGS"
    
    img_map = {
        "brushs": "images/everyDayThings/hairbrush.png",
        "boxs": "images/everyDayThings/box.png",
        "dictionarys": "images/everyDayThings/dictionary.png",
        "doges": "images/animals/clean/dog.png",
        "notebookses": "images/everyDayThings/notebook.png",
        "toothbrushs": "images/everyDayThings/toothbrush.png",
        "bookes": "images/everyDayThings/book.png",
        "penciles": "images/everyDayThings/pencil.png",
        "lettres": "images/everyDayThings/letter.png",
        "newspaperes": "images/everyDayThings/newspaper.png",
        "glasss": "images/everyDayThings/glasses.png",
        "passportes": "images/everyDayThings/passport.png",
        "magazinees": "images/everyDayThings/magazine.png"
    }
    
    items = ex.get('items', [])
    cards = []
    for idx, it in enumerate(items):
        item_num = it.get('item_number', idx + 1)
        word = it.get('question', '') or it.get('prompt_text', '')
        correct = it.get('correct_answer', '')
        audio_file = it.get('audio_file_path', f'audio/8/8_4_{item_num}.mp3')
        rec_id = f"p27_ex2_i{item_num}"
        img_url = img_map.get(word.strip().lower(), "images/everyDayThings/pencil.png")
        if os.path.exists(img_url):
            mtime = int(os.path.getmtime(img_url))
            img_src = f"{img_url}?v={mtime}"
        else:
            img_src = img_url
            
        cards.append(f'''          <div class="ghibli-char-card" style="display:flex; align-items:center; gap:16px; padding:14px 18px; background:rgba(255,255,255,0.92); border-radius:18px; border:1.5px solid #e2d7c3; box-shadow:0 4px 12px rgba(0,0,0,0.05); box-sizing:border-box;">
            <div style="width:58px; height:58px; flex-shrink:0; display:flex; align-items:center; justify-content:center; background:#fff; border-radius:12px; border:1px solid #ebdcc5; padding:4px; box-sizing:border-box;">
              <img src="{img_src}" alt="{word}" style="max-width:100%; max-height:100%; object-fit:contain;" loading="eager" decoding="async">
            </div>
            <div style="flex-grow:1; display:flex; flex-direction:column; gap:8px;">
              <div style="display:flex; align-items:center; justify-content:space-between; gap:10px;">
                <div style="display:flex; align-items:center; gap:8px;">
                  <span class="item-index" style="font-weight:800; color:#2d5a27; font-size:1.05rem; min-width:22px;">{item_num}.</span>
                  <button class="ghibli-audio-play-btn" data-audio="{audio_file}" title="Play Audio" style="position:static; transform:none; width:28px; height:28px; font-size:0.75rem;"><i class="fa-solid fa-play"></i></button>
                  <span style="font-weight:700; color:#b33927; font-size:1.05rem; text-decoration:line-through;">{word}</span>
                </div>
                <div class="voice-recorder-controls">
                  <button class="voice-btn rec-btn" data-id="{rec_id}"><i class="fa-solid fa-microphone"></i> Rec</button>
                  <button class="voice-btn play-rec-btn hidden" data-id="{rec_id}"><i class="fa-solid fa-play"></i> My Voice</button>
                </div>
              </div>
              <div class="ghibli-input-wrap" style="width:100%;">
                <input type="text" class="ghibli-input" data-correct="{correct}" placeholder="Type correct spelling..." autocomplete="off" style="width:100%; font-size:0.98rem; font-weight:600; padding:8px 12px; border-radius:10px; border:1.5px solid #d4c5a9; background:#fff;">
              </div>
            </div>
          </div>''')
          
    return f'''
    <section class="ghibli-section">
      <div class="ghibli-section-header">
        <div class="ghibli-ex-num">{ex_id}</div>
        <div>
          <h3 class="ghibli-ex-instruction">{instruction}</h3>
          <p class="ghibli-ex-subtext">Look at each misspelled word, listen to the pronunciation, and type the correct spelling!</p>
        </div>
      </div>
      <div style="display:grid; grid-template-columns:repeat(auto-fill, minmax(280px, 1fr)); gap:16px;">
        {chr(10).join(cards)}
      </div>
    </section>
    '''

def render_pictures_what_it_shows_8_5(ex, ex_idx, page_num):
    ex_id = "8.5"
    instruction = "WRITE DOWN WHAT EACH PICTURE SHOWS"
    
    items = [
        {"num": "Example", "correct": "two watches", "display_correct": "two watches", "img": "images/everyDayThings/8_5_watches.png", "is_eg": True, "rec_id": "p27_ex3_eg"},
        {"num": "1.", "correct": "three sandwiches", "display_correct": "three sandwiches", "img": "images/everyDayThings/8_5_sandwiches.png", "is_eg": False, "rec_id": "p27_ex3_i1"},
        {"num": "2.", "correct": "two necklaces", "display_correct": "two necklaces", "img": "images/everyDayThings/8_5_necklaces.png", "is_eg": False, "rec_id": "p27_ex3_i2"},
        {"num": "3.", "correct": "four bags", "display_correct": "four bags", "img": "images/everyDayThings/8_5_bags.png", "is_eg": False, "rec_id": "p27_ex3_i3"},
        {"num": "4.", "correct": "three toothbrushes", "display_correct": "three toothbrushes", "img": "images/everyDayThings/8_5_toothbrushes.png", "is_eg": False, "rec_id": "p27_ex3_i4"},
        {"num": "5.", "correct": "two diaries", "display_correct": "two diaries", "img": "images/everyDayThings/8_5_diaries.png", "is_eg": False, "rec_id": "p27_ex3_i5"},
        {"num": "6.", "correct": "two cats", "display_correct": "two cats", "img": "images/everyDayThings/8_5_cats.png", "is_eg": False, "rec_id": "p27_ex3_i6"},
        {"num": "7.", "correct": "one apple|an apple", "display_correct": "one apple", "img": "images/everyDayThings/8_5_apple.png", "is_eg": False, "rec_id": "p27_ex3_i7"}
    ]
    
    cards = []
    for it in items:
        img_url = it.get('img', '')
        if os.path.exists(img_url):
            mtime = int(os.path.getmtime(img_url))
            img_src = f"{img_url}?v={mtime}"
        else:
            img_src = img_url
            
        num_label = it.get('num', '')
        correct_val = it.get('correct', '')
        display_val = it.get('display_correct', correct_val)
        rec_id = it.get('rec_id', '')
        is_eg = it.get('is_eg', False)

        if is_eg:
            cards.append(f'''          <div class="ghibli-char-card example-card" style="display:flex; flex-direction:column; align-items:center; text-align:center; padding:18px 16px; background:rgba(255,255,255,0.95); border-radius:20px; border:2px solid #2d5a27; box-shadow:0 6px 18px rgba(45,90,39,0.12); box-sizing:border-box;">
            <div style="display:flex; justify-content:space-between; align-items:center; width:100%; margin-bottom:12px;">
              <div style="display:flex; align-items:center; gap:8px;">
                <span class="item-index" style="font-weight:800; color:#2d5a27; font-size:1.1rem;">{num_label}</span>
                <span class="ghibli-example-badge" style="background:#2d5a27; color:#fff; padding:3px 10px; border-radius:12px; font-weight:700; font-size:0.75rem; text-transform:uppercase;">Example</span>
              </div>
              <div class="voice-recorder-controls">
                <button class="voice-btn rec-btn" data-id="{rec_id}"><i class="fa-solid fa-microphone"></i> Rec</button>
                <button class="voice-btn play-rec-btn hidden" data-id="{rec_id}"><i class="fa-solid fa-play"></i> My Voice</button>
              </div>
            </div>
            <div style="width:100%; height:140px; display:flex; align-items:center; justify-content:center; background:#fff; border-radius:14px; border:1px solid #ebdcc5; margin-bottom:14px; padding:6px; box-sizing:border-box;">
              <img src="{img_src}" alt="{display_val}" style="max-width:100%; max-height:100%; object-fit:contain; filter:drop-shadow(0 4px 6px rgba(0,0,0,0.10));" loading="eager" decoding="async">
            </div>
            <div class="ghibli-input-wrap" style="width:100%;">
              <input type="text" class="ghibli-input example-input" data-correct="{correct_val}" value="{display_val}" readonly style="width:100%; text-align:center; font-size:1.02rem; font-weight:700; padding:10px 12px; border-radius:12px; border-color:#2d5a27; background:rgba(45,90,39,0.12); color:#2d5a27;">
            </div>
          </div>''')
        else:
            cards.append(f'''          <div class="ghibli-char-card" style="display:flex; flex-direction:column; align-items:center; text-align:center; padding:18px 16px; background:rgba(255,255,255,0.92); border-radius:20px; border:1.5px solid #e2d7c3; box-shadow:0 6px 18px rgba(0,0,0,0.06); box-sizing:border-box;">
            <div style="display:flex; justify-content:space-between; align-items:center; width:100%; margin-bottom:12px;">
              <span class="item-index" style="font-weight:800; color:#2d5a27; font-size:1.1rem;">{num_label}</span>
              <div class="voice-recorder-controls">
                <button class="voice-btn rec-btn" data-id="{rec_id}"><i class="fa-solid fa-microphone"></i> Rec</button>
                <button class="voice-btn play-rec-btn hidden" data-id="{rec_id}"><i class="fa-solid fa-play"></i> My Voice</button>
              </div>
            </div>
            <div style="width:100%; height:140px; display:flex; align-items:center; justify-content:center; background:#fff; border-radius:14px; border:1px solid #ebdcc5; margin-bottom:14px; padding:6px; box-sizing:border-box;">
              <img src="{img_src}" alt="Picture {num_label}" style="max-width:100%; max-height:100%; object-fit:contain; filter:drop-shadow(0 4px 6px rgba(0,0,0,0.10));" loading="eager" decoding="async">
            </div>
            <div class="ghibli-input-wrap" style="width:100%;">
              <input type="text" class="ghibli-input" data-correct="{correct_val}" placeholder="Type what picture shows..." autocomplete="off" style="width:100%; text-align:center; font-size:1.02rem; font-weight:600; padding:10px 12px; border-radius:12px; border:1.5px solid #d4c5a9; background:#fff;">
            </div>
          </div>''')

    return f'''
    <section class="ghibli-section">
      <div class="ghibli-section-header">
        <div class="ghibli-ex-num">{ex_id}</div>
        <div>
          <h3 class="ghibli-ex-instruction">{instruction}</h3>
          <p class="ghibli-ex-subtext">Look at each picture, count the items, and type the number and plural noun!</p>
        </div>
      </div>
      <div style="display:grid; grid-template-columns:repeat(auto-fill, minmax(220px, 1fr)); gap:20px;">
        {chr(10).join(cards)}
      </div>
    </section>
    '''

def render_jobs_9_1(ex, ex_idx, page_num):
    config_path = 'images/jobs/jobs_config.json'
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
    else:
        config = {}

    p_key = f"p{page_num}"
    p_items = config.get(p_key, [])
    
    p30_words = [
        'scientist', 'pilot', 'firefighter', 'gardener', 'nurse', 'farmer',
        'chef', 'receptionist', 'vet', 'teacher', 'businessman', 'mechanic',
        'artist', 'hairdresser', 'waitress', 'construction worker'
    ]
    p31_words = [
        'driver', 'electrician', 'actor', 'businesswoman', 'police officer', 'dentist',
        'waiter', 'engineer', 'cleaner', 'doctor', 'sales assistant', 'judge'
    ]
    words_list = p30_words if page_num == 30 else p31_words

    chips_html = ' '.join([f'<span class="word-chip word-panel-tag" style="background:#fff; padding:6px 14px; border-radius:12px; font-weight:600; font-size:0.95rem; color:#2b261f; border:1.5px solid #dcd1be; box-shadow:0 2px 4px rgba(0,0,0,0.04); display:inline-block; margin:4px; cursor:default;">{w}</span>' for w in words_list])

    cards = []
    if p_items:
        for it in p_items:
            img_url = it.get('img', '')
            if os.path.exists(img_url):
                mtime = int(os.path.getmtime(img_url))
                img_src = f"{img_url}?v={mtime}"
            else:
                img_src = img_url
            
            num_label = it.get('num', '')
            correct_val = it.get('correct', '')
            audio_path = it.get('audio', '')
            rec_id = it.get('rec_id', '')
            is_eg = it.get('is_example', False)

            if is_eg:
                cards.append(f'''          <div class="ghibli-char-card example-card" style="display:flex; flex-direction:column; align-items:center; text-align:center; padding:18px 16px; background:rgba(255,255,255,0.95); border-radius:20px; border:2px solid #2d5a27; box-shadow:0 6px 18px rgba(45,90,39,0.12); box-sizing:border-box; width:100%;">
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
            <div class="job-img-wrap" style="width:100%; height:140px; display:flex; align-items:center; justify-content:center; background:#fff; border-radius:14px; border:1px solid #ebdcc5; margin-bottom:14px; padding:6px; box-sizing:border-box;">
              <img src="{img_src}" alt="{correct_val}" style="max-width:100%; max-height:100%; object-fit:contain; filter:drop-shadow(0 4px 6px rgba(0,0,0,0.10));" loading="eager" decoding="async">
            </div>
            <div class="ghibli-input-wrap" style="width:100%; box-sizing:border-box;">
              <input type="text" class="ghibli-input example-input" data-correct="{correct_val}" value="{correct_val}" readonly style="width:100%; min-width:0; max-width:100%; box-sizing:border-box; text-align:center; font-size:1.02rem; font-weight:700; padding:10px 12px; border-radius:12px; border-color:#2d5a27; background:rgba(45,90,39,0.12); color:#2d5a27;">
            </div>
          </div>''')
            else:
                cards.append(f'''          <div class="ghibli-char-card" style="display:flex; flex-direction:column; align-items:center; text-align:center; padding:18px 16px; background:rgba(255,255,255,0.92); border-radius:20px; border:1.5px solid #e2d7c3; box-shadow:0 6px 18px rgba(0,0,0,0.06); box-sizing:border-box; width:100%;">
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
            <div class="job-img-wrap" style="width:100%; height:140px; display:flex; align-items:center; justify-content:center; background:#fff; border-radius:14px; border:1px solid #ebdcc5; margin-bottom:14px; padding:6px; box-sizing:border-box;">
              <img src="{img_src}" alt="Job Occupation" style="max-width:100%; max-height:100%; object-fit:contain; filter:drop-shadow(0 4px 6px rgba(0,0,0,0.10));" loading="eager" decoding="async">
            </div>
            <div class="ghibli-input-wrap" style="width:100%; box-sizing:border-box;">
              <input type="text" class="ghibli-input" data-correct="{correct_val}" placeholder="Type answer..." autocomplete="off" style="width:100%; min-width:0; max-width:100%; box-sizing:border-box; text-align:center; font-size:1.02rem; font-weight:600; padding:10px 12px; border-radius:12px; border:1.5px solid #d4c5a9; background:#fff;">
            </div>
          </div>''')

    ex_id = escape(ex.get("exercise_id") or "9.1")
    instruction = escape(ex.get("instruction") or "JOBS • WRITE THE WORDS FROM THE PANEL UNDER THE CORRECT PICTURES")
    
    return f'''
    <section class="ghibli-section">
      <div class="ghibli-section-header">
        <div class="ghibli-ex-num">{ex_id}</div>
        <div>
          <h3 class="ghibli-ex-instruction">{instruction}</h3>
          <p class="ghibli-ex-subtext">Look at each job illustration, listen to the pronunciation, and type the correct occupation under each picture!</p>
        </div>
      </div>
      <div class="ghibli-word-bank-panel" style="background:rgba(255,255,255,0.75); backdrop-filter:blur(10px); border-radius:18px; padding:18px 22px; margin-bottom:28px; border:1.5px solid #d4c5a9; box-shadow:0 4px 14px rgba(0,0,0,0.05);">
        <div style="display:flex; align-items:center; gap:8px; margin-bottom:12px; font-weight:800; color:#2d5a27; font-size:1rem;"><i class="fa-solid fa-briefcase"></i> <span>Word Panel</span></div>
        <div style="display:flex; flex-wrap:wrap; gap:8px;">{chips_html}</div>
      </div>
      <div class="jobs-grid" style="display:grid; grid-template-columns:repeat(auto-fill, minmax(210px, 1fr)); gap:20px;">
        {chr(10).join(cards)}
      </div>
    </section>
    '''

def render_exercise(ex, ex_idx, page_num):
    ex_id = str(ex.get("exercise_id") or "")
    instruction_str = str(ex.get("instruction", "")).upper()
    if page_num == 18 or ex_id == "4.1":
        return render_ghibli_family_tree(ex, ex_idx, page_num)
    elif page_num == 19 or ex_id == "4.2":
        return render_ghibli_animals_exercise(ex, ex_idx, page_num)
    elif page_num == 21 and (ex_id == "5.5" or ex_idx == 2 or "CHART" in instruction_str):
        return render_ghibli_substitution_chart_5_5(ex, ex_idx, page_num)
    elif page_num == 23 and (ex_id == "6.3" or ex_idx == 0):
        return render_ghibli_reading_exercise_6_3(ex, ex_idx, page_num)
    elif page_num in [24, 25] or (ex_id == "7.1" and page_num < 30) or "EVERYDAY THINGS" in instruction_str:
        return render_everyday_things_7_1(ex, ex_idx, page_num)
    elif page_num == 27 and (ex_id == "8.3" or ex_idx == 0 or "REWRITE THE SINGULAR NOUNS" in instruction_str):
        return render_plurals_8_3(ex, ex_idx, page_num)
    elif page_num == 27 and (ex_id == "8.4" or ex_idx == 1 or "CORRECTING THE SPELLINGS" in instruction_str):
        return render_spelling_corrections_8_4(ex, ex_idx, page_num)
    elif page_num == 27 and (ex_id == "8.5" or ex_idx == 2 or "WRITE DOWN WHAT EACH PICTURE SHOWS" in instruction_str):
        return render_pictures_what_it_shows_8_5(ex, ex_idx, page_num)
    elif page_num in [30, 31]:
        return render_jobs_9_1(ex, ex_idx, page_num)
    elif page_num == 33 and (ex_id == "10.4" or ex_idx == 1 or "WORKPLACE" in instruction_str or "LABELS" in instruction_str) and u2:
        return u2.render_workplaces_10_4(ex, ex_idx, page_num)
    elif page_num == 34 and (ex_id == "10.6" or ex_idx == 0 or "SAY THE SENTENCES" in instruction_str) and u2:
        return u2.render_spoken_scenes_10_6(ex, ex_idx, page_num)
    elif page_num == 35 and (ex_id == "10.8" or ex_idx == 1 or "LISTEN TO THE AUDIO AND ANSWER" in instruction_str) and u2:
        return u2.render_audio_listening_10_8(ex, ex_idx, page_num)
    elif page_num == 36 and (ex_id == "11.1" or ex_idx == 0 or "MATCH THE PICTURES TO THE CORRECT TIMES" in instruction_str) and u2:
        return u2.render_telling_time_11_1(ex, ex_idx, page_num)
    elif page_num == 36 and (ex_id == "11.2" or ex_idx == 1 or "MARK THE CORRECT TIMES" in instruction_str) and u2:
        return u2.render_audio_clocks_11_2(ex, ex_idx, page_num)
    elif page_num == 37 and (ex_id == "11.4" or ex_idx == 1 or "SAY EACH TIME OUT LOUD" in instruction_str) and u2:
        return u2.render_spoken_time_11_4(ex, ex_idx, page_num)
    elif page_num in [38, 39] and u2:
        return u2.render_routines_12_1(ex, ex_idx, page_num)
    elif page_num == 40 and (ex_id == "13.1" or ex_idx == 0 or "MATCH THE PICTURES TO THE CORRECT SENTENCES" in instruction_str) and u2:
        return u2.render_marion_timeline_13_1(ex, ex_idx, page_num)
    elif page_num == 41 and (ex_id == "13.5" or ex_idx == 2 or "SAY THESE VERBS OUT LOUD" in instruction_str) and u2:
        return u2.render_pronunciation_verbs_13_5(ex, ex_idx, page_num)
    elif page_num == 42 and (ex_id == "14.2" or ex_idx == 1 or "MARK THE SENTENCES THAT ARE CORRECT" in instruction_str) and u2:
        return u2.render_sentence_choice_pairs_14_2(ex, ex_idx, page_num)
    elif page_num == 44 and (ex_id == "14.6" or ex_idx == 1 or "READ THE EMAIL" in instruction_str) and u2:
        return u2.render_reading_email_14_6(ex, ex_idx, page_num)
    elif page_num == 45 and (ex_id == "14.7" or ex_idx == 0 or "NUMBER THE PICTURES" in instruction_str) and u2:
        return u2.render_audio_listen_numbered_slots_14_7(ex, ex_idx, page_num)
    elif page_num == 45 and (ex_id == "14.8" or ex_idx == 1 or "LISTEN TO 14.7 AGAIN" in instruction_str) and u2:
        return u2.render_multiple_choice_14_8(ex, ex_idx, page_num)
    elif ex_id in ["8.1", "10.3", "10.5", "13.2", "14.1"] or "CROSS OUT" in instruction_str:
        return render_cross_out(ex, ex_idx, page_num)
    elif page_num == 28 and (ex_id == "8.6" or ex_idx == 0):
        return render_matching_exercise_8_6(ex, ex_idx, page_num)
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

    p_uid, p_utitle, p_exrange = get_parent_unit(page_num)
    if isinstance(p_uid, int):
        unit_subtitle_str = f"🌿 Unit {p_uid} • Lesson: {unit_title} • Page {page_num}"
        unit_tag_str = f"Unit {p_uid} • Lesson: {unit_title}"
        full_unit_btn = f'<a href="unit{p_uid}.html" class="ghibli-btn ghibli-btn-gold" title="Open Complete Unit {p_uid} Module"><i class="fa-solid fa-book-open"></i> Full Unit {p_uid}</a>'
    else:
        unit_subtitle_str = f"🌿 {p_uid} • {unit_title} • Page {page_num}"
        unit_tag_str = f"{p_uid} • {unit_title}"
        full_unit_btn = '<a href="index.html" class="ghibli-btn ghibli-btn-gold"><i class="fa-solid fa-house"></i> Home Hub</a>'

    bottom_check_bar = ""
    if total_items > 0 or len(exercises) > 0:
        bottom_check_bar = '''
    <!-- Bottom Check Answers Bar -->
    <div class="bottom-action-bar" style="display: flex; align-items: center; justify-content: center; gap: 16px; margin: 32px 0 20px 0; padding: 20px; background: rgba(255, 255, 255, 0.4); backdrop-filter: blur(8px); border-radius: 20px; border: 1.5px solid rgba(255, 255, 255, 0.5);">
      <button class="ghibli-btn ghibli-btn-primary ghibli-check-btn-bottom" style="font-size: 1.05rem; padding: 12px 28px; box-shadow: 0 4px 14px rgba(45,90,39,0.3); cursor: pointer;"><i class="fa-solid fa-circle-check"></i> Check Answers</button>
      <button class="ghibli-btn ghibli-btn-secondary ghibli-reset-btn-bottom" style="font-size: 1rem; padding: 12px 24px; cursor: pointer;"><i class="fa-solid fa-rotate-left"></i> Reset Answers</button>
    </div>
        '''

    v_tag = int(time.time())

    html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Teacher Lewis's Practice Book • Unit {p_uid} • Page {page_num}: {unit_title} | Studio Ghibli Edition</title>
  
  <!-- Early Theme Init to prevent white flash (FOUC) -->
  <script>
    (function() {{
      try {{
        var t = localStorage.getItem('ghibli_theme') || 'day';
        if (t !== 'day') document.documentElement.className = 'theme-' + t;
      }} catch(e) {{}}
    }})();
  </script>

  <!-- Critical CSS to prevent layout shift & oversize image blowout on first load -->
  <style>
    img {{ max-width: 100%; height: auto; display: block; }}
    .ghibli-avatar-wrap {{ width: 76px; height: 76px; position: relative; flex-shrink: 0; }}
    .ghibli-avatar-img {{ width: 76px; height: 76px; max-width: 76px; max-height: 76px; border-radius: 50%; object-fit: cover; aspect-ratio: 1/1; }}
    .mascot-avatar-wrap {{ width: 220px; height: 220px; position: relative; flex-shrink: 0; }}
    .mascot-avatar {{ width: 220px; height: 220px; max-width: 220px; max-height: 220px; border-radius: 50%; object-fit: cover; aspect-ratio: 1/1; }}
    .page-turn-bar {{ display: flex; align-items: center; justify-content: space-between; gap: 12px; padding: 12px 24px; background: rgba(255,255,255,0.92); box-shadow: 0 4px 16px rgba(0,0,0,0.06); border-radius: 40px; margin: 0 auto 20px auto; max-width: 800px; border: 1.5px solid rgba(255,255,255,0.5); }}
    .page-turn-badge {{ font-family: var(--font-heading); font-weight: 800; color: #2d5a27; font-size: 1rem; }}
  </style>

  <!-- Local Stylesheet (Loaded first for 0ms local styling) -->
  <link rel="stylesheet" href="ghibli_page12.css?v={v_tag}">

  <!-- External Fonts & Icons -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Outfit:wght@500;600;700;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
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
          <span class="ghibli-subtitle">{unit_subtitle_str}</span>
        </div>
      </a>
      <div class="ghibli-header-actions">
        <a href="index.html" class="ghibli-btn ghibli-btn-secondary"><i class="fa-solid fa-house"></i> Home Hub</a>
        {full_unit_btn}
        <a href="ghibli_reader.html?page={page_num}" class="ghibli-btn ghibli-btn-gold" title="Continuous Music Reader Mode"><i class="fa-solid fa-headphones"></i> Reader Mode</a>
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

  <!-- Floating Check Answers Button (Fixed Left-Hand Side) -->
  <button class="ghibli-floating-check-btn" id="ghibliFloatingCheckBtn" title="Check Answers (Always Available)">
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
      <img src="images/ghibli/mascot.webp" alt="Kodama Mascot" class="mascot-avatar" id="mascotAvatarImg" width="220" height="220" loading="eager" decoding="async">
    </div>
  </div>

  <script src="ghibli_audio.js?v={v_tag}"></script>
  <script src="ghibli_page_engine.js?v={v_tag}"></script>
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

        out_path1 = os.path.join(OUTPUT_DIR, f"ghibli_p{p_num:03d}.html")
        out_path2 = os.path.join(OUTPUT_DIR, f"ghibli_page{p_num:03d}.html")
        with open(out_path1, "w", encoding="utf-8") as f:
            f.write(html_code)
        with open(out_path2, "w", encoding="utf-8") as f:
            f.write(html_code)

    print(f"SUCCESS: Generated all page-by-page HTML files matching ghibli_page12.css styling!")

if __name__ == "__main__":
    main()
