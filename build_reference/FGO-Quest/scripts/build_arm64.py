"""Build locked FEX and the FGO-compatible ARM64 core with Windows-hosted LLVM."""
import argparse
from datetime import datetime
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'source' / 'AstroQuest' / 'shadps4-arm64-main'
FEX = SOURCE / 'runtime' / 'sources' / 'fex'
FEX_BUILD = ROOT / 'build' / 'fex'
CORE_BUILD = ROOT / 'build' / 'arm64'
CMAKE = Path(r'D:\Program Files\Microsoft Visual Studio\18\Community\Common7\IDE\CommonExtensions\Microsoft\CMake\CMake\bin\cmake.exe')
NINJA = Path(r'D:\Program Files\Microsoft Visual Studio\18\Community\Common7\IDE\CommonExtensions\Microsoft\CMake\Ninja\ninja.exe')
TOOLCHAIN = ROOT / 'scripts' / 'fgo-arm64.cmake'

def run(command, stage):
    environment = os.environ.copy()
    environment.pop('INCLUDE', None)
    environment.pop('LIB', None)
    environment['GIT_CONFIG_COUNT'] = '1'
    environment['GIT_CONFIG_KEY_0'] = 'safe.directory'
    environment['GIT_CONFIG_VALUE_0'] = '*'
    environment['PATH'] = os.pathsep.join([str(ROOT / 'tools' / 'shims'),
                                          str(ROOT.parent / 'tools' / 'llvm-21.1.8' / 'bin'),
                                          str(Path(sys.executable).parent),
                                          r'D:\Program Files\Git\usr\bin',
                                          r'D:\Program Files\Git\cmd', environment['PATH']])
    evidence = ROOT / 'evidence'
    stamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log = evidence / f'{stage}_{stamp}.log'
    (evidence / f'{stage}_{stamp}.command.json').write_text(json.dumps(command, indent=2), encoding='utf-8')
    print(f'{stage}: {log}', flush=True)
    with log.open('w', encoding='utf-8') as output:
        result = subprocess.run(command, env=environment, stdout=output, stderr=subprocess.STDOUT)
    print(f'{stage}: exit={result.returncode}', flush=True)
    if result.returncode:
        print(log.read_text(encoding='utf-8', errors='replace')[-7000:], flush=True)
        raise SystemExit(result.returncode)

def configure(source, build, extra):
    run([str(CMAKE), '-S', str(source), '-B', str(build), '-G', 'Ninja',
         f'-DCMAKE_MAKE_PROGRAM={NINJA}', f'-DCMAKE_TOOLCHAIN_FILE={TOOLCHAIN}',
         '-DCMAKE_BUILD_TYPE=Release', '-DCMAKE_CXX_SCAN_FOR_MODULES=OFF',
         '-DCMAKE_POLICY_VERSION_MINIMUM=3.5', f'-DPython_EXECUTABLE={sys.executable}',
         f'-DPython3_EXECUTABLE={sys.executable}', *extra], build.name + '_configure')

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('stage', choices=['fex', 'core'])
    args = parser.parse_args()
    if args.stage == 'fex':
        configure(FEX, FEX_BUILD, [
            '-DBUILD_FEXCORE_ONLY=ON', f'-DFEXCORE_SMOKE_SOURCE={SOURCE / "runtime/probes/fexcore-smoke.cpp"}',
            '-DTUNE_CPU=none', '-DBUILD_TESTING=OFF', '-DBUILD_FEX_LINUX_TESTS=OFF',
            '-DBUILD_THUNKS=OFF', '-DBUILD_FEXCONFIG=OFF', '-DENABLE_GDB_SYMBOLS=OFF',
            '-DENABLE_LTO=OFF', '-DENABLE_JEMALLOC_GLIBC_ALLOC=OFF',
            '-DENABLE_OFFLINE_TELEMETRY=OFF', '-DENABLE_VIXL_DISASSEMBLER=OFF',
            '-DENABLE_VIXL_SIMULATOR=OFF', '-DENABLE_ZYDIS=OFF', '-DENABLE_FEXCORE_PROFILER=OFF'])
        run([str(CMAKE), '--build', str(FEX_BUILD), '--target', 'fexcore-smoke', '--parallel', '10'], 'fex_build')
    else:
        sr = ROOT / 'tools' / 'sysroot-arm64'
        font_tool = ROOT.parent / 'FGO-PC/build/src/imgui/renderer/Dear_ImGui_FontEmbed.exe'
        configure(SOURCE, CORE_BUILD, [
            f'-DCMAKE_C_FLAGS=--target=aarch64-linux-gnu --gcc-toolchain={sr.as_posix()}/usr',
            '-DENABLE_BACHATA_RUNTIME=ON', '-DENABLE_FEX_GUEST_CPU=ON',
            f'-DFEXCORE_GUEST_CPU_SOURCE_DIR={FEX}', f'-DFEXCORE_GUEST_CPU_BUILD_DIR={FEX_BUILD}',
            f'-DIMGUI_FONT_EMBED_EXECUTABLE={font_tool}',
            f'-DX11_Xext_LIB:FILEPATH={sr / "usr/lib/aarch64-linux-gnu/libXext.so"}',
            f'-DXEXT_LIB:FILEPATH={sr / "usr/lib/aarch64-linux-gnu/libXext.so"}',
            '-DENABLE_USERFAULTFD=OFF', '-DENABLE_DISCORD_RPC=OFF', '-DENABLE_UPDATER=OFF',
            '-DENABLE_TESTS=OFF', '-DSDL_X11_XCURSOR=OFF', '-DSDL_X11_XDBE=OFF',
            '-DALSOFT_UPDATE_BUILD_VERSION=OFF',
            '-DSDL_X11_XINPUT=OFF', '-DSDL_X11_XFIXES=OFF', '-DSDL_X11_XRANDR=OFF',
            '-DSDL_X11_XSCRNSAVER=OFF', '-DSDL_X11_XSHAPE=OFF', '-DSDL_X11_XSYNC=OFF',
            '-DSDL_X11_XTEST=OFF', '-DSDL_WAYLAND=OFF'])
        run([str(CMAKE), '--build', str(CORE_BUILD), '--target', 'shadps4', '--parallel', '10'], 'core_build')

if __name__ == '__main__':
    main()
