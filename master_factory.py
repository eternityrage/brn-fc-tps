import os
import sys
import random
import argparse
import subprocess
import glob

# Ensure clean UTF-8 on Windows
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

from engine.audio import create_synchronized_audio
from engine.modes import ALL_MODES
from engine.asset_hub import get_or_fetch_asset, get_random_pair, get_catalog

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

TITLES_POOL = [
    "CAN YOU STOP IN THE SHADOW?",
    "99% FAIL TO PAUSE IN TIME!",
    "STOP IT AT THE RIGHT MOMENT",
    "CAN YOU PAUSE PERFECTLY?",
    "TRY TO STOP AT 100% MATCH",
    "LEVEL 1: CAN YOU CATCH IT?",
    "ONLY 1% CAN HIT THE TARGET!",
    "STOP WHEN ALL PIECES LOCK!",
    "TAP TO PAUSE AND WIN!"
]

def get_clean_assets():
    pngs = glob.glob(os.path.join(ASSETS_DIR, "*.png"))
    clean = []
    for p in pngs:
        base = os.path.splitext(os.path.basename(p))[0]
        if not base.endswith("_test") and not base.endswith("_outline"):
            clean.append(base)
    return clean

def generate_reel_by_mode(hero_name, item_name, mode_name, output_filename, color_name=None, title=None, duration=8.0, fps=60):
    hero_path = get_or_fetch_asset(hero_name)
    item_path = get_or_fetch_asset(item_name)
    
    if not hero_path or not item_path:
        print(f"[ERROR] Could not resolve assets: {hero_name} or {item_name}")
        return None
        
    if mode_name not in ALL_MODES:
        mode_name = "swing_horizontal"
        
    mode_func = ALL_MODES[mode_name]
    
    if not color_name or color_name not in OUTLINE_COLORS:
        color_name = random.choice(list(OUTLINE_COLORS.keys()))
    outline_color = OUTLINE_COLORS[color_name]
    
    if not title:
        title = random.choice(TITLES_POOL)
        
    final_output = os.path.join(OUTPUT_DIR, output_filename)
    temp_video = os.path.join(OUTPUT_DIR, f"temp_{output_filename}")
    temp_audio = os.path.join(OUTPUT_DIR, f"temp_audio_{output_filename}.wav")
    
    print(f"\n[+] Rendering [{mode_name.upper()}] Reel: {output_filename}")
    print(f"Hero: {hero_name} | Item: {item_name} | Color: {color_name}")
    print(f"Title: {title}")
    
    # 1. Render Video
    win_moments = mode_func(hero_path, item_path, temp_video, duration, fps, outline_color, title)
    
    # 2. Synthesize Audio
    create_synchronized_audio(duration, win_moments, temp_audio)
    
    # 3. Mux Video + Audio with FFmpeg
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
        
    print(f"[SUCCESS] Generated: {final_output} ({round(os.path.getsize(final_output)/(1024*1024), 2)} MB)")
    return final_output

def main():
    parser = argparse.ArgumentParser(description="Master Viral Puzzle Reel Factory (22 Modes, 1,595+ Online Assets)")
    parser.add_argument("--count", type=int, default=5, help="Number of unique reels to generate")
    parser.add_argument("--mode", type=str, default="all", choices=["all"] + list(ALL_MODES.keys()), help="Gameplay Mode")
    parser.add_argument("--hero", type=str, default=None, help="Hero asset name")
    parser.add_argument("--item", type=str, default=None, help="Sub-item asset name")
    parser.add_argument("--color", type=str, default=None, help="Outline color")
    parser.add_argument("--duration", type=float, default=8.0, help="Duration in seconds")
    args = parser.parse_args()
    
    all_mode_names = list(ALL_MODES.keys())
    
    for i in range(args.count):
        chosen_mode = random.choice(all_mode_names) if args.mode == "all" else args.mode
        
        if args.hero and args.item:
            hero, item = args.hero, args.item
        else:
            h_key, i_key, _, _ = get_random_pair()
            hero = args.hero if args.hero else h_key
            item = args.item if args.item else i_key
            
        fname = f"reel_{chosen_mode}_{i+1:02d}_{hero}_{item}.mp4"
        generate_reel_by_mode(
            hero_name=hero,
            item_name=item,
            mode_name=chosen_mode,
            output_filename=fname,
            color_name=args.color,
            duration=args.duration
        )

if __name__ == "__main__":
    main()
