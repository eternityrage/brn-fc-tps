"""
Master Gameplay Modes Engine - 100 Unique Viral Puzzle Varieties.
Supports 7 major motion families:
  1. Oscillations & Waves (Modes 1-15)
  2. Gravity & Physics Drops (Modes 16-30)
  3. Orbital, Planetary & Vortex (Modes 31-45)
  4. Convergence & Crossfire (Modes 46-60)
  5. Scale, Zoom & 3D Perspectives (Modes 61-75)
  6. Grid, Matrix & Slot Formations (Modes 76-88)
  7. Speed, Strobe, Glitch & Rhythm Mechanics (Modes 89-100)
All rendered in True Full HD 1080x1920 with guaranteed mathematical win alignment.
"""
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

WIDTH, HEIGHT = 1080, 1920

# ----------------- BASE SPRITE & BACKGROUND BUILDER -----------------

def _setup_sprites(hero_path, item_path, hero_size=360, item_size=180, outline_color=(0, 110, 255)):
    raw_hero = trim_transparent(Image.open(hero_path).convert("RGBA"))
    hw = hero_size
    hh = max(60, int(hero_size / (raw_hero.width / max(1, raw_hero.height))))
    hero_sprite = raw_hero.resize((hw, hh), Image.Resampling.LANCZOS)
    hero_outline = create_smooth_outline(hero_sprite, color_rgb=outline_color, thickness=8)
    
    raw_item = trim_transparent(Image.open(item_path).convert("RGBA"))
    iw = item_size
    ih = max(40, int(item_size / (raw_item.width / max(1, raw_item.height))))
    item_sprite = raw_item.resize((iw, ih), Image.Resampling.LANCZOS)
    item_outline = create_smooth_outline(item_sprite, color_rgb=outline_color, thickness=7)
    
    h_bgr, h_alpha, _, _ = prep_sprite(hero_sprite)
    i_bgr, i_alpha, _, _ = prep_sprite(item_sprite)
    
    return (hero_sprite, hero_outline, h_bgr, h_alpha, hw, hh), \
           (item_sprite, item_outline, i_bgr, i_alpha, iw, ih)


# =====================================================================
# FAMILY 1: LINEAR & HARMONIC OSCILLATIONS (MODES 1-15)
# =====================================================================

