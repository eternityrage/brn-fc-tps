"""
Network Publisher for the Viral Puzzle Reel Network.
Publishes distinct, high-energy puzzle reels across all 6 thematic Facebook Pages:
1. BrainFocus Taps (1319646877895110)
2. MindMath Taps (1309712825557751)
3. BrainFog Taps (1316150674917146)
4. BrainTaps Flow (1227319627140685)
5. MindView Taps (1334005973127654)
6. MindQuiz Focus (1350182274839663)
"""
import os
import sys
import json
import time
import random
import argparse
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv

# Load local environment if present
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path, override=True)

from upload.upload_facebook import upload_to_facebook
from master_factory import generate_reel_by_mode
from engine.asset_hub import get_catalog, get_or_fetch_asset
from page_profiles import (
    ACTIVE_PAGE_IDS,
    PAGE_PROFILES,
    pick_page_assets,
    get_page_metadata
)

PUBLISHED_LOG = Path(__file__).parent / "published_reels.json"
LOCAL_TOKENS_PATH = Path(r"C:\Users\kreg9\facebook_pages_tokens.json")


def load_all_page_tokens():
    """
    Loads page tokens securely from environment secret or local file.
    Does NOT expose tokens.
    """
    tokens = {}

    # 1. Check if FACEBOOK_PAGES_JSON is in environment (used in GitHub Actions)
    env_json = os.getenv("FACEBOOK_PAGES_JSON") or os.getenv("PAGE_TOKENS_JSON")
    if env_json:
        try:
            tokens = json.loads(env_json)
        except Exception as e:
            print(f"[network] Warning parsing FACEBOOK_PAGES_JSON: {e}")

    # 2. Check local fallback file if running on host
    if not tokens and LOCAL_TOKENS_PATH.exists():
        try:
            with open(LOCAL_TOKENS_PATH, "r", encoding="utf-8") as f:
                tokens = json.load(f)
        except Exception as e:
            print(f"[network] Notice reading local tokens: {e}")

    return tokens


def get_token_for_page(page_id, loaded_tokens):
    """Retrieves access token for a specific page."""
    entry = loaded_tokens.get(page_id)
    if isinstance(entry, dict):
        return entry.get("access_token")
    elif isinstance(entry, str):
        return entry
    
    # Fallback to general token from environment
    return (
        os.getenv("FACEBOOK_ACCESS_TOKEN") or
        os.getenv("META_ACCESS_TOKEN") or
        os.getenv("META_LONG_LIVED_ACCESS_TOKEN")
    )


def record_published_reel(entry):
    history = []
    if PUBLISHED_LOG.exists():
        try:
            with open(PUBLISHED_LOG, "r", encoding="utf-8") as f:
                history = json.load(f)
        except Exception:
            history = []
    history.append(entry)
    with open(PUBLISHED_LOG, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)


