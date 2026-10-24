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
    """
    Renders a hyper-polished, realistic studio puzzle background with:
    - Safe-zone aware layout (completely un-cramped, perfect margins for Facebook & IG Reels)
    - Multi-layered ambient occlusion and drop shadows for realistic depth
    - Glassmorphism & metallic card accents with generous internal padding
    - Vibrant, spaced badge pills and un-cramped call-to-action container
    """
    cx, cy = width / 2, height * 0.47
    max_radius = math.hypot(width, height) / 1.45
    y, x = np.ogrid[:height, :width]
    dist = np.clip(np.hypot(x - cx, y - cy) / max_radius, 0.0, 1.0)
    
    # Premium deep-vignette studio backdrop (warm-center to cool-slate vignette)
    c_center = np.array([255, 255, 255], dtype=np.float32)
    c_edge = np.array([210, 222, 238], dtype=np.float32)
    bg_np = (c_center * (1.0 - dist[:, :, None]) + c_edge * dist[:, :, None]).astype(np.uint8)
    
    bg_img = Image.fromarray(bg_np, mode="RGB").convert("RGBA")
    draw = ImageDraw.Draw(bg_img)
    icx, icy = int(cx), int(cy)
    
    # Realistic glowing target arena rings
    draw.ellipse([icx - 460, icy - 460, icx + 460, icy + 460], outline=(160, 180, 208, 50), width=6)
    draw.ellipse([icx - 420, icy - 420, icx + 420, icy + 420], fill=(240, 246, 255, 50), outline=(150, 175, 205, 90), width=3)
    draw.ellipse([icx - 140, icy - 140, icx + 140, icy + 140], outline=(165, 185, 215, 60), width=2)
    
    # Arena reticle ticks & crosshairs
    for angle in [0, 45, 90, 135, 180, 225, 270, 315]:
        rad = math.radians(angle)
        r1 = 420
        r2 = 450 if angle % 90 == 0 else 435
        x1 = icx + int(r1 * math.cos(rad))
        y1 = icy + int(r1 * math.sin(rad))
        x2 = icx + int(r2 * math.cos(rad))
        y2 = icy + int(r2 * math.sin(rad))
        draw.line([x1, y1, x2, y2], fill=(140, 165, 195, 160 if angle % 90 == 0 else 90), width=4 if angle % 90 == 0 else 2)

    # ------------------ TOP CONTAINER: TITLE CARD ------------------
    clean_title = title_text.encode('ascii', 'ignore').decode('ascii').strip().upper()
    if not clean_title:
        clean_title = "CAN YOU STOP IN THE SHADOW?"
        
    card_margin_x = 56
    card_w = width - (card_margin_x * 2)  # 968px wide
    card_left = card_margin_x
    card_right = card_left + card_w
    top_y = 100
    
    # Internal text constraints (generous 48px padding on sides)
    max_text_w = card_w - 96
    
    font_size = 52
    title_font = get_bold_font(font_size)
    bbox = draw.textbbox((0, 0), clean_title, font=title_font)
    tw = bbox[2] - bbox[0]
    
    while tw > max_text_w and font_size > 40:
        font_size -= 2
        title_font = get_bold_font(font_size)
        bbox = draw.textbbox((0, 0), clean_title, font=title_font)
        tw = bbox[2] - bbox[0]
        
    lines = [clean_title]
    if tw > max_text_w:
        # Wrap into 2 balanced lines with generous line height
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
        
        font_size = 44
        title_font = get_bold_font(font_size)
        w1 = draw.textbbox((0, 0), lines[0], font=title_font)[2] - draw.textbbox((0, 0), lines[0], font=title_font)[0]
        w2 = draw.textbbox((0, 0), lines[1], font=title_font)[2] - draw.textbbox((0, 0), lines[1], font=title_font)[0]
        while max(w1, w2) > max_text_w and font_size > 32:
            font_size -= 2
            title_font = get_bold_font(font_size)
            w1 = draw.textbbox((0, 0), lines[0], font=title_font)[2] - draw.textbbox((0, 0), lines[0], font=title_font)[0]
            w2 = draw.textbbox((0, 0), lines[1], font=title_font)[2] - draw.textbbox((0, 0), lines[1], font=title_font)[0]
        card_h = 210  # Generous height for 2 lines
    else:
        card_h = 148  # Generous height for 1 line
        
    # Multi-layered soft drop shadows for realistic depth
    for offset, alpha in [(12, 35), (8, 60), (4, 90)]:
        draw.rounded_rectangle(
            [card_left + 2, top_y + offset, card_right + 2, top_y + card_h + offset],
            radius=32, fill=(160, 178, 205, alpha)
        )
        
    # Main Glass/Enamel Container Card
    draw.rounded_rectangle(
        [card_left, top_y, card_right, top_y + card_h],
        radius=32, fill=(255, 255, 255, 252),
        outline=(205, 220, 240, 255), width=3
    )
    # Subtle inner top rim light for realism
    draw.rounded_rectangle(
        [card_left + 2, top_y + 2, card_right - 2, top_y + card_h // 2],
        radius=30, outline=(255, 255, 255, 220), width=2
    )

    # Render centered text with generous breathing space
    sample_bbox = draw.textbbox((0, 0), "A", font=title_font)
    line_h = sample_bbox[3] - sample_bbox[1]
    line_spacing = 16 if len(lines) > 1 else 0
    total_text_h = len(lines) * line_h + (len(lines) - 1) * line_spacing
    start_y = top_y + (card_h - total_text_h) // 2
    
    for i, line in enumerate(lines):
        line_bbox = draw.textbbox((0, 0), line, font=title_font)
        lw = line_bbox[2] - line_bbox[0]
        lx = (width - lw) // 2
        ly = start_y + i * (line_h + line_spacing) - line_bbox[1]
        draw.text((lx, ly), line, fill=(15, 23, 42, 255), font=title_font)

    # ------------------ BADGES ROW (SPACED & UN-CRAMPED) ------------------
    badge_font = get_bold_font(32)
    badge_y = top_y + card_h + 24
    
    def draw_sleek_badge(bx, by, bw, bh, text, bg_color, dot_color=None):
        # Soft shadow
        draw.rounded_rectangle([bx + 2, by + 5, bx + bw + 2, by + bh + 5], radius=bh // 2, fill=(150, 170, 195, 70))
        # Main pill container
        draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=bh // 2, fill=bg_color, outline=(255, 255, 255, 180), width=2)
        tbox = draw.textbbox((0, 0), text, font=badge_font)
        tbw = tbox[2] - tbox[0]
        tbh = tbox[3] - tbox[1]
        text_x = bx + (bw - tbw) // 2
        if dot_color:
            text_x += 14
            dot_r = 7
            dot_cx = bx + (bw - tbw) // 2 - 12
            dot_cy = by + bh // 2
            draw.ellipse([dot_cx - dot_r, dot_cy - dot_r, dot_cx + dot_r, dot_cy + dot_r], fill=dot_color)
        draw.text((text_x, by + (bh - tbh) // 2 - tbox[1]), text, fill=(255, 255, 255), font=badge_font)

    # Spaced badges: 56px margins, 68px height
    draw_sleek_badge(card_margin_x, badge_y, 280, 68, "99% FAIL", (225, 29, 72), dot_color=(255, 220, 0))
    draw_sleek_badge(width - card_margin_x - 330, badge_y, 330, 68, "TAP TO PAUSE", (14, 116, 244), dot_color=(56, 189, 248))

    # ------------------ BOTTOM CTA CONTAINER (SAFE ZONE REPOSITIONED) ------------------
    # Positioned at y = 1580 (height - 340) to be completely ABOVE Facebook/Instagram Reels UI
    clean_sub = subtitle.encode('ascii', 'ignore').decode('ascii').strip().upper()
    if not clean_sub:
        clean_sub = "TAP SCREEN TO PAUSE IN TIME!"
        
    sub_font = get_bold_font(38)
    c_bbox = draw.textbbox((0, 0), clean_sub, font=sub_font)
    cw = c_bbox[2] - c_bbox[0]
    ch = c_bbox[3] - c_bbox[1]
    
    # Generous container padding: +120px width, 88px height
    bar_w = min(width - 120, cw + 120)
    bar_h = 88
    bot_y = height - 340
    bx1 = (width - bar_w) // 2
    bx2 = bx1 + bar_w
    by1 = bot_y
    by2 = by1 + bar_h
    
    # Ambient shadow
    draw.rounded_rectangle([bx1 + 2, by1 + 6, bx2 + 2, by2 + 6], radius=bar_h // 2, fill=(15, 23, 42, 60))
    # Sleek dark cyber pill with neon cyan rim
    draw.rounded_rectangle([bx1, by1, bx2, by2], radius=bar_h // 2, fill=(15, 23, 42, 245), outline=(56, 189, 248, 230), width=3)
    # Inner subtle highlight
    draw.rounded_rectangle([bx1 + 2, by1 + 2, bx2 - 2, by1 + bar_h // 2], radius=bar_h // 2, outline=(255, 255, 255, 50), width=1)
    # Centered text with generous padding
    draw.text((bx1 + (bar_w - cw) // 2, by1 + (bar_h - ch) // 2 - c_bbox[1]), clean_sub, fill=(255, 255, 255), font=sub_font)
    
    return bg_img


def smooth_playable_oscillation(t, t_win, freq, amp, direction=1):
    phase = 0.0 if direction == 1 else math.pi
    raw_sin = math.sin(2 * math.pi * freq * (t - t_win) + phase)
    shaped = math.copysign(abs(raw_sin) ** 0.85, raw_sin)
    return amp * shaped
