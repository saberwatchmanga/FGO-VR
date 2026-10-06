"""Fetch pinned, official Android build dependencies into the FGO workspace."""
import concurrent.futures
import hashlib
import json
from pathlib import Path
import shutil
import urllib.request
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'tools' / 'android'
CACHE = ROOT / 'tools' / 'downloads'
BASE = 'https://dl.google.com/android/repository/'
WANTED = {
    'ndk;27.3.13750724': ('android-ndk-r27d-windows.zip', OUT / 'ndk' / 'android-ndk-r27d'),
    'platforms;android-36': ('platform-36_r02.zip', OUT / 'sdk' / 'platforms' / 'android-36'),
    'build-tools;36.0.0': ('build-tools_r36_windows.zip', OUT / 'sdk' / 'build-tools' / '36.0.0'),
    'platform-tools': (None, OUT / 'sdk' / 'platform-tools'),
}

def digest(path, kind):
    h = hashlib.new(kind)
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

def fetch_package(spec):
    package, archive, destination = spec
    relative = archive.findtext('complete/url')
    size = int(archive.findtext('complete/size'))
    checksum_node = archive.find('complete/checksum')
    kind = checksum_node.attrib.get('type', 'sha1')
    expected = checksum_node.text.strip()
    target = CACHE / Path(relative).name
    if not target.exists() or target.stat().st_size != size or digest(target, kind) != expected:
        partial = target.with_suffix(target.suffix + '.partial')
        print(f'downloading {relative}: {size // 1048576} MiB', flush=True)
        with urllib.request.urlopen(BASE + relative, timeout=90) as response, partial.open('wb') as stream:
            shutil.copyfileobj(response, stream, 4 * 1024 * 1024)
        if partial.stat().st_size != size or digest(partial, kind) != expected:
            raise RuntimeError(f'official checksum mismatch: {relative}')
        partial.replace(target)
    destination.mkdir(parents=True, exist_ok=True)
    stamp = destination / '.fgo-official-archive.sha256'
    sha256 = digest(target, 'sha256')
    if not stamp.exists() or stamp.read_text().strip() != sha256:
        print(f'extracting {relative}', flush=True)
        with zipfile.ZipFile(target) as archive_zip:
            names = [name for name in archive_zip.namelist() if name and not name.endswith('/')]
            top = {name.split('/')[0] for name in names}
            strip = len(top) == 1 and all('/' in name for name in names)
            for name in names:
                relative_path = name.split('/', 1)[1] if strip else name
                output = (destination / relative_path).resolve()
                if not output.is_relative_to(destination.resolve()):
                    raise RuntimeError(f'unsafe archive entry: {name}')
                output.parent.mkdir(parents=True, exist_ok=True)
                with archive_zip.open(name) as source, output.open('wb') as stream:
                    shutil.copyfileobj(source, stream)
        stamp.write_text(sha256 + '\n')
    print(f'ready {package}: {destination}', flush=True)
    return {'package': package, 'url': BASE + relative, 'bytes': size,
            'official_checksum_type': kind, 'official_checksum': expected,
            'sha256': sha256, 'directory': str(destination)}

def main():
    CACHE.mkdir(parents=True, exist_ok=True)
    data = urllib.request.urlopen(BASE + 'repository2-1.xml', timeout=60).read()
    (CACHE / 'repository2-1.xml').write_bytes(data)
    specs = {}
    for package in ET.fromstring(data):
        name = package.attrib.get('path')
        if name not in WANTED:
            continue
        wanted_url, destination = WANTED[name]
        for archive in package.findall('archives/archive'):
            if archive.findtext('host-os') not in (None, 'windows'):
                continue
            url = archive.findtext('complete/url')
            if wanted_url is None or url == wanted_url:
                specs[name] = (name, archive, destination)
    if set(specs) != set(WANTED):
        raise RuntimeError(f'missing official packages: {set(WANTED) - set(specs)}')
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        records = list(pool.map(fetch_package, specs.values()))
    manifest = ROOT / 'evidence' / 'android_toolchain.json'
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding='utf-8')

if __name__ == '__main__':
    main()
