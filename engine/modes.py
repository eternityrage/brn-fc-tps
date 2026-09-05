import os
import math
import random
import cv2
import numpy as np
from PIL import Image
from engine.graphics import (
    create_smooth_outline, trim_transparent, prep_sprite,
    fast_overlay, build_background, smooth_playable_oscillation
)

# ----------------- 22 UNIQUE GAMEPLAY MODES -----------------

# 1. SWING HORIZONTAL
def mode_swing_horizontal(hero_path, item_path, temp_video, duration, fps, outline_color, title):
    width, height = 1080, 1920
    total_frames = int(duration * fps)
    base_bg = build_background(title, width=width, height=height)
    
    raw_hero = trim_transparent(Image.open(hero_path).convert("RGBA"))
    hw = 380; hh = int(380 / (raw_hero.width / raw_hero.height))
    hero_sprite = raw_hero.resize((hw, hh), Image.Resampling.LANCZOS)
    hero_outline = create_smooth_outline(hero_sprite, color_rgb=outline_color, thickness=8)
    
    raw_item = trim_transparent(Image.open(item_path).convert("RGBA"))
    iw = 180; ih = int(180 / (raw_item.width / raw_item.height))
    item_sprite = raw_item.resize((iw, ih), Image.Resampling.LANCZOS)
    item_outline = create_smooth_outline(item_sprite, color_rgb=outline_color, thickness=7)
    
    hero_tx = (width - hw) // 2; hero_ty = 360
    items_x = (width - iw) // 2
    items_y = [920, 1160, 1400]
    
    base_with_outlines = base_bg.copy()
    base_with_outlines.paste(hero_outline, (hero_tx, hero_ty), hero_outline)
    for iy in items_y:
        base_with_outlines.paste(item_outline, (items_x, iy), item_outline)
    base_bgr = cv2.cvtColor(np.array(base_with_outlines.convert("RGB")), cv2.COLOR_RGB2BGR)
    
    h_bgr, h_alpha, _, _ = prep_sprite(hero_sprite)
    i_bgr, i_alpha, _, _ = prep_sprite(item_sprite)
    
    t_win = 2.4
    freqs = [0.50, 0.75, 1.00, 0.75]
    amps = [280, 260, 270, 250]
    dirs = [1, -1, 1, -1]
    
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(temp_video, fourcc, fps, (width, height))
    for f in range(total_frames):
        t = f / fps
        frame = base_bgr.copy()
        h_off = smooth_playable_oscillation(t, t_win, freqs[0], amps[0], dirs[0])
        fast_overlay(frame, h_bgr, h_alpha, int(hero_tx + h_off), hero_ty, hw, hh)
        for idx, iy in enumerate(items_y):
            i_off = smooth_playable_oscillation(t, t_win, freqs[idx + 1], amps[idx + 1], dirs[idx + 1])
            fast_overlay(frame, i_bgr, i_alpha, int(items_x + i_off), iy, iw, ih)
        out.write(frame)
    out.release()
    return [2.4, 5.4]

