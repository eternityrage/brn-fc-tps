import os
import json
import ssl
import random
import urllib.request

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
CATALOG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "microsoft_assets_catalog.json")

os.makedirs(ASSETS_DIR, exist_ok=True)

# Load catalog
_catalog = None

def get_catalog():
    global _catalog
    if _catalog is None:
        if os.path.exists(CATALOG_PATH):
            with open(CATALOG_PATH, "r", encoding="utf-8") as f:
                _catalog = json.load(f)
        else:
            _catalog = {}
    return _catalog

def get_or_fetch_asset(asset_key):
    """
    Returns the absolute path to the asset PNG.
    If it does not exist locally in assets/, it downloads it automatically
    from Microsoft's raw GitHub CDN on-the-fly and caches it.
    """
    local_path = os.path.join(ASSETS_DIR, f"{asset_key}.png")
    if os.path.exists(local_path) and os.path.getsize(local_path) > 1000:
        return local_path
        
    catalog = get_catalog()
    if asset_key not in catalog:
        # Check if maybe user passed a name without underscores or case mismatch
        clean_key = asset_key.lower().replace(" ", "_").replace("-", "_")
        if clean_key in catalog:
            asset_key = clean_key
        else:
            print(f"[WARN] Asset '{asset_key}' not in catalog, fallback to parrot.")
            return get_or_fetch_asset("parrot")
            
    asset_info = catalog[asset_key]
    url = asset_info["url"]
    
    ctx = ssl._create_unverified_context()
    headers = {"User-Agent": "Mozilla/5.0"}
    req = urllib.request.Request(url, headers=headers)
    
    try:
        print(f"[ASSET HUB] Downloading '{asset_key}' on-the-fly from Microsoft repository...")
        with urllib.request.urlopen(req, context=ctx) as resp, open(local_path, "wb") as f:
            f.write(resp.read())
        print(f"[ASSET HUB] Cached '{asset_key}' ({round(os.path.getsize(local_path)/1024, 1)} KB)")
        return local_path
    except Exception as e:
        print(f"[ASSET HUB] Failed to download '{asset_key}': {e}")
        # Fallback to a local asset if download fails
        existing = [f for f in os.listdir(ASSETS_DIR) if f.endswith(".png")]
        if existing:
            return os.path.join(ASSETS_DIR, existing[0])
        return None

def get_random_pair():
    """
    Seamlessly picks 2 random distinct 3D assets from all 1,595 items,
    downloads them on-the-fly if needed, and returns (hero_key, item_key, hero_path, item_path).
    """
    catalog = get_catalog()
    all_keys = list(catalog.keys())
    
    hero_key = random.choice(all_keys)
    item_key = random.choice(all_keys)
    while item_key == hero_key:
        item_key = random.choice(all_keys)
        
    hero_path = get_or_fetch_asset(hero_key)
    item_path = get_or_fetch_asset(item_key)
    
    return hero_key, item_key, hero_path, item_path

def search_assets(keyword):
    """Search for assets matching a keyword (e.g. 'cat', 'car', 'fruit')."""
    catalog = get_catalog()
    kw = keyword.lower()
    matches = [k for k in catalog.keys() if kw in k]
    return matches

if __name__ == "__main__":
    cat = get_catalog()
    print(f"Asset Hub loaded with {len(cat)} online assets ready to pull seamlessly!")
    h_k, i_k, h_p, i_p = get_random_pair()
    print(f"Sample random pair: {h_k} -> {h_p} & {i_k} -> {i_p}")
