import os
import math
import cv2
import numpy as np
import pathlib
from PIL import Image, ImageDraw, ImageFont

# Path to bundled high-contrast bold font
BASE_DIR = pathlib.Path(__file__).parent.parent
BUNDLED_FONT_PATH = BASE_DIR / "assets" / "fonts" / "font_bold.ttf"


def get_bold_font(size):
    """Loads bundled bold TrueType font with cross-platform fallbacks."""
    # 1. Bundled repo font
    if BUNDLED_FONT_PATH.exists():
        try:
            return ImageFont.truetype(str(BUNDLED_FONT_PATH), size)
        except Exception:
            pass

    # 2. Linux system paths
    linux_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
    ]
    for p in linux_paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass

    # 3. Windows system paths
    win_paths = [
        r"C:\Windows\Fonts\arialbd.ttf",
        r"C:\Windows\Fonts\segoeuib.ttf",
        r"C:\Windows\Fonts\impact.ttf"
    ]
    for p in win_paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass

    return ImageFont.load_default()


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


def build_background(title_text="CAN YOU STOP IN THE SHADOW?", subtitle="TAP SCREEN TO PAUSE IN TIME!", width=1080, height=1920):
    cx, cy = width / 2, height * 0.46
    max_radius = math.hypot(width, height) / 1.5
    y, x = np.ogrid[:height, :width]
    dist = np.clip(np.hypot(x - cx, y - cy) / max_radius, 0.0, 1.0)
    
    # Modern studio vignette background
    c_center = np.array([255, 255, 255], dtype=np.float32)
    c_edge = np.array([218, 226, 238], dtype=np.float32)
    bg_np = (c_center * (1.0 - dist[:, :, None]) + c_edge * dist[:, :, None]).astype(np.uint8)
    
    bg_img = Image.fromarray(bg_np, mode="RGB").convert("RGBA")
    draw = ImageDraw.Draw(bg_img)
    
    icx, icy = int(cx), int(cy)
    # Center target reticle rings
    draw.ellipse([icx - 450, icy - 450, icx + 450, icy + 450], outline=(175, 190, 212, 70), width=5)
    draw.ellipse([icx - 410, icy - 410, icx + 410, icy + 410], fill=(235, 242, 252, 60), outline=(170, 185, 210, 80), width=3)
    draw.ellipse([icx - 120, icy - 120, icx + 120, icy + 120], outline=(180, 195, 215, 60), width=2)
    
    # Target crosshairs
    draw.line([icx - 460, icy, icx - 415, icy], fill=(160, 175, 200, 140), width=4)
    draw.line([icx + 415, icy, icx + 460, icy], fill=(160, 175, 200, 140), width=4)
    draw.line([icx, icy - 460, icx, icy - 415], fill=(160, 175, 200, 140), width=4)
    draw.line([icx, icy + 415, icx, icy + 460], fill=(160, 175, 200, 140), width=4)
    
    # Clean emoji from title_text for clean bold typography
    clean_title = title_text.encode('ascii', 'ignore').decode('ascii').strip().upper()
    if not clean_title:
        clean_title = "CAN YOU STOP IN THE SHADOW?"
        
    # Smart Multi-Line Auto-Wrapping & Dynamic Card Sizing
    max_title_w = width - 160  # 920px max content width inside card
    
    # 1. Check if it fits on a single line
    lines = [clean_title]
    font_size = 54
    title_font = get_bold_font(font_size)
    bbox = draw.textbbox((0, 0), clean_title, font=title_font)
    tw = bbox[2] - bbox[0]
    
    while tw > max_title_w and font_size > 42:
        font_size -= 2
        title_font = get_bold_font(font_size)
        bbox = draw.textbbox((0, 0), clean_title, font=title_font)
        tw = bbox[2] - bbox[0]
        
    if tw > max_title_w:
        # 2. Wrap into 2 balanced lines
        words = clean_title.split()
        best_diff = 999
        best_split = len(words) // 2
        for i in range(1, len(words)):
            l1 = " ".join(words[:i])
            l2 = " ".join(words[i:])
            diff = abs(len(l1) - len(l2))
            if diff < best_diff:
                best_diff = diff
                best_split = i
        lines = [" ".join(words[:best_split]), " ".join(words[best_split:])]
        
        font_size = 46
        title_font = get_bold_font(font_size)
        w1 = draw.textbbox((0, 0), lines[0], font=title_font)[2] - draw.textbbox((0, 0), lines[0], font=title_font)[0]
        w2 = draw.textbbox((0, 0), lines[1], font=title_font)[2] - draw.textbbox((0, 0), lines[1], font=title_font)[0]
        while max(w1, w2) > max_title_w and font_size > 34:
            font_size -= 2
            title_font = get_bold_font(font_size)
            w1 = draw.textbbox((0, 0), lines[0], font=title_font)[2] - draw.textbbox((0, 0), lines[0], font=title_font)[0]
            w2 = draw.textbbox((0, 0), lines[1], font=title_font)[2] - draw.textbbox((0, 0), lines[1], font=title_font)[0]
        card_h = 196
    else:
        card_h = 136
        
    top_y = 110
    card_left = 46
    card_right = width - 46
    
    # Shadow under main title card
    draw.rounded_rectangle([card_left + 4, top_y + 8, card_right + 4, top_y + card_h + 8],
                           radius=28, fill=(180, 195, 215, 100))
    # Main title card
    draw.rounded_rectangle([card_left, top_y, card_right, top_y + card_h],
                           radius=28, fill=(255, 255, 255, 252),
                           outline=(195, 210, 230, 255), width=4)
    
    # Draw centered text line(s)
    sample_bbox = draw.textbbox((0, 0), "A", font=title_font)
    line_h = sample_bbox[3] - sample_bbox[1]
    line_spacing = 10 if len(lines) > 1 else 0
    total_text_h = len(lines) * line_h + (len(lines) - 1) * line_spacing
    start_y = top_y + (card_h - total_text_h) // 2
    
    for i, line in enumerate(lines):
        line_bbox = draw.textbbox((0, 0), line, font=title_font)
        lw = line_bbox[2] - line_bbox[0]
        lx = (width - lw) // 2
        ly = start_y + i * (line_h + line_spacing) - line_bbox[1]
        draw.text((lx, ly), line, fill=(15, 23, 42, 255), font=title_font)
    
    # Badges placed dynamically below title card
    badge_font = get_bold_font(34)
    def draw_badge(bx, by, bw, bh, text, bg_color, dot_color=None):
        draw.rounded_rectangle([bx + 3, by + 4, bx + bw + 3, by + bh + 4], radius=18, fill=(170, 185, 205, 80))
        draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=18, fill=bg_color)
        tbox = draw.textbbox((0, 0), text, font=badge_font)
        tbw = tbox[2] - tbox[0]
        tbh = tbox[3] - tbox[1]
        text_x = bx + (bw - tbw) // 2
        if dot_color:
            text_x += 12
            dot_r = 8
            dot_cx = bx + (bw - tbw) // 2 - 14
            dot_cy = by + bh // 2
            draw.ellipse([dot_cx - dot_r, dot_cy - dot_r, dot_cx + dot_r, dot_cy + dot_r], fill=dot_color)
        draw.text((text_x, by + (bh - tbh) // 2 - tbox[1]), text, fill=(255, 255, 255), font=badge_font)
        
    badge_y = top_y + card_h + 20
    draw_badge(50, badge_y, 270, 66, "99% FAIL", (225, 29, 72), dot_color=(255, 220, 0))
    draw_badge(width - 370, badge_y, 320, 66, "TAP TO PAUSE", (14, 116, 244), dot_color=(56, 189, 248))
    
    # Bottom Call to Action Bar
    clean_sub = subtitle.encode('ascii', 'ignore').decode('ascii').strip().upper()
    if not clean_sub:
        clean_sub = "TAP SCREEN TO PAUSE IN TIME!"
        
    sub_font = get_bold_font(40)
    bot_y = height - 210
    c_bbox = draw.textbbox((0, 0), clean_sub, font=sub_font)
    cw = c_bbox[2] - c_bbox[0]
    ch = c_bbox[3] - c_bbox[1]
    
    bar_w = cw + 90
    bar_h = 80
    bx1 = (width - bar_w) // 2
    bx2 = bx1 + bar_w
    by1 = bot_y
    by2 = by1 + bar_h
    
    draw.rounded_rectangle([bx1 + 4, by1 + 6, bx2 + 4, by2 + 6], radius=24, fill=(15, 23, 42, 70))
    draw.rounded_rectangle([bx1, by1, bx2, by2], radius=24, fill=(20, 27, 41, 245), outline=(56, 189, 248, 220), width=4)
    draw.text((bx1 + (bar_w - cw) // 2, by1 + (bar_h - ch) // 2 - c_bbox[1]), clean_sub, fill=(255, 255, 255), font=sub_font)
    
    return bg_img


def smooth_playable_oscillation(t, t_win, freq, amp, direction=1):
    phase = 0.0 if direction == 1 else math.pi
    raw_sin = math.sin(2 * math.pi * freq * (t - t_win) + phase)
    shaped = math.copysign(abs(raw_sin) ** 0.85, raw_sin)
    return amp * shaped
