import os
import math
import random
import argparse
import glob
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

OUTLINE_COLORS = {
    "electric_blue": (0, 110, 255),
    "crimson_red": (235, 35, 45),
    "neon_green": (20, 210, 80),
    "cyber_yellow": (255, 190, 0),
    "hot_pink": (255, 40, 140),
    "deep_purple": (160, 40, 240)
}

HOOK_TITLES = [
    "CAN YOU STOP IN THE SHADOW?",
    "99% FAIL TO PAUSE IN TIME!",
    "STOP IT AT THE RIGHT MOMENT",
    "CAN YOU PAUSE PERFECTLY?",
    "TRY TO STOP AT 100% MATCH",
    "LEVEL 1: CAN YOU CATCH IT?"
]

def create_smooth_outline(rgba_img, color_rgb=(0, 110, 255), thickness=8):
    img_np = np.array(rgba_img)
    h, w = img_np.shape[:2]
    alpha = img_np[:, :, 3]
    
    _, thresh = cv2.threshold(alpha, 35, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    
    outline_canvas = np.zeros((h, w, 4), dtype=np.uint8)
    rgba_color = (int(color_rgb[0]), int(color_rgb[1]), int(color_rgb[2]), 255)
    cv2.drawContours(outline_canvas, contours, -1, rgba_color, thickness=thickness, lineType=cv2.LINE_AA)
    
    return Image.fromarray(outline_canvas, mode="RGBA")

def trim_transparent_borders(img):
    bbox = img.getbbox()
    return img.crop(bbox) if bbox else img

def build_background(title_text, width=1080, height=1920):
    cx, cy = width / 2, height * 0.46
    max_radius = math.hypot(width, height) / 1.5
    y, x = np.ogrid[:height, :width]
    dist = np.clip(np.hypot(x - cx, y - cy) / max_radius, 0.0, 1.0)
    
    c_center = np.array([255, 255, 255], dtype=np.float32)
    c_edge = np.array([225, 230, 238], dtype=np.float32)
    bg_np = (c_center * (1.0 - dist[:, :, None]) + c_edge * dist[:, :, None]).astype(np.uint8)
    
    bg_img = Image.fromarray(bg_np, mode="RGB").convert("RGBA")
    draw = ImageDraw.Draw(bg_img)
    
    # Faint target arena circle
    icx, icy = int(cx), int(cy)
    draw.ellipse([icx - 440, icy - 440, icx + 440, icy + 440], outline=(180, 195, 215, 60), width=4)
    draw.ellipse([icx - 410, icy - 410, icx + 410, icy + 410], fill=(235, 242, 252, 50), outline=(180, 195, 215, 70), width=2)
    
    try:
        title_font = ImageFont.truetype("arialbd.ttf", 44)
        badge_font = ImageFont.truetype("arialbd.ttf", 30)
        sub_font = ImageFont.truetype("arial.ttf", 32)
    except:
        title_font = badge_font = sub_font = ImageFont.load_default()
        
    top_y = 120
    draw.rounded_rectangle([60, top_y, width - 60, top_y + 110], radius=24, fill=(255, 255, 255, 230), outline=(210, 222, 238, 255), width=3)
    
    bbox = draw.textbbox((0, 0), title_text, font=title_font)
    tw = bbox[2] - bbox[0]
    draw.text(((width - tw) // 2, top_y + 32), title_text, fill=(15, 23, 42, 255), font=title_font)
    
    def draw_badge(bx, by, text, bg_color=(225, 29, 72)):
        bw, bh = 170, 56
        draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=16, fill=bg_color)
        tbox = draw.textbbox((0, 0), text, font=badge_font)
        draw.text((bx + (bw - (tbox[2] - tbox[0])) // 2, by + 12), text, fill=(255, 255, 255), font=badge_font)
        
    draw_badge(80, top_y + 130, "99% FAIL")
    draw_badge(width - 250, top_y + 130, "PAUSE")
    
    bot_y = height - 200
    cta_text = "Tap screen to pause & comment your screenshot!"
    c_bbox = draw.textbbox((0, 0), cta_text, font=sub_font)
    cw = c_bbox[2] - c_bbox[0]
    draw.rounded_rectangle([(width - cw) // 2 - 30, bot_y - 12, (width + cw) // 2 + 30, bot_y + 50],
                           radius=20, fill=(30, 41, 59, 230))
    draw.text(((width - cw) // 2, bot_y), cta_text, fill=(255, 255, 255), font=sub_font)
    
    return bg_img

def prep_sprite(pil_img):
    np_img = np.array(pil_img)
    rgb = np_img[:, :, :3]
    bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    alpha = np_img[:, :, 3].astype(np.float32) / 255.0
    return bgr, alpha, pil_img.width, pil_img.height

def fast_overlay(frame, sprite_bgr, sprite_alpha, x, y, sw, sh, width=1080, height=1920):
    x1, y1 = max(0, x), max(0, y)
    x2, y2 = min(width, x + sw), min(height, y + sh)
    if x1 >= x2 or y1 >= y2:
        return
    sx1, sy1 = x1 - x, y1 - y
    sx2, sy2 = sx1 + (x2 - x1), sy1 + (y2 - y1)
    a = sprite_alpha[sy1:sy2, sx1:sx2, None]
    frame[y1:y2, x1:x2] = (1.0 - a) * frame[y1:y2, x1:x2] + a * sprite_bgr[sy1:sy2, sx1:sx2]

def generate_single_video(hero_path, item_path, output_path, outline_color_name=None, title=None, duration=8.0, fps=60):
    width, height = 1080, 1920
    total_frames = int(duration * fps)
    
    if not outline_color_name or outline_color_name not in OUTLINE_COLORS:
        outline_color_name = random.choice(list(OUTLINE_COLORS.keys()))
    outline_color = OUTLINE_COLORS[outline_color_name]
    
    if not title:
        title = random.choice(HOOK_TITLES)
        
    print(f"\n==========================================")
    print(f"Rendering: {os.path.basename(output_path)}")
    print(f"Hero: {os.path.basename(hero_path)} | Item: {os.path.basename(item_path)}")
    print(f"Color: {outline_color_name} | Title: {title}")
    
    base_bg = build_background(title, width, height)
    
    raw_hero = Image.open(hero_path).convert("RGBA")
    raw_hero = trim_transparent_borders(raw_hero)
    h_aspect = raw_hero.width / raw_hero.height
    hero_w = 400 if h_aspect > 1.0 else int(400 * h_aspect)
    hero_h = int(400 / h_aspect) if h_aspect > 1.0 else 400
    hero_sprite = raw_hero.resize((hero_w, hero_h), Image.Resampling.LANCZOS)
    hero_outline = create_smooth_outline(hero_sprite, color_rgb=outline_color, thickness=8)
    
    raw_item = Image.open(item_path).convert("RGBA")
    raw_item = trim_transparent_borders(raw_item)
    i_aspect = raw_item.width / raw_item.height
    item_w = 180 if i_aspect > 1.0 else int(180 * i_aspect)
    item_h = int(180 / i_aspect) if i_aspect > 1.0 else 180
    item_sprite = raw_item.resize((item_w, item_h), Image.Resampling.LANCZOS)
    item_outline = create_smooth_outline(item_sprite, color_rgb=outline_color, thickness=7)
    
    hero_tx = (width - hero_w) // 2
    hero_ty = 360
    
    items_x = (width - item_w) // 2
    items_y_coords = [920, 1160, 1400]
    
    base_with_outlines = base_bg.copy()
    base_with_outlines.paste(hero_outline, (hero_tx, hero_ty), hero_outline)
    for iy in items_y_coords:
        base_with_outlines.paste(item_outline, (items_x, iy), item_outline)
        
    base_bgr = cv2.cvtColor(np.array(base_with_outlines.convert("RGB")), cv2.COLOR_RGB2BGR)
    
    h_bgr, h_alpha, hw, hh = prep_sprite(hero_sprite)
    i_bgr, i_alpha, iw, ih = prep_sprite(item_sprite)
    # GUARANTEED ALIGNMENT FORMULA:
    # All items pass through x = 0 at exact moments: t = t_win + k * 2.0s
    t_first_win = 2.35
    freqs = [0.75, 1.25, 1.75, 2.25]
    amps = [320, 290, 310, 280]
    directions = [1, -1, 1, -1] # Alternate crossing directions
    
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    video_out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    for f in range(total_frames):
        t = f / fps
        frame = base_bgr.copy()
        
        # Hero
        h_phase = 0.0 if directions[0] == 1 else math.pi
        h_offset = amps[0] * math.sin(2 * math.pi * freqs[0] * (t - t_first_win) + h_phase)
        hx = int(hero_tx + h_offset)
        fast_overlay(frame, h_bgr, h_alpha, hx, hero_ty, hw, hh)
        
        # 3 Sub-items
        for i, iy in enumerate(items_y_coords):
            idx = i + 1
            i_phase = 0.0 if directions[idx] == 1 else math.pi
            i_offset = amps[idx] * math.sin(2 * math.pi * freqs[idx] * (t - t_first_win) + i_phase)
            ix = int(items_x + i_offset)
            fast_overlay(frame, i_bgr, i_alpha, ix, iy, iw, ih)
            
        video_out.write(frame)
        
    video_out.release()
    print(f"Finished: {output_path} ({round(os.path.getsize(output_path)/(1024*1024), 2)} MB)")
    return output_path

def get_available_assets():
    png_files = glob.glob(os.path.join(ASSETS_DIR, "*.png"))
    # Filter out preview/test files
    valid = [f for f in png_files if not f.endswith("_test.png") and not f.endswith("_outline.png")]
    return valid

def main():
    parser = argparse.ArgumentParser(description="Automated Viral Puzzle Reel Generator")
    parser.add_argument("--count", type=int, default=1, help="Number of random reels to generate")
    parser.add_argument("--hero", type=str, default=None, help="Name of hero asset (e.g. parrot, duck, tree)")
    parser.add_argument("--item", type=str, default=None, help="Name of sub-item asset (e.g. tomato, egg)")
    parser.add_argument("--color", type=str, default=None, choices=list(OUTLINE_COLORS.keys()), help="Outline color")
    parser.add_argument("--duration", type=float, default=8.0, help="Duration in seconds (default: 8.0s)")
    parser.add_argument("--fps", type=int, default=60, help="Frame rate (default: 60)")
    args = parser.parse_args()
    
    assets = get_available_assets()
    if not assets:
        print("No assets found in assets/ folder. Run fetch_assets.py first.")
        return
        
    asset_map = {os.path.splitext(os.path.basename(p))[0]: p for p in assets}
    
    for i in range(args.count):
        if args.hero and args.hero in asset_map:
            hero_path = asset_map[args.hero]
        else:
            hero_path = random.choice(assets)
            
        if args.item and args.item in asset_map:
            item_path = asset_map[args.item]
        else:
            item_path = random.choice(assets)
            # Avoid same hero and item if possible
            if len(assets) > 1 and item_path == hero_path:
                other_assets = [a for a in assets if a != hero_path]
                item_path = random.choice(other_assets)
                
        h_name = os.path.splitext(os.path.basename(hero_path))[0]
        i_name = os.path.splitext(os.path.basename(item_path))[0]
        out_name = f"reel_{i+1:02d}_{h_name}_{i_name}.mp4"
        out_path = os.path.join(OUTPUT_DIR, out_name)
        
        generate_single_video(
            hero_path=hero_path,
            item_path=item_path,
            output_path=out_path,
            outline_color_name=args.color,
            duration=args.duration,
            fps=args.fps
        )

if __name__ == "__main__":
    main()
