# 🎯 Master Viral Puzzle Reel Studio (22 Modes, 113+ Assets)

An automated, enterprise-grade programmatic video factory designed to continuously generate viral **"Stop in the Shadow" / "Pause Challenge"** reels for Instagram, Facebook, TikTok, and YouTube Shorts (inspired by top channels like *MindTwist Arena* that achieve millions of views per reel).

---

## 🌟 Engine Highlights

- **🎮 22 Distinct Gameplay Modes:** Never post the same format twice. From classic horizontal swings and gravity drops to rotating Ferris wheels, scale zoom challenges, diagonal crosshairs, and 3-tier wave pyramids!
- **🦁 113+ High-Resolution 3D Assets:** Sourced from Microsoft's open-source 3D library (Mammals, Birds, Marine Life, Reptiles, Fruits, Foods, Vehicles, Gems).
- **♾️ Infinite Unique Variations:** Over **5.9 Million** unique combinations of modes, characters, items, outline colors, and titles.
- **🎵 Procedural Rhythmic Audio:** Synced 120 BPM clock ticking, suspense heartbeat rumble, and winning chimes at alignment moments.
- **🎯 Mathematical Alignment Guarantee:** Every reel features designated, mathematically certified frames where all moving objects fit dead center into their shadows simultaneously.
- **☁️ 24/7 Cloud Publishing Pipeline:** Fully automated with GitHub Actions to run continuously and generate videos automatically.

---

## 🕹️ Complete Catalog of 22 Modes

| # | Mode Name | Description |
|---|---|---|
| 1 | `swing_horizontal` | Hero + 3 stacked items swinging left-to-right across center silhouettes |
| 2 | `swing_vertical` | 3 vertical columns oscillating up-and-down across center outlines |
| 3 | `swing_opposing` | Alternating rows swinging in opposing directions simultaneously |
| 4 | `falling_gravity` | Items dropping continuously from the sky through target hoop baskets |
| 5 | `rising_bubbles` | Items floating continuously upwards from the bottom through target hoops |
| 6 | `orbit_carousel` | 4 items rotating around a circular ring into 4 outlines |
| 7 | `orbit_counter_rotating` | Dual rings: outer items rotate clockwise, inner items rotate counter-clockwise |
| 8 | `zoom_pulse` | Central item pulsing between 0.45× and 1.55× scale; pause at exact 1.000× match |
| 9 | `dual_zoom_inverse` | Left item shrinks while Right item expands; pause when both hit 1.000×! |
| 10 | `crossfire_4way` | 4 items converging from Top, Bottom, Left, Right into central targets |
| 11 | `crossfire_diagonal_x` | 4 items flying in from the 4 diagonal corners (X-crosshair) |
| 12 | `pyramid_wave` | 3-tier triangle pyramid (1, 2, 3 items) in harmonic wave alignment |
| 13 | `inverted_pyramid` | Upside-down pyramid (3, 2, 1 items) oscillating in harmonic waves |
| 14 | `diamond_grid` | 4 items forming a diamond shape expanding and contracting |
| 15 | `matrix_2x2` | 4 items in a 2×2 grid, alternating horizontal and vertical oscillations |
| 16 | `slot_machine` | 3 vertical reels scrolling; pause when jackpot items hit the center payline |
| 17 | `conveyor_belt` | Items moving along a horizontal conveyor track across target outlines |
| 18 | `zigzag_snake` | Items weaving left and right through target gates down the screen |
| 19 | `pendulum_arc` | Items swinging along a curved pendulum arc through center gravity |
| 20 | `rebound_bounce` | Items bouncing off screen walls and crossing at the exact center shadow |
| 21 | `radar_sweep` | Central character + 4 items rotating at harmonic speeds, locking into alignment |
| 22 | `target_lock_crosshair` | Outer bracket corners zooming in while center character locks into target crosshair |

---

## 🚀 How to Run Locally

### 1. Generate Batches of Random Reels
Generate 10 completely unique reels with random modes, animals, and colors:
```bash
python master_factory.py --count 10
```

### 2. Run a Specific Mode
```bash
python master_factory.py --count 3 --mode pyramid_wave
python master_factory.py --count 3 --mode orbit_counter_rotating
python master_factory.py --count 3 --mode slot_machine
python master_factory.py --count 3 --mode zoom_pulse
```

### 3. Generate a Custom Pairing
```bash
python master_factory.py --hero tiger --item gem --mode crossfire_4way --color crimson_red
```

---

## 🤖 24/7 Publishing & GitHub Automation

The workflow file `.github/workflows/generate_reels.yml` is ready.

### How It Works:
1. **Scheduled Cloud Runs:** Runs automatically in GitHub's cloud daily (or every few hours).
2. **On-Demand Runs:** You can go to your GitHub repository from your phone, click **Actions → Auto Viral Reels Generator → Run workflow**, choose your video count and mode, and download the finished MP4 files.
3. **Automated Publishing Strategy:**
   - Download the generated batch `.zip`.
   - Post directly to Instagram Reels / YouTube Shorts / TikTok / Facebook Reels.
   - Use the in-app trending audio for algorithm boosts.
   - Pin the comment: *"99% fail to pause when all fit the shadow! Drop your screenshot 👇"*
