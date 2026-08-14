import json

correct_map = {
    0: "Sam's grandmother.",
    1: "Sam's grandfather.",
    2: "Sam's father.",
    3: "Sam's mother.",
    4: "Sam's brother.",
    5: "Sam's sister.",
    6: "Sam's friend.",
    7: "Sam's cousin."
}

with open('output_json/page_022.json', 'r', encoding='utf-8') as f:
    p22 = json.load(f)

for ex in p22['exercises']:
    if ex['exercise_id'] == '6.2':
        ex['audio_file_path'] = 'audio/6/6_2_uk.mp3'
        for i, item in enumerate(ex['items']):
            item['audio_file_path'] = 'audio/6/6_2_uk.mp3'
            if i in correct_map:
                item['correct_answer'] = correct_map[i]

with open('output_json/page_022.json', 'w', encoding='utf-8') as f:
    json.dump(p22, f, indent=2)

with open('output_json/all_pages_consolidated.json', 'r', encoding='utf-8') as f:
    consolidated = json.load(f)

for p in consolidated['pages']:
    if p.get('page_number') == 22:
        for ex in p['exercises']:
            if ex['exercise_id'] == '6.2':
                ex['audio_file_path'] = 'audio/6/6_2_uk.mp3'
                for i, item in enumerate(ex['items']):
                    item['audio_file_path'] = 'audio/6/6_2_uk.mp3'
                    if i in correct_map:
                        item['correct_answer'] = correct_map[i]

with open('output_json/all_pages_consolidated.json', 'w', encoding='utf-8') as f:
    json.dump(consolidated, f, indent=2)

print('Updated Page 22 JSON data successfully!')
