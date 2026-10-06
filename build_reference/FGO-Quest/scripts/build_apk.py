"""Compile the independent FGO OpenXR host and package the newly built ARM64 core."""
import argparse
from datetime import datetime
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import zipfile

ROOT = Path(__file__).resolve().parents[1]
HOST = ROOT / 'source' / 'AstroQuest' / 'quest-host'
CORE_SOURCE = ROOT / 'source' / 'AstroQuest' / 'shadps4-arm64-main'
OUT = ROOT / 'build' / 'quest'
SDK = ROOT / 'tools' / 'android' / 'sdk'
BT = SDK / 'build-tools' / '36.0.0'
NDK = ROOT / 'tools' / 'android' / 'ndk' / 'android-ndk-r27d'
JAVA = Path(r'C:\Program Files\ojdkbuild\java-17-openjdk-17.0.3.0.6-1\bin')
PLATFORM = SDK / 'platforms' / 'android-36' / 'android.jar'
LLVM = ROOT.parent / 'tools' / 'llvm-21.1.8' / 'bin'
ORIGINAL_APK = ROOT.parent / 'AstroQuest-0.13-Quest3.apk'

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def run(command, name):
    log = ROOT / 'evidence' / f'{name}_{datetime.now():%Y%m%d_%H%M%S}.log'
    print(f'{name}: {log}', flush=True)
    (log.with_suffix('.command.json')).write_text(json.dumps([str(x) for x in command], indent=2), encoding='utf-8')
    with log.open('w', encoding='utf-8') as stream:
        result = subprocess.run([str(x) for x in command], stdout=stream, stderr=subprocess.STDOUT)
    if result.returncode:
        print(log.read_text(encoding='utf-8', errors='replace')[-9000:], flush=True)
        raise SystemExit(result.returncode)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host-only', action='store_true')
    args = parser.parse_args()
    libs = OUT / 'staging' / 'lib' / 'arm64-v8a'
    assets = OUT / 'staging' / 'assets'
    for path in (libs, assets, OUT / 'classes', OUT / 'dex'):
        path.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(ORIGINAL_APK) as original:
        (libs / 'libfgo_ld.so').write_bytes(original.read('lib/arm64-v8a/libastro_ld.so'))
        (libs / 'libopenxr_loader.so').write_bytes(original.read('lib/arm64-v8a/libopenxr_loader.so'))
    compiler = NDK / 'toolchains' / 'llvm' / 'prebuilt' / 'windows-x86_64' / 'bin' / 'clang++.exe'
    openxr_headers = ROOT.parent / 'source' / 'AstroQuest' / 'shadps4-arm64-main' / 'externals' / 'openxr-sdk' / 'include'
    native_files = sorted((HOST / 'cpp').glob('*.cpp'))
    run([compiler, '--target=aarch64-linux-android32', '-std=c++20', '-O2', '-fPIC',
         '-fvisibility=hidden', '-Wall', '-Wextra', '-Wno-unused-parameter',
         '-Wno-missing-field-initializers', '-I', openxr_headers, '-I', CORE_SOURCE / 'src' / 'core' / 'vr',
         *native_files, '-shared', '-static-libstdc++', '-Wl,--no-undefined',
         '-Wl,-soname,libfgovr.so', '-L', libs, '-lopenxr_loader',
         '-lEGL', '-lGLESv3', '-landroid', '-lnativewindow', '-laaudio', '-llog', '-lz',
         '-o', libs / 'libfgovr.so'], 'android_native')
    java_files = sorted((HOST / 'java').rglob('*.java'))
    run([JAVA / 'javac.exe', '-Xlint:-options', '-source', '11', '-target', '11',
         '-classpath', PLATFORM, '-d', OUT / 'classes', *java_files], 'android_java')
    run([JAVA / 'java.exe', '-cp', BT / 'lib' / 'd8.jar', 'com.android.tools.r8.D8',
         '--lib', PLATFORM, '--min-api', '32', '--output', OUT / 'dex',
         *sorted((OUT / 'classes').rglob('*.class'))], 'android_dex')
    if args.host_only:
        print('Host native, Java and dex compilation passed; APK not yet packaged.', flush=True)
        return
    core = ROOT / 'build' / 'arm64' / 'shadps4'
    if not core.is_file():
        raise RuntimeError('New FGO ARM64 core missing: do not package the original Astro core.')
    runtime = OUT / 'runtime'
    with zipfile.ZipFile(ORIGINAL_APK) as original:
        with zipfile.ZipFile(io.BytesIO(original.read('assets/runtime.zip'))) as source:
            for entry in source.infolist():
                if entry.is_dir() or entry.filename == 'host/shadps4-arm64-fex':
                    continue
                path = (runtime / entry.filename).resolve()
                if not path.is_relative_to(runtime.resolve()):
                    raise RuntimeError('runtime archive path escapes staging')
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(source.read(entry))
    deployed_core = runtime / 'host' / 'shadps4-arm64-fex'
    run([LLVM / 'llvm-strip.exe', '-o', deployed_core, core], 'strip_fgo_core')
    digest = hashlib.sha256()
    with zipfile.ZipFile(assets / 'runtime.zip', 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for path in sorted(runtime.rglob('*')):
            if not path.is_file(): continue
            relative = path.relative_to(runtime).as_posix()
            data = path.read_bytes()
            digest.update(relative.encode() + b'\0' + data)
            entry = zipfile.ZipInfo(relative, (2026, 1, 1, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            entry.external_attr = 0o755 << 16
            archive.writestr(entry, data)
    (assets / 'runtime.stamp').write_text(digest.hexdigest() + '\n')
    provenance = {'application': 'FGO VR Quest 3', 'package': 'com.fgovr.quest',
                  'upstream_commit': '9f42c44d4e838e3a0df67913e350c4f098110862',
                  'runtime_source_apk_sha256': sha(ORIGINAL_APK),
                  'unstripped_fgo_core_sha256': sha(core), 'packaged_fgo_core_sha256': sha(deployed_core),
                  'game_assets_embedded': False, 'device_game_acceptance': 'pending'}
    (assets / 'fgo-build.json').write_text(json.dumps(provenance, indent=2), encoding='utf-8')
    run([BT / 'aapt2.exe', 'compile', '--dir', HOST / 'res', '-o', OUT / 'res.zip'], 'aapt_compile')
    base = OUT / 'base.apk'
    run([BT / 'aapt2.exe', 'link', '-o', base, '-I', PLATFORM,
         '--manifest', HOST / 'AndroidManifest.xml', '-A', assets, '--debug-mode',
         '--min-sdk-version', '32', '--target-sdk-version', '32', OUT / 'res.zip'], 'aapt_link')
    with zipfile.ZipFile(base, 'a', zipfile.ZIP_DEFLATED) as archive:
        archive.write(OUT / 'dex' / 'classes.dex', 'classes.dex')
        for path in sorted(libs.glob('*.so')):
            archive.write(path, 'lib/arm64-v8a/' + path.name)
    aligned = OUT / 'aligned.apk'
    run([BT / 'zipalign.exe', '-p', '-f', '4', base, aligned], 'apk_align')
    key_dir = ROOT / 'tools' / 'signing'
    key_dir.mkdir(parents=True, exist_ok=True)
    key = key_dir / 'fgo-local-development.keystore'
    if not key.exists():
        run([JAVA / 'keytool.exe', '-genkeypair', '-noprompt', '-keystore', key,
             '-alias', 'fgovr-local', '-storepass', 'android', '-keypass', 'android',
             '-keyalg', 'RSA', '-keysize', '2048', '-validity', '10000',
             '-dname', 'CN=FGO VR Local Development'], 'development_signing_key')
    # Preserve the already headset-validated 0.1.0 release.
    apk = ROOT.parent / 'FGO-Resolution' / 'delivery' / 'FGO-VR-0.2.0-Quest3.apk'
    apk.parent.mkdir(parents=True, exist_ok=True)
    signer = [JAVA / 'java.exe', '-jar', BT / 'lib' / 'apksigner.jar']
    run([*signer, 'sign', '--ks', key, '--ks-key-alias', 'fgovr-local',
         '--ks-pass', 'pass:android', '--key-pass', 'pass:android', '--out', apk, aligned], 'apk_sign')
    run([*signer, 'verify', '--verbose', '--print-certs', apk], 'apk_signature_verify')
    run([BT / 'zipalign.exe', '-c', '-p', '4', apk], 'apk_alignment_verify')
    run([BT / 'aapt2.exe', 'dump', 'badging', apk], 'apk_badging')
    provenance.update(apk=str(apk), apk_sha256=sha(apk), apk_bytes=apk.stat().st_size)
    (apk.parent / 'quest_manifest.json').write_text(json.dumps(provenance, indent=2), encoding='utf-8')
    print(f'APK ready: {apk} ({apk.stat().st_size / 1048576:.1f} MiB)', flush=True)

if __name__ == '__main__':
    main()
