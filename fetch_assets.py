import os
import ssl
import urllib.request
from PIL import Image

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
os.makedirs(ASSETS_DIR, exist_ok=True)

ITEMS = {
    "parrot": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Parrot/3D/parrot_3d.png",
    "tomato": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Tomato/3D/tomato_3d.png",
    "duck": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Duck/3D/duck_3d.png",
    "flamingo": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Flamingo/3D/flamingo_3d.png",
    "egg": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Egg/3D/egg_3d.png",
    "motorcycle": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Motorcycle/3D/motorcycle_3d.png",
    "tree": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Deciduous%20tree/3D/deciduous_tree_3d.png",
    "rooster": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Rooster/3D/rooster_3d.png"
}

def download_all():
    ctx = ssl._create_unverified_context()
    headers = {"User-Agent": "Mozilla/5.0"}
    downloaded = []
    
    for name, url in ITEMS.items():
        out_path = os.path.join(ASSETS_DIR, f"{name}.png")
        if os.path.exists(out_path) and os.path.getsize(out_path) > 1000:
            print(f"Already exists: {name}")
            downloaded.append(name)
            continue
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, context=ctx) as resp, open(out_path, "wb") as f:
                f.write(resp.read())
            print(f"Downloaded: {name} -> {out_path} ({os.path.getsize(out_path)} bytes)")
            downloaded.append(name)
        except Exception as e:
            print(f"Failed {name}: {e}")
            
    print(f"Total downloaded assets: {len(downloaded)} / {len(ITEMS)}")

if __name__ == "__main__":
    download_all()
