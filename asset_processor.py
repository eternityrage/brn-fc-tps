import os
import sys
from PIL import Image
from rembg import remove

def process_raw_image(input_image_path, output_name=None):
    """
    Takes any standard photo (JPG, PNG with background),
    removes the background using AI (rembg),
    crops empty transparent padding,
    and saves it to the assets/ directory ready for reel generation.
    """
    assets_dir = os.path.join(os.path.dirname(__file__), "assets")
    os.makedirs(assets_dir, exist_ok=True)
    
    if not output_name:
        base = os.path.splitext(os.path.basename(input_image_path))[0]
        output_name = f"{base}_sticker.png"
    elif not output_name.endswith(".png"):
        output_name += ".png"
        
    out_path = os.path.join(assets_dir, output_name)
    
    print(f"Loading image: {input_image_path}...")
    inp = Image.open(input_image_path).convert("RGBA")
    
    print("Removing background with AI...")
    cutout = remove(inp)
    
    # Trim empty transparent space around the subject
    bbox = cutout.getbbox()
    if bbox:
        cutout = cutout.crop(bbox)
        
    cutout.save(out_path, "PNG")
    print(f"Saved sticker to: {out_path} ({cutout.size[0]}x{cutout.size[1]})")
    return out_path

if __name__ == "__main__":
    if len(sys.argv) > 1:
        img_path = sys.argv[1]
        out_name = sys.argv[2] if len(sys.argv) > 2 else None
        process_raw_image(img_path, out_name)
    else:
        print("Usage: python asset_processor.py <path_to_any_photo.jpg> [optional_output_name]")