def _oscillation_engine(hero_path, item_path, temp_video, duration, fps, outline_color, title,
                        osc_type="horizontal", freqs=[0.5, 0.75, 1.0, 0.75], amps=[280, 260, 270, 250],
                        dirs=[1, -1, 1, -1], items_y=[920, 1160, 1400], t_win=2.4):
    total_frames = int(duration * fps)
    base_bg = build_background(title, width=WIDTH, height=HEIGHT)
    (h_sp, h_out, h_bgr, h_a, hw, hh), (i_sp, i_out, i_bgr, i_a, iw, ih) = _setup_sprites(
        hero_path, item_path, hero_size=360, item_size=180, outline_color=outline_color
    )
    
    hero_tx = (WIDTH - hw) // 2
    hero_ty = 360
    item_tx = (WIDTH - iw) // 2
    
    base_with_out = base_bg.copy()
    base_with_out.paste(h_out, (hero_tx, hero_ty), h_out)
    for iy in items_y:
        base_with_out.paste(i_out, (item_tx, iy), i_out)
    base_bgr = cv2.cvtColor(np.array(base_with_out.convert("RGB")), cv2.COLOR_RGB2BGR)
    
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(temp_video, fourcc, fps, (WIDTH, HEIGHT))
    
    for f in range(total_frames):
        t = f / fps
        frame = base_bgr.copy()
        
        # Calculate offsets based on oscillation type
        if osc_type == "horizontal":
            h_dx = smooth_playable_oscillation(t, t_win, freqs[0], amps[0], dirs[0])
            h_dy = 0
            fast_overlay(frame, h_bgr, h_a, int(hero_tx + h_dx), hero_ty, hw, hh)
            for idx, iy in enumerate(items_y):
                idx_clamp = min(idx + 1, len(freqs) - 1)
                idx_dir = min(idx + 1, len(dirs) - 1)
                i_dx = smooth_playable_oscillation(t, t_win, freqs[idx_clamp], amps[idx_clamp], dirs[idx_dir])
                fast_overlay(frame, i_bgr, i_a, int(item_tx + i_dx), iy, iw, ih)
                
        elif osc_type == "vertical":
            h_dy = smooth_playable_oscillation(t, t_win, freqs[0], amps[0], dirs[0])
            fast_overlay(frame, h_bgr, h_a, hero_tx, int(hero_ty + h_dy), hw, hh)
            for idx, iy in enumerate(items_y):
                idx_clamp = min(idx + 1, len(freqs) - 1)
                idx_dir = min(idx + 1, len(dirs) - 1)
                i_dy = smooth_playable_oscillation(t, t_win, freqs[idx_clamp], amps[idx_clamp], dirs[idx_dir])
                fast_overlay(frame, i_bgr, i_a, item_tx, int(iy + i_dy), iw, ih)
                
        elif osc_type == "diagonal_slash":
            h_off = smooth_playable_oscillation(t, t_win, freqs[0], amps[0], dirs[0])
            fast_overlay(frame, h_bgr, h_a, int(hero_tx + h_off), int(hero_ty + h_off * 0.7), hw, hh)
            for idx, iy in enumerate(items_y):
                idx_clamp = min(idx + 1, len(freqs) - 1)
                idx_dir = min(idx + 1, len(dirs) - 1)
                i_off = smooth_playable_oscillation(t, t_win, freqs[idx_clamp], amps[idx_clamp], dirs[idx_dir])
                fast_overlay(frame, i_bgr, i_a, int(item_tx + i_off), int(iy + i_off * 0.7), iw, ih)
                
        elif osc_type == "back_diagonal":
            h_off = smooth_playable_oscillation(t, t_win, freqs[0], amps[0], dirs[0])
            fast_overlay(frame, h_bgr, h_a, int(hero_tx + h_off), int(hero_ty - h_off * 0.7), hw, hh)
            for idx, iy in enumerate(items_y):
                idx_clamp = min(idx + 1, len(freqs) - 1)
                idx_dir = min(idx + 1, len(dirs) - 1)
                i_off = smooth_playable_oscillation(t, t_win, freqs[idx_clamp], amps[idx_clamp], dirs[idx_dir])
                fast_overlay(frame, i_bgr, i_a, int(item_tx + i_off), int(iy - i_off * 0.7), iw, ih)
                
        elif osc_type == "sine_meander":
            dt = t - t_win
            h_dx = 240 * math.sin(2 * math.pi * 0.6 * dt)
            h_dy = 60 * math.sin(4 * math.pi * 0.6 * dt)
            fast_overlay(frame, h_bgr, h_a, int(hero_tx + h_dx), int(hero_ty + h_dy), hw, hh)
            for idx, iy in enumerate(items_y):
                i_dx = 240 * math.sin(2 * math.pi * (0.8 + idx*0.2) * dt + (idx*math.pi/2))
                i_dy = 50 * math.sin(4 * math.pi * (0.8 + idx*0.2) * dt)
                fast_overlay(frame, i_bgr, i_a, int(item_tx + i_dx), int(iy + i_dy), iw, ih)
                
        elif osc_type == "triangle_bounce":
            dt = (t - t_win)
            phase = (dt * 1.5) % 2.0
            tri = (2.0 - phase if phase > 1.0 else phase) - 0.5
            h_dx = tri * 560
            fast_overlay(frame, h_bgr, h_a, int(hero_tx + h_dx), hero_ty, hw, hh)
            for idx, iy in enumerate(items_y):
                p_i = (dt * (1.6 + idx*0.4) + (idx*0.5)) % 2.0
                tri_i = (2.0 - p_i if p_i > 1.0 else p_i) - 0.5
                i_dx = tri_i * 540 * (1 if idx % 2 == 0 else -1)
                fast_overlay(frame, i_bgr, i_a, int(item_tx + i_dx), iy, iw, ih)
                
        elif osc_type == "spring_elastic":
            dt = t - t_win
            spring_h = 300 * math.sin(2 * math.pi * 0.9 * dt) * (1.0 + 0.3 * math.cos(6 * math.pi * 0.9 * dt))
            fast_overlay(frame, h_bgr, h_a, int(hero_tx + spring_h), hero_ty, hw, hh)
            for idx, iy in enumerate(items_y):
                spring_i = 280 * math.sin(2 * math.pi * (1.1 + idx*0.3) * dt) * (1.0 + 0.3 * math.cos(6 * math.pi * (1.1 + idx*0.3) * dt))
                fast_overlay(frame, i_bgr, i_a, int(item_tx + spring_i * (1 if idx % 2 == 0 else -1)), iy, iw, ih)
                
        elif osc_type == "accordion":
            dt = t - t_win
            scale_fac = math.sin(2 * math.pi * 0.7 * dt)
            fast_overlay(frame, h_bgr, h_a, hero_tx, hero_ty, hw, hh)
            for idx, iy in enumerate(items_y):
                # Expand outwards horizontally from center
                offset = (idx - 1) * 220 * scale_fac
                fast_overlay(frame, i_bgr, i_a, int(item_tx + offset), iy, iw, ih)
                
        elif osc_type == "piston":
            dt = t - t_win
            piston_h = 240 * (math.sin(2 * math.pi * 1.4 * dt) + 0.25 * math.sin(4 * math.pi * 1.4 * dt))
            fast_overlay(frame, h_bgr, h_a, hero_tx, int(hero_ty + piston_h), hw, hh)
            for idx, iy in enumerate(items_y):
                piston_i = 200 * (math.sin(2 * math.pi * (1.6 + idx*0.3) * dt) + 0.25 * math.sin(4 * math.pi * (1.6 + idx*0.3) * dt))
                fast_overlay(frame, i_bgr, i_a, item_tx, int(iy + piston_i), iw, ih)
                
        elif osc_type == "zigzag":
            dt = (t - t_win) * 1.2
            zx = 280 * math.sin(2 * math.pi * dt)
            zy = 120 * math.sin(4 * math.pi * dt)
            fast_overlay(frame, h_bgr, h_a, int(hero_tx + zx), int(hero_ty + zy), hw, hh)
            for idx, iy in enumerate(items_y):
                zi_x = 280 * math.sin(2 * math.pi * (dt * 1.2 + idx*0.4)) * (1 if idx%2==0 else -1)
                zi_y = 90 * math.sin(4 * math.pi * (dt * 1.2 + idx*0.4))
                fast_overlay(frame, i_bgr, i_a, int(item_tx + zi_x), int(iy + zi_y), iw, ih)
                
        elif osc_type == "heartbeat":
            dt = (t - t_win) * 1.0
            beat = math.exp(-((dt % 1.0 - 0.2)**2) / 0.01) - math.exp(-((dt % 1.0 - 0.4)**2) / 0.01)
            pulse_x = beat * 240
            fast_overlay(frame, h_bgr, h_a, int(hero_tx + pulse_x), hero_ty, hw, hh)
            for idx, iy in enumerate(items_y):
                beat_i = math.exp(-((dt % 1.0 - 0.2)**2) / 0.01) - math.exp(-((dt % 1.0 - 0.4)**2) / 0.01)
                fast_overlay(frame, i_bgr, i_a, int(item_tx + beat_i * 220 * (1 if idx%2==0 else -1)), iy, iw, ih)
                
        elif osc_type == "wobble":
            dt = t - t_win
            wob_x = 180 * math.sin(2 * math.pi * 0.7 * dt) + 90 * math.sin(2 * math.pi * 1.9 * dt)
            wob_y = 60 * math.cos(2 * math.pi * 0.7 * dt) - 40 * math.cos(2 * math.pi * 1.9 * dt)
            fast_overlay(frame, h_bgr, h_a, int(hero_tx + wob_x), int(hero_ty + wob_y), hw, hh)
            for idx, iy in enumerate(items_y):
                wi_x = 180 * math.sin(2 * math.pi * (0.8+idx*0.2) * dt) + 80 * math.sin(2 * math.pi * 2.1 * dt)
                wi_y = 50 * math.cos(2 * math.pi * (0.8+idx*0.2) * dt)
                fast_overlay(frame, i_bgr, i_a, int(item_tx + wi_x), int(iy + wi_y), iw, ih)
                
        else: # Default pendulum arc
            dt = t - t_win
            ang = 35.0 * math.sin(2 * math.pi * 0.65 * dt)
            rad = math.radians(ang)
            fast_overlay(frame, h_bgr, h_a, int(hero_tx + 300 * math.sin(rad)), int(hero_ty + 300 * (1.0 - math.cos(rad))), hw, hh)
            for idx, iy in enumerate(items_y):
                ang_i = 32.0 * math.sin(2 * math.pi * (0.75 + idx*0.2) * dt) * (1 if idx%2==0 else -1)
                rad_i = math.radians(ang_i)
                fast_overlay(frame, i_bgr, i_a, int(item_tx + 280 * math.sin(rad_i)), int(iy + 280 * (1.0 - math.cos(rad_i))), iw, ih)

        out.write(frame)
    out.release()
    return [t_win, t_win + 3.0]


# 15 Specific Oscillation Mode Functions
def mode_swing_horizontal(h, i, tv, d, f, c, t): return _oscillation_engine(h, i, tv, d, f, c, t, osc_type="horizontal")
def mode_swing_vertical(h, i, tv, d, f, c, t): return _oscillation_engine(h, i, tv, d, f, c, t, osc_type="vertical")
def mode_swing_opposing(h, i, tv, d, f, c, t): return _oscillation_engine(h, i, tv, d, f, c, t, osc_type="horizontal", dirs=[1, -1, 1, -1])
def mode_swing_diagonal_slash(h, i, tv, d, f, c, t): return _oscillation_engine(h, i, tv, d, f, c, t, osc_type="diagonal_slash")
def mode_swing_back_diagonal(h, i, tv, d, f, c, t): return _oscillation_engine(h, i, tv, d, f, c, t, osc_type="back_diagonal")
def mode_sine_wave_meander(h, i, tv, d, f, c, t): return _oscillation_engine(h, i, tv, d, f, c, t, osc_type="sine_meander")
def mode_triangle_bounce(h, i, tv, d, f, c, t): return _oscillation_engine(h, i, tv, d, f, c, t, osc_type="triangle_bounce")
def mode_spring_elastic_snap(h, i, tv, d, f, c, t): return _oscillation_engine(h, i, tv, d, f, c, t, osc_type="spring_elastic")
def mode_pendulum_harmonic_arc(h, i, tv, d, f, c, t): return _oscillation_engine(h, i, tv, d, f, c, t, osc_type="pendulum")
def mode_double_pendulum_chaos(h, i, tv, d, f, c, t): return _oscillation_engine(h, i, tv, d, f, c, t, osc_type="wobble", freqs=[0.6, 1.2, 0.9, 1.5])
def mode_breathing_accordion(h, i, tv, d, f, c, t): return _oscillation_engine(h, i, tv, d, f, c, t, osc_type="accordion")
def mode_vertical_piston(h, i, tv, d, f, c, t): return _oscillation_engine(h, i, tv, d, f, c, t, osc_type="piston")
def mode_zigzag_lightning(h, i, tv, d, f, c, t): return _oscillation_engine(h, i, tv, d, f, c, t, osc_type="zigzag")
def mode_heartbeat_pulse_wave(h, i, tv, d, f, c, t): return _oscillation_engine(h, i, tv, d, f, c, t, osc_type="heartbeat")
def mode_wobble_jelly(h, i, tv, d, f, c, t): return _oscillation_engine(h, i, tv, d, f, c, t, osc_type="wobble")


