"""
Thematic Page Profiles and Content Engine for the Viral Puzzle Reel Network.
Configures 6 distinct Facebook Pages with specialized gameplay modes,
diverse asset categories, viral copy, and interactive pinned challenges.
"""
import random
from typing import Dict, List, Tuple, Any

# Master list of all 6 active pages (excluding PlanView Lens & Buildings Bountsy)
ACTIVE_PAGE_IDS = [
    "1319646877895110",  # BrainFocus Taps
    "1309712825557751",  # MindMath Taps
    "1316150674917146",  # BrainFog Taps
    "1227319627140685",  # BrainTaps Flow
    "1334005973127654",  # MindView Taps
    "1350182274839663",  # MindQuiz Focus
]

# 18 rich asset category keywords
CATEGORY_KEYWORDS = {
    "wildlife_animals": [
        "cat", "dog", "lion", "tiger", "bear", "wolf", "fox", "deer", "horse", "zebra",
        "elephant", "rhino", "hippo", "monkey", "gorilla", "panda", "koala", "rabbit",
        "mouse", "hamster", "bat", "hedgehog", "otter", "sloth", "kangaroo", "badger",
        "beaver", "camel", "llama", "giraffe", "cow", "ox", "pig", "boar", "ram", "sheep",
        "goat", "leopard"
    ],
    "birds_and_flying": [
        "bird", "blackbird", "eagle", "owl", "parrot", "peacock", "flamingo", "swan",
        "duck", "goose", "turkey", "rooster", "chicken", "dove", "penguin",
        "butterfly", "honeybee", "bee", "fly", "mosquito", "dragonfly"
    ],
    "ocean_and_marine": [
        "fish", "blowfish", "shark", "whale", "dolphin", "octopus", "squid", "crab",
        "lobster", "shrimp", "seahorse", "jellyfish", "coral", "shell", "spiral_shell",
        "water_wave", "anchor"
    ],
    "reptiles_and_bugs": [
        "snake", "lizard", "crocodile", "alligator", "turtle", "frog", "snail", "caterpillar",
        "ant", "beetle", "lady_beetle", "spider", "scorpion", "worm"
    ],
    "delicious_food": [
        "pizza", "hamburger", "hot_dog", "french_fries", "taco", "burrito", "sandwich",
        "spaghetti", "sushi", "ramen", "curry_rice", "pot_of_food", "bacon", "steak",
        "poultry_leg", "meat_on_bone", "bread", "croissant", "bagel", "pretzel", "cheese",
        "egg", "pancakes", "waffle", "popcorn", "butter"
    ],
    "fruits_and_sweets": [
        "apple", "banana", "grapes", "watermelon", "strawberry", "blueberries", "cherries",
        "peach", "mango", "pineapple", "coconut", "kiwi", "avocado", "ice_cream", "soft_ice_cream",
        "shaved_ice", "doughnut", "cookie", "cupcake", "shortcake", "candy", "lollipop",
        "chocolate_bar", "custard", "honey_pot"
    ],
    "beverages_and_drinks": [
        "coffee", "hot_beverage", "teacup_without_handle", "cup_with_straw", "bubble_tea",
        "beer", "wine_glass", "cocktail_glass", "tropical_drink", "bottle_with_popping_cork",
        "beverage_box", "milk_glass", "baby_bottle", "ice"
    ],
    "sports_and_fitness": [
        "soccer_ball", "basketball", "american_football", "baseball", "tennis", "volleyball",
        "rugby_football", "pool_8_ball", "bowling", "boxing_glove", "martial_arts_uniform",
        "skis", "snowboarder", "skateboard", "roller_skate", "badminton", "table_tennis",
        "field_hockey", "ice_hockey", "lacrosse", "cricket_game", "trophy", "medal"
    ],
    "gaming_and_toys": [
        "video_game", "joystick", "game_die", "dice", "puzzle", "jigsaw", "teddy_bear",
        "pinata", "magic_wand", "kite", "yo_yo", "chess_pawn", "spade_suit", "heart_suit",
        "diamond_suit", "club_suit", "joker", "clown_face", "alien_monster"
    ],
    "math_numbers_shapes": [
        "abacus", "calculator", "triangular_ruler", "straight_ruler", "keycap_digit",
        "plus", "minus", "divide", "multiply", "hundred_points", "square", "circle",
        "triangle", "diamond", "cube", "star", "cross_mark", "check_mark_button",
        "infinity", "heavy_dollar_sign", "chart_increasing", "bar_chart"
    ],
    "space_and_sci_fi": [
        "rocket", "satellite", "ringed_planet", "earth", "globe", "full_moon", "crescent_moon",
        "sun", "star", "sparkles", "shooting_star", "milky_way", "telescope", "alien",
        "flying_saucer", "robot", "comet"
    ],
    "energy_and_alertness": [
        "high_voltage", "zap", "lightning", "fire", "collision", "bomb", "firecracker",
        "sparkler", "alarm_clock", "stopwatch", "timer_clock", "hourglass", "battery",
        "light_bulb", "flashlight", "candle", "red_exclamation_mark"
    ],
    "nature_and_plants": [
        "blossom", "cherry_blossom", "rose", "sunflower", "tulip", "hibiscus", "bouquet",
        "four_leaf_clover", "maple_leaf", "fallen_leaf", "herb", "seedling", "evergreen_tree",
        "deciduous_tree", "palm_tree", "cactus", "mushroom"
    ],
    "vehicles_and_travel": [
        "automobile", "sport_utility_vehicle", "pickup_truck", "delivery_truck", "fire_engine",
        "police_car", "ambulance", "bus", "trolleybus", "racing_car", "motorcycle", "motor_scooter",
        "bicycle", "airplane", "small_airplane", "helicopter", "rocket", "speedboat", "ferry",
        "ship", "anchor", "fuel_pump", "traffic_light"
    ],
    "tools_and_instruments": [
        "hammer", "wrench", "screwdriver", "nut_and_bolt", "gear", "magnet", "microscope",
        "telescope", "compass", "level_slider", "control_knobs", "scissors", "clamp",
        "key", "old_key", "lock", "unlocked", "chains", "hook"
    ],
    "music_and_audio": [
        "musical_note", "musical_score", "microphone", "headphone", "radio", "saxophone",
        "guitar", "musical_keyboard", "trumpet", "violin", "banjo", "drum", "bell",
        "loudspeaker", "megaphone"
    ],
    "flow_and_elements": [
        "droplet", "sweat_droplets", "water_wave", "bubbles", "gem_stone", "crystal_ball",
        "ring", "sparkles", "dizzy", "cyclone", "snowflake", "wind_face", "fog"
    ],
    "faces_and_reactions": [
        "grinning_face", "smiling_face", "winking_face", "heart_eyes", "star_struck",
        "face_with_tears_of_joy", "thinking_face", "exploding_head", "partying_face",
        "sunglasses", "nerd_face", "detective", "superhero", "supervillain", "mage"
    ]
}


PAGE_PROFILES: Dict[str, Dict[str, Any]] = {
    "1319646877895110": {
        "slug": "brainfocus",
        "name": "BrainFocus Taps",
        "tagline": "Precision Reflex & Microsecond Timing",
        "preferred_modes": [
            "swing_horizontal",
            "falling_gravity",
            "pulsing_scale",
            "laser_scan",
            "orbit_carousel",
            "teleport_snap"
        ],
        "primary_categories": [
            "gaming_and_toys",
            "sports_and_fitness",
            "energy_and_alertness",
            "tools_and_instruments"
        ],
        "outline_colors": ["electric_blue", "cyber_yellow", "crimson_red"],
        "titles": [
            "BrainFocus Challenge: Can You Stop It? 🎯",
            "99% Fail This Reflex Test! Can You Pause in Time? ⚡",
            "Ultimate Eye-Hand Coordination Challenge! 🧠",
            "Stop Inside the Shadow! Only 1% Get It First Try 🏆",
            "Microsecond Precision Test: Freeze The Exact Frame! ⏱️",
            "Can You Hit 100% Match? Tap Pause to Win! 🧩"
        ],
        "hooks": [
            "🎯 99% of people fail to stop this in the outline! Can you do it on the first try?",
            "⚡ Tap pause when the shape hits the exact outline! Prove your reflex in the comments!",
            "🧠 Ultimate Mind Focus Test: Stop inside the shadow! What was your reaction time?",
            "🔥 Warning: This puzzle is harder than it looks! Double tap if you hit it!",
            "🏆 Test your hand-eye coordination! Pause at the exact frame to win!"
        ],
        "pinned_comments": [
            "📌 CHALLENGE RULES:\n1. Tap pause when the shape fits exactly inside the outline! 🎯\n2. Drop a screenshot of your attempt below 👇\n3. Be honest: Did you get it on your 1st try? (Only 1% can!) 🏆",
            "🎯 REFLEX TEST: How many attempts did it take you to get a 100% perfect match? Drop your screenshot below 👇 #BrainFocus",
            "⚡ DID YOU PAUSE IN TIME? Post your screenshot in the comments! If you nailed it on the 1st try, you have top 1% reaction speed! 🚀"
        ],
        "hashtags": [
            "#BrainFocus", "#BrainFocusTaps", "#ReflexTest", "#FocusChallenge",
            "#ViralReels", "#BrainTeaser", "#PauseChallenge", "#MindGames"
        ]
    },

    "1309712825557751": {
        "slug": "mindmath",
        "name": "MindMath Taps",
        "tagline": "Mental Math & Calculation Reflex Speed",
        "preferred_modes": [
            "slot_machine",
            "matrix_2x2",
            "triple_threat",
            "harmonic_pendulum",
            "crossfire_diagonal_x",
            "pulsing_scale"
        ],
        "primary_categories": [
            "math_numbers_shapes",
            "gaming_and_toys",
            "tools_and_instruments"
        ],
        "outline_colors": ["cyber_yellow", "electric_blue", "neon_green"],
        "titles": [
            "MindMath Reflex: Pause On The Exact Number! 🔢",
            "Quick Mental Calculation: Can You Freeze In Time? ⚡",
            "99% Can't Count Fast Enough! Tap Pause To Win 🎲",
            "Math IQ Speed Test: Stop At 100% Precision! 📐",
            "Mental Math Rush: Align The Right Equation! 💡",
            "Probability & Speed: Hit The Winning Number! 🏆"
        ],
        "hooks": [
            "🔢 Quick calculation challenge! Pause when the number locks into the outline!",
            "🎲 99% fail to count in time! Prove your numerical speed in the comments!",
            "⚡ Lightning Math Test: Calculate and freeze at the exact millisecond!",
            "📐 Can you spot the geometric match before time runs out? Tap to pause!"
        ],
        "pinned_comments": [
            "🔢 MATH IQ CHALLENGE:\n1. Pause when the number locks into the outline! ⏱️\n2. Comment your attempt screenshot below 👇\n3. How many tries did it take you? 🧠 #MindMath",
            "🎲 CALCULATION SPEED TEST: Drop your screenshot below! Can you hit 100% precision on try #1? 👇 #MindMathTaps",
            "💡 QUICK MATH: Pause the reel at the perfect alignment! Drop your screenshot to prove your math IQ! 🏆"
        ],
        "hashtags": [
            "#MindMath", "#MindMathTaps", "#MathIQ", "#NumberPuzzle",
            "#MentalAgility", "#MathChallenge", "#ViralReels", "#BrainTraining"
        ]
    },

    "1316150674917146": {
        "slug": "brainfog",
        "name": "BrainFog Taps",
        "tagline": "High-Voltage Alertness & Wake-Up Drills",
        "preferred_modes": [
            "shockwave_pulse",
            "strobe_flash",
            "teleport_snap",
            "vortex_spin",
            "falling_gravity",
            "zigzag_dash"
        ],
        "primary_categories": [
            "energy_and_alertness",
            "space_and_sci_fi",
            "beverages_and_drinks",
            "faces_and_reactions"
        ],
        "outline_colors": ["cyber_yellow", "crimson_red", "electric_blue"],
        "titles": [
            "BrainFog Wake-Up Test! Shock Your Reflexes ⚡",
            "Clear The Morning Fog: Can You Tap In Time? ☕",
            "100% Alertness Drill! Freeze The Frame Instantly 🔥",
            "Only Awake Minds Can Catch This! Stop It! 🚀",
            "Morning Brain Buster: Beat The Shockwave! ⚡",
            "High-Voltage Reflex: Pause At 100% Power! 💥"
        ],
        "hooks": [
            "⚡ Still feel sleepy? Take this high-voltage reflex test to shock your brain awake!",
            "☕ Morning Brain Fog Buster: Pause right inside the glowing shockwave!",
            "🔥 Only 1% of people can react fast enough to freeze this frame!",
            "💥 High-speed reaction drill! Tap the screen the instant the outline charges up!"
        ],
        "pinned_comments": [
            "⚡ BRAIN FOG DESTROYER:\n1. Wake up your brain: Hit pause right inside the glowing shockwave! 💥\n2. Share your screenshot below 👇\n3. Are you 100% awake yet? ☕ #BrainFog",
            "🔥 ALERTNESS CHECK: Are your morning reflexes awake? Drop your pause screenshot below! 👇 #BrainFogTaps",
            "⚡ MORNING WAKE-UP DRILL: Pause the reel at 100% alignment! Tag a friend who needs their morning coffee! ☕👇"
        ],
        "hashtags": [
            "#BrainFog", "#BrainFogTaps", "#MorningRoutine", "#WakeUpCall",
            "#MentalClarity", "#ReflexDrill", "#HighVoltage", "#ViralReels"
        ]
    },

    "1227319627140685": {
        "slug": "braintaps_flow",
        "name": "BrainTaps Flow",
        "tagline": "Satisfying ASMR & Hypnotic Momentum Loops",
        "preferred_modes": [
            "harmonic_pendulum",
            "orbit_carousel",
            "spiral_galaxy",
            "color_shift",
            "swing_horizontal",
            "radar_sweep"
        ],
        "primary_categories": [
            "flow_and_elements",
            "nature_and_plants",
            "music_and_audio",
            "ocean_and_marine"
        ],
        "outline_colors": ["neon_green", "electric_blue", "deep_purple"],
        "titles": [
            "Satisfying Flow State: Can You Match The Rhythm? 🌊",
            "Hypnotic ASMR Tap: Pause At The Harmonic Beat 🧘",
            "Smooth Momentum Challenge! Freeze In Perfect Flow ✨",
            "Deep Focus Flow: Hit The Zen Alignment! 💎",
            "Infinite Rhythm Tap: Catch The Ripple In Time 🌀",
            "Pure ASMR Harmony: Stop Right On The Pulse 🎵"
        ],
        "hooks": [
            "🌊 Enter the flow state! Can you pause at the exact moment of harmonic symmetry?",
            "✨ Oddly satisfying rhythm test: Tap to pause when the soothing pulse locks in!",
            "💎 Find your focus zen! 99% tap too early or too late. Can you time the flow?",
            "🌀 Hypnotic ASMR puzzle loop: Watch the rhythm, find the beat, freeze the frame!"
        ],
        "pinned_comments": [
            "🌊 FLOW STATE TEST:\n1. Watch the rhythmic wave and tap pause at the harmonic sync point! 🎵\n2. Post your screenshot below 👇\n3. Did you feel the flow? 🧘 #BrainTapsFlow",
            "✨ ODDLY SATISFYING CHALLENGE: Drop your screenshot below when you catch the exact ripple! 👇 #FlowState",
            "💎 ZEN FOCUS: Hit pause at pure 100% alignment! Share your result with us below 👇 #ASMRPuzzle"
        ],
        "hashtags": [
            "#BrainTapsFlow", "#ASMRPuzzle", "#SatisfyingVideo", "#FlowState",
            "#ZenGaming", "#OddlySatisfying", "#HypnoticLoop", "#ViralReels"
        ]
    },

    "1334005973127654": {
        "slug": "mindview",
        "name": "MindView Taps",
        "tagline": "3D Spatial IQ & Multi-Dimensional Perspectives",
        "preferred_modes": [
            "prism_split",
            "isometric_cube",
            "card_flip_3d",
            "crossfire_diagonal_x",
            "vortex_spin",
            "spiral_galaxy"
        ],
        "primary_categories": [
            "tools_and_instruments",
            "space_and_sci_fi",
            "vehicles_and_travel",
            "flow_and_elements"
        ],
        "outline_colors": ["deep_purple", "electric_blue", "cyber_yellow"],
        "titles": [
            "3D Spatial Perspective IQ: Can You Align It? 🧊",
            "Optical Illusion Challenge: Your Eyes Will Trick You! 👁️",
            "Multi-Dimensional Pause Test! Stop At True Angle 📐",
            "Isometric Perception Test: Only High IQ Pass! 🔮",
            "Rotational IQ Puzzle: Freeze At True Perspective! 🌀",
            "Perspective Shift: Stop When The 3D Object Fits! 🛸"
        ],
        "hooks": [
            "🧊 3D Spatial IQ Test: Your brain's depth perception will be tested to the limit!",
            "👁️ Optical Illusion Alert! Can you freeze the frame right when the angle locks?",
            "📐 99% misjudge the rotational perspective! Can you pause at true 100%?",
            "🔮 Multi-dimensional puzzle: Don't let the isometric illusion trick your eyes!"
        ],
        "pinned_comments": [
            "👁️ SPATIAL IQ TEST:\n1. Watch the 3D rotation and pause when the perspective locks in 3D! 🧊\n2. Screenshot your alignment and reply below 👇\n3. Rate the difficulty from 1-10! #MindView",
            "🧊 3D PERSPECTIVE CHECK: Did you catch the true isometric angle? Drop your screenshot below! 👇 #MindViewTaps",
            "📐 OPTICAL PUZZLE: Pause at the exact moment of perspective alignment! Show us your score! 👇"
        ],
        "hashtags": [
            "#MindView", "#MindViewTaps", "#SpatialIQ", "#OpticalIllusion",
            "#3DPuzzle", "#PerspectiveTest", "#BrainTeaser", "#ViralReels"
        ]
    },

    "1350182274839663": {
        "slug": "mindquiz",
        "name": "MindQuiz Focus",
        "tagline": "Rapid-Fire Visual Trivia & Spotlight Challenges",
        "preferred_modes": [
            "whack_a_mole",
            "spotlight_reveal",
            "shadow_morph",
            "matrix_2x2",
            "triple_threat",
            "slot_machine"
        ],
        "primary_categories": [
            "wildlife_animals",
            "birds_and_flying",
            "ocean_and_marine",
            "delicious_food",
            "fruits_and_sweets",
            "faces_and_reactions"
        ],
        "outline_colors": ["crimson_red", "hot_pink", "cyber_yellow"],
        "titles": [
            "MindQuiz Spotlight: Can You Catch The Odd One? 🕵️",
            "Rapid-Fire Visual Quiz: Freeze The Target Item! 🐾",
            "Speed Trivia Challenge: Pause On The Secret Symbol! 🍕",
            "Observation IQ Test: 99% Miss This Detail! 🔍",
            "Spot The Target: Fast Reflex Trivia Challenge! 🏆",
            "Lightning Eye Quiz: Freeze On The Winning Clue! 🎯"
        ],
        "hooks": [
            "🐾 Rapid-Fire Animal & Object Spotlight! Freeze the reel when the item appears!",
            "🕵️ Observation IQ Test: 99% miss the fast change! Can you catch the clue?",
            "🍕 Food & Item Trivia Challenge! Tap pause right on the spotlighted answer!",
            "🔍 Spot the difference in milliseconds! Only sharp eyes can freeze the match!"
        ],
        "pinned_comments": [
            "🐾 SPOTLIGHT QUIZ:\n1. Find the target object and freeze the reel right on it! 🎯\n2. Post your proof screenshot below 👇\n3. Name the item in the comments! 🏆 #MindQuiz",
            "🕵️ TRIVIA SPEED RUN: Did you spot the target in time? Drop your screenshot below! 👇 #MindQuizFocus",
            "🍕 OBSERVATION TEST: Freeze the frame on the exact match! Drop your proof in the comments! 👇"
        ],
        "hashtags": [
            "#MindQuiz", "#MindQuizFocus", "#TriviaReel", "#SpotTheDifference",
            "#ObservationTest", "#QuizChallenge", "#ViralReels", "#VisualQuiz"
        ]
    }
}


