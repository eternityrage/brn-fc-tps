import os
import math
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

def create_smooth_outline(rgba_img, color_rgb=(0, 110, 255), thickness=8):
    """Generates smooth anti-aliased outline from an RGBA PIL image."""
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

def build_background(title_text="CAN YOU STOP IN THE SHADOW?", width=1080, height=1920):
    cx, cy = width / 2, height * 0.46
    max_radius = math.hypot(width, height) / 1.5
    y, x = np.ogrid[:height, :width]
    dist = np.clip(np.hypot(x - cx, y - cy) / max_radius, 0.0, 1.0)
    
    c_center = np.array([255, 255, 255], dtype=np.float32)
    c_edge = np.array([225, 230, 238], dtype=np.float32)
    bg_np = (c_center * (1.0 - dist[:, :, None]) + c_edge * dist[:, :, None]).astype(np.uint8)
    
    bg_img = Image.fromarray(bg_np, mode="RGB").convert("RGBA")
    draw = ImageDraw.Draw(bg_img)
    
    # Target arena watermark rings
    icx, icy = int(cx), int(cy)
    draw.ellipse([icx - 440, icy - 440, icx + 440, icy + 440], outline=(180, 195, 215, 60), width=4)
    draw.ellipse([icx - 410, icy - 410, icx + 410, icy + 410], fill=(235, 242, 252, 50), outline=(180, 195, 215, 70), width=2)
    
    try:
        title_font = ImageFont.truetype("arialbd.ttf", 44)
        badge_font = ImageFont.truetype("arialbd.ttf", 30)
        sub_font = ImageFont.truetype("arial.ttf", 32)
    except:
        title_font = badge_font = sub_font = ImageFont.load_default()
        
    # Top banner
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
    
    # Bottom text
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

def render_puzzle_reel(
    hero_img_path,
    item_img_path,
    output_mp4_path,
    duration=8.0,
    fps=60,
    t_first_win=2.35, # Exact moment in seconds when all 4 hit dead center
    hero_outline_color=(0, 110, 255),
    items_outline_color=(0, 110, 255)
):
    width, height = 1080, 1920
    total_frames = int(duration * fps)
    
    print(f"Preparing base background...")
    base_bg = build_background(width=width, height=height)
    
    # 1. Prepare Hero Object
    raw_hero = Image.open(hero_img_path).convert("RGBA")
    raw_hero = trim_transparent_borders(raw_hero)
    hero_target_size = 400
    h_aspect = raw_hero.width / raw_hero.height
    if h_aspect > 1.0:
        hero_w = hero_target_size
        hero_h = int(hero_w / h_aspect)
    else:
        hero_h = hero_target_size
        hero_w = int(hero_h * h_aspect)
    hero_sprite = raw_hero.resize((hero_w, hero_h), Image.Resampling.LANCZOS)
    hero_outline = create_smooth_outline(hero_sprite, color_rgb=hero_outline_color, thickness=8)
    
    # 2. Prepare 3 Stacked Sub-Items
    raw_item = Image.open(item_img_path).convert("RGBA")
    raw_item = trim_transparent_borders(raw_item)
    item_size = 180
    i_aspect = raw_item.width / raw_item.height
    if i_aspect > 1.0:
        item_w = item_size
        item_h = int(item_w / i_aspect)
    else:
        item_h = item_size
        item_w = int(item_h * i_aspect)
    item_sprite = raw_item.resize((item_w, item_h), Image.Resampling.LANCZOS)
    item_outline = create_smooth_outline(item_sprite, color_rgb=items_outline_color, thickness=7)
    
    # Target Center Coordinates (The Shadows)
    hero_target_x = (width - hero_w) // 2
    hero_target_y = 360
    
    items_x = (width - item_w) // 2
    items_y_coords = [920, 1160, 1400]
    
    # Pre-stamp Static Outlines onto base background
    base_with_outlines = base_bg.copy()
    base_with_outlines.paste(hero_outline, (hero_target_x, hero_target_y), hero_outline)
    for iy in items_y_coords:
        base_with_outlines.paste(item_outline, (items_x, iy), item_outline)
        
    base_bgr = cv2.cvtColor(np.array(base_with_outlines.convert("RGB")), cv2.COLOR_RGB2BGR)
    
    hero_bgr, hero_alpha, hw, hh = prep_sprite(hero_sprite)
    item_bgr, item_alpha, iw, ih = prep_sprite(item_sprite)
    
    # MATHEMATICAL HARMONIC ALIGNMENT FORMULA:
    # All items are designed to pass through x = 0 at exact moments:
    # t = t_first_win + k * 2.0s (e.g. 2.35s, 4.35s, 6.35s)
    # At all other times, they are moving at different frequencies and opposite directions!
    freqs = [0.75, 1.25, 1.75, 2.25]
    amps = [320, 290, 310, 280]
    directions = [1, -1, 1, -1] # Alternate left/right crossings
    
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    video_out = cv2.VideoWriter(output_mp4_path, fourcc, fps, (width, height))
    
    print(f"Rendering {total_frames} frames ({duration}s @ {fps}fps) to {output_mp4_path}...")
    print(f"Guaranteed alignment moments occur at t = {t_first_win}s, {t_first_win+2.0}s, {t_first_win+4.0}s")
    
    for frame_idx in range(total_frames):
        t = frame_idx / fps
        frame = base_bgr.copy()
        
        # 1. Hero Position
        h_phase = 0.0 if directions[0] == 1 else math.pi
        h_offset = amps[0] * math.sin(2 * math.pi * freqs[0] * (t - t_first_win) + h_phase)
        hx = int(hero_target_x + h_offset)
        fast_overlay(frame, hero_bgr, hero_alpha, hx, hero_target_y, hw, hh)
        
        # 2. Three Sub-Items Position
        for i, iy in enumerate(items_y_coords):
            idx = i + 1
            i_phase = 0.0 if directions[idx] == 1 else math.pi
            i_offset = amps[idx] * math.sin(2 * math.pi * freqs[idx] * (t - t_first_win) + i_phase)
            ix = int(items_x + i_offset)
            fast_overlay(frame, item_bgr, item_alpha, ix, iy, iw, ih)
            
        video_out.write(frame)
        
    video_out.release()
    print(f"Successfully rendered: {output_mp4_path}")
    return output_mp4_path

if __name__ == "__main__":
    assets_dir = "C:/Users/kreg9/viral_puzzle_reels/assets"
    out_dir = "C:/Users/kreg9/viral_puzzle_reels/output"
    os.makedirs(out_dir, exist_ok=True)
    
    hero_file = os.path.join(assets_dir, "parrot.png")
    item_file = os.path.join(assets_dir, "tomato.png")
    output_file = os.path.join(out_dir, "viral_shadow_puzzle_reel.mp4")
    
    render_puzzle_reel(
        hero_img_path=hero_file,
        item_img_path=item_file,
        output_mp4_path=output_file,
        duration=8.0,
        fps=60,
        t_first_win=2.35 # Frame 141 is the exact alignment frame!
    )
