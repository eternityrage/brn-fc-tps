"""
BrainFocus Taps (brn-fc-tps) - Automated Daily Reel Publisher
Generates a fresh viral puzzle reel using dynamic 3D assets and 22 gameplay modes,
publishes directly to Facebook Reels with an engagement pinned comment,
and optionally publishes to Instagram Reels.
"""
import os
import sys
import json
import time
import random
import glob
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load local environment if present
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path, override=True)

from upload.upload_facebook import upload_to_facebook
from upload.upload_instagram import upload_to_instagram
from master_factory import (
    ALL_MODES,
    generate_reel_by_mode,
    get_random_pair,
    get_catalog
)

PUBLISHED_LOG = "published_reels.json"

VIRAL_TITLES = [
    "BrainFocus Challenge: Can You Stop It? 🎯",
    "99% Fail This Reflex Test! Can You Pause in Time? ⚡",
    "Ultimate Eye-Hand Coordination Challenge! 🧠",
    "Stop Inside the Shadow! Only 1% Get It First Try 🏆",
    "Impossible Pause Challenge! How Fast Are Your Reflexes? ⏱️",
    "Test Your Brain Focus: Freeze the Exact Frame! 🎯",
    "Can You Hit 100% Match? Tap Pause to Win! 🧩"
]

VIRAL_HOOKS = [
    "🎯 99% of people fail to stop this in the outline! Can you do it on the first try?",
    "⚡ Tap pause when the shape hits the exact outline! Prove your reflex in the comments!",
    "🧠 Ultimate Mind Focus Test: Stop inside the shadow! What was your reaction time?",
    "🔥 Warning: This puzzle is harder than it looks! Double tap if you hit it!",
    "🏆 Test your hand-eye coordination! Pause at the exact frame to win!",
    "⏳ Only 1 in 100 people can freeze the frame precisely in the middle!",
    "✨ Harmonic Reflex Challenge! Can you spot when all pieces align?",
    "🧩 Stop the object right in its shadow! Did you get it?"
]

PINNED_COMMENTS = [
    "📌 CHALLENGE RULES:\n1. Tap pause when the shape fits exactly inside the outline! 🎯\n2. Drop a screenshot of your attempt below 👇\n3. Be honest: Did you get it on your 1st try? (Only 1% can!) 🏆",
    "🎯 REFLEX TEST: How many attempts did it take you to get a 100% perfect match? Drop your screenshot below 👇 #BrainFocus",
    "🧠 FOCUS CHALLENGE:\n✅ Level 1: Hit pause in the shadow\n✅ Level 2: Screenshot your proof\n✅ Level 3: Tag a friend who thinks they have faster reflexes! 👇",
    "⚡ DID YOU PAUSE IN TIME? Post your screenshot in the comments! If you nailed it on the 1st try, you have top 1% reaction speed! 🚀",
    "👇 COMMENT YOUR RESULT: Pause the video at the exact millisecond when the outline matches. Show us your screenshot! 🎯"
]

VIRAL_HASHTAGS = [
    "#BrainFocus",
    "#BrainFocusTaps",
    "#BrainPuzzle",
    "#MindTwist",
    "#FocusChallenge",
    "#ReflexTest",
    "#StopMotionChallenge",
    "#BrainTeaser",
    "#ViralReels",
    "#MindGames",
    "#DailyChallenge",
    "#PuzzleReel",
    "#CoordinationTest",
    "#PauseChallenge"
]


def generate_viral_metadata(mode_name, hero_name, item_name):
    title = random.choice(VIRAL_TITLES)
    hook = random.choice(VIRAL_HOOKS)
    pinned_comment = random.choice(PINNED_COMMENTS)
    tags = " ".join(random.sample(VIRAL_HASHTAGS, k=min(9, len(VIRAL_HASHTAGS))))
    
    formatted_mode = mode_name.replace('_', ' ').title()
    formatted_hero = hero_name.replace('_', ' ').title()
    formatted_item = item_name.replace('_', ' ').title()
    
    description = (
        f"{hook}\n\n"
        f"🎮 Mode: {formatted_mode}\n"
        f"🔍 Objects: {formatted_hero} & {formatted_item}\n\n"
        f"⚡ Test your timing! Pause when the object aligns perfectly with the glowing outline.\n"
        f"Drop your screenshot or attempt in the comments below! 👇\n\n"
        f"{tags}"
    )
    return title, description, pinned_comment