def build_categorized_pool(catalog: Dict[str, Any]) -> Dict[str, List[str]]:
    """Organize all 1,595 assets in the catalog into rich categories."""
    pool: Dict[str, List[str]] = {cat: [] for cat in CATEGORY_KEYWORDS}
    pool["general_objects"] = []

    for key in catalog.keys():
        assigned = False
        for cat_name, keywords in CATEGORY_KEYWORDS.items():
            if any(kw in key for kw in keywords):
                pool[cat_name].append(key)
                assigned = True
                break
        if not assigned:
            pool["general_objects"].append(key)

    return pool


def pick_page_assets(page_id: str, catalog: Dict[str, Any]) -> Tuple[str, str]:
    """
    Selects 2 distinct, exciting 3D assets tailored to the page's theme,
    while rotating across all categories to guarantee endless variety.
    """
    profile = PAGE_PROFILES.get(page_id, PAGE_PROFILES["1319646877895110"])
    pool = build_categorized_pool(catalog)
    all_keys = list(catalog.keys())

    # 70% chance to pick hero from primary categories; 30% chance from any category
    primary_cats = profile.get("primary_categories", [])
    if random.random() < 0.70 and primary_cats:
        chosen_cat = random.choice(primary_cats)
        cat_items = pool.get(chosen_cat, [])
        hero = random.choice(cat_items) if cat_items else random.choice(all_keys)
    else:
        hero = random.choice(all_keys)

    # Pick item from a complementary category or general pool
    item = random.choice(all_keys)
    attempts = 0
    while item == hero and attempts < 20:
        item = random.choice(all_keys)
        attempts += 1

    return hero, item


def get_page_metadata(page_id: str, mode_name: str, hero_name: str, item_name: str) -> Tuple[str, str, str]:
    """Generates tailored title, caption description, and pinned comment for a page."""
    profile = PAGE_PROFILES.get(page_id, PAGE_PROFILES["1319646877895110"])
    
    title = random.choice(profile["titles"])
    hook = random.choice(profile["hooks"])
    pinned = random.choice(profile["pinned_comments"])
    tags = " ".join(random.sample(profile["hashtags"], k=min(7, len(profile["hashtags"]))))
    
    formatted_mode = mode_name.replace('_', ' ').title()
    formatted_hero = hero_name.replace('_', ' ').title()
    formatted_item = item_name.replace('_', ' ').title()

    description = (
        f"{hook}\n\n"
        f"🎮 Challenge: {formatted_mode}\n"
        f"🔍 Objects: {formatted_hero} & {formatted_item}\n\n"
        f"⚡ Test your timing! Pause when the object aligns perfectly with the outline.\n"
        f"Drop your screenshot or attempt in the comments below! 👇\n\n"
        f"{tags}"
    )

    return title, description, pinned
