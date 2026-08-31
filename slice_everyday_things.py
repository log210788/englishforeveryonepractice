import os, json
import numpy as np
from PIL import Image

def slice_master_image():
    with open('images/everyDayThings/detected_items.json', 'r', encoding='utf-8') as f:
        text = f.read().strip()
        if text.startswith('`json'):
            text = text[7:]
        if text.endswith('`'):
            text = text[:-3]
        items = json.loads(text)

    master_path = r'images\everyDayThings\Gemini_Generated_Image_ (2).png'
    master_img = Image.open(master_path).convert('RGBA')
    w, h = master_img.size
    col_w = w / 7.0
    row_h = h / 5.0

    out_dir = r'images\everyDayThings'
    os.makedirs(out_dir, exist_ok=True)

    name_mapping = {
        1: 'coins.png',
        2: 'dictionary.png',
        3: 'pencil.png',
        4: 'passport.png',
        5: 'camera.png',
        6: 'clock.png',
        7: 'coffee_cup.png',
        8: 'id_card.png',
        9: 'earphones.png',
        10: 'bottle_of_water.png',
        11: 'map.png',
        12: 'apple.png',
        13: 'box.png',
        14: 'sunglasses_alt.png',
        15: 'notepad.png',
        16: 'tablet.png',
        17: 'toothbrush.png',
        18: 'sandwich.png',
        19: 'letter.png',
        20: 'camera_alt.png',
        21: 'notebook.png',
        22: 'mirror.png',
        23: 'sunglasses.png',
        24: 'keys.png',
        25: 'newspaper.png',
        26: 'hairbrush.png',
        27: 'necklace.png',
        28: 'wallet.png',
        29: 'necklace_alt.png',
        30: 'book.png',
        31: 'glasses.png',
        32: 'laptop.png',
        33: 'umbrella.png',
        34: 'magazine.png',
        35: 'pen.png'
    }

    for item in items:
        idx = item['cell_idx']
        r = item['row'] - 1
        c = item['col'] - 1
        filename = name_mapping.get(idx, f'item_{idx:02d}.png')
        
        x1 = int(c * col_w)
        y1 = int(r * row_h)
        x2 = int((c + 1) * col_w)
        y2 = int((r + 1) * row_h)
        
        crop = master_img.crop((x1, y1, x2, y2))
        crop_arr = np.array(crop)
        
        r_chan, g_chan, b_chan = crop_arr[:,:,0], crop_arr[:,:,1], crop_arr[:,:,2]
        is_bg = (r_chan > 240) & (g_chan > 240) & (b_chan > 240)
        is_fg = ~is_bg
        
        if np.any(is_fg):
            ys, xs = np.where(is_fg)
            min_y, max_y = max(0, ys.min() - 8), min(crop_arr.shape[0], ys.max() + 9)
            min_x, max_x = max(0, xs.min() - 8), min(crop_arr.shape[1], xs.max() + 9)
            
            trimmed = crop.crop((min_x, min_y, max_x, max_y))
            save_path = os.path.join(out_dir, filename)
            trimmed.save(save_path, 'PNG')
            print('Saved [%02d] %s -> %s (%s)' % (idx, item['item_name'], save_path, str(trimmed.size)))

if __name__ == '__main__':
    slice_master_image()
