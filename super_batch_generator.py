import os
import sys
import math
import random
import argparse
import subprocess
import glob
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import scipy.io.wavfile as wavfile

# Ensure clean UTF-8 printing on Windows
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

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

HOOK_TITLES = {
    "swing": [
        "CAN YOU STOP IN THE SHADOW?",
        "TAP TO PAUSE PERFECTLY!",
        "99% FAIL TO PAUSE IN TIME!",
        "CAN YOU STOP ALL 4 AT ONCE?"
    ],
    "falling": [
        "CATCH THEM BEFORE THEY FALL!",
        "PAUSE WHEN THEY HIT THE HOOP!",
        "CAN YOU CATCH ALL 3 FALLING?",
        "STOP AT 100% PERFECT DROP!"
    ],
    "orbit": [
        "STOP THE ROTATING WHEEL!",
        "CAN YOU PAUSE THE CAROUSEL?",
        "LOCK ALL 4 IN THE CIRCLE!",
        "99% CANNOT TIME THE SPIN!"
    ],
    "zoom": [
        "PAUSE AT EXACT 100% SIZE!",
        "STOP WHEN IT FITS THE OUTLINE!",
        "CAN YOU CATCH THE EXACT SCALE?",
        "99% PAUSE TOO EARLY OR LATE!"
    ],
    "crossfire": [
        "STOP THE 4-WAY CROSSFIRE!",
        "PAUSE WHEN ALL 4 MEET!",
        "CAN YOU LOCK THE CROSSHAIR?",
        "99% FAIL TO TIME THE IMPACT!"
    ],
    "pyramid": [
        "99% FAIL THE PYRAMID CHALLENGE!",
        "CAN YOU ALIGN THE WHOLE PYRAMID?",
        "STOP WHEN ALL EGGS FORM A TRIANGLE!",
        "LOCK ALL 7 PIECES IN PLACE!"
    ]
}

# ----------------- ASSET & OUTLINE HELPERS -----------------

