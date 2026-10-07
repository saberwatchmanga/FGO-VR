# Fixed Source and Build Inputs

The upstream AstroQuest source is pinned to commit 9f42c44d4e838e3a0df67913e350c4f098110862.

    python tools/prepare_source.py pc C:\work\fgo-pc-source
    python tools/prepare_source.py quest C:\work\fgo-quest-source

Apply only the matching platform complete.patch. core.patch is a review delta and must not be stacked on top. Keep the source snapshots and submodule manifest; do not submit nested Git repositories. Text snapshots may differ only because of Windows line endings.

## Recorded toolchain

- Windows: LLVM 21.1.8 and the Visual Studio 2022 SDK; Visual Studio 2026 supplies CMake and Ninja.
- Quest: Java 17, Android NDK r27d, SDK 36, and build-tools 36.
- Quest core: the pinned Debian ARM64 sysroot.
- FEX: commit f2b679f6028ce1c38875233aecfcf5d3f8ebecec.
- FFmpeg: commit 94dde08c8a9e4271a93a2a7e4159e9fb05d30c0a.

upstream/arm64-sysroot-lock.json records the Debian package versions, download URLs, and SHA-256 hashes used for this build. Rebuilds should use that lock file rather than current rolling-repository packages. prepare_arm64_sysroot.py documents part of the build flow; it is not a complete installer for all locked dependencies. FEX also requires the pinned commit and its upstream runtime build flow, plus patches/build-support/fex-fexcore-only.patch. prepare_source.py only prepares AstroQuest and its Git submodules.

The Windows original-resolution fallback core corresponds to patches/baseline/fgo-pcvr.patch. The optional resolution core corresponds to patches/fgo-resolution-pc-complete.patch. The baseline directory contains a loading patch retained as an earlier desktop implementation reference; do not combine it with the PCVR or complete patch.

build_reference contains the required build scripts and a snapshot of the current process. The PC build enables OpenXR. The Quest host uses Android OpenXR/EGL; its core is ARM64/glibc, runs the original x86 game through FEX, and uses Turnip for Vulkan. The APK build reuses the maintainer-provided AstroQuest 0.13 runtime library and packages the locally built core.

Script paths for Visual Studio and Java are snapshots from the development machine and may need adjustment. Quest also needs the upstream AstroQuest APK runtime, LLVM, the sysroot, and the PC font-embedding tool. Scripts contain no game data, release-signing private key, or GitHub credentials. An APK signed with a different key cannot directly replace an installed APK with another signature.

Full historical build and device logs are not included. Public verification is summarized in TESTING.md; file checks are recorded in SHA256SUMS and artifact-manifest.json.

The full PC 0.2.1 patch is based on the pinned source commit and includes the graphics-pool/Backing-budget repair and optional Windows failure diagnostics. The opt-in diagnostics match the accepted executable. EmulatorSettings process fields are not written to the saved configuration. Launch-PCVR.cmd selects the original core at 100/OFF and the accepted scaled core when a higher profile is enabled; Launch-PCVR-Original.cmd selects the original-resolution fallback; Resolution-Settings.cmd opens the profile tool. The Quest complete.patch remains at 0.2.0; do not apply platform patches across targets.