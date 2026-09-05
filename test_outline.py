import cv2
import numpy as np
from PIL import Image

def generate_smooth_outline(rgba_image, color_rgb=(0, 120, 255), thickness=6):
    """
    Given a PIL RGBA image, creates a matching smooth anti-aliased outline.
    color_rgb: (R, G, B) e.g. (0, 120, 255) for vibrant royal blue
    thickness: line thickness in pixels
    """
    img_np = np.array(rgba_image)
    h, w = img_np.shape[:2]
    
    alpha = img_np[:, :, 3]
    # Threshold alpha to find the solid silhouette
    _, thresh = cv2.threshold(alpha, 40, 255, cv2.THRESH_BINARY)
    
    # Find external contours
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    
    # Create empty RGBA canvas
    outline_canvas = np.zeros((h, w, 4), dtype=np.uint8)
    
    # Draw anti-aliased contours
    # Note: OpenCV expects BGR
    bgr_color = (color_rgb[2], color_rgb[1], color_rgb[0], 255)
    cv2.drawContours(outline_canvas, contours, -1, bgr_color, thickness=thickness, lineType=cv2.LINE_AA)
    
    return Image.fromarray(outline_canvas)

if __name__ == "__main__":
    test_img = Image.open("C:/Users/kreg9/viral_puzzle_reels/assets/parrot.png").convert("RGBA")
    outline = generate_smooth_outline(test_img, color_rgb=(0, 102, 255), thickness=8)
    outline.save("C:/Users/kreg9/viral_puzzle_reels/assets/parrot_outline_test.png")
    print("Saved parrot_outline_test.png successfully!")
