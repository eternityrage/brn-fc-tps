import os
import ssl
import urllib.request

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
os.makedirs(ASSETS_DIR, exist_ok=True)

# Curated 120+ High Quality 3D Transparent PNGs from Microsoft Fluent UI Emoji
ASSET_CATALOG = {
    # --- ANIMALS: MAMMALS & WILDLIFE ---
    "lion": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Lion/3D/lion_3d.png",
    "tiger": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Tiger/3D/tiger_3d.png",
    "bear": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Bear/3D/bear_3d.png",
    "panda": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Panda/3D/panda_3d.png",
    "koala": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Koala/3D/koala_3d.png",
    "monkey": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Monkey/3D/monkey_3d.png",
    "gorilla": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Gorilla/3D/gorilla_3d.png",
    "fox": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Fox/3D/fox_3d.png",
    "wolf": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Wolf/3D/wolf_3d.png",
    "rabbit": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Rabbit/3D/rabbit_3d.png",
    "deer": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Deer/3D/deer_3d.png",
    "horse": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Horse/3D/horse_3d.png",
    "zebra": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Zebra/3D/zebra_3d.png",
    "giraffe": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Giraffe/3D/giraffe_3d.png",
    "elephant": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Elephant/3D/elephant_3d.png",
    "pig": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Pig/3D/pig_3d.png",
    "dog": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Dog/3D/dog_3d.png",
    "cat": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Cat/3D/cat_3d.png",
    "hamster": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Hamster/3D/hamster_3d.png",
    "hedgehog": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Hedgehog/3D/hedgehog_3d.png",
    "bat": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Bat/3D/bat_3d.png",
    "otter": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Otter/3D/otter_3d.png",
    "sloth": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Sloth/3D/sloth_3d.png",
    "skunk": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Skunk/3D/skunk_3d.png",
    "badger": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Badger/3D/badger_3d.png",

    # --- BIRDS ---
    "parrot": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Parrot/3D/parrot_3d.png",
    "duck": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Duck/3D/duck_3d.png",
    "flamingo": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Flamingo/3D/flamingo_3d.png",
    "rooster": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Rooster/3D/rooster_3d.png",
    "chicken": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Chicken/3D/chicken_3d.png",
    "eagle": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Eagle/3D/eagle_3d.png",
    "owl": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Owl/3D/owl_3d.png",
    "swan": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Swan/3D/swan_3d.png",
    "penguin": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Penguin/3D/penguin_3d.png",
    "peacock": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Peacock/3D/peacock_3d.png",
    "dove": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Dove/3D/dove_3d.png",
    "turkey": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Turkey/3D/turkey_3d.png",

    # --- MARINE & REPTILES ---
    "dolphin": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Dolphin/3D/dolphin_3d.png",
    "whale": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Whale/3D/whale_3d.png",
    "shark": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Shark/3D/shark_3d.png",
    "octopus": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Octopus/3D/octopus_3d.png",
    "squid": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Squid/3D/squid_3d.png",
    "crab": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Crab/3D/crab_3d.png",
    "lobster": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Lobster/3D/lobster_3d.png",
    "shrimp": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Shrimp/3D/shrimp_3d.png",
    "fish": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Fish/3D/fish_3d.png",
    "tropical_fish": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Tropical%20fish/3D/tropical_fish_3d.png",
    "blowfish": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Blowfish/3D/blowfish_3d.png",
    "turtle": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Turtle/3D/turtle_3d.png",
    "frog": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Frog/3D/frog_3d.png",
    "crocodile": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Crocodile/3D/crocodile_3d.png",
    "lizard": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Lizard/3D/lizard_3d.png",
    "snake": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Snake/3D/snake_3d.png",

    # --- INSECTS ---
    "butterfly": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Butterfly/3D/butterfly_3d.png",
    "honeybee": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Honeybee/3D/honeybee_3d.png",
    "lady_beetle": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Lady%20beetle/3D/lady_beetle_3d.png",
    "snail": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Snail/3D/snail_3d.png",
    "ant": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Ant/3D/ant_3d.png",
    "caterpillar": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Bug/3D/bug_3d.png",

    # --- FRUITS & FOODS ---
    "tomato": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Tomato/3D/tomato_3d.png",
    "egg": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Egg/3D/egg_3d.png",
    "apple": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Red%20apple/3D/red_apple_3d.png",
    "green_apple": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Green%20apple/3D/green_apple_3d.png",
    "banana": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Banana/3D/banana_3d.png",
    "strawberry": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Strawberry/3D/strawberry_3d.png",
    "watermelon": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Watermelon/3D/watermelon_3d.png",
    "grapes": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Grapes/3D/grapes_3d.png",
    "peach": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Peach/3D/peach_3d.png",
    "cherries": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Cherries/3D/cherries_3d.png",
    "lemon": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Lemon/3D/lemon_3d.png",
    "orange": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Tangerine/3D/tangerine_3d.png",
    "pineapple": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Pineapple/3D/pineapple_3d.png",
    "avocado": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Avocado/3D/avocado_3d.png",
    "carrot": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Carrot/3D/carrot_3d.png",
    "corn": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Ear%20of%20corn/3D/ear_of_corn_3d.png",
    "broccoli": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Broccoli/3D/broccoli_3d.png",
    "mushroom": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Mushroom/3D/mushroom_3d.png",
    "pizza": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Pizza/3D/pizza_3d.png",
    "hamburger": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Hamburger/3D/hamburger_3d.png",
    "cookie": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Cookie/3D/cookie_3d.png",
    "doughnut": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Doughnut/3D/doughnut_3d.png",
    "cupcake": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Cupcake/3D/cupcake_3d.png",
    "ice_cream": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Soft%20ice%20cream/3D/soft_ice_cream_3d.png",
    "lollipop": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Lollipop/3D/lollipop_3d.png",
    "popcorn": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Popcorn/3D/popcorn_3d.png",
    "french_fries": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/French%20fries/3D/french_fries_3d.png",

    # --- VEHICLES & OBJECTS ---
    "motorcycle": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Motorcycle/3D/motorcycle_3d.png",
    "bicycle": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Bicycle/3D/bicycle_3d.png",
    "automobile": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Automobile/3D/automobile_3d.png",
    "racing_car": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Racing%20car/3D/racing_car_3d.png",
    "police_car": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Police%20car/3D/police_car_3d.png",
    "fire_engine": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Fire%20engine/3D/fire_engine_3d.png",
    "ambulance": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Ambulance/3D/ambulance_3d.png",
    "airplane": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Airplane/3D/airplane_3d.png",
    "rocket": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Rocket/3D/rocket_3d.png",
    "helicopter": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Helicopter/3D/helicopter_3d.png",
    "speedboat": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Speedboat/3D/speedboat_3d.png",
    "locomotive": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Locomotive/3D/locomotive_3d.png",

    # --- ITEMS, GEMS & SPORTS ---
    "gem": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Gem%20stone/3D/gem_stone_3d.png",
    "trophy": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Trophy/3D/trophy_3d.png",
    "crown": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Crown/3D/crown_3d.png",
    "ring": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Ring/3D/ring_3d.png",
    "soccer_ball": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Soccer%20ball/3D/soccer_ball_3d.png",
    "basketball": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Basketball/3D/basketball_3d.png",
    "tennis": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Tennis/3D/tennis_3d.png",
    "magic_wand": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Magic%20wand/3D/magic_wand_3d.png",
    "bell": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Bell/3D/bell_3d.png",
    "guitar": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Guitar/3D/guitar_3d.png",
    "heart": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Red%20heart/3D/red_heart_3d.png",
    "fire": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Fire/3D/fire_3d.png",
    "sparkles": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Sparkles/3D/sparkles_3d.png",
    "star": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Star/3D/star_3d.png",
    "tree": "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/assets/Deciduous%20tree/3D/deciduous_tree_3d.png"
}

def download_mega_pack():
    ctx = ssl._create_unverified_context()
    headers = {"User-Agent": "Mozilla/5.0"}
    success_count = 0
    total = len(ASSET_CATALOG)
    
    print(f"Syncing mega asset library ({total} high-res 3D assets)...")
    for idx, (name, url) in enumerate(ASSET_CATALOG.items()):
        out_path = os.path.join(ASSETS_DIR, f"{name}.png")
        if os.path.exists(out_path) and os.path.getsize(out_path) > 1000:
            success_count += 1
            continue
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, context=ctx) as resp, open(out_path, "wb") as f:
                f.write(resp.read())
            success_count += 1
            if success_count % 10 == 0:
                print(f"Downloaded [{success_count}/{total}] assets...")
        except Exception as e:
            # Skip gracefully if an asset is not found
            pass
            
    print(f"\n[DONE] Mega Asset Library Ready! Total available: {success_count} assets.")

if __name__ == "__main__":
    download_mega_pack()