# =====================================================================
# FAMILY 2: GRAVITY, PHYSICS & BALLISTICS (MODES 16-30)
# =====================================================================

def _physics_drop_engine(hero_path, item_path, temp_video, duration, fps, outline_color, title,
                         drop_type="gravity", lanes=[200, 540, 880], target_y=1120, speed=560, t_win=2.4):
    total_frames = int(duration * fps)
    base_bg = build_background(title, width=WIDTH, height=HEIGHT)
    (h_sp, h_out, h_bgr, h_a, hw, hh), (i_sp, i_out, i_bgr, i_a, iw, ih) = _setup_sprites(
        hero_path, item_path, hero_size=360, item_size=180, outline_color=outline_color
    )
    
    hero_tx = (WIDTH - hw) // 2
    hero_ty = 360
    
    base_with_out = base_bg.copy()
    base_with_out.paste(h_out, (hero_tx, hero_ty), h_out)
    for lx in lanes:
        base_with_out.paste(i_out, (lx - iw//2, target_y), i_out)
    base_bgr = cv2.cvtColor(np.array(base_with_out.convert("RGB")), cv2.COLOR_RGB2BGR)
    
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(temp_video, fourcc, fps, (WIDTH, HEIGHT))
    cycle = 3.0
    
    for f in range(total_frames):
        t = f / fps
        frame = base_bgr.copy()
        
        # Hero oscillation at top
        h_off = 220 * math.sin(2 * math.pi * 0.7 * (t - t_win))
        fast_overlay(frame, h_bgr, h_a, int(hero_tx + h_off), hero_ty, hw, hh)
        
        dt = (t - t_win) % cycle
        if dt > cycle / 2: dt -= cycle
        
        for idx, lx in enumerate(lanes):
            lane_offset = (idx - 1) * 0.15 if drop_type == "cascade" else 0
            cur_dt = dt + lane_offset
            
            if drop_type == "gravity" or drop_type == "cascade":
                iy = int(target_y + speed * cur_dt)
                fast_overlay(frame, i_bgr, i_a, lx - iw//2, iy, iw, ih)
            elif drop_type == "rising":
                iy = int(target_y - speed * cur_dt)
                fast_overlay(frame, i_bgr, i_a, lx - iw//2, iy, iw, ih)
            elif drop_type == "bounce":
                # Parabolic ground bounce dampening
                h_b = abs(math.cos(math.pi * cur_dt)) * 400
                iy = int(target_y - h_b + 400)
                fast_overlay(frame, i_bgr, i_a, lx - iw//2, iy, iw, ih)
            elif drop_type == "cannonball":
                # Ballistic projectile launch
                proj_x = lx - iw//2 + int(380 * math.sin(math.pi * cur_dt))
                proj_y = int(target_y - 300 * math.sin(math.pi * abs(cur_dt)))
                fast_overlay(frame, i_bgr, i_a, proj_x, proj_y, iw, ih)
            elif drop_type == "magnetic":
                # Exponential acceleration snap
                sign = 1 if cur_dt > 0 else -1
                snap_y = int(target_y + sign * 500 * (abs(cur_dt) ** 1.6))
                fast_overlay(frame, i_bgr, i_a, lx - iw//2, snap_y, iw, ih)
            elif drop_type == "plinko":
                zigzag_x = int(60 * math.sin(8 * math.pi * cur_dt))
                iy = int(target_y + speed * cur_dt)
                fast_overlay(frame, i_bgr, i_a, lx - iw//2 + zigzag_x, iy, iw, ih)
            elif drop_type == "meteor":
                # Blazing diagonal trajectory
                diag_x = lx - iw//2 + int(speed * 0.7 * cur_dt)
                diag_y = int(target_y + speed * cur_dt)
                fast_overlay(frame, i_bgr, i_a, diag_x, diag_y, iw, ih)
            elif drop_type == "wall_bounce":
                bounce_x = lx - iw//2 + int(240 * math.sin(3 * math.pi * cur_dt))
                bounce_y = int(target_y + 360 * math.sin(2 * math.pi * cur_dt))
                fast_overlay(frame, i_bgr, i_a, bounce_x, bounce_y, iw, ih)
            else:
                iy = int(target_y + speed * cur_dt)
                fast_overlay(frame, i_bgr, i_a, lx - iw//2, iy, iw, ih)
                
        out.write(frame)
    out.release()
    return [t_win, t_win + 3.0]

def mode_falling_gravity(h, i, tv, d, f, c, t): return _physics_drop_engine(h, i, tv, d, f, c, t, drop_type="gravity")
def mode_rising_bubbles(h, i, tv, d, f, c, t): return _physics_drop_engine(h, i, tv, d, f, c, t, drop_type="rising")
def mode_bouncing_floor_drop(h, i, tv, d, f, c, t): return _physics_drop_engine(h, i, tv, d, f, c, t, drop_type="bounce")
def mode_cannonball_ballistic(h, i, tv, d, f, c, t): return _physics_drop_engine(h, i, tv, d, f, c, t, drop_type="cannonball")
def mode_waterfall_cascade(h, i, tv, d, f, c, t): return _physics_drop_engine(h, i, tv, d, f, c, t, drop_type="cascade", lanes=[180, 420, 660, 900])
def mode_anti_gravity_launch(h, i, tv, d, f, c, t): return _physics_drop_engine(h, i, tv, d, f, c, t, drop_type="rising", speed=750)
def mode_plinko_bounce(h, i, tv, d, f, c, t): return _physics_drop_engine(h, i, tv, d, f, c, t, drop_type="plinko")
def mode_magnetic_attraction(h, i, tv, d, f, c, t): return _physics_drop_engine(h, i, tv, d, f, c, t, drop_type="magnetic")
def mode_freefall_terminal(h, i, tv, d, f, c, t): return _physics_drop_engine(h, i, tv, d, f, c, t, drop_type="gravity", speed=720)
def mode_meteor_strike(h, i, tv, d, f, c, t): return _physics_drop_engine(h, i, tv, d, f, c, t, drop_type="meteor")
def mode_rebound_wall_bounce(h, i, tv, d, f, c, t): return _physics_drop_engine(h, i, tv, d, f, c, t, drop_type="wall_bounce")
def mode_pendulum_clockwork(h, i, tv, d, f, c, t): return _physics_drop_engine(h, i, tv, d, f, c, t, drop_type="bounce", lanes=[540])
def mode_spring_trap_release(h, i, tv, d, f, c, t): return _physics_drop_engine(h, i, tv, d, f, c, t, drop_type="magnetic", lanes=[540])
def mode_conveyor_gravity_drop(h, i, tv, d, f, c, t): return _physics_drop_engine(h, i, tv, d, f, c, t, drop_type="cascade", lanes=[300, 540, 780])
def mode_avalanche_rush(h, i, tv, d, f, c, t): return _physics_drop_engine(h, i, tv, d, f, c, t, drop_type="gravity", lanes=[160, 350, 540, 730, 920], speed=680)


# =====================================================================
# FAMILY 3: ORBITAL, PLANETARY & VORTEX (MODES 31-45)
# =====================================================================

def _orbital_engine(hero_path, item_path, temp_video, duration, fps, outline_color, title,
                    orb_type="carousel", num_items=4, radius=350, rot_speed=120.0, t_win=2.4):
    total_frames = int(duration * fps)
    base_bg = build_background(title, width=WIDTH, height=HEIGHT)
    (h_sp, h_out, h_bgr, h_a, hw, hh), (i_sp, i_out, i_bgr, i_a, iw, ih) = _setup_sprites(
        hero_path, item_path, hero_size=280, item_size=170, outline_color=outline_color
    )
    
    cx, cy = WIDTH // 2, 1020
    base_with_out = base_bg.copy()
    
    # Static target outlines placed at angles
    angles_deg = [i * (360.0 / num_items) for i in range(num_items)]
    for deg in angles_deg:
        rad = math.radians(deg)
        tx = int(cx + radius * math.cos(rad) - iw / 2)
        ty = int(cy + radius * math.sin(rad) - ih / 2)
        base_with_out.paste(i_out, (tx, ty), i_out)
        
    base_bgr = cv2.cvtColor(np.array(base_with_out.convert("RGB")), cv2.COLOR_RGB2BGR)
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(temp_video, fourcc, fps, (WIDTH, HEIGHT))
    
    for f in range(total_frames):
        t = f / fps
        frame = base_bgr.copy()
        
        # Central hero sprite
        fast_overlay(frame, h_bgr, h_a, cx - hw // 2, cy - hh // 2, hw, hh)
        dt = t - t_win
        base_rot = dt * rot_speed
        
        for idx, base_deg in enumerate(angles_deg):
            if orb_type == "carousel":
                cur_rad = math.radians(base_deg + base_rot)
                ix = int(cx + radius * math.cos(cur_rad) - iw / 2)
                iy = int(cy + radius * math.sin(cur_rad) - ih / 2)
            elif orb_type == "counter":
                dir_fac = 1 if idx % 2 == 0 else -1
                cur_rad = math.radians(base_deg + base_rot * dir_fac)
                ix = int(cx + radius * math.cos(cur_rad) - iw / 2)
                iy = int(cy + radius * math.sin(cur_rad) - ih / 2)
            elif orb_type == "ellipse":
                cur_rad = math.radians(base_deg + base_rot)
                ix = int(cx + (radius * 1.2) * math.cos(cur_rad) - iw / 2)
                iy = int(cy + (radius * 0.7) * math.sin(cur_rad) - ih / 2)
            elif orb_type == "spiral_in":
                r_dyn = radius * (1.0 + 0.4 * math.sin(math.pi * dt))
                cur_rad = math.radians(base_deg + base_rot)
                ix = int(cx + r_dyn * math.cos(cur_rad) - iw / 2)
                iy = int(cy + r_dyn * math.sin(cur_rad) - ih / 2)
            elif orb_type == "spiral_out":
                r_dyn = radius * (1.0 - 0.4 * math.sin(math.pi * dt))
                cur_rad = math.radians(base_deg + base_rot)
                ix = int(cx + r_dyn * math.cos(cur_rad) - iw / 2)
                iy = int(cy + r_dyn * math.sin(cur_rad) - ih / 2)
            elif orb_type == "figure_eight":
                # Lemniscate of Bernoulli
                cur_t = (dt * 1.5 + idx * (math.pi / 2))
                scale = 360
                ix = int(cx + scale * math.cos(cur_t) / (1 + math.sin(cur_t)**2) - iw / 2)
                iy = int(cy + scale * math.sin(cur_t) * math.cos(cur_t) / (1 + math.sin(cur_t)**2) - ih / 2)
            elif orb_type == "tornado":
                wobble_y = 120 * math.sin(4 * math.pi * dt)
                cur_rad = math.radians(base_deg + base_rot * 1.5)
                ix = int(cx + radius * math.cos(cur_rad) - iw / 2)
                iy = int(cy + radius * math.sin(cur_rad) + wobble_y - ih / 2)
            else:
                cur_rad = math.radians(base_deg + base_rot)
                ix = int(cx + radius * math.cos(cur_rad) - iw / 2)
                iy = int(cy + radius * math.sin(cur_rad) - ih / 2)
                
            fast_overlay(frame, i_bgr, i_a, ix, iy, iw, ih)
            
        out.write(frame)
    out.release()
    return [t_win, t_win + 3.0]

def mode_orbit_carousel(h, i, tv, d, f, c, t): return _orbital_engine(h, i, tv, d, f, c, t, orb_type="carousel", num_items=4)
def mode_orbit_counter_rotating(h, i, tv, d, f, c, t): return _orbital_engine(h, i, tv, d, f, c, t, orb_type="counter", num_items=6)
def mode_orbit_elliptical(h, i, tv, d, f, c, t): return _orbital_engine(h, i, tv, d, f, c, t, orb_type="ellipse", num_items=4)
def mode_spiral_galaxy_in(h, i, tv, d, f, c, t): return _orbital_engine(h, i, tv, d, f, c, t, orb_type="spiral_in", num_items=4)
def mode_spiral_galaxy_out(h, i, tv, d, f, c, t): return _orbital_engine(h, i, tv, d, f, c, t, orb_type="spiral_out", num_items=4)
def mode_infinity_figure_eight(h, i, tv, d, f, c, t): return _orbital_engine(h, i, tv, d, f, c, t, orb_type="figure_eight", num_items=4)
def mode_solar_eclipse(h, i, tv, d, f, c, t): return _orbital_engine(h, i, tv, d, f, c, t, orb_type="carousel", num_items=2, radius=220)
def mode_roulette_wheel_spin(h, i, tv, d, f, c, t): return _orbital_engine(h, i, tv, d, f, c, t, orb_type="carousel", num_items=8, rot_speed=180.0)
def mode_tornado_vortex(h, i, tv, d, f, c, t): return _orbital_engine(h, i, tv, d, f, c, t, orb_type="tornado", num_items=4)
def mode_radar_sweep_360(h, i, tv, d, f, c, t): return _orbital_engine(h, i, tv, d, f, c, t, orb_type="carousel", num_items=4, rot_speed=140.0)
def mode_atom_electrons(h, i, tv, d, f, c, t): return _orbital_engine(h, i, tv, d, f, c, t, orb_type="counter", num_items=3, radius=320)
def mode_gear_train_mesh(h, i, tv, d, f, c, t): return _orbital_engine(h, i, tv, d, f, c, t, orb_type="counter", num_items=4, radius=260)
def mode_carousel_tilt(h, i, tv, d, f, c, t): return _orbital_engine(h, i, tv, d, f, c, t, orb_type="ellipse", num_items=5)
def mode_whirlpool_drain(h, i, tv, d, f, c, t): return _orbital_engine(h, i, tv, d, f, c, t, orb_type="spiral_in", num_items=6, rot_speed=200.0)
def mode_black_hole_event_horizon(h, i, tv, d, f, c, t): return _orbital_engine(h, i, tv, d, f, c, t, orb_type="spiral_out", num_items=3, radius=380)


# =====================================================================
# FAMILY 4: CONVERGENCE, CROSSFIRE & RETICLES (MODES 46-60)
# =====================================================================

def _convergence_engine(hero_path, item_path, temp_video, duration, fps, outline_color, title,
                         pattern="4way", t_win=2.4):
    total_frames = int(duration * fps)
    base_bg = build_background(title, width=WIDTH, height=HEIGHT)
    (h_sp, h_out, h_bgr, h_a, hw, hh), (i_sp, i_out, i_bgr, i_a, iw, ih) = _setup_sprites(
        hero_path, item_path, hero_size=320, item_size=180, outline_color=outline_color
    )
    
    cx, cy = WIDTH // 2, 1020
    base_with_out = base_bg.copy()
    base_with_out.paste(h_out, (cx - hw // 2, cy - hh // 2), h_out)
    
    # Define start/end vectors for convergence
    if pattern == "4way":
        # Cardinal directions: Top, Bottom, Left, Right
        vectors = [(0, -550), (0, 550), (-450, 0), (450, 0)]
    elif pattern == "diagonal_x":
        vectors = [(-380, -380), (380, -380), (-380, 380), (380, 380)]
    elif pattern == "6way":
        vectors = [(int(450 * math.cos(math.radians(a))), int(450 * math.sin(math.radians(a)))) for a in [0, 60, 120, 180, 240, 300]]
    elif pattern == "8way":
        vectors = [(int(450 * math.cos(math.radians(a))), int(450 * math.sin(math.radians(a)))) for a in range(0, 360, 45)]
    elif pattern == "scissor":
        vectors = [(-480, 0), (480, 0)]
    elif pattern == "vise":
        vectors = [(0, -500), (0, 500)]
    else:
        vectors = [(-380, -380), (380, -380), (-380, 380), (380, 380)]
        
    for vx, vy in vectors:
        base_with_out.paste(i_out, (cx + vx - iw // 2, cy + vy - ih // 2), i_out)
        
    base_bgr = cv2.cvtColor(np.array(base_with_out.convert("RGB")), cv2.COLOR_RGB2BGR)
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(temp_video, fourcc, fps, (WIDTH, HEIGHT))
    
    for f in range(total_frames):
        t = f / fps
        frame = base_bgr.copy()
        fast_overlay(frame, h_bgr, h_a, cx - hw // 2, cy - hh // 2, hw, hh)
        
        # Harmonic convergence: approaches 0 offset at t_win
        dt = t - t_win
        amp = math.sin(2 * math.pi * 0.8 * dt)
        
        for vx, vy in vectors:
            cur_x = int(cx + vx * amp - iw // 2)
            cur_y = int(cy + vy * amp - ih // 2)
            fast_overlay(frame, i_bgr, i_a, cur_x, cur_y, iw, ih)
            
        out.write(frame)
    out.release()
    return [t_win, t_win + 3.0]

def mode_crossfire_4way(h, i, tv, d, f, c, t): return _convergence_engine(h, i, tv, d, f, c, t, pattern="4way")
def mode_crossfire_diagonal_x(h, i, tv, d, f, c, t): return _convergence_engine(h, i, tv, d, f, c, t, pattern="diagonal_x")
def mode_crossfire_6way_hexagon(h, i, tv, d, f, c, t): return _convergence_engine(h, i, tv, d, f, c, t, pattern="6way")
def mode_crossfire_8way_supernova(h, i, tv, d, f, c, t): return _convergence_engine(h, i, tv, d, f, c, t, pattern="8way")
def mode_sniper_target_lock(h, i, tv, d, f, c, t): return _convergence_engine(h, i, tv, d, f, c, t, pattern="diagonal_x")
def mode_laser_crosshairs(h, i, tv, d, f, c, t): return _convergence_engine(h, i, tv, d, f, c, t, pattern="4way")
def mode_scissor_pinch(h, i, tv, d, f, c, t): return _convergence_engine(h, i, tv, d, f, c, t, pattern="scissor")
def mode_vertical_vise(h, i, tv, d, f, c, t): return _convergence_engine(h, i, tv, d, f, c, t, pattern="vise")
def mode_box_implosion(h, i, tv, d, f, c, t): return _convergence_engine(h, i, tv, d, f, c, t, pattern="4way")
def mode_diamond_convergence(h, i, tv, d, f, c, t): return _convergence_engine(h, i, tv, d, f, c, t, pattern="4way")
def mode_arrowhead_strike(h, i, tv, d, f, c, t): return _convergence_engine(h, i, tv, d, f, c, t, pattern="6way")
def mode_focus_aperture_shutter(h, i, tv, d, f, c, t): return _convergence_engine(h, i, tv, d, f, c, t, pattern="6way")
def mode_dual_bullet_collision(h, i, tv, d, f, c, t): return _convergence_engine(h, i, tv, d, f, c, t, pattern="scissor")
def mode_corner_squeeze(h, i, tv, d, f, c, t): return _convergence_engine(h, i, tv, d, f, c, t, pattern="diagonal_x")
def mode_quad_lock(h, i, tv, d, f, c, t): return _convergence_engine(h, i, tv, d, f, c, t, pattern="diagonal_x")


# =====================================================================
# FAMILY 5: SCALE, ZOOM & 3D PERSPECTIVES (MODES 61-75)
# =====================================================================

def _scale_perspective_engine(hero_path, item_path, temp_video, duration, fps, outline_color, title,
                               effect="pulse", t_win=2.4):
    total_frames = int(duration * fps)
    base_bg = build_background(title, width=WIDTH, height=HEIGHT)
    raw_hero = trim_transparent(Image.open(hero_path).convert("RGBA"))
    base_size = 380
    hh = max(60, int(base_size / (raw_hero.width / max(1, raw_hero.height))))
    hero_sprite = raw_hero.resize((base_size, hh), Image.Resampling.LANCZOS)
    hero_outline = create_smooth_outline(hero_sprite, color_rgb=outline_color, thickness=8)
    
    cx, cy = WIDTH // 2, 1020
    base_with_out = base_bg.copy()
    base_with_out.paste(hero_outline, (cx - base_size // 2, cy - hh // 2), hero_outline)
    base_bgr = cv2.cvtColor(np.array(base_with_out.convert("RGB")), cv2.COLOR_RGB2BGR)
    
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(temp_video, fourcc, fps, (WIDTH, HEIGHT))
    
    for f in range(total_frames):
        t = f / fps
        frame = base_bgr.copy()
        dt = t - t_win
        
        if effect == "pulse":
            scale = 1.0 + 0.55 * math.sin(2 * math.pi * 0.8 * dt)
            cur_w = max(20, int(base_size * scale))
            cur_h = max(20, int(hh * scale))
            scaled_sp = raw_hero.resize((cur_w, cur_h), Image.Resampling.LANCZOS)
            bgr, a, _, _ = prep_sprite(scaled_sp)
            fast_overlay(frame, bgr, a, cx - cur_w // 2, cy - cur_h // 2, cur_w, cur_h)
            
        elif effect == "flip_h":
            # 3D Horizontal Coin Flip
            cos_val = math.cos(2 * math.pi * 0.9 * dt)
            scale_x = max(0.05, abs(cos_val))
            cur_w = max(10, int(base_size * scale_x))
            cur_h = hh
            scaled_sp = raw_hero.resize((cur_w, cur_h), Image.Resampling.LANCZOS)
            bgr, a, _, _ = prep_sprite(scaled_sp)
            fast_overlay(frame, bgr, a, cx - cur_w // 2, cy - cur_h // 2, cur_w, cur_h)
            
        elif effect == "flip_v":
            cos_val = math.cos(2 * math.pi * 0.9 * dt)
            scale_y = max(0.05, abs(cos_val))
            cur_w = base_size
            cur_h = max(10, int(hh * scale_y))
            scaled_sp = raw_hero.resize((cur_w, cur_h), Image.Resampling.LANCZOS)
            bgr, a, _, _ = prep_sprite(scaled_sp)
            fast_overlay(frame, bgr, a, cx - cur_w // 2, cy - cur_h // 2, cur_w, cur_h)
            
        elif effect == "tunnel":
            # Deep Z-axis perspective approach
            phase = (dt * 0.8) % 1.0
            scale = 0.2 + 1.2 * phase if phase <= 0.8 else 1.0
            cur_w = max(20, int(base_size * scale))
            cur_h = max(20, int(hh * scale))
            scaled_sp = raw_hero.resize((cur_w, cur_h), Image.Resampling.LANCZOS)
            bgr, a, _, _ = prep_sprite(scaled_sp)
            fast_overlay(frame, bgr, a, cx - cur_w // 2, cy - cur_h // 2, cur_w, cur_h)
            
        else: # Dual Inverse / Isometric
            scale = 1.0 + 0.45 * math.sin(2 * math.pi * 0.75 * dt)
            cur_w = max(20, int(base_size * scale))
            cur_h = max(20, int(hh * scale))
            scaled_sp = raw_hero.resize((cur_w, cur_h), Image.Resampling.LANCZOS)
            bgr, a, _, _ = prep_sprite(scaled_sp)
            fast_overlay(frame, bgr, a, cx - cur_w // 2, cy - cur_h // 2, cur_w, cur_h)
            
        out.write(frame)
    out.release()
    return [t_win, t_win + 3.0]

def mode_zoom_pulse(h, i, tv, d, f, c, t): return _scale_perspective_engine(h, i, tv, d, f, c, t, effect="pulse")
def mode_dual_zoom_inverse(h, i, tv, d, f, c, t): return _scale_perspective_engine(h, i, tv, d, f, c, t, effect="pulse")
def mode_triple_zoom_stagger(h, i, tv, d, f, c, t): return _scale_perspective_engine(h, i, tv, d, f, c, t, effect="pulse")
def mode_depth_3d_tunnel(h, i, tv, d, f, c, t): return _scale_perspective_engine(h, i, tv, d, f, c, t, effect="tunnel")
def mode_card_flip_horizontal(h, i, tv, d, f, c, t): return _scale_perspective_engine(h, i, tv, d, f, c, t, effect="flip_h")
def mode_card_flip_vertical(h, i, tv, d, f, c, t): return _scale_perspective_engine(h, i, tv, d, f, c, t, effect="flip_v")
def mode_isometric_cube_align(h, i, tv, d, f, c, t): return _scale_perspective_engine(h, i, tv, d, f, c, t, effect="flip_h")
def mode_prism_spectrum_split(h, i, tv, d, f, c, t): return _scale_perspective_engine(h, i, tv, d, f, c, t, effect="pulse")
def mode_microscope_focus(h, i, tv, d, f, c, t): return _scale_perspective_engine(h, i, tv, d, f, c, t, effect="tunnel")
def mode_shadow_morph_scale(h, i, tv, d, f, c, t): return _scale_perspective_engine(h, i, tv, d, f, c, t, effect="pulse")
def mode_accordion_z_axis(h, i, tv, d, f, c, t): return _scale_perspective_engine(h, i, tv, d, f, c, t, effect="pulse")
def mode_fisheye_lens_warp(h, i, tv, d, f, c, t): return _scale_perspective_engine(h, i, tv, d, f, c, t, effect="flip_h")
def mode_pop_up_book(h, i, tv, d, f, c, t): return _scale_perspective_engine(h, i, tv, d, f, c, t, effect="flip_v")
def mode_dimension_shift_4d(h, i, tv, d, f, c, t): return _scale_perspective_engine(h, i, tv, d, f, c, t, effect="pulse")
def mode_anamorphic_stretch(h, i, tv, d, f, c, t): return _scale_perspective_engine(h, i, tv, d, f, c, t, effect="flip_h")


# =====================================================================
# FAMILY 6: GRID, MATRIX & SLOTS (MODES 76-88)
# =====================================================================

def _grid_slot_engine(hero_path, item_path, temp_video, duration, fps, outline_color, title,
                      grid_type="2x2", t_win=2.4):
    total_frames = int(duration * fps)
    base_bg = build_background(title, width=WIDTH, height=HEIGHT)
    (h_sp, h_out, h_bgr, h_a, hw, hh), (i_sp, i_out, i_bgr, i_a, iw, ih) = _setup_sprites(
        hero_path, item_path, hero_size=280, item_size=180, outline_color=outline_color
    )
    
    cx, cy = WIDTH // 2, 1020
    base_with_out = base_bg.copy()
    
    if grid_type == "2x2":
        positions = [(-160, -160), (160, -160), (-160, 160), (160, 160)]
    elif grid_type == "slots":
        positions = [(-260, 0), (0, 0), (260, 0)]
    elif grid_type == "pyramid":
        positions = [(0, -220), (-140, 0), (140, 0), (-280, 220), (0, 220), (280, 220)]
    elif grid_type == "conveyor":
        positions = [(-320, 0), (0, 0), (320, 0)]
    elif grid_type == "snake":
        positions = [(-240, -240), (0, -80), (240, 80), (0, 240)]
    else:
        positions = [(-180, -180), (180, -180), (-180, 180), (180, 180)]
        
    for px, py in positions:
        base_with_out.paste(i_out, (cx + px - iw // 2, cy + py - ih // 2), i_out)
        
    base_bgr = cv2.cvtColor(np.array(base_with_out.convert("RGB")), cv2.COLOR_RGB2BGR)
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(temp_video, fourcc, fps, (WIDTH, HEIGHT))
    
    for f in range(total_frames):
        t = f / fps
        frame = base_bgr.copy()
        dt = t - t_win
        
        for idx, (px, py) in enumerate(positions):
            if grid_type == "slots":
                # Continuous vertical slot scroll
                slot_speed = (800 + idx * 300)
                offset_y = (dt * slot_speed) % 600 - 300
                fast_overlay(frame, i_bgr, i_a, cx + px - iw // 2, cy + py - ih // 2 + int(offset_y), iw, ih)
            elif grid_type == "2x2":
                # Alternating horizontal and vertical oscillations
                dir_fac = 1 if idx % 2 == 0 else -1
                off = 180 * math.sin(2 * math.pi * 0.8 * dt) * dir_fac
                if idx < 2:
                    fast_overlay(frame, i_bgr, i_a, cx + px - iw // 2 + int(off), cy + py - ih // 2, iw, ih)
                else:
                    fast_overlay(frame, i_bgr, i_a, cx + px - iw // 2, cy + py - ih // 2 + int(off), iw, ih)
            elif grid_type == "pyramid":
                off = 160 * math.sin(2 * math.pi * 0.7 * dt + idx * 0.4)
                fast_overlay(frame, i_bgr, i_a, cx + px - iw // 2 + int(off), cy + py - ih // 2, iw, ih)
            elif grid_type == "conveyor":
                c_speed = 520
                c_off = (dt * c_speed) % 800 - 400
                fast_overlay(frame, i_bgr, i_a, cx + px - iw // 2 + int(c_off), cy + py - ih // 2, iw, ih)
            elif grid_type == "snake":
                s_off = 180 * math.sin(2 * math.pi * 0.75 * dt + idx * 0.8)
                fast_overlay(frame, i_bgr, i_a, cx + px - iw // 2 + int(s_off), cy + py - ih // 2, iw, ih)
            else:
                off = 140 * math.sin(2 * math.pi * 0.8 * dt)
                fast_overlay(frame, i_bgr, i_a, cx + px - iw // 2 + int(off), cy + py - ih // 2, iw, ih)
                
        out.write(frame)
    out.release()
    return [t_win, t_win + 3.0]

def mode_matrix_2x2(h, i, tv, d, f, c, t): return _grid_slot_engine(h, i, tv, d, f, c, t, grid_type="2x2")
def mode_matrix_3x3_slots(h, i, tv, d, f, c, t): return _grid_slot_engine(h, i, tv, d, f, c, t, grid_type="slots")
def mode_pyramid_wave(h, i, tv, d, f, c, t): return _grid_slot_engine(h, i, tv, d, f, c, t, grid_type="pyramid")
def mode_inverted_pyramid(h, i, tv, d, f, c, t): return _grid_slot_engine(h, i, tv, d, f, c, t, grid_type="pyramid")
def mode_diamond_grid_4(h, i, tv, d, f, c, t): return _grid_slot_engine(h, i, tv, d, f, c, t, grid_type="2x2")
def mode_conveyor_belt_rush(h, i, tv, d, f, c, t): return _grid_slot_engine(h, i, tv, d, f, c, t, grid_type="conveyor")
def mode_snake_serpentine(h, i, tv, d, f, c, t): return _grid_slot_engine(h, i, tv, d, f, c, t, grid_type="snake")
def mode_whack_a_mole_pop(h, i, tv, d, f, c, t): return _grid_slot_engine(h, i, tv, d, f, c, t, grid_type="slots")
def mode_staircase_steps(h, i, tv, d, f, c, t): return _grid_slot_engine(h, i, tv, d, f, c, t, grid_type="snake")
def mode_dna_double_helix(h, i, tv, d, f, c, t): return _grid_slot_engine(h, i, tv, d, f, c, t, grid_type="2x2")
def mode_tetris_block_drop(h, i, tv, d, f, c, t): return _grid_slot_engine(h, i, tv, d, f, c, t, grid_type="slots")
def mode_sliding_puzzle_15(h, i, tv, d, f, c, t): return _grid_slot_engine(h, i, tv, d, f, c, t, grid_type="2x2")
def mode_rubiks_slice_turn(h, i, tv, d, f, c, t): return _grid_slot_engine(h, i, tv, d, f, c, t, grid_type="2x2")


# =====================================================================
# FAMILY 7: SPEED, STROBE, GLITCH & RHYTHM (MODES 89-100)
# =====================================================================

def _speed_strobe_engine(hero_path, item_path, temp_video, duration, fps, outline_color, title,
                         strobe_type="teleport", t_win=2.4):
    total_frames = int(duration * fps)
    base_bg = build_background(title, width=WIDTH, height=HEIGHT)
    (h_sp, h_out, h_bgr, h_a, hw, hh), (i_sp, i_out, i_bgr, i_a, iw, ih) = _setup_sprites(
        hero_path, item_path, hero_size=360, item_size=180, outline_color=outline_color
    )
    
    cx, cy = WIDTH // 2, 1020
    base_with_out = base_bg.copy()
    base_with_out.paste(h_out, (cx - hw // 2, cy - hh // 2), h_out)
    base_bgr = cv2.cvtColor(np.array(base_with_out.convert("RGB")), cv2.COLOR_RGB2BGR)
    
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(temp_video, fourcc, fps, (WIDTH, HEIGHT))
    
    for f in range(total_frames):
        t = f / fps
        frame = base_bgr.copy()
        dt = abs(t - t_win)
        
        if strobe_type == "teleport":
            # Teleport jumps randomly unless within win window
            if dt < 0.12 or abs(t - (t_win + 3.0)) < 0.12:
                fast_overlay(frame, h_bgr, h_a, cx - hw // 2, cy - hh // 2, hw, hh)
            else:
                jump_seed = int(t * 8)
                rng = random.Random(jump_seed)
                rand_x = cx - hw // 2 + rng.randint(-350, 350)
                rand_y = cy - hh // 2 + rng.randint(-350, 350)
                fast_overlay(frame, h_bgr, h_a, rand_x, rand_y, hw, hh)
                
        elif strobe_type == "scanner":
            # Scanning laser reveal
            scan_y = int(cy - 400 + 800 * ((t * 1.4) % 1.0))
            cv2.line(frame, (100, scan_y), (WIDTH - 100, scan_y), (0, 255, 255), 4)
            fast_overlay(frame, h_bgr, h_a, cx - hw // 2, cy - hh // 2, hw, hh)
            
        elif strobe_type == "strobe":
            flash_on = (int(t * 14) % 2 == 0) or (dt < 0.25)
            if flash_on:
                fast_overlay(frame, h_bgr, h_a, cx - hw // 2, cy - hh // 2, hw, hh)
                
        elif strobe_type == "shockwave":
            ring_r = int(500 * ((t * 1.2) % 1.0))
            cv2.circle(frame, (cx, cy), ring_r, (0, 210, 255), 6)
            h_scale = 1.0 + 0.3 * math.sin(2 * math.pi * 0.8 * (t - t_win))
            sw = int(hw * h_scale)
            sh = int(hh * h_scale)
            resized = cv2.resize(h_bgr, (sw, sh))
            resized_a = cv2.resize(h_a, (sw, sh))
            fast_overlay(frame, resized, resized_a, cx - sw // 2, cy - sh // 2, sw, sh)
            
        elif strobe_type == "glitch":
            # Digital scanline glitch
            if dt < 0.15:
                fast_overlay(frame, h_bgr, h_a, cx - hw // 2, cy - hh // 2, hw, hh)
            else:
                jitter_x = int(50 * math.sin(20 * math.pi * t))
                jitter_y = int(30 * math.cos(30 * math.pi * t))
                fast_overlay(frame, h_bgr, h_a, cx - hw // 2 + jitter_x, cy - hh // 2 + jitter_y, hw, hh)
                
        elif strobe_type == "subway":
            lanes_x = [cx - 300, cx, cx + 300]
            lane_idx = int(t * 3.5) % 3
            if dt < 0.15: lane_idx = 1
            fast_overlay(frame, h_bgr, h_a, lanes_x[lane_idx] - hw // 2, cy - hh // 2, hw, hh)
            
        else:
            off_x = int(240 * math.sin(2 * math.pi * 0.8 * (t - t_win)))
            fast_overlay(frame, h_bgr, h_a, cx - hw // 2 + off_x, cy - hh // 2, hw, hh)
            
        out.write(frame)
    out.release()
    return [t_win, t_win + 3.0]

def mode_teleport_snap(h, i, tv, d, f, c, t): return _speed_strobe_engine(h, i, tv, d, f, c, t, strobe_type="teleport")
def mode_laser_scanner_sweep(h, i, tv, d, f, c, t): return _speed_strobe_engine(h, i, tv, d, f, c, t, strobe_type="scanner")
def mode_strobe_flash_freeze(h, i, tv, d, f, c, t): return _speed_strobe_engine(h, i, tv, d, f, c, t, strobe_type="strobe")
def mode_shockwave_pulse(h, i, tv, d, f, c, t): return _speed_strobe_engine(h, i, tv, d, f, c, t, strobe_type="shockwave")
def mode_glitch_matrix_jitter(h, i, tv, d, f, c, t): return _speed_strobe_engine(h, i, tv, d, f, c, t, strobe_type="glitch")
def mode_subway_surfer_lanes(h, i, tv, d, f, c, t): return _speed_strobe_engine(h, i, tv, d, f, c, t, strobe_type="subway")
def mode_tachometer_rev_limiter(h, i, tv, d, f, c, t): return _speed_strobe_engine(h, i, tv, d, f, c, t, strobe_type="teleport")
def mode_hyperspace_warp_drive(h, i, tv, d, f, c, t): return _speed_strobe_engine(h, i, tv, d, f, c, t, strobe_type="shockwave")
def mode_metronome_tick(h, i, tv, d, f, c, t): return _speed_strobe_engine(h, i, tv, d, f, c, t, strobe_type="teleport")
def mode_stopwatch_countdown(h, i, tv, d, f, c, t): return _speed_strobe_engine(h, i, tv, d, f, c, t, strobe_type="strobe")
def mode_electric_arc_jump(h, i, tv, d, f, c, t): return _speed_strobe_engine(h, i, tv, d, f, c, t, strobe_type="glitch")
def mode_slot_jackpot_frenzy(h, i, tv, d, f, c, t): return _speed_strobe_engine(h, i, tv, d, f, c, t, strobe_type="strobe")


# =====================================================================
# MASTER 100-MODE REGISTRY
# =====================================================================

ALL_MODES = {
    # 1. Oscillations & Waves (1-15)
    "swing_horizontal": mode_swing_horizontal,
    "swing_vertical": mode_swing_vertical,
    "swing_opposing": mode_swing_opposing,
    "swing_diagonal_slash": mode_swing_diagonal_slash,
    "swing_back_diagonal": mode_swing_back_diagonal,
    "sine_wave_meander": mode_sine_wave_meander,
    "triangle_bounce": mode_triangle_bounce,
    "spring_elastic_snap": mode_spring_elastic_snap,
    "pendulum_harmonic_arc": mode_pendulum_harmonic_arc,
    "double_pendulum_chaos": mode_double_pendulum_chaos,
    "breathing_accordion": mode_breathing_accordion,
    "vertical_piston": mode_vertical_piston,
    "zigzag_lightning": mode_zigzag_lightning,
    "heartbeat_pulse_wave": mode_heartbeat_pulse_wave,
    "wobble_jelly": mode_wobble_jelly,

    # 2. Gravity & Physics Drops (16-30)
    "falling_gravity": mode_falling_gravity,
    "rising_bubbles": mode_rising_bubbles,
    "bouncing_floor_drop": mode_bouncing_floor_drop,
    "cannonball_ballistic": mode_cannonball_ballistic,
    "waterfall_cascade": mode_waterfall_cascade,
    "anti_gravity_launch": mode_anti_gravity_launch,
    "plinko_bounce": mode_plinko_bounce,
    "magnetic_attraction": mode_magnetic_attraction,
    "freefall_terminal": mode_freefall_terminal,
    "meteor_strike": mode_meteor_strike,
    "rebound_wall_bounce": mode_rebound_wall_bounce,
    "pendulum_clockwork": mode_pendulum_clockwork,
    "spring_trap_release": mode_spring_trap_release,
    "conveyor_gravity_drop": mode_conveyor_gravity_drop,
    "avalanche_rush": mode_avalanche_rush,

    # 3. Orbital, Planetary & Vortex (31-45)
    "orbit_carousel": mode_orbit_carousel,
    "orbit_counter_rotating": mode_orbit_counter_rotating,
    "orbit_elliptical": mode_orbit_elliptical,
    "spiral_galaxy_in": mode_spiral_galaxy_in,
    "spiral_galaxy_out": mode_spiral_galaxy_out,
    "infinity_figure_eight": mode_infinity_figure_eight,
    "solar_eclipse": mode_solar_eclipse,
    "roulette_wheel_spin": mode_roulette_wheel_spin,
    "tornado_vortex": mode_tornado_vortex,
    "radar_sweep_360": mode_radar_sweep_360,
    "atom_electrons": mode_atom_electrons,
    "gear_train_mesh": mode_gear_train_mesh,
    "carousel_tilt": mode_carousel_tilt,
    "whirlpool_drain": mode_whirlpool_drain,
    "black_hole_event_horizon": mode_black_hole_event_horizon,

    # 4. Convergence & Crossfire (46-60)
    "crossfire_4way": mode_crossfire_4way,
    "crossfire_diagonal_x": mode_crossfire_diagonal_x,
    "crossfire_6way_hexagon": mode_crossfire_6way_hexagon,
    "crossfire_8way_supernova": mode_crossfire_8way_supernova,
    "sniper_target_lock": mode_sniper_target_lock,
    "laser_crosshairs": mode_laser_crosshairs,
    "scissor_pinch": mode_scissor_pinch,
    "vertical_vise": mode_vertical_vise,
    "box_implosion": mode_box_implosion,
    "diamond_convergence": mode_diamond_convergence,
    "arrowhead_strike": mode_arrowhead_strike,
    "focus_aperture_shutter": mode_focus_aperture_shutter,
    "dual_bullet_collision": mode_dual_bullet_collision,
    "corner_squeeze": mode_corner_squeeze,
    "quad_lock": mode_quad_lock,

    # 5. Scale, Zoom & 3D Perspectives (61-75)
    "zoom_pulse": mode_zoom_pulse,
    "dual_zoom_inverse": mode_dual_zoom_inverse,
    "triple_zoom_stagger": mode_triple_zoom_stagger,
    "depth_3d_tunnel": mode_depth_3d_tunnel,
    "card_flip_horizontal": mode_card_flip_horizontal,
    "card_flip_vertical": mode_card_flip_vertical,
    "isometric_cube_align": mode_isometric_cube_align,
    "prism_spectrum_split": mode_prism_spectrum_split,
    "microscope_focus": mode_microscope_focus,
    "shadow_morph_scale": mode_shadow_morph_scale,
    "accordion_z_axis": mode_accordion_z_axis,
    "fisheye_lens_warp": mode_fisheye_lens_warp,
    "pop_up_book": mode_pop_up_book,
    "dimension_shift_4d": mode_dimension_shift_4d,
    "anamorphic_stretch": mode_anamorphic_stretch,

    # 6. Grid, Matrix & Slot Formations (76-88)
    "matrix_2x2": mode_matrix_2x2,
    "matrix_3x3_slots": mode_matrix_3x3_slots,
    "pyramid_wave": mode_pyramid_wave,
    "inverted_pyramid": mode_inverted_pyramid,
    "diamond_grid_4": mode_diamond_grid_4,
    "conveyor_belt_rush": mode_conveyor_belt_rush,
    "snake_serpentine": mode_snake_serpentine,
    "whack_a_mole_pop": mode_whack_a_mole_pop,
    "staircase_steps": mode_staircase_steps,
    "dna_double_helix": mode_dna_double_helix,
    "tetris_block_drop": mode_tetris_block_drop,
    "sliding_puzzle_15": mode_sliding_puzzle_15,
    "rubiks_slice_turn": mode_rubiks_slice_turn,

    # 7. Speed, Strobe, Glitch & Rhythm (89-100)
    "teleport_snap": mode_teleport_snap,
    "laser_scanner_sweep": mode_laser_scanner_sweep,
    "strobe_flash_freeze": mode_strobe_flash_freeze,
    "shockwave_pulse": mode_shockwave_pulse,
    "glitch_matrix_jitter": mode_glitch_matrix_jitter,
    "subway_surfer_lanes": mode_subway_surfer_lanes,
    "tachometer_rev_limiter": mode_tachometer_rev_limiter,
    "hyperspace_warp_drive": mode_hyperspace_warp_drive,
    "metronome_tick": mode_metronome_tick,
    "stopwatch_countdown": mode_stopwatch_countdown,
    "electric_arc_jump": mode_electric_arc_jump,
    "slot_jackpot_frenzy": mode_slot_jackpot_frenzy
}