def get_published_history():
    if os.path.exists(PUBLISHED_LOG):
        try:
            with open(PUBLISHED_LOG, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []
    return []


def record_published_reel(entry):
    history = get_published_history()
    history.append(entry)
    with open(PUBLISHED_LOG, 'w', encoding='utf-8') as f:
        json.dump(history, f, indent=2)


def main():
    print("=" * 60)
    print("🚀 BRAINFOCUS TAPS (brn-fc-tps) AUTO PUBLISHER STARTING")
    print(f"⏰ Current UTC Time: {datetime.utcnow().isoformat()}Z")
    print("=" * 60)

    # CLI args: mode, hero, item
    requested_mode = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] else None
    requested_hero = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] else None
    requested_item = sys.argv[3] if len(sys.argv) > 3 and sys.argv[3] else None

    # Pick Mode
    available_modes = list(ALL_MODES.keys())
    if requested_mode and requested_mode in available_modes:
        selected_mode = requested_mode
    else:
        selected_mode = random.choice(available_modes)

    # Pick Assets
    if requested_hero and requested_item:
        hero, item = requested_hero, requested_item
    else:
        h_key, i_key, _, _ = get_random_pair()
        hero = requested_hero if requested_hero else h_key
        item = requested_item if requested_item else i_key

    timestamp_str = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    out_filename = f"reel_{selected_mode}_{hero}_{item}_{timestamp_str}.mp4"

    print(f"🎯 Selected Gameplay Mode: {selected_mode}")
    print(f"📦 Selected Assets: Hero={hero}, Item={item}")

    # Generate the viral video reel (7 seconds, 30 fps)
    output_video = generate_reel_by_mode(
        hero_name=hero,
        item_name=item,
        mode_name=selected_mode,
        output_filename=out_filename,
        duration=7.0,
        fps=30
    )

    if not output_video or not os.path.exists(output_video):
        print("❌ Error: Video generation failed!")
        sys.exit(1)

    print(f"✅ Video generated successfully: {output_video}")

    # Prepare caption, metadata, and pinned comment
    title, description, pinned_comment = generate_viral_metadata(selected_mode, hero, item)
    print(f"📝 Title: {title}")
    print(f"📝 Description:\n{description}")
    print(f"📌 Pinned Comment:\n{pinned_comment}")

    publish_record = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "video_file": os.path.basename(output_video),
        "mode": selected_mode,
        "hero": hero,
        "item": item,
        "title": title,
        "pinned_comment": pinned_comment,
        "facebook": None,
        "instagram": None
    }

    # 1. Publish to Facebook Reels + Pinned Comment
    try:
        fb_result = upload_to_facebook(
            output_video,
            description,
            title=title,
            pinned_comment=pinned_comment
        )
        publish_record["facebook"] = fb_result
    except Exception as e:
        print(f"❌ Facebook upload error: {e}")
        publish_record["facebook"] = {"status": "failed", "error": str(e)}

    # 2. Publish to Instagram Reels (if configured)
    try:
        ig_caption = f"{title}\n\n{description}"
        ig_result = upload_to_instagram(output_video, caption=ig_caption)
        publish_record["instagram"] = ig_result
    except Exception as e:
        print(f"❌ Instagram upload error: {e}")
        publish_record["instagram"] = {"status": "failed", "error": str(e)}

    # Save to published history
    record_published_reel(publish_record)
    print("=" * 60)
    print("🎉 PUBLISHING PIPELINE RUN COMPLETED")
    print(f"Log updated: {PUBLISHED_LOG}")
    print("=" * 60)


if __name__ == '__main__':
    main()