def create_smooth_outline(rgba_img, color_rgb=(0, 110, 255), thickness=7):
    img_np = np.array(rgba_img)
    h, w = img_np.shape[:2]
    alpha = img_np[:, :, 3]
    _, thresh = cv2.threshold(alpha, 35, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    
    outline_canvas = np.zeros((h, w, 4), dtype=np.uint8)
    rgba_color = (int(color_rgb[0]), int(color_rgb[1]), int(color_rgb[2]), 255)
    cv2.drawContours(outline_canvas, contours, -1, rgba_color, thickness=thickness, lineType=cv2.LINE_AA)
    return Image.fromarray(outline_canvas, mode="RGBA")

def trim_transparent(img):
    bbox = img.getbbox()
    return img.crop(bbox) if bbox else img

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

# ----------------- BACKGROUND BUILDER -----------------

def build_background(title_text, subtitle="Tap screen to pause & comment your screenshot!", width=1080, height=1920):
    cx, cy = width / 2, height * 0.46
    max_radius = math.hypot(width, height) / 1.5
    y, x = np.ogrid[:height, :width]
    dist = np.clip(np.hypot(x - cx, y - cy) / max_radius, 0.0, 1.0)
    
    c_center = np.array([255, 255, 255], dtype=np.float32)
    c_edge = np.array([225, 230, 238], dtype=np.float32)
    bg_np = (c_center * (1.0 - dist[:, :, None]) + c_edge * dist[:, :, None]).astype(np.uint8)
    
    bg_img = Image.fromarray(bg_np, mode="RGB").convert("RGBA")
    draw = ImageDraw.Draw(bg_img)
    
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
    c_bbox = draw.textbbox((0, 0), subtitle, font=sub_font)
    cw = c_bbox[2] - c_bbox[0]
    draw.rounded_rectangle([(width - cw) // 2 - 30, bot_y - 12, (width + cw) // 2 + 30, bot_y + 50],
                           radius=20, fill=(30, 41, 59, 230))
    draw.text(((width - cw) // 2, bot_y), subtitle, fill=(255, 255, 255), font=sub_font)
    return bg_img

# ----------------- AUDIO GENERATOR -----------------

def create_synchronized_audio(duration, win_moments, output_wav):
    sample_rate = 44100
    total_samples = int(duration * sample_rate)
    t = np.linspace(0, duration, total_samples, endpoint=False)
    
    # 1. Subtle low suspense drone
    drone = 0.10 * np.sin(2 * np.pi * 60 * t)
    
    # 2. Metronome Clock Tick every 0.5s
    tick_sound = np.zeros(total_samples, dtype=np.float32)
    tick_len = int(0.04 * sample_rate)
    t_tick = np.linspace(0, 0.04, tick_len, endpoint=False)
    click = (np.sin(2 * np.pi * 1800 * t_tick) * np.exp(-t_tick * 120) * 0.4 +
             np.sin(2 * np.pi * 900 * t_tick) * np.exp(-t_tick * 80) * 0.25)
    
    for tick_time in np.arange(0.0, duration, 0.5):
        idx = int(tick_time * sample_rate)
        end_idx = min(idx + tick_len, total_samples)
        tick_sound[idx:end_idx] += click[:end_idx - idx]
        
    # 3. Alignment Chime on winning moments
    chime_sound = np.zeros(total_samples, dtype=np.float32)
    chime_len = int(0.35 * sample_rate)
    t_chime = np.linspace(0, 0.35, chime_len, endpoint=False)
    bell = (np.sin(2 * np.pi * 1046.5 * t_chime) + 0.5 * np.sin(2 * np.pi * 2093 * t_chime)) * np.exp(-t_chime * 10) * 0.4
    
    for w_time in win_moments:
        if w_time < duration:
            idx = int(w_time * sample_rate)
            end_idx = min(idx + chime_len, total_samples)
            chime_sound[idx:end_idx] += bell[:end_idx - idx]
            
    mix = drone + tick_sound + chime_sound
    mix = mix / (np.max(np.abs(mix)) + 1e-5) * 0.85
    audio_int16 = (mix * 32767).astype(np.int16)
    stereo = np.column_stack((audio_int16, audio_int16))
    wavfile.write(output_wav, sample_rate, stereo)

# ----------------- EASING & VELOCITY PROFILE -----------------

def smooth_playable_oscillation(t, t_win, freq, amp, direction=1):
    """
    Playable oscillation with gentle sweet-spot easing:
    Slows down pleasantly around the middle so human reaction time can catch it!
    """
    phase = 0.0 if direction == 1 else math.pi
    raw_sin = math.sin(2 * math.pi * freq * (t - t_win) + phase)
    # Applying a soft cubic shaping softens the velocity peak at center
    # while keeping exact zero crossing at t = t_win!
    shaped = math.copysign(abs(raw_sin) ** 0.85, raw_sin)
    return amp * shaped

# ----------------- VARIATION 1: SWING MODE -----------------

def render_swing_mode(hero_path, item_path, temp_video, duration, fps, outline_color, title):
    width, height = 1080, 1920
    total_frames = int(duration * fps)
    base_bg = build_background(title, width=width, height=height)
    
    # Load & prep Hero (top)
    raw_hero = trim_transparent(Image.open(hero_path).convert("RGBA"))
    h_aspect = raw_hero.width / raw_hero.height
    hw = 380 if h_aspect > 1.0 else int(380 * h_aspect)
    hh = int(380 / h_aspect) if h_aspect > 1.0 else 380
    hero_sprite = raw_hero.resize((hw, hh), Image.Resampling.LANCZOS)
    hero_outline = create_smooth_outline(hero_sprite, color_rgb=outline_color, thickness=8)
    
    # Load & prep Item (bottom column of 3)
    raw_item = trim_transparent(Image.open(item_path).convert("RGBA"))
    i_aspect = raw_item.width / raw_item.height
    iw = 180 if i_aspect > 1.0 else int(180 * i_aspect)
    ih = int(180 / i_aspect) if i_aspect > 1.0 else 180
    item_sprite = raw_item.resize((iw, ih), Image.Resampling.LANCZOS)
    item_outline = create_smooth_outline(item_sprite, color_rgb=outline_color, thickness=7)
    
    hero_tx = (width - hw) // 2
    hero_ty = 360
    items_x = (width - iw) // 2
    items_y = [920, 1160, 1400]
    
    # Stamp Outlines
    base_with_outlines = base_bg.copy()
    base_with_outlines.paste(hero_outline, (hero_tx, hero_ty), hero_outline)
    for iy in items_y:
        base_with_outlines.paste(item_outline, (items_x, iy), item_outline)
    base_bgr = cv2.cvtColor(np.array(base_with_outlines.convert("RGB")), cv2.COLOR_RGB2BGR)
    
    h_bgr, h_alpha, _, _ = prep_sprite(hero_sprite)
    i_bgr, i_alpha, _, _ = prep_sprite(item_sprite)
    
    # Gentler, playable frequencies (approx 0.5 to 0.9 Hz)
    # Alignment occurs cleanly every 2.0s: t = 2.4s, 4.4s, 6.4s
    t_win = 2.4
    freqs = [0.50, 0.75, 1.00, 0.75]
    amps = [280, 260, 270, 250]
    dirs = [1, -1, 1, -1]
    
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(temp_video, fourcc, fps, (width, height))
    
    for f in range(total_frames):
        t = f / fps
        frame = base_bgr.copy()
        
        # Hero
        h_off = smooth_playable_oscillation(t, t_win, freqs[0], amps[0], dirs[0])
        fast_overlay(frame, h_bgr, h_alpha, int(hero_tx + h_off), hero_ty, hw, hh)
        
        # 3 Sub-items
        for idx, iy in enumerate(items_y):
            i_off = smooth_playable_oscillation(t, t_win, freqs[idx + 1], amps[idx + 1], dirs[idx + 1])
            fast_overlay(frame, i_bgr, i_alpha, int(items_x + i_off), iy, iw, ih)
            
        out.write(frame)
    out.release()
    return [2.4, 4.4, 6.4]

# ----------------- VARIATION 2: FALLING / DROP MODE -----------------

def render_falling_mode(hero_path, item_path, temp_video, duration, fps, outline_color, title):
    """
    Items drop continuously from top to bottom, passing through target hoop outlines!
    """
    width, height = 1080, 1920
    total_frames = int(duration * fps)
    base_bg = build_background(title, subtitle="Catch all 3 items falling into the rings! 👇", width=width, height=height)
    
    # Top Hero
    raw_hero = trim_transparent(Image.open(hero_path).convert("RGBA"))
    h_aspect = raw_hero.width / raw_hero.height
    hw = 360 if h_aspect > 1.0 else int(360 * h_aspect)
    hh = int(360 / h_aspect) if h_aspect > 1.0 else 360
    hero_sprite = raw_hero.resize((hw, hh), Image.Resampling.LANCZOS)
    hero_outline = create_smooth_outline(hero_sprite, color_rgb=outline_color, thickness=8)
    
    # 3 Falling Items
    raw_item = trim_transparent(Image.open(item_path).convert("RGBA"))
    i_aspect = raw_item.width / raw_item.height
    iw = 190 if i_aspect > 1.0 else int(190 * i_aspect)
    ih = int(190 / i_aspect) if i_aspect > 1.0 else 190
    item_sprite = raw_item.resize((iw, ih), Image.Resampling.LANCZOS)
    item_outline = create_smooth_outline(item_sprite, color_rgb=outline_color, thickness=7)
    
    hero_tx = (width - hw) // 2
    hero_ty = 350
    
    # 3 target outline rings horizontally at bottom
    target_y = 1250
    lane_x = [180, (width - iw) // 2, width - 180 - iw]
    
    base_with_outlines = base_bg.copy()
    base_with_outlines.paste(hero_outline, (hero_tx, hero_ty), hero_outline)
    for lx in lane_x:
        base_with_outlines.paste(item_outline, (lx, target_y), item_outline)
    base_bgr = cv2.cvtColor(np.array(base_with_outlines.convert("RGB")), cv2.COLOR_RGB2BGR)
    
    h_bgr, h_alpha, _, _ = prep_sprite(hero_sprite)
    i_bgr, i_alpha, _, _ = prep_sprite(item_sprite)
    
    # Hero gently floats left-right, aligning at t_win = 2.5s and 5.5s
    t_win = 2.5
    cycle_duration = 3.0 # Every 3 seconds items loop down
    drop_speed = 500 # px/sec
    
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(temp_video, fourcc, fps, (width, height))
    
    for f in range(total_frames):
        t = f / fps
        frame = base_bgr.copy()
        
        # Hero floats left-right and hits center at t_win
        h_off = 180 * math.sin(2 * math.pi * (1.0 / cycle_duration) * (t - t_win))
        fast_overlay(frame, h_bgr, h_alpha, int(hero_tx + h_off), hero_ty, hw, hh)
        
        # 3 items drop down from top (Y = 600 to 1800)
        # At t = t_win, y_offset is exactly 0 -> item is at target_y
        for idx, lx in enumerate(lane_x):
            # Stagger starting positions slightly so they travel with visual rhythm
            # but all cross target_y at t = t_win + k*cycle_duration!
            delta_t = (t - t_win) % cycle_duration
            if delta_t > cycle_duration / 2:
                delta_t -= cycle_duration
            cur_y = int(target_y + drop_speed * delta_t)
            fast_overlay(frame, i_bgr, i_alpha, lx, cur_y, iw, ih)
            
        out.write(frame)
    out.release()
    return [2.5, 5.5]

# ----------------- VARIATION 3: ORBIT / CAROUSEL MODE -----------------

def render_orbit_mode(hero_path, item_path, temp_video, duration, fps, outline_color, title):
    """
    Items rotate around a circle; pause when they click into the outline targets!
    """
    width, height = 1080, 1920
    total_frames = int(duration * fps)
    base_bg = build_background(title, subtitle="Pause when all 4 lock into the circle! 👇", width=width, height=height)
    
    # Center Hero
    raw_hero = trim_transparent(Image.open(hero_path).convert("RGBA"))
    h_aspect = raw_hero.width / raw_hero.height
    hw = 280 if h_aspect > 1.0 else int(280 * h_aspect)
    hh = int(280 / h_aspect) if h_aspect > 1.0 else 280
    hero_sprite = raw_hero.resize((hw, hh), Image.Resampling.LANCZOS)
    
    # 4 Orbiting Items
    raw_item = trim_transparent(Image.open(item_path).convert("RGBA"))
    i_aspect = raw_item.width / raw_item.height
    iw = 170 if i_aspect > 1.0 else int(170 * i_aspect)
    ih = int(170 / i_aspect) if i_aspect > 1.0 else 170
    item_sprite = raw_item.resize((iw, ih), Image.Resampling.LANCZOS)
    item_outline = create_smooth_outline(item_sprite, color_rgb=outline_color, thickness=7)
    
    center_x, center_y = width // 2, 1020
    orbit_radius = 350
    
    # 4 target positions at 0, 90, 180, 270 degrees
    base_with_outlines = base_bg.copy()
    for angle_deg in [0, 90, 180, 270]:
        rad = math.radians(angle_deg)
        tx = int(center_x + orbit_radius * math.cos(rad) - iw / 2)
        ty = int(center_y + orbit_radius * math.sin(rad) - ih / 2)
        base_with_outlines.paste(item_outline, (tx, ty), item_outline)
        
    base_bgr = cv2.cvtColor(np.array(base_with_outlines.convert("RGB")), cv2.COLOR_RGB2BGR)
    
    h_bgr, h_alpha, _, _ = prep_sprite(hero_sprite)
    i_bgr, i_alpha, _, _ = prep_sprite(item_sprite)
    
    # Static Hero in center
    hero_cx = center_x - hw // 2
    hero_cy = center_y - hh // 2
    
    # Rotation speed: 1 full rotation every 3.0s (120 deg/sec)
    # Aligns at t_win = 2.4s, 5.4s
    t_win = 2.4
    rot_speed_deg = 360.0 / 3.0 # 120 deg/sec
    
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(temp_video, fourcc, fps, (width, height))
    
    for f in range(total_frames):
        t = f / fps
        frame = base_bgr.copy()
        
        # Center Hero
        fast_overlay(frame, h_bgr, h_alpha, hero_cx, hero_cy, hw, hh)
        
        # 4 rotating items
        base_angle = (t - t_win) * rot_speed_deg
        for i_idx, base_deg in enumerate([0, 90, 180, 270]):
            cur_deg = base_deg + base_angle
            rad = math.radians(cur_deg)
            ix = int(center_x + orbit_radius * math.cos(rad) - iw / 2)
            iy = int(center_y + orbit_radius * math.sin(rad) - ih / 2)
            fast_overlay(frame, i_bgr, i_alpha, ix, iy, iw, ih)
            
        out.write(frame)
    out.release()
    return [2.4, 5.4]

# ----------------- VARIATION 4: ZOOM / SCALE MATCH MODE -----------------

def render_zoom_mode(hero_path, item_path, temp_video, duration, fps, outline_color, title):
    width, height = 1080, 1920
    total_frames = int(duration * fps)
    base_bg = build_background(title, subtitle="Pause when the size fits 100% into the shadow! 👇", width=width, height=height)
    
    raw_hero = trim_transparent(Image.open(hero_path).convert("RGBA"))
    h_aspect = raw_hero.width / raw_hero.height
    base_w = 420 if h_aspect > 1.0 else int(420 * h_aspect)
    base_h = int(420 / h_aspect) if h_aspect > 1.0 else 420
    hero_base = raw_hero.resize((base_w, base_h), Image.Resampling.LANCZOS)
    hero_outline = create_smooth_outline(hero_base, color_rgb=outline_color, thickness=8)
    
    # 2 Sub-items below
    raw_item = trim_transparent(Image.open(item_path).convert("RGBA"))
    i_aspect = raw_item.width / raw_item.height
    iw = 180 if i_aspect > 1.0 else int(180 * i_aspect)
    ih = int(180 / i_aspect) if i_aspect > 1.0 else 180
    item_sprite = raw_item.resize((iw, ih), Image.Resampling.LANCZOS)
    item_outline = create_smooth_outline(item_sprite, color_rgb=outline_color, thickness=7)
    
    hero_center_x, hero_center_y = width // 2, 540
    hero_tx = hero_center_x - base_w // 2
    hero_ty = hero_center_y - base_h // 2
    
    sub_y = [1120, 1380]
    sub_x = (width - iw) // 2
    
    base_with_outlines = base_bg.copy()
    base_with_outlines.paste(hero_outline, (hero_tx, hero_ty), hero_outline)
    for sy in sub_y:
        base_with_outlines.paste(item_outline, (sub_x, sy), item_outline)
    base_bgr = cv2.cvtColor(np.array(base_with_outlines.convert("RGB")), cv2.COLOR_RGB2BGR)
    
    h_bgr_orig, h_alpha_orig, _, _ = prep_sprite(hero_base)
    i_bgr, i_alpha, _, _ = prep_sprite(item_sprite)
    
    t_win = 2.4
    zoom_freq = 0.55 # pulses every ~1.8s
    
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(temp_video, fourcc, fps, (width, height))
    
    for f in range(total_frames):
        t = f / fps
        frame = base_bgr.copy()
        
        # Scale pulses between 0.45x and 1.55x, hitting exactly 1.000 at t_win!
        scale_factor = 1.0 + 0.50 * math.sin(2 * math.pi * zoom_freq * (t - t_win))
        cur_w = max(10, int(base_w * scale_factor))
        cur_h = max(10, int(base_h * scale_factor))
        
        h_resized_bgr = cv2.resize(h_bgr_orig, (cur_w, cur_h), interpolation=cv2.INTER_LINEAR)
        h_resized_alpha = cv2.resize(h_alpha_orig, (cur_w, cur_h), interpolation=cv2.INTER_LINEAR)
        
        cur_hx = hero_center_x - cur_w // 2
        cur_hy = hero_center_y - cur_h // 2
        fast_overlay(frame, h_resized_bgr, h_resized_alpha, cur_hx, cur_hy, cur_w, cur_h)
        
        # 2 Sub items swing across their targets
        for idx, sy in enumerate(sub_y):
            s_off = smooth_playable_oscillation(t, t_win, 0.75 + idx*0.25, 260, 1 if idx==0 else -1)
            fast_overlay(frame, i_bgr, i_alpha, int(sub_x + s_off), sy, iw, ih)
            
        out.write(frame)
    out.release()
    return [2.4, 5.4]

# ----------------- VARIATION 5: CROSSFIRE MODE -----------------

def render_crossfire_mode(hero_path, item_path, temp_video, duration, fps, outline_color, title):
    width, height = 1080, 1920
    total_frames = int(duration * fps)
    base_bg = build_background(title, subtitle="Stop when all 4 cross into the targets! 👇", width=width, height=height)
    
    # Center Hero
    raw_hero = trim_transparent(Image.open(hero_path).convert("RGBA"))
    h_aspect = raw_hero.width / raw_hero.height
    hw = 260 if h_aspect > 1.0 else int(260 * h_aspect)
    hh = int(260 / h_aspect) if h_aspect > 1.0 else 260
    hero_sprite = raw_hero.resize((hw, hh), Image.Resampling.LANCZOS)
    hero_outline = create_smooth_outline(hero_sprite, color_rgb=outline_color, thickness=7)
    
    # 4 Converging Items
    raw_item = trim_transparent(Image.open(item_path).convert("RGBA"))
    i_aspect = raw_item.width / raw_item.height
    iw = 160 if i_aspect > 1.0 else int(160 * i_aspect)
    ih = int(160 / i_aspect) if i_aspect > 1.0 else 160
    item_sprite = raw_item.resize((iw, ih), Image.Resampling.LANCZOS)
    item_outline = create_smooth_outline(item_sprite, color_rgb=outline_color, thickness=7)
    
    cx, cy = width // 2, 1020
    # 4 Targets placed symmetrically around center
    offset_dist = 220
    targets = [
        (cx, cy - offset_dist), # Top
        (cx, cy + offset_dist), # Bottom
        (cx - offset_dist, cy), # Left
        (cx + offset_dist, cy)  # Right
    ]
    
    base_with_outlines = base_bg.copy()
    base_with_outlines.paste(hero_outline, (cx - hw // 2, cy - hh // 2), hero_outline)
    for tx, ty in targets:
        base_with_outlines.paste(item_outline, (tx - iw // 2, ty - ih // 2), item_outline)
    base_bgr = cv2.cvtColor(np.array(base_with_outlines.convert("RGB")), cv2.COLOR_RGB2BGR)
    
    h_bgr, h_alpha, _, _ = prep_sprite(hero_sprite)
    i_bgr, i_alpha, _, _ = prep_sprite(item_sprite)
    
    t_win = 2.4
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(temp_video, fourcc, fps, (width, height))
    
    for f in range(total_frames):
        t = f / fps
        frame = base_bgr.copy()
        
        # Static Hero in center
        fast_overlay(frame, h_bgr, h_alpha, cx - hw // 2, cy - hh // 2, hw, hh)
        
        # 4 items oscillate in from 4 directions
        # Top & Bottom move vertically; Left & Right move horizontally
        v_off1 = smooth_playable_oscillation(t, t_win, 0.75, 260, 1)
        v_off2 = smooth_playable_oscillation(t, t_win, 0.75, 260, -1)
        h_off1 = smooth_playable_oscillation(t, t_win, 0.75, 260, 1)
        h_off2 = smooth_playable_oscillation(t, t_win, 0.75, 260, -1)
        
        # Top item
        fast_overlay(frame, i_bgr, i_alpha, targets[0][0] - iw // 2, int(targets[0][1] + v_off1 - ih // 2), iw, ih)
        # Bottom item
        fast_overlay(frame, i_bgr, i_alpha, targets[1][0] - iw // 2, int(targets[1][1] + v_off2 - ih // 2), iw, ih)
        # Left item
        fast_overlay(frame, i_bgr, i_alpha, int(targets[2][0] + h_off1 - iw // 2), targets[2][1] - ih // 2, iw, ih)
        # Right item
        fast_overlay(frame, i_bgr, i_alpha, int(targets[3][0] + h_off2 - iw // 2), targets[3][1] - ih // 2, iw, ih)
        
        out.write(frame)
    out.release()
    return [2.4, 5.4]

# ----------------- VARIATION 6: PYRAMID WAVE MODE -----------------

def render_pyramid_mode(hero_path, item_path, temp_video, duration, fps, outline_color, title):
    """
    Directly mirrors the viral Pigeon + Pyramid of Eggs layout from the user screenshots!
    """
    width, height = 1080, 1920
    total_frames = int(duration * fps)
    base_bg = build_background(title, subtitle="Stop when all 7 pieces lock into the pyramid! 👇", width=width, height=height)
    
    # Hero on top
    raw_hero = trim_transparent(Image.open(hero_path).convert("RGBA"))
    h_aspect = raw_hero.width / raw_hero.height
    hw = 360 if h_aspect > 1.0 else int(360 * h_aspect)
    hh = int(360 / h_aspect) if h_aspect > 1.0 else 360
    hero_sprite = raw_hero.resize((hw, hh), Image.Resampling.LANCZOS)
    hero_outline = create_smooth_outline(hero_sprite, color_rgb=outline_color, thickness=8)
    
    # 6 Pyramid items
    raw_item = trim_transparent(Image.open(item_path).convert("RGBA"))
    i_aspect = raw_item.width / raw_item.height
    iw = 150 if i_aspect > 1.0 else int(150 * i_aspect)
    ih = int(150 / i_aspect) if i_aspect > 1.0 else 150
    item_sprite = raw_item.resize((iw, ih), Image.Resampling.LANCZOS)
    item_outline = create_smooth_outline(item_sprite, color_rgb=outline_color, thickness=7)
    
    cx = width // 2
    hero_tx = cx - hw // 2
    hero_ty = 350
    
    # 3 Pyramid Tiers:
    # Tier 1: 1 item at y=880
    # Tier 2: 2 items at y=1100
    # Tier 3: 3 items at y=1320
    pyramid_rows = [
        [(cx, 880)],                                     # Row 1 (1 item)
        [(cx - 110, 1100), (cx + 110, 1100)],            # Row 2 (2 items)
        [(cx - 220, 1320), (cx, 1320), (cx + 220, 1320)] # Row 3 (3 items)
    ]
    
    base_with_outlines = base_bg.copy()
    base_with_outlines.paste(hero_outline, (hero_tx, hero_ty), hero_outline)
    for row in pyramid_rows:
        for px, py in row:
            base_with_outlines.paste(item_outline, (px - iw // 2, py - ih // 2), item_outline)
    base_bgr = cv2.cvtColor(np.array(base_with_outlines.convert("RGB")), cv2.COLOR_RGB2BGR)
    
    h_bgr, h_alpha, _, _ = prep_sprite(hero_sprite)
    i_bgr, i_alpha, _, _ = prep_sprite(item_sprite)
    
    t_win = 2.4
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(temp_video, fourcc, fps, (width, height))
    
    for f in range(total_frames):
        t = f / fps
        frame = base_bgr.copy()
        
        # Hero moves horizontally
        h_off = smooth_playable_oscillation(t, t_win, 0.55, 270, 1)
        fast_overlay(frame, h_bgr, h_alpha, int(hero_tx + h_off), hero_ty, hw, hh)
        
        # Tier 1 (1 item)
        off_r1 = smooth_playable_oscillation(t, t_win, 0.75, 260, -1)
        fast_overlay(frame, i_bgr, i_alpha, int(pyramid_rows[0][0][0] - iw // 2 + off_r1), pyramid_rows[0][0][1] - ih // 2, iw, ih)
        
        # Tier 2 (2 items)
        off_r2 = smooth_playable_oscillation(t, t_win, 0.90, 250, 1)
        for px, py in pyramid_rows[1]:
            fast_overlay(frame, i_bgr, i_alpha, int(px - iw // 2 + off_r2), py - ih // 2, iw, ih)
            
        # Tier 3 (3 items)
        off_r3 = smooth_playable_oscillation(t, t_win, 0.65, 240, -1)
        for px, py in pyramid_rows[2]:
            fast_overlay(frame, i_bgr, i_alpha, int(px - iw // 2 + off_r3), py - ih // 2, iw, ih)
            
        out.write(frame)
    out.release()
    return [2.4, 5.4]

# ----------------- MAIN PIPELINE (VIDEO + AUDIO MUX) -----------------

def generate_viral_reel(
    hero_name,
    item_name,
    output_filename,
    mode="swing",
    outline_color_name=None,
    title=None,
    duration=8.0,
    fps=60
):
    hero_path = os.path.join(ASSETS_DIR, f"{hero_name}.png")
    item_path = os.path.join(ASSETS_DIR, f"{item_name}.png")
    
    if not os.path.exists(hero_path) or not os.path.exists(item_path):
        print(f"Error: Asset missing: {hero_name} or {item_name}")
        return None
        
    if not outline_color_name or outline_color_name not in OUTLINE_COLORS:
        outline_color_name = random.choice(list(OUTLINE_COLORS.keys()))
    outline_color = OUTLINE_COLORS[outline_color_name]
    
    if not title:
        title = random.choice(HOOK_TITLES.get(mode, HOOK_TITLES["swing"]))
        
    final_output = os.path.join(OUTPUT_DIR, output_filename)
    temp_video = os.path.join(OUTPUT_DIR, f"temp_{output_filename}")
    temp_audio = os.path.join(OUTPUT_DIR, f"temp_audio_{output_filename}.wav")
    
    print(f"\n[+] Rendering [{mode.upper()}] Reel: {output_filename}")
    print(f"Hero: {hero_name} | Items: {item_name} | Color: {outline_color_name}")
    print(f"Title: {title}")
    
    # Render Video based on mode (6 unique modes)
    if mode == "falling":
        win_moments = render_falling_mode(hero_path, item_path, temp_video, duration, fps, outline_color, title)
    elif mode == "orbit":
        win_moments = render_orbit_mode(hero_path, item_path, temp_video, duration, fps, outline_color, title)
    elif mode == "zoom":
        win_moments = render_zoom_mode(hero_path, item_path, temp_video, duration, fps, outline_color, title)
    elif mode == "crossfire":
        win_moments = render_crossfire_mode(hero_path, item_path, temp_video, duration, fps, outline_color, title)
    elif mode == "pyramid":
        win_moments = render_pyramid_mode(hero_path, item_path, temp_video, duration, fps, outline_color, title)
    else: # default swing
        win_moments = render_swing_mode(hero_path, item_path, temp_video, duration, fps, outline_color, title)
        
    # 2. Synthesize Synchronized Audio
    print(f"Synthesizing synchronized sound track...")
    create_synchronized_audio(duration, win_moments, temp_audio)
    
    # 3. Mux Video + Audio with FFmpeg
    print(f"Muxing final video with audio using FFmpeg...")
    cmd = [
        "ffmpeg", "-y",
        "-i", temp_video,
        "-i", temp_audio,
        "-c:v", "copy",
        "-c:a", "aac",
        "-shortest",
        final_output
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Clean up temp files
    if os.path.exists(temp_video):
        os.remove(temp_video)
    if os.path.exists(temp_audio):
        os.remove(temp_audio)
        
    print(f"[SUCCESS] Generated final reel with sound: {final_output} ({round(os.path.getsize(final_output)/(1024*1024), 2)} MB)")
    return final_output

def get_clean_assets():
    pngs = glob.glob(os.path.join(ASSETS_DIR, "*.png"))
    clean = []
    for p in pngs:
        base = os.path.splitext(os.path.basename(p))[0]
        if not base.endswith("_test") and not base.endswith("_outline"):
            clean.append(base)
    return clean

def main():
    parser = argparse.ArgumentParser(description="Multi-Variation Viral Puzzle Reel Generator")
    parser.add_argument("--count", type=int, default=3, help="Number of reels to generate")
    parser.add_argument("--mode", type=str, default="all", choices=["all", "swing", "falling", "orbit", "zoom", "crossfire", "pyramid"], help="Motion style")
    parser.add_argument("--hero", type=str, default=None, help="Hero asset name")
    parser.add_argument("--item", type=str, default=None, help="Sub-item asset name")
    parser.add_argument("--color", type=str, default=None, help="Outline color")
    parser.add_argument("--duration", type=float, default=8.0, help="Duration in seconds")
    args = parser.parse_args()
    
    available = get_clean_assets()
    if len(available) < 2:
        print("Need at least 2 assets in assets/ folder. Run download_mega_pack.py first.")
        return
        
    # Categorize items into heroes (animals/vehicles/birds) and items (fruits/foods/gems)
    heroes_pool = [a for a in available if a in [
        "lion", "tiger", "bear", "panda", "koala", "monkey", "fox", "wolf", "rabbit",
        "deer", "horse", "zebra", "giraffe", "elephant", "dog", "cat", "frog", "turtle",
        "parrot", "duck", "flamingo", "rooster", "eagle", "owl", "swan", "penguin", "peacock",
        "motorcycle", "bicycle", "automobile", "airplane", "rocket"
    ]]
    items_pool = [a for a in available if a in [
        "tomato", "egg", "apple", "banana", "strawberry", "watermelon", "grapes", "peach",
        "cherries", "lemon", "orange", "pineapple", "avocado", "carrot", "gem", "trophy"
    ]]
    
    if not heroes_pool:
        heroes_pool = available
    if not items_pool:
        items_pool = available
        
    modes = ["swing", "falling", "orbit", "zoom", "crossfire", "pyramid"] if args.mode == "all" else [args.mode]
    
    for i in range(args.count):
        chosen_mode = modes[i % len(modes)]
        hero = args.hero if args.hero else random.choice(heroes_pool)
        item = args.item if args.item else random.choice(items_pool)
        while item == hero and len(items_pool) > 1:
            item = random.choice(items_pool)
            
        fname = f"viral_{chosen_mode}_{i+1:02d}_{hero}_{item}.mp4"
        generate_viral_reel(
            hero_name=hero,
            item_name=item,
            output_filename=fname,
            mode=chosen_mode,
            outline_color_name=args.color,
            duration=args.duration
        )

if __name__ == "__main__":
    main()
