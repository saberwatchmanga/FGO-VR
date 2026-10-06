# Third-party attribution

This FGO compatibility work builds on AstroQuest v0.13, pinned at
`9f42c44d4e838e3a0df67913e350c4f098110862`, and shadPS4 / shadps4-arm64.
Preserved upstream licenses, dependency sources and notices are in
[upstream/THIRD-PARTY-NOTICES.md](upstream/THIRD-PARTY-NOTICES.md),
[upstream/.gitmodules](upstream/.gitmodules) and
[upstream/pinned_core_submodules.txt](upstream/pinned_core_submodules.txt).
Paths in the original notice refer to the upstream source checkout.

Complete FGO changes and modified source snapshots accompany this release.
Use tools/prepare_source.py to obtain the exact upstream checkout with submodules
and apply one complete platform patch. Original source notices are retained.
The build reference scripts record additional pinned FEX, sysroot and runtime inputs.

The Windows bundle includes the official Android platform-tools ADB utility and
its required Windows libraries for optional Quest settings transfer. Its
NOTICE.txt and source.properties accompany the files in the package.
Android platform-tools: https://developer.android.com/tools/releases/platform-tools
MinGW libwinpthread: https://www.mingw-w64.org/ (its bundled notice is retained).

Microsoft Visual C++ runtime, Virtual Desktop and game/console system data are
external requirements and are not bundled. No FGO game, PKG, firmware, keys or
user save data are included. FGO and the original game's characters belong to
their respective rights holders. This is an unofficial compatibility project.
