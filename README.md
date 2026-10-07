# FGO VR — PCVR 0.2.1 / Quest 3 0.2.0

English | [简体中文](README.zh-CN.md)

Play **Fate/Grand Order VR feat. Mash Kyrielight** using an AstroQuest/shadPS4-based compatibility build. This project targets the Japanese PS4 title **CUSA09078**, game versions **01.00 / 01.01**.

- **PCVR:** OpenXR through Virtual Desktop and VDXR.
- **Standalone Quest 3:** a local ARM64 core using FEX and Turnip; the PC does not stream the game frames.

This is currently a **private preview**. The repository and releases will stay private/draft until the planned release video is published. Packages include no PS4 game data, PKGs, firmware, keys, or user saves. Provide your own extracted game.

## Downloads

Preview packages are staged in the [draft releases](https://github.com/saberwatchmanga/FGO-VR/releases):

| File | Component |
| --- | --- |
| `FGO-VR-0.2.1-PCVR-Windows.zip` | Windows PCVR build and external resolution settings |
| `FGO-VR-0.2.0-Quest3.apk` | Standalone Quest 3 build, unchanged in this PC update |
| `FGO-VR-0.2.1-Source.zip` | Pinned patches, modified source snapshots, build references, and licenses |
| `SHA256SUMS` / `artifact-manifest.json` | File verification and component versions |

## Windows / PCVR quick start

Requirements: 64-bit Windows, a Vulkan-capable GPU and driver, Microsoft Visual C++ runtime, Virtual Desktop Streamer on the PC, and Virtual Desktop on the headset.

1. Extract `FGO-VR-0.2.1-PCVR-Windows.zip`.
2. Put your extracted base game in `FGO-PC/games/CUSA09078`, including `eboot.bin`. Put the optional update beside it in `FGO-PC/games/CUSA09078-UPDATE`. The update cannot run without the base game.
3. Connect the headset through Virtual Desktop and keep the Streamer running.
4. Double-click **`Launch-PCVR.cmd`**. The launcher selects VDXR for this process without changing the system OpenXR setting. Close the game window to exit.
5. To change resolution, open **`Resolution-Settings.cmd`**. It requires Python 3 with Tk. Save the setting, then restart the game. Without Python, edit `FGO-Resolution/settings.json` or use a direct launcher under `profiles`.
6. **`Launch-PCVR-Original.cmd`** always uses the original-resolution build with the same saves.

The original Chinese-named launchers are also retained. Optional system fonts follow the upstream AstroQuest instructions; console system files are not bundled.

Save location: `FGO-PC/runtime-vr/user/home/1000/savedata/CUSA09078`. Close the game before backing up the entire title directory.

## Standalone Quest 3 quick start

Install `FGO-VR-0.2.0-Quest3.apk` (package `com.fgovr.quest`, version code 2). Updating with the same signature can preserve app data. Enable USB debugging and copy your extracted game folders to:

```text
/data/local/tmp/fgovr/games/CUSA09078
/data/local/tmp/fgovr/games/CUSA09078-UPDATE
```

Make the files readable. See [Quest installation](docs/INSTALL_QUEST.md) for the commands and upgrade details.

With one Quest connected by USB, use the Windows settings tool to push the Quest resolution setting, then close and restart the app. The tool backs up the existing configuration and changes only `fgo_render_scale`.

Logs and settings are under `/sdcard/Android/data/com.fgovr.quest/files/`. `vrhost.txt` accepts `fgo_render_scale=100/110/125`. Once launched, the game runs locally on the headset.

## Resolution profiles

Both components default to **100 / OFF**. Higher settings increase GPU and memory use. These are game-internal rendering profiles; VDXR's displayed resolution percentage is a separate measurement.

| Profile | PCVR | Quest 3 | Observed result |
| --- | --- | --- | --- |
| 100 | Original resolution | Original resolution | Quest user reported strong aliasing |
| 110 | Available | Available | Quest user found it acceptable, with visible aliasing |
| 125 | Startup checked | Available | Quest user reported noticeable stutter |
| 150 | Available | PC only | PC user reported good image quality and completed a full playthrough |

Quest **110** is the suggested starting profile. If performance is poor, return to 100. The tested PC was an i5-13400F / RTX 4070 / 64 GB RAM; no quantitative FPS or complete-story performance claim is made.

Verified per-eye targets are 1408×1512 at 100, 1536×1663 at 110, 1792×1890 at 125, and 2048×2268 at PC150. The patch replaces the game's verified canonical 1.4f request while preserving other requests and allocation checks, preventing repeated scale multiplication.

### PCVR 0.2.1 transition fix

Higher resolution previously exhausted the game's fixed graphics memory pool during a story transition. A malformed out-of-memory message then caused a second crash. PCVR 0.2.1 grows the graphics pool and its matching process-local backing/direct-memory budget together, and corrects the message format. The extra budget is not written to saved settings.

On **October 7, 2026**, the user confirmed **a completed full playthrough on PCVR / VDXR at 1.50×**. The previously crashing transition also passed its retest, and the recorded session exited normally. PC125/150 startup checks and the 100 rollback check also passed. The Quest APK and Quest source remain at 0.2.0; this PC fix has not been applied to Quest.

See [testing details](TESTING.md) and the [user acceptance record](docs/USER_ACCEPTANCE_20261007.md).

## Controls

| Input | Mapping |
| --- | --- |
| Left Touch stick | Menu directions |
| Left / right grip | L1 / R1 |
| Left / right trigger | L2 / R2 |
| Right A | Cross / confirm |
| Both stick clicks together | Recenter |
| Keyboard Q / E | Confirm |
| Keyboard arrows | Menu selection |

Right-hand aim pose is bridged to the game's ordinary DualShock tracking. Basic controls work. Complete Move behavior, precise pointing, and every training interaction have not been validated.

## Current limits

- Quest125 stutters on the user's headset; Quest110 still has aliasing.
- **PCVR / VDXR 1.50×: full game completion confirmed by the user.** PC125 has only been startup-checked in this repair round.
- Repeated-run stability, measured headset FPS, and comfort on other hardware have not been separately assessed.
- Extra reprojection layers, complete Move support, and some tracking interfaces still have gaps.
- This build targets FGO VR. Other PSVR games need their own compatibility checks.

## Source, builds, and credits

Based on [AstroQuest](https://github.com/bigmak94/AstroQuest), pinned to commit `9f42c44d4e838e3a0df67913e350c4f098110862`, and [shadPS4](https://github.com/shadps4-emu/shadPS4).

Complete platform patches are in `patches`; modified files are in `source_snapshot`. **Apply one complete patch for the chosen platform. Do not stack earlier phase patches on top.**

`tools/prepare_source.py` obtains the fixed upstream source and applies the selected platform patch. See [build instructions](docs/BUILD.md) for pinned inputs and reference scripts. Some developer paths need adjustment; a clean-machine one-click build is not claimed. Release signing keys are not included.

Source notices are retained under GPL-2.0-or-later and the applicable third-party licenses. See [LICENSE](LICENSE), [THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md), and the upstream notices. This is an unofficial compatibility project; the original game and characters belong to their respective rights holders.

## Support

If this project is useful to you, you can support its continued development on [Ko-fi / terry2418](https://ko-fi.com/terry2418). Thank you for your support.
