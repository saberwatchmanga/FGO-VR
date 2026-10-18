# SteamVR / Steam Link

PCVR 0.2.2 adds an optional SteamVR launcher alongside the existing Virtual Desktop / VDXR launcher. It uses the same emulator core, game files, saves and resolution profiles. Virtual Desktop is not required for this alternative.

## Start with Steam Link

1. Install Steam and SteamVR on the Windows PC, and Steam Link on the supported headset. Supply your own extracted Japanese CUSA09078 game as described in the README.
2. Open Steam Link in the headset, connect to the PC, and confirm that SteamVR is running with the headset and controllers connected.
3. From the Windows desktop, run **`Launch-PCVR-SteamVR.cmd`**. The Chinese-named **`启动FGO-VR-PCVR-SteamVR.cmd`** is an equivalent entry point. The launcher does not start Steam or SteamVR for you.
4. Close the game window to exit. PCVR saves remain in `FGO-PC/runtime-vr/user/home/1000/savedata/CUSA09078`.

The package defaults to original resolution (100 / OFF). Use `Resolution-Settings.cmd` to choose another profile, then restart the game. For a direct original-resolution comparison, run this in PowerShell from the package folder:

```powershell
& '.\Launch-PCVR-SteamVR.cmd' -RenderScale 100
```

`Launch-PCVR.cmd` continues to select VDXR for Virtual Desktop users. `Launch-PCVR-Original.cmd` remains its original-resolution entry. Close the game before changing routes.

## Runtime selection and troubleshooting

The SteamVR launcher locates the installed 64-bit runtime through OpenVR paths, OpenXR registration or Steam libraries. It validates the JSON manifest and the referenced DLL, then sets `XR_RUNTIME_JSON` only for the launcher and its child game. It does not change the system OpenXR default, start another SteamVR instance, or alter Windows audio devices.

If SteamVR is not already running, the launcher asks you to connect first and stops before starting the game. Seeing a `vrserver` process is only a launch guard; it does not establish headset readiness.

If detection fails, specify your own SteamVR installation path. This is an example, not a fixed requirement:

```powershell
& '.\Launch-PCVR-SteamVR.cmd' -OpenXrManifest 'D:\SteamLibrary\steamapps\common\SteamVR\steamxr_win64.json'
```

For a configuration check that does not start the game or SteamVR:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File '.\FGO-PC\scripts\launch_pc.ps1' -Mode PcVr -OpenXrRuntime SteamVR -CheckOnly
```

Session folders under `FGO-PC/sessions` include `_SteamVR`; `run.json` records the executable hash, actual runtime manifest, resolution and exit status. Close the game before sharing logs, and remove private paths or identifiers.

If views or sound are duplicated, first connect through Steam Link and reach SteamVR before starting this launcher. This launch order follows the feedback in [issue #1](https://github.com/saberwatchmanga/FGO-VR/issues/1). The exact cause of that reporter's duplicate stream/audio has not been independently diagnosed. If symptoms remain, check SteamVR/Windows audio routing and report the connection method and selected runtime; the launcher does not force an audio device.

## Validation boundary

On October 18, 2026, the maintainer confirmed successful startup on **Quest 3 → Steam Link → Windows SteamVR**. The matching short session used **150%** internal resolution and exited normally. Logs show an active headset session, submitted stereo frames and tracked controllers. This is startup validation, not a SteamVR full playthrough, an audio-quality assessment or a performance benchmark. See the [acceptance record](USER_ACCEPTANCE_20261018.md).

The existing **VDXR 150% full playthrough** result is retained. Quest standalone remains version 0.2.0 and is unchanged.

**Steam Frame hardware and its controller mapping have not been tested.** Quest 3 verifies the common Windows SteamVR/OpenXR route; it does not establish native SteamOS execution or standalone Steam Frame compatibility. The current native suggested bindings cover Oculus Touch. Other interaction profiles may need additional work based on actual device evidence.

Thanks to **@tkp206093** for the SteamVR feedback and launch-order findings in issue #1.

References: [Valve Steam Link setup](https://help.steampowered.com/en/faqs/view/0E2C-406B-9135-38A4), [Khronos runtime discovery and override](https://github.com/KhronosGroup/OpenXR-SDK-Source/blob/main/specification/loader/runtime.adoc).
