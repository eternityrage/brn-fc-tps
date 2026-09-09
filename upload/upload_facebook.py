"""
Facebook Reels Direct Uploader via Meta Graph API v21.0
3-step Resumable Video Reels Publishing
"""
import os
import requests
from pathlib import Path
from dotenv import load_dotenv

# Load .env if present (local dev only)
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path, override=True)


def upload_to_facebook(video_path, description, title="BrainFocus Puzzle"):
    """
    Upload video to Facebook Page as a Reel.
    
    Returns dict with upload status and details.
    """
    print("\n" + "=" * 60)
    print("📘 FACEBOOK REEL UPLOAD STARTING")
    print("=" * 60)

    # Get credentials from environment
    access_token = (
        os.getenv('FACEBOOK_ACCESS_TOKEN') or 
        os.getenv('FB_ACCESS_TOKEN') or 
        os.getenv('META_ACCESS_TOKEN') or
        os.getenv('META_LONG_LIVED_ACCESS_TOKEN')
    )
    page_id = (
        os.getenv('FACEBOOK_PAGE_ID') or 
        os.getenv('FB_PAGE_ID') or 
        os.getenv('PAGE_ID')
    )

    def mask(s):
        return f"{s[:4]}...{s[-4:]}" if s and len(s) > 8 else ("***" if s else "MISSING")

    print(f"[facebook] Target Page ID: {page_id}")
    print(f"[facebook] Access Token: {mask(access_token)}")

    if not access_token:
        print("[facebook] ⚠️ Skipping - FACEBOOK_ACCESS_TOKEN / META_ACCESS_TOKEN not set")
        return {'status': 'skipped', 'reason': 'Missing access token', 'platform': 'facebook'}

    if not page_id:
        print("[facebook] ⚠️ Skipping - FACEBOOK_PAGE_ID not set")
        return {'status': 'skipped', 'reason': 'Missing page ID', 'platform': 'facebook'}

    video_path_obj = Path(video_path)
    if not video_path_obj.exists():
        error_msg = f"Video file not found: {video_path}"
        print(f"[facebook] ❌ {error_msg}")
        return {'status': 'failed', 'error': error_msg, 'platform': 'facebook'}

    file_size = video_path_obj.stat().st_size
    file_size_mb = file_size / (1024 * 1024)
    print(f"[facebook] Video File: {video_path_obj.name} ({file_size_mb:.2f} MB)")

    api_version = "v21.0"
    base_url = f"https://graph.facebook.com/{api_version}/{page_id}/video_reels"

    try:
        # Step 1: Initialize Upload Session
        print("[facebook] Step 1/3: Initiating Reel upload session...")
        start_data = {
            'access_token': access_token,
            'upload_phase': 'start',
            'file_size': file_size
        }
        res_start = requests.post(base_url, data=start_data, timeout=30)
        if res_start.status_code != 200:
            err_text = res_start.text
            print(f"[facebook] ❌ Start Phase Error ({res_start.status_code}): {err_text}")
            return {'status': 'failed', 'error': f"Start Phase Failed: {err_text}", 'platform': 'facebook'}

        start_json = res_start.json()
        video_id = start_json.get('video_id')
        upload_url = start_json.get('upload_url')

        if not video_id or not upload_url:
            raise Exception(f"Invalid response from start phase: {start_json}")

        print(f"[facebook] Session initialized. Video ID: {video_id}")

        # Step 2: Transfer Video Binary Bytes
        print("[facebook] Step 2/3: Transferring video binary bytes to Meta servers...")
        headers = {
            'Authorization': f'OAuth {access_token}',
            'offset': '0',
            'file_size': str(file_size)
        }
        with open(video_path, 'rb') as f:
            res_transfer = requests.post(upload_url, headers=headers, data=f, timeout=600)

        if res_transfer.status_code != 200:
            err_text = res_transfer.text
            print(f"[facebook] ❌ Transfer Phase Error ({res_transfer.status_code}): {err_text}")
            return {'status': 'failed', 'error': f"Transfer Phase Failed: {err_text}", 'platform': 'facebook'}

        print("[facebook] Binary upload complete!")

        # Step 3: Finish & Publish Reel
        print("[facebook] Step 3/3: Publishing Reel on Facebook Page...")
        finish_data = {
            'access_token': access_token,
            'upload_phase': 'finish',
            'video_id': video_id,
            'title': title,
            'description': description,
            'video_state': 'PUBLISHED'
        }
        res_finish = requests.post(base_url, data=finish_data, timeout=60)
        finish_json = res_finish.json()

        if res_finish.status_code == 200 and finish_json.get('success'):
            print(f"[facebook] 🌟 SUCCESS! Reel published successfully!")
            print(f"[facebook] Video ID: {video_id}")
            print(f"[facebook] View at: https://facebook.com/{video_id}")
            print("=" * 60)
            return {
                'id': video_id,
                'platform': 'facebook',
                'status': 'success',
                'url': f"https://facebook.com/{video_id}"
            }
        else:
            err_text = res_finish.text
            print(f"[facebook] ❌ Finish Phase Error ({res_finish.status_code}): {err_text}")
            return {'status': 'failed', 'error': f"Finish Phase Failed: {err_text}", 'platform': 'facebook'}

    except Exception as e:
        print(f"[facebook] ❌ Unexpected exception: {e}")
        return {'status': 'failed', 'error': str(e), 'platform': 'facebook'}
