# Steam Link / SteamVR Startup Acceptance — October 18, 2026

The maintainer tested the optional SteamVR launcher using Quest 3 and reported: **the test succeeded; connecting through Steam Link first, then launching the program, was sufficient.** Publication of the update and a reply to issue #1 were explicitly authorized.

The matching local record shows game version 01.01, the existing accepted optional-resolution core (`563be6008f73855c3b4425c93bca104692999e97f0fb16cf956c5d3aa40123c1`), **150%** internal resolution, an explicitly selected SteamVR manifest, approximately **52 seconds** of process runtime and exit code **0**. Runtime logs show a focused headset session, stereo frame submission at 2048×2268 per eye, and tracked controllers. Private session logs, paths, game data and saves are not distributed.

This records successful startup through **Quest 3 → Steam Link → Windows SteamVR**. It is not a second full-playthrough result, an audio-quality test, a quantitative performance benchmark, a repeated-run stability result, or confirmation of precise pointing. It does not establish Steam Frame hardware/controller support, SteamOS native execution or standalone Frame support.

The previous [VDXR 150% full-playthrough acceptance](USER_ACCEPTANCE_20261007.md) remains valid. The native Windows cores, their memory-pool repair, and the Quest 0.2.0 APK are unchanged in the 0.2.2 launcher update.

Structural launcher regression checks covered VDXR and SteamVR core selection, original-resolution fallback, manifest/DLL validation, process-local runtime override, the no-autostart guard, and protection of accepted files and system OpenXR registration. These checks are separate from the user-reported hardware startup result.
