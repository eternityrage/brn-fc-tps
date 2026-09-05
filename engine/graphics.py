import os
import math
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

def create_smooth_outline(rgba_img, color_rgb=(0, 110, 255), thickness=7):
    """Draws an anti-aliased outline around any transparent RGBA image."""
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

def smooth_playable_oscillation(t, t_win, freq, amp, direction=1):
    phase = 0.0 if direction == 1 else math.pi
    raw_sin = math.sin(2 * math.pi * freq * (t - t_win) + phase)
    shaped = math.copysign(abs(raw_sin) ** 0.85, raw_sin)
    return amp * shaped