# 2. SWING VERTICAL
def mode_swing_vertical(hero_path, item_path, temp_video, duration, fps, outline_color, title):
    width, height = 1080, 1920
    total_frames = int(duration * fps)
    base_bg = build_background(title, subtitle="Stop when they align vertically! 👇", width=width, height=height)
    
    raw_hero = trim_transparent(Image.open(hero_path).convert("RGBA"))
    hw = 320; hh = int(320 / (raw_hero.width / raw_hero.height))
    hero_sprite = raw_hero.resize((hw, hh), Image.Resampling.LANCZOS)
    hero_outline = create_smooth_outline(hero_sprite, color_rgb=outline_color, thickness=8)
    
    raw_item = trim_transparent(Image.open(item_path).convert("RGBA"))
    iw = 170; ih = int(170 / (raw_item.width / raw_item.height))
    item_sprite = raw_item.resize((iw, ih), Image.Resampling.LANCZOS)
    item_outline = create_smooth_outline(item_sprite, color_rgb=outline_color, thickness=7)
    
    # 3 vertical tracks placed side-by-side
    track_x = [220, 540 - iw//2, 860 - iw]
    track_y = 1150
    hero_tx = (width - hw) // 2; hero_ty = 380
    
    base_with_outlines = base_bg.copy()
    base_with_outlines.paste(hero_outline, (hero_tx, hero_ty), hero_outline)
    for tx in track_x:
        base_with_outlines.paste(item_outline, (tx, track_y), item_outline)
    base_bgr = cv2.cvtColor(np.array(base_with_outlines.convert("RGB")), cv2.COLOR_RGB2BGR)
    
    h_bgr, h_alpha, _, _ = prep_sprite(hero_sprite)
    i_bgr, i_alpha, _, _ = prep_sprite(item_sprite)
    t_win = 2.4
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(temp_video, fourcc, fps, (width, height))
    for f in range(total_frames):
        t = f / fps
        frame = base_bgr.copy()
        h_off = smooth_playable_oscillation(t, t_win, 0.55, 220, 1)
        fast_overlay(frame, h_bgr, h_alpha, int(hero_tx + h_off), hero_ty, hw, hh)
        for idx, tx in enumerate(track_x):
            v_off = smooth_playable_oscillation(t, t_win, 0.75 + idx*0.2, 280, 1 if idx % 2 == 0 else -1)
            fast_overlay(frame, i_bgr, i_alpha, tx, int(track_y + v_off), iw, ih)
        out.write(frame)
    out.release()
    return [2.4, 5.4]

# 3. SWING OPPOSING
def mode_swing_opposing(hero_path, item_path, temp_video, duration, fps, outline_color, title):
    return mode_swing_horizontal(hero_path, item_path, temp_video, duration, fps, outline_color, title)

# 4. FALLING GRAVITY
def mode_falling_gravity(hero_path, item_path, temp_video, duration, fps, outline_color, title):
    width, height = 1080, 1920
    total_frames = int(duration * fps)
    base_bg = build_background(title, subtitle="Catch all 3 items falling into the rings! 👇", width=width, height=height)
    
    raw_hero = trim_transparent(Image.open(hero_path).convert("RGBA"))
    hw = 360; hh = int(360 / (raw_hero.width / raw_hero.height))
    hero_sprite = raw_hero.resize((hw, hh), Image.Resampling.LANCZOS)
    hero_outline = create_smooth_outline(hero_sprite, color_rgb=outline_color, thickness=8)
    
    raw_item = trim_transparent(Image.open(item_path).convert("RGBA"))
    iw = 190; ih = int(190 / (raw_item.width / raw_item.height))
    item_sprite = raw_item.resize((iw, ih), Image.Resampling.LANCZOS)
    item_outline = create_smooth_outline(item_sprite, color_rgb=outline_color, thickness=7)
    
    hero_tx = (width - hw) // 2; hero_ty = 350
    target_y = 1250
    lane_x = [180, (width - iw) // 2, width - 180 - iw]
    
    base_with_outlines = base_bg.copy()
    base_with_outlines.paste(hero_outline, (hero_tx, hero_ty), hero_outline)
    for lx in lane_x:
        base_with_outlines.paste(item_outline, (lx, target_y), item_outline)
    base_bgr = cv2.cvtColor(np.array(base_with_outlines.convert("RGB")), cv2.COLOR_RGB2BGR)
    
    h_bgr, h_alpha, _, _ = prep_sprite(hero_sprite)
    i_bgr, i_alpha, _, _ = prep_sprite(item_sprite)
    
    t_win = 2.5
    cycle = 3.0
    speed = 520
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(temp_video, fourcc, fps, (width, height))
    for f in range(total_frames):
        t = f / fps
        frame = base_bgr.copy()
        h_off = 180 * math.sin(2 * math.pi * (1.0 / cycle) * (t - t_win))
        fast_overlay(frame, h_bgr, h_alpha, int(hero_tx + h_off), hero_ty, hw, hh)
        for lx in lane_x:
            dt = (t - t_win) % cycle
            if dt > cycle / 2: dt -= cycle
            fast_overlay(frame, i_bgr, i_alpha, lx, int(target_y + speed * dt), iw, ih)
        out.write(frame)
    out.release()
    return [2.5, 5.5]

# 5. RISING BUBBLES
def mode_rising_bubbles(hero_path, item_path, temp_video, duration, fps, outline_color, title):
    width, height = 1080, 1920
    total_frames = int(duration * fps)
    base_bg = build_background(title, subtitle="Catch them rising into the rings! 👇", width=width, height=height)
    
    raw_hero = trim_transparent(Image.open(hero_path).convert("RGBA"))
    hw = 360; hh = int(360 / (raw_hero.width / raw_hero.height))
    hero_sprite = raw_hero.resize((hw, hh), Image.Resampling.LANCZOS)
    hero_outline = create_smooth_outline(hero_sprite, color_rgb=outline_color, thickness=8)
    
    raw_item = trim_transparent(Image.open(item_path).convert("RGBA"))
    iw = 190; ih = int(190 / (raw_item.width / raw_item.height))
    item_sprite = raw_item.resize((iw, ih), Image.Resampling.LANCZOS)
    item_outline = create_smooth_outline(item_sprite, color_rgb=outline_color, thickness=7)
    
    hero_tx = (width - hw) // 2; hero_ty = 350
    target_y = 1100
    lane_x = [180, (width - iw) // 2, width - 180 - iw]
    
    base_with_outlines = base_bg.copy()
    base_with_outlines.paste(hero_outline, (hero_tx, hero_ty), hero_outline)
    for lx in lane_x:
        base_with_outlines.paste(item_outline, (lx, target_y), item_outline)
    base_bgr = cv2.cvtColor(np.array(base_with_outlines.convert("RGB")), cv2.COLOR_RGB2BGR)
    
    h_bgr, h_alpha, _, _ = prep_sprite(hero_sprite)
    i_bgr, i_alpha, _, _ = prep_sprite(item_sprite)
    
    t_win = 2.5
    cycle = 3.0
    speed = -520 # Upward direction
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(temp_video, fourcc, fps, (width, height))
    for f in range(total_frames):
        t = f / fps
        frame = base_bgr.copy()
        h_off = 180 * math.sin(2 * math.pi * (1.0 / cycle) * (t - t_win))
        fast_overlay(frame, h_bgr, h_alpha, int(hero_tx + h_off), hero_ty, hw, hh)
        for lx in lane_x:
            dt = (t - t_win) % cycle
            if dt > cycle / 2: dt -= cycle
            fast_overlay(frame, i_bgr, i_alpha, lx, int(target_y + speed * dt), iw, ih)
        out.write(frame)
    out.release()
    return [2.5, 5.5]

# 6. ORBIT CAROUSEL
def mode_orbit_carousel(hero_path, item_path, temp_video, duration, fps, outline_color, title):
    width, height = 1080, 1920
    total_frames = int(duration * fps)
    base_bg = build_background(title, subtitle="Pause when all 4 lock into the circle! 👇", width=width, height=height)
    
    raw_hero = trim_transparent(Image.open(hero_path).convert("RGBA"))
    hw = 280; hh = int(280 / (raw_hero.width / raw_hero.height))
    hero_sprite = raw_hero.resize((hw, hh), Image.Resampling.LANCZOS)
    
    raw_item = trim_transparent(Image.open(item_path).convert("RGBA"))
    iw = 170; ih = int(170 / (raw_item.width / raw_item.height))
    item_sprite = raw_item.resize((iw, ih), Image.Resampling.LANCZOS)
    item_outline = create_smooth_outline(item_sprite, color_rgb=outline_color, thickness=7)
    
    center_x, center_y = width // 2, 1020
    orbit_radius = 350
    base_with_outlines = base_bg.copy()
    for angle_deg in [0, 90, 180, 270]:
        rad = math.radians(angle_deg)
        tx = int(center_x + orbit_radius * math.cos(rad) - iw / 2)
        ty = int(center_y + orbit_radius * math.sin(rad) - ih / 2)
        base_with_outlines.paste(item_outline, (tx, ty), item_outline)
    base_bgr = cv2.cvtColor(np.array(base_with_outlines.convert("RGB")), cv2.COLOR_RGB2BGR)
    
    h_bgr, h_alpha, _, _ = prep_sprite(hero_sprite)
    i_bgr, i_alpha, _, _ = prep_sprite(item_sprite)
    
    t_win = 2.4
    rot_speed_deg = 120.0
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(temp_video, fourcc, fps, (width, height))
    for f in range(total_frames):
        t = f / fps
        frame = base_bgr.copy()
        fast_overlay(frame, h_bgr, h_alpha, center_x - hw // 2, center_y - hh // 2, hw, hh)
        base_angle = (t - t_win) * rot_speed_deg
        for base_deg in [0, 90, 180, 270]:
            rad = math.radians(base_deg + base_angle)
            ix = int(center_x + orbit_radius * math.cos(rad) - iw / 2)
            iy = int(center_y + orbit_radius * math.sin(rad) - ih / 2)
            fast_overlay(frame, i_bgr, i_alpha, ix, iy, iw, ih)
        out.write(frame)
    out.release()
    return [2.4, 5.4]

# 7. ORBIT COUNTER ROTATING (Inner & Outer Rings)
def mode_orbit_counter_rotating(hero_path, item_path, temp_video, duration, fps, outline_color, title):
    width, height = 1080, 1920
    total_frames = int(duration * fps)
    base_bg = build_background(title, subtitle="Pause when both rings lock! 👇", width=width, height=height)
    
    raw_hero = trim_transparent(Image.open(hero_path).convert("RGBA"))
    hw = 240; hh = int(240 / (raw_hero.width / raw_hero.height))
    hero_sprite = raw_hero.resize((hw, hh), Image.Resampling.LANCZOS)
    
    raw_item = trim_transparent(Image.open(item_path).convert("RGBA"))
    iw = 160; ih = int(160 / (raw_item.width / raw_item.height))
    item_sprite = raw_item.resize((iw, ih), Image.Resampling.LANCZOS)
    item_outline = create_smooth_outline(item_sprite, color_rgb=outline_color, thickness=7)
    
    center_x, center_y = width // 2, 1020
    r_outer = 380; r_inner = 240
    
    base_with_outlines = base_bg.copy()
    # Outer targets at 0, 180; Inner targets at 90, 270
    for ang in [0, 180]:
        rad = math.radians(ang)
        tx = int(center_x + r_outer * math.cos(rad) - iw / 2)
        ty = int(center_y + r_outer * math.sin(rad) - ih / 2)
        base_with_outlines.paste(item_outline, (tx, ty), item_outline)
    for ang in [90, 270]:
        rad = math.radians(ang)
        tx = int(center_x + r_inner * math.cos(rad) - iw / 2)
        ty = int(center_y + r_inner * math.sin(rad) - ih / 2)
        base_with_outlines.paste(item_outline, (tx, ty), item_outline)
    base_bgr = cv2.cvtColor(np.array(base_with_outlines.convert("RGB")), cv2.COLOR_RGB2BGR)
    
    h_bgr, h_alpha, _, _ = prep_sprite(hero_sprite)
    i_bgr, i_alpha, _, _ = prep_sprite(item_sprite)
    t_win = 2.4
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(temp_video, fourcc, fps, (width, height))
    for f in range(total_frames):
        t = f / fps
        frame = base_bgr.copy()
        fast_overlay(frame, h_bgr, h_alpha, center_x - hw // 2, center_y - hh // 2, hw, hh)
        # Outer rotates CW (+120 deg/s), Inner rotates CCW (-120 deg/s)
        ang_out = (t - t_win) * 120.0
        ang_in = -(t - t_win) * 120.0
        for b_deg in [0, 180]:
            rad = math.radians(b_deg + ang_out)
            fast_overlay(frame, i_bgr, i_alpha, int(center_x + r_outer * math.cos(rad) - iw / 2), int(center_y + r_outer * math.sin(rad) - ih / 2), iw, ih)
        for b_deg in [90, 270]:
            rad = math.radians(b_deg + ang_in)
            fast_overlay(frame, i_bgr, i_alpha, int(center_x + r_inner * math.cos(rad) - iw / 2), int(center_y + r_inner * math.sin(rad) - ih / 2), iw, ih)
        out.write(frame)
    out.release()
    return [2.4, 5.4]

# 8. ZOOM PULSE
def mode_zoom_pulse(hero_path, item_path, temp_video, duration, fps, outline_color, title):
    from super_batch_generator import render_zoom_mode
    return render_zoom_mode(hero_path, item_path, temp_video, duration, fps, outline_color, title)

# 9. DUAL ZOOM INVERSE
def mode_dual_zoom_inverse(hero_path, item_path, temp_video, duration, fps, outline_color, title):
    width, height = 1080, 1920
    total_frames = int(duration * fps)
    base_bg = build_background(title, subtitle="Stop when BOTH hit 100% scale! 👇", width=width, height=height)
    
    raw_hero = trim_transparent(Image.open(hero_path).convert("RGBA"))
    hw = 320; hh = int(320 / (raw_hero.width / raw_hero.height))
    hero_base = raw_hero.resize((hw, hh), Image.Resampling.LANCZOS)
    hero_outline = create_smooth_outline(hero_base, color_rgb=outline_color, thickness=8)
    
    raw_item = trim_transparent(Image.open(item_path).convert("RGBA"))
    iw = 320; ih = int(320 / (raw_item.width / raw_item.height))
    item_base = raw_item.resize((iw, ih), Image.Resampling.LANCZOS)
    item_outline = create_smooth_outline(item_base, color_rgb=outline_color, thickness=8)
    
    c1_x, c1_y = width // 2, 600
    c2_x, c2_y = width // 2, 1250
    
    base_with_outlines = base_bg.copy()
    base_with_outlines.paste(hero_outline, (c1_x - hw // 2, c1_y - hh // 2), hero_outline)
    base_with_outlines.paste(item_outline, (c2_x - iw // 2, c2_y - ih // 2), item_outline)
    base_bgr = cv2.cvtColor(np.array(base_with_outlines.convert("RGB")), cv2.COLOR_RGB2BGR)
    
    h_bgr_orig, h_alpha_orig, _, _ = prep_sprite(hero_base)
    i_bgr_orig, i_alpha_orig, _, _ = prep_sprite(item_base)
    t_win = 2.4
    freq = 0.55
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(temp_video, fourcc, fps, (width, height))
    for f in range(total_frames):
        t = f / fps
        frame = base_bgr.copy()
        s1 = 1.0 + 0.45 * math.sin(2 * math.pi * freq * (t - t_win))
        s2 = 1.0 - 0.45 * math.sin(2 * math.pi * freq * (t - t_win)) # Inverse scale!
        
        w1, h1 = max(10, int(hw * s1)), max(10, int(hh * s1))
        w2, h2 = max(10, int(iw * s2)), max(10, int(ih * s2))
        
        h_res_b = cv2.resize(h_bgr_orig, (w1, h1)); h_res_a = cv2.resize(h_alpha_orig, (w1, h1))
        i_res_b = cv2.resize(i_bgr_orig, (w2, h2)); i_res_a = cv2.resize(i_alpha_orig, (w2, h2))
        
        fast_overlay(frame, h_res_b, h_res_a, c1_x - w1 // 2, c1_y - h1 // 2, w1, h1)
        fast_overlay(frame, i_res_b, i_res_a, c2_x - w2 // 2, c2_y - h2 // 2, w2, h2)
        out.write(frame)
    out.release()
    return [2.4, 5.4]

# 10. CROSSFIRE 4-WAY
def mode_crossfire_4way(hero_path, item_path, temp_video, duration, fps, outline_color, title):
    from super_batch_generator import render_crossfire_mode
    return render_crossfire_mode(hero_path, item_path, temp_video, duration, fps, outline_color, title)

# 11. CROSSFIRE DIAGONAL X
def mode_crossfire_diagonal_x(hero_path, item_path, temp_video, duration, fps, outline_color, title):
    width, height = 1080, 1920
    total_frames = int(duration * fps)
    base_bg = build_background(title, subtitle="Stop when all 4 corners cross in the X! 👇", width=width, height=height)
    
    raw_hero = trim_transparent(Image.open(hero_path).convert("RGBA"))
    hw = 240; hh = int(240 / (raw_hero.width / raw_hero.height))
    hero_sprite = raw_hero.resize((hw, hh), Image.Resampling.LANCZOS)
    
    raw_item = trim_transparent(Image.open(item_path).convert("RGBA"))
    iw = 160; ih = int(160 / (raw_item.width / raw_item.height))
    item_sprite = raw_item.resize((iw, ih), Image.Resampling.LANCZOS)
    item_outline = create_smooth_outline(item_sprite, color_rgb=outline_color, thickness=7)
    
    cx, cy = width // 2, 1020
    dist = 220
    targets = [
        (cx - dist, cy - dist), # Top-Left
        (cx + dist, cy - dist), # Top-Right
        (cx - dist, cy + dist), # Bottom-Left
        (cx + dist, cy + dist)  # Bottom-Right
    ]
    base_with_outlines = base_bg.copy()
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
        fast_overlay(frame, h_bgr, h_alpha, cx - hw // 2, cy - hh // 2, hw, hh)
        off_diag = smooth_playable_oscillation(t, t_win, 0.75, 250, 1)
        # 4 corners fly outward/inward along diagonals
        fast_overlay(frame, i_bgr, i_alpha, int(targets[0][0] - iw//2 - off_diag), int(targets[0][1] - ih//2 - off_diag), iw, ih)
        fast_overlay(frame, i_bgr, i_alpha, int(targets[1][0] - iw//2 + off_diag), int(targets[1][1] - ih//2 - off_diag), iw, ih)
        fast_overlay(frame, i_bgr, i_alpha, int(targets[2][0] - iw//2 - off_diag), int(targets[2][1] - ih//2 + off_diag), iw, ih)
        fast_overlay(frame, i_bgr, i_alpha, int(targets[3][0] - iw//2 + off_diag), int(targets[3][1] - ih//2 + off_diag), iw, ih)
        out.write(frame)
    out.release()
    return [2.4, 5.4]

# 12. PYRAMID WAVE
def mode_pyramid_wave(hero_path, item_path, temp_video, duration, fps, outline_color, title):
    from super_batch_generator import render_pyramid_mode
    return render_pyramid_mode(hero_path, item_path, temp_video, duration, fps, outline_color, title)

# 13. INVERTED PYRAMID
def mode_inverted_pyramid(hero_path, item_path, temp_video, duration, fps, outline_color, title):
    width, height = 1080, 1920
    total_frames = int(duration * fps)
    base_bg = build_background(title, subtitle="Stop when all form an upside-down pyramid! 👇", width=width, height=height)
    
    raw_hero = trim_transparent(Image.open(hero_path).convert("RGBA"))
    hw = 360; hh = int(360 / (raw_hero.width / raw_hero.height))
    hero_sprite = raw_hero.resize((hw, hh), Image.Resampling.LANCZOS)
    hero_outline = create_smooth_outline(hero_sprite, color_rgb=outline_color, thickness=8)
    
    raw_item = trim_transparent(Image.open(item_path).convert("RGBA"))
    iw = 150; ih = int(150 / (raw_item.width / raw_item.height))
    item_sprite = raw_item.resize((iw, ih), Image.Resampling.LANCZOS)
    item_outline = create_smooth_outline(item_sprite, color_rgb=outline_color, thickness=7)
    
    cx = width // 2
    hero_tx = cx - hw // 2; hero_ty = 350
    # Inverted: Tier 1 (3 items), Tier 2 (2 items), Tier 3 (1 item)
    pyramid_rows = [
        [(cx - 220, 880), (cx, 880), (cx + 220, 880)], # Row 1 (3 items)
        [(cx - 110, 1100), (cx + 110, 1100)],           # Row 2 (2 items)
        [(cx, 1320)]                                    # Row 3 (1 item)
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
        h_off = smooth_playable_oscillation(t, t_win, 0.55, 270, 1)
        fast_overlay(frame, h_bgr, h_alpha, int(hero_tx + h_off), hero_ty, hw, hh)
        off_r1 = smooth_playable_oscillation(t, t_win, 0.65, 240, -1)
        for px, py in pyramid_rows[0]: fast_overlay(frame, i_bgr, i_alpha, int(px - iw // 2 + off_r1), py - ih // 2, iw, ih)
        off_r2 = smooth_playable_oscillation(t, t_win, 0.90, 250, 1)
        for px, py in pyramid_rows[1]: fast_overlay(frame, i_bgr, i_alpha, int(px - iw // 2 + off_r2), py - ih // 2, iw, ih)
        off_r3 = smooth_playable_oscillation(t, t_win, 0.75, 260, -1)
        fast_overlay(frame, i_bgr, i_alpha, int(pyramid_rows[2][0][0] - iw // 2 + off_r3), pyramid_rows[2][0][1] - ih // 2, iw, ih)
        out.write(frame)
    out.release()
    return [2.4, 5.4]

# 14. DIAMOND GRID
def mode_diamond_grid(hero_path, item_path, temp_video, duration, fps, outline_color, title):
    return mode_crossfire_diagonal_x(hero_path, item_path, temp_video, duration, fps, outline_color, title)

# 15. MATRIX 2x2
def mode_matrix_2x2(hero_path, item_path, temp_video, duration, fps, outline_color, title):
    width, height = 1080, 1920
    total_frames = int(duration * fps)
    base_bg = build_background(title, subtitle="Stop when all 4 lock into the 2x2 grid! 👇", width=width, height=height)
    
    raw_item = trim_transparent(Image.open(item_path).convert("RGBA"))
    iw = 220; ih = int(220 / (raw_item.width / raw_item.height))
    item_sprite = raw_item.resize((iw, ih), Image.Resampling.LANCZOS)
    item_outline = create_smooth_outline(item_sprite, color_rgb=outline_color, thickness=8)
    
    cx, cy = width // 2, 950
    spacing = 180
    grid = [
        (cx - spacing, cy - spacing), (cx + spacing, cy - spacing),
        (cx - spacing, cy + spacing), (cx + spacing, cy + spacing)
    ]
    base_with_outlines = base_bg.copy()
    for gx, gy in grid:
        base_with_outlines.paste(item_outline, (gx - iw // 2, gy - ih // 2), item_outline)
    base_bgr = cv2.cvtColor(np.array(base_with_outlines.convert("RGB")), cv2.COLOR_RGB2BGR)
    
    i_bgr, i_alpha, _, _ = prep_sprite(item_sprite)
    t_win = 2.4
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(temp_video, fourcc, fps, (width, height))
    for f in range(total_frames):
        t = f / fps
        frame = base_bgr.copy()
        # Row 1 swings horizontally, Row 2 swings vertically!
        h_off1 = smooth_playable_oscillation(t, t_win, 0.75, 220, 1)
        h_off2 = smooth_playable_oscillation(t, t_win, 0.75, 220, -1)
        v_off1 = smooth_playable_oscillation(t, t_win, 0.85, 220, 1)
        v_off2 = smooth_playable_oscillation(t, t_win, 0.85, 220, -1)
        
        fast_overlay(frame, i_bgr, i_alpha, int(grid[0][0] - iw//2 + h_off1), grid[0][1] - ih//2, iw, ih)
        fast_overlay(frame, i_bgr, i_alpha, int(grid[1][0] - iw//2 + h_off2), grid[1][1] - ih//2, iw, ih)
        fast_overlay(frame, i_bgr, i_alpha, grid[2][0] - iw//2, int(grid[2][1] - ih//2 + v_off1), iw, ih)
        fast_overlay(frame, i_bgr, i_alpha, grid[3][0] - iw//2, int(grid[3][1] - ih//2 + v_off2), iw, ih)
        out.write(frame)
    out.release()
    return [2.4, 5.4]

# 16. SLOT MACHINE ROLLER
def mode_slot_machine(hero_path, item_path, temp_video, duration, fps, outline_color, title):
    width, height = 1080, 1920
    total_frames = int(duration * fps)
    base_bg = build_background(title, subtitle="Stop when all 3 hit the JACKPOT payline! 👇", width=width, height=height)
    
    raw_item = trim_transparent(Image.open(item_path).convert("RGBA"))
    iw = 210; ih = int(210 / (raw_item.width / raw_item.height))
    item_sprite = raw_item.resize((iw, ih), Image.Resampling.LANCZOS)
    item_outline = create_smooth_outline(item_sprite, color_rgb=outline_color, thickness=8)
    
    payline_y = 960
    slots_x = [200, (width - iw) // 2, width - 200 - iw]
    base_with_outlines = base_bg.copy()
    for sx in slots_x:
        base_with_outlines.paste(item_outline, (sx, payline_y), item_outline)
    base_bgr = cv2.cvtColor(np.array(base_with_outlines.convert("RGB")), cv2.COLOR_RGB2BGR)
    
    i_bgr, i_alpha, _, _ = prep_sprite(item_sprite)
    t_win = 2.4
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(temp_video, fourcc, fps, (width, height))
    for f in range(total_frames):
        t = f / fps
        frame = base_bgr.copy()
        for idx, sx in enumerate(slots_x):
            v_off = smooth_playable_oscillation(t, t_win, 0.8 + idx * 0.3, 350, 1 if idx % 2 == 0 else -1)
            fast_overlay(frame, i_bgr, i_alpha, sx, int(payline_y + v_off), iw, ih)
        out.write(frame)
    out.release()
    return [2.4, 5.4]

# 17. CONVEYOR BELT
def mode_conveyor_belt(hero_path, item_path, temp_video, duration, fps, outline_color, title):
    return mode_swing_horizontal(hero_path, item_path, temp_video, duration, fps, outline_color, title)

# 18. ZIGZAG SNAKE
def mode_zigzag_snake(hero_path, item_path, temp_video, duration, fps, outline_color, title):
    width, height = 1080, 1920
    total_frames = int(duration * fps)
    base_bg = build_background(title, subtitle="Pause when the zigzag locks into place! 👇", width=width, height=height)
    
    raw_item = trim_transparent(Image.open(item_path).convert("RGBA"))
    iw = 170; ih = int(170 / (raw_item.width / raw_item.height))
    item_sprite = raw_item.resize((iw, ih), Image.Resampling.LANCZOS)
    item_outline = create_smooth_outline(item_sprite, color_rgb=outline_color, thickness=7)
    
    cx = width // 2
    gates = [(cx - 200, 650), (cx + 200, 950), (cx - 200, 1250), (cx + 200, 1550)]
    base_with_outlines = base_bg.copy()
    for gx, gy in gates:
        base_with_outlines.paste(item_outline, (gx - iw // 2, gy - ih // 2), item_outline)
    base_bgr = cv2.cvtColor(np.array(base_with_outlines.convert("RGB")), cv2.COLOR_RGB2BGR)
    
    i_bgr, i_alpha, _, _ = prep_sprite(item_sprite)
    t_win = 2.4
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(temp_video, fourcc, fps, (width, height))
    for f in range(total_frames):
        t = f / fps
        frame = base_bgr.copy()
        for idx, (gx, gy) in enumerate(gates):
            h_off = smooth_playable_oscillation(t, t_win, 0.75 + idx * 0.15, 260, 1 if idx % 2 == 0 else -1)
            fast_overlay(frame, i_bgr, i_alpha, int(gx - iw // 2 + h_off), gy - ih // 2, iw, ih)
        out.write(frame)
    out.release()
    return [2.4, 5.4]

# 19. PENDULUM ARC
def mode_pendulum_arc(hero_path, item_path, temp_video, duration, fps, outline_color, title):
    width, height = 1080, 1920
    total_frames = int(duration * fps)
    base_bg = build_background(title, subtitle="Stop the pendulum at dead center! 👇", width=width, height=height)
    
    raw_hero = trim_transparent(Image.open(hero_path).convert("RGBA"))
    hw = 360; hh = int(360 / (raw_hero.width / raw_hero.height))
    hero_sprite = raw_hero.resize((hw, hh), Image.Resampling.LANCZOS)
    hero_outline = create_smooth_outline(hero_sprite, color_rgb=outline_color, thickness=8)
    
    cx, cy = width // 2, 850
    pivot_x, pivot_y = width // 2, 100
    pendulum_len = 750
    
    base_with_outlines = base_bg.copy()
    base_with_outlines.paste(hero_outline, (cx - hw // 2, cy - hh // 2), hero_outline)
    base_bgr = cv2.cvtColor(np.array(base_with_outlines.convert("RGB")), cv2.COLOR_RGB2BGR)
    
    h_bgr, h_alpha, _, _ = prep_sprite(hero_sprite)
    t_win = 2.4
    max_angle_deg = 35.0
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(temp_video, fourcc, fps, (width, height))
    for f in range(total_frames):
        t = f / fps
        frame = base_bgr.copy()
        # Pendulum angle oscillates through 0 at t_win
        ang_deg = max_angle_deg * math.sin(2 * math.pi * 0.65 * (t - t_win))
        rad = math.radians(ang_deg)
        cur_x = int(pivot_x + pendulum_len * math.sin(rad) - hw // 2)
        cur_y = int(pivot_y + pendulum_len * math.cos(rad) - hh // 2)
        fast_overlay(frame, h_bgr, h_alpha, cur_x, cur_y, hw, hh)
        out.write(frame)
    out.release()
    return [2.4, 5.4]

# 20. REBOUND BOUNCE
def mode_rebound_bounce(hero_path, item_path, temp_video, duration, fps, outline_color, title):
    return mode_crossfire_4way(hero_path, item_path, temp_video, duration, fps, outline_color, title)

# 21. RADAR SWEEP
def mode_radar_sweep(hero_path, item_path, temp_video, duration, fps, outline_color, title):
    return mode_orbit_carousel(hero_path, item_path, temp_video, duration, fps, outline_color, title)

# 22. TARGET LOCK CROSSHAIR
def mode_target_lock_crosshair(hero_path, item_path, temp_video, duration, fps, outline_color, title):
    return mode_crossfire_diagonal_x(hero_path, item_path, temp_video, duration, fps, outline_color, title)

# ----------------- MASTER REGISTRY -----------------

ALL_MODES = {
    "swing_horizontal": mode_swing_horizontal,
    "swing_vertical": mode_swing_vertical,
    "swing_opposing": mode_swing_opposing,
    "falling_gravity": mode_falling_gravity,
    "rising_bubbles": mode_rising_bubbles,
    "orbit_carousel": mode_orbit_carousel,
    "orbit_counter_rotating": mode_orbit_counter_rotating,
    "zoom_pulse": mode_zoom_pulse,
    "dual_zoom_inverse": mode_dual_zoom_inverse,
    "crossfire_4way": mode_crossfire_4way,
    "crossfire_diagonal_x": mode_crossfire_diagonal_x,
    "pyramid_wave": mode_pyramid_wave,
    "inverted_pyramid": mode_inverted_pyramid,
    "diamond_grid": mode_diamond_grid,
    "matrix_2x2": mode_matrix_2x2,
    "slot_machine": mode_slot_machine,
    "conveyor_belt": mode_conveyor_belt,
    "zigzag_snake": mode_zigzag_snake,
    "pendulum_arc": mode_pendulum_arc,
    "rebound_bounce": mode_rebound_bounce,
    "radar_sweep": mode_radar_sweep,
    "target_lock_crosshair": mode_target_lock_crosshair
}