def publish_for_page(page_id, loaded_tokens, override_mode=None, override_hero=None, override_item=None):
    profile = PAGE_PROFILES.get(page_id)
    if not profile:
        print(f"[network] Unknown page ID: {page_id}")
        return None

    page_name = profile["name"]
    print("\n" + "=" * 65)
    print(f"🌟 PROCESSING PAGE: {page_name} ({page_id})")
    print(f"📌 Tagline: {profile['tagline']}")
    print("=" * 65)

    access_token = get_token_for_page(page_id, loaded_tokens)
    if not access_token:
        print(f"[network] ❌ Missing access token for {page_name}")
        return None

    # Load recent history for this page to prevent consecutive repetitions
    recent_modes = []
    recent_assets = set()
    if PUBLISHED_LOG.exists():
        try:
            with open(PUBLISHED_LOG, "r", encoding="utf-8") as f:
                hist = json.load(f)
                page_hist = [h for h in hist if h.get("page_id") == page_id]
                recent_modes = [h.get("mode") for h in page_hist[-4:] if h.get("mode")]
                for h in page_hist[-12:]:
                    if h.get("hero"): recent_assets.add(h.get("hero"))
                    if h.get("item"): recent_assets.add(h.get("item"))
        except Exception:
            pass

    # Pick gameplay mode (prioritize fresh mode not used in last 4 reels of this page)
    if override_mode:
        selected_mode = override_mode
    else:
        candidate_modes = [m for m in profile["preferred_modes"] if m not in recent_modes]
        if not candidate_modes:
            candidate_modes = profile["preferred_modes"]
        selected_mode = random.choice(candidate_modes)

    # Pick 3D assets from Microsoft catalog (excluding recently used assets)
    catalog = get_catalog()
    if override_hero and override_item:
        hero, item = override_hero, override_item
    else:
        hero, item = pick_page_assets(page_id, catalog, recent_assets=recent_assets)

    # Pick outline color
    outline_color = random.choice(profile["outline_colors"])

    # Metadata (Title, Caption Hook, Pinned Challenge Comment)
    title, description, pinned_comment = get_page_metadata(page_id, selected_mode, hero, item)

    timestamp_str = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    out_filename = f"reel_{profile['slug']}_{selected_mode}_{hero}_{item}_{timestamp_str}.mp4"

    print(f"🎮 Selected Mode: {selected_mode}")
    print(f"📦 Selected 3D Assets: Hero='{hero}' | Item='{item}'")
    print(f"🎨 Theme Color: {outline_color}")
    print(f"📝 Title: {title}")
    print(f"📌 Pinned Challenge:\n{pinned_comment}\n")

    # Generate the viral video reel (7 seconds, 30 fps)
    output_video = generate_reel_by_mode(
        hero_name=hero,
        item_name=item,
        mode_name=selected_mode,
        output_filename=out_filename,
        color_name=outline_color,
        title=title,
        duration=7.0,
        fps=30
    )

    if not output_video or not os.path.exists(output_video):
        print(f"[network] ❌ Failed to generate video for {page_name}")
        return None

    print(f"[network] ✅ Video generated: {output_video}")

    publish_record = {
        "timestamp": datetime.now(timezone.utc).isoformat() + "Z",
        "page_id": page_id,
        "page_name": page_name,
        "video_file": os.path.basename(output_video),
        "mode": selected_mode,
        "hero": hero,
        "item": item,
        "title": title,
        "pinned_comment": pinned_comment,
        "facebook": None
    }

    # Upload to Facebook Reel
    try:
        fb_result = upload_to_facebook(
            output_video,
            description,
            title=title,
            pinned_comment=pinned_comment,
            target_page_id=page_id,
            target_access_token=access_token
        )
        publish_record["facebook"] = fb_result
    except Exception as e:
        print(f"[network] ❌ Facebook upload exception for {page_name}: {e}")
        publish_record["facebook"] = {"status": "failed", "error": str(e)}

    # Save to history log
    record_published_reel(publish_record)
    return publish_record


def main():
    parser = argparse.ArgumentParser(description="Multi-Page Viral Puzzle Reel Network Publisher")
    parser.add_argument("--page", help="Specific page ID or slug (e.g. brainfocus, mindmath, brainfog, braintaps_flow, mindview, mindquiz, or 'all')", default="all")
    parser.add_argument("--mode", help="Specific gameplay mode", default=None)
    parser.add_argument("--hero", help="Specific hero asset", default=None)
    parser.add_argument("--item", help="Specific item asset", default=None)

    args = parser.parse_args()

    print("=" * 65)
    print("🚀 VIRAL PUZZLE REEL NETWORK PUBLISHER STARTING")
    print(f"⏰ Current UTC Time: {datetime.now(timezone.utc).isoformat()}")
    print("=" * 65)

    tokens = load_all_page_tokens()
    print(f"[network] Loaded tokens for {len(tokens)} pages.")

    # Resolve target pages
    target_pages = []
    slug_to_id = {v["slug"]: k for k, v in PAGE_PROFILES.items()}

    if args.page == "all":
        target_pages = ACTIVE_PAGE_IDS
    elif args.page in PAGE_PROFILES:
        target_pages = [args.page]
    elif args.page.lower() in slug_to_id:
        target_pages = [slug_to_id[args.page.lower()]]
    else:
        print(f"[network] Unknown target page '{args.page}'. Available: {list(slug_to_id.keys())} or 'all'")
        sys.exit(1)

    print(f"[network] Target Pages to publish ({len(target_pages)}): {[PAGE_PROFILES[p]['name'] for p in target_pages]}")

    results = []
    for pid in target_pages:
        res = publish_for_page(
            page_id=pid,
            loaded_tokens=tokens,
            override_mode=args.mode,
            override_hero=args.hero,
            override_item=args.item
        )
        results.append(res)
        # Small delay between page publications to avoid rate limits
        if pid != target_pages[-1]:
            print("\n⏳ Pausing 5 seconds before next page...\n")
            time.sleep(5)

    print("\n" + "=" * 65)
    print("🎉 ALL TARGET PAGES PROCESSED!")
    print(f"Log updated: {PUBLISHED_LOG}")
    print("=" * 65)


if __name__ == "__main__":
    main()
