# 🧠 BrainFocus Taps (`brn-fc-tps`)

An automated, 24/7 programmatic viral puzzle reels generator and publishing pipeline for **Facebook Reels** and **Instagram Reels**. Inspired by viral channels like *MindTwist Arena* that drive millions of organic views and massive comment section engagement.

---

## 🌟 Highlights

- **🎮 22 Unique Gameplay Modes:** Swing, gravity falls, orbital carousels, zoom pulses, 4-way crossfire, pyramids, slot machines, radar sweeps, and more.
- **🦁 1,595+ 3D Assets:** High-resolution Microsoft Fluent 3D Emoji catalog dynamically downloaded and cached on demand.
- **🎯 Mathematical Alignment Guarantee:** Every video includes guaranteed harmonic alignment frames where all moving pieces snap perfectly inside their outlines.
- **🎵 Procedural Synchronized Audio:** 120 BPM clock ticking, suspense heartbeat rumble, and winning chimes precisely timed to alignment moments.
- **☁️ Zero-Maintenance 24/7 Publishing:** Fully automated via GitHub Actions with scheduled cron triggers (3× daily) and manual dispatch.
- **🔒 Zero-Credentials Leak Architecture:** All tokens, page IDs, and API secrets are read strictly from GitHub Repository Secrets / Environment Variables. Zero private data committed to git.

---

## 🕹️ Catalog of 22 Gameplay Modes

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

## 🚀 Local Usage

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Generate Batches of Reels Locally
```bash
# Generate 5 random reels
python master_factory.py --count 5

# Generate specific mode
python master_factory.py --count 1 --mode pyramid_wave

# Generate specific hero and item pairing
python master_factory.py --hero tiger --item gem --mode crossfire_4way
```

### 3. Run the Daily Publisher Locally
```bash
python daily_puzzle_publisher.py
```
*(Requires `FACEBOOK_ACCESS_TOKEN` and `FACEBOOK_PAGE_ID` in your `.env` file or environment).*

---

## 🤖 GitHub Actions 24/7 Automation

The repository includes `.github/workflows/auto_publish_reels.yml`:

### Schedules:
- **04:00 UTC** (Morning Reel)
- **12:00 UTC** (Afternoon Peak Reel)
- **20:00 UTC** (Evening Primetime Reel)

### Required GitHub Secrets:
Add these in your repository: **Settings → Secrets and variables → Actions → New repository secret**:

| Secret Name | Description | Example |
|---|---|---|
| `FACEBOOK_ACCESS_TOKEN` | Meta Long-Lived User / Page Access Token | `EAAM2K...` |
| `FACEBOOK_PAGE_ID` | Facebook Page ID to publish Reels to | `1319646877895110` |
| `INSTAGRAM_ACCOUNT_ID` | *(Optional)* Connected Instagram Business Account ID | `178414...` |

When configured, the Action automatically renders a fresh viral reel, composes an engaging caption with viral hooks and hashtags, publishes the video directly to Facebook Reels (and Instagram Reels), and commits the publishing history back to `published_reels.json`.

---

## 🔒 Security Notice

This repository is **100% public-ready and safe**. No tokens, credentials, or private IDs are hardcoded in the codebase. All credentials must be supplied via GitHub Secrets or environment variables.
