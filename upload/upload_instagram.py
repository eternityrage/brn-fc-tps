"""
Direct Resumable Instagram Reel Uploader via Meta Graph API v21.0
Includes auto-compression if > 12MB & smart container processing polling.
"""
import os
import sys
import time
import json
import requests
import pathlib
import subprocess
from dotenv import load_dotenv

env_path = pathlib.Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path, override=True)


def upload_to_instagram(video_path, caption=""):
    print("\n" + "=" * 60)
    print("📸 INSTAGRAM REEL UPLOAD (Direct Resumable Graph API v21.0)")
    print("=" * 60)

    access_token = (
        os.getenv('INSTAGRAM_ACCESS_TOKEN') or 
        os.getenv('IG_ACCESS_TOKEN') or 
        os.getenv('FACEBOOK_ACCESS_TOKEN') or 
        os.getenv('FB_ACCESS_TOKEN') or
        os.getenv('META_ACCESS_TOKEN')
    )
    user_id = os.getenv('INSTAGRAM_ACCOUNT_ID') or os.getenv('IG_USER_ID')

    if not access_token:
        print("[instagram] ⚠️ Skipping - missing access token")
        return {'status': 'skipped', 'reason': 'Missing access token', 'platform': 'instagram'}

    # Attempt to query linked IG account if page ID provided
    fb_page_id = os.getenv('FACEBOOK_PAGE_ID') or os.getenv('FB_PAGE_ID')
    if not user_id and fb_page_id:
        try:
            ig_r = requests.get(
                f"https://graph.facebook.com/v21.0/{fb_page_id}?fields=instagram_business_account&access_token={access_token}",
                timeout=15
            )
            if ig_r.status_code == 200:
                acct = ig_r.json().get('instagram_business_account')
                if acct and acct.get('id'):
                    user_id = acct['id']
                    print(f"[instagram] Discovered connected Instagram Account ID: {user_id}")
        except Exception as e:
            print(f"[instagram] Could not auto-detect IG user ID: {e}")

    if not user_id:
        print("[instagram] ⚠️ Skipping - no Instagram Business Account linked to this Page")
        return {'status': 'skipped', 'reason': 'No Instagram Business Account', 'platform': 'instagram'}

    video_path_obj = pathlib.Path(video_path)
    if not video_path_obj.exists():
        print(f"[instagram] ❌ Video file not found: {video_path}")
        return {'status': 'failed', 'error': 'Video file not found', 'platform': 'instagram'}

    upload_file_path = str(video_path_obj)
    file_size = video_path_obj.stat().st_size

    # Auto-compress video if payload > 12 MB for smooth direct transfer
    if file_size > 12 * 1024 * 1024:
        print(f"[instagram] ℹ️ File size ({file_size/(1024*1024):.2f} MB) > 12MB. Optimizing with FFmpeg...")
        compressed_path = str(video_path_obj.parent / f"ig_opt_{video_path_obj.name}")
        try:
            cmd = [
                "ffmpeg", "-y", "-i", str(video_path_obj),
                "-fs", "11M",
                "-c:v", "libx264", "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-b:a", "128k", "-ar", "44100",
                "-movflags", "+faststart",
                compressed_path
            ]
            subprocess.run(cmd, capture_output=True, check=True)
            if os.path.exists(compressed_path) and os.path.getsize(compressed_path) > 0:
                upload_file_path = compressed_path
                file_size = os.path.getsize(compressed_path)
                print(f"[instagram] ✅ Optimized size: {file_size/(1024*1024):.2f} MB")
        except Exception as comp_err:
            print(f"[instagram] ⚠️ FFmpeg optimization notice: {comp_err}")

    api_base = "https://graph.facebook.com/v21.0"

    try:
        # Step 1: Create Resumable Container
        print("[instagram] Step 1/3: Creating resumable REELS container...")
        c_params = {
            'media_type': 'REELS',
            'upload_type': 'resumable',
            'caption': caption[:2200] if caption else '',
            'access_token': access_token,
            'share_to_feed': False
        }
        c_res = requests.post(f"{api_base}/{user_id}/media", params=c_params, timeout=30)
        if c_res.status_code not in (200, 201):
            err = c_res.json().get('error', {}).get('message', c_res.text)
            raise Exception(f"Container creation failed: {err}")

        c_data = c_res.json()
        container_id = c_data.get('id')
        upload_uri = c_data.get('uri')
        print(f"[instagram] ✅ Container ID: {container_id}")

        # Step 2: Transfer Video Bytes
        print("[instagram] Step 2/3: Transferring video bytes to Meta Servers...")
        with open(upload_file_path, 'rb') as f:
            video_bytes = f.read()

        up_headers = {
            'Authorization': f'OAuth {access_token}',
            'offset': '0',
            'file_size': str(file_size),
            'Content-Type': 'video/mp4'
        }
        up_res = requests.post(upload_uri, headers=up_headers, data=video_bytes, timeout=120)
        if up_res.status_code not in (200, 201):
            err = up_res.json().get('error', {}).get('message', up_res.text) if up_res.text else 'Transfer error'
            raise Exception(f"Video binary transfer failed: {err}")

        print("[instagram] ✅ Video bytes transferred successfully!")

        # Step 3: Wait for Meta Container Processing and Publish
        print("[instagram] Step 3/3: Waiting for Meta container processing...")
        max_wait = 180
        waited = 0
        while waited < max_wait:
            time.sleep(30 if waited == 0 else 20)
            waited += 30 if waited == 0 else 20
            print(f"[instagram] Attempting publish (elapsed {waited}s)...")
            pub_res = requests.post(
                f"{api_base}/{user_id}/media_publish",
                params={'creation_id': container_id, 'access_token': access_token},
                timeout=60
            )
            if pub_res.status_code in (200, 201):
                media_id = pub_res.json().get('id', container_id)
                print(f"[instagram] 🌟 SUCCESS! Media published (ID: {media_id})")
                return {'status': 'success', 'id': media_id, 'platform': 'instagram', 'wait_s': waited}

            err_msg = ""
            try:
                err_msg = pub_res.json().get('error', {}).get('message', '')
            except Exception:
                pass
            print(f"[instagram] Still processing ({err_msg}). Retrying...")

        raise Exception(f"Publish timed out after {max_wait}s")

    except Exception as e:
        print(f"[instagram] ❌ Error: {e}")
        return {'status': 'failed', 'error': str(e), 'platform': 'instagram'}
