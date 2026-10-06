"""Build a portable Debian 13 ARM64 development sysroot; no package manager."""
import concurrent.futures
import argparse
import hashlib
import io
import json
import lzma
from pathlib import Path, PurePosixPath
import posixpath
import shutil
import tarfile
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
SYSROOT = ROOT / 'tools' / 'sysroot-arm64'
CACHE = ROOT / 'tools' / 'debian-cache'
MIRROR = 'https://deb.debian.org/debian/'
PACKAGES = '''libc6 libc6-dev linux-libc-dev gcc-14-base libgcc-14-dev libstdc++-14-dev
libstdc++6 libgcc-s1 libatomic1 libgomp1 libitm1 libasan8 liblsan0 libtsan2 libubsan1
libvulkan-dev libvulkan1 libx11-dev libx11-6 libxext-dev libxext6 libxcb1-dev libxcb1
libxau-dev libxau6 libxdmcp-dev libxdmcp6 x11proto-dev xorg-sgml-doctools xtrans-dev
libcap-dev libcap2 libdrm-dev libdrm2 libdrm-common libexpat1-dev libexpat1
libudev-dev libudev1 uuid-dev libuuid1'''.split()

def download(url, path, expected=None):
    if path.exists() and (expected is None or hashlib.sha256(path.read_bytes()).hexdigest() == expected):
        return path.read_bytes()
    with urllib.request.urlopen(url, timeout=120) as response:
        data = response.read()
    if expected and hashlib.sha256(data).hexdigest() != expected:
        raise RuntimeError(f'checksum mismatch: {url}')
    path.write_bytes(data)
    return data

def ar_members(data):
    if data[:8] != b'!<arch>\n':
        raise RuntimeError('invalid Debian ar archive')
    offset = 8
    while offset + 60 <= len(data):
        header = data[offset:offset + 60]
        name = header[:16].decode().strip().rstrip('/')
        size = int(header[48:58])
        yield name, data[offset + 60:offset + 60 + size]
        offset += 60 + size + (size & 1)

def normalized(path):
    parts = list(PurePosixPath(posixpath.normpath(path.lstrip('/'))).parts)
    if parts and parts[0] in {'lib', 'lib64', 'bin', 'sbin'}:
        parts.insert(0, 'usr')
    if '..' in parts:
        raise RuntimeError(f'unsafe sysroot path: {path}')
    return '/'.join(parts)

def prepare_package(item):
    name, metadata = item
    filename = metadata['Filename']
    data = download(MIRROR + filename, CACHE / Path(filename).name, metadata['SHA256'])
    print(f'cached {name} {metadata["Version"]}', flush=True)
    return name, metadata, data

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--packages', nargs='+')
    selected = parser.parse_args().packages or PACKAGES
    CACHE.mkdir(parents=True, exist_ok=True)
    SYSROOT.mkdir(parents=True, exist_ok=True)
    package_index = {}
    for suite in ('trixie', 'trixie-updates'):
        relative = f'dists/{suite}/main/binary-arm64/Packages.xz'
        index = lzma.decompress(download(MIRROR + relative, CACHE / f'{suite}-Packages.xz')).decode()
        for stanza in index.split('\n\n'):
            fields = {}
            for line in stanza.splitlines():
                if line and not line.startswith(' ') and ': ' in line:
                    key, value = line.split(': ', 1)
                    fields[key] = value
            if fields.get('Package') in selected:
                package_index[fields['Package']] = fields
    missing = set(selected) - package_index.keys()
    if missing:
        raise RuntimeError(f'packages unavailable: {missing}')
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        archives = list(pool.map(prepare_package, [(name, package_index[name]) for name in selected]))
    links, records = [], []
    for name, metadata, archive in archives:
        payload = next((data for member, data in ar_members(archive) if member.startswith('data.tar')), None)
        if payload is None:
            raise RuntimeError(f'no tar payload: {name}')
        with tarfile.open(fileobj=io.BytesIO(payload), mode='r:*') as tar:
            for member in tar:
                relative = normalized(member.name)
                if not relative or relative.startswith('usr/share/'):
                    continue
                output = (SYSROOT / relative).resolve()
                if not output.is_relative_to(SYSROOT.resolve()):
                    raise RuntimeError(f'archive escapes sysroot: {member.name}')
                if member.isdir():
                    output.mkdir(parents=True, exist_ok=True)
                elif member.isreg():
                    output.parent.mkdir(parents=True, exist_ok=True)
                    with tar.extractfile(member) as source, output.open('wb') as target:
                        shutil.copyfileobj(source, target)
                elif member.issym() or member.islnk():
                    source = member.linkname if member.islnk() or member.linkname.startswith('/') else posixpath.join(posixpath.dirname(member.name), member.linkname)
                    links.append((relative, normalized(source)))
        records.append({'package': name, 'version': metadata['Version'],
                        'url': MIRROR + metadata['Filename'], 'sha256': metadata['SHA256']})
    for _ in range(12):
        pending = []
        for relative, source in links:
            target_path = SYSROOT / relative
            source_path = SYSROOT / source
            if not source_path.exists():
                pending.append((relative, source))
            elif source_path.is_file():
                target_path.parent.mkdir(parents=True, exist_ok=True)
                if target_path.resolve() != source_path.resolve():
                    shutil.copyfile(source_path, target_path)
            elif not target_path.exists():
                shutil.copytree(source_path, target_path, dirs_exist_ok=True)
        if len(pending) == len(links):
            links = pending
            break
        links = pending
    # GCC/libc link scripts use /lib; mirrored files keep Windows lexical path lookup simple.
    for name in ('lib', 'lib64', 'include'):
        source = SYSROOT / 'usr' / name
        if source.exists():
            shutil.copytree(source, SYSROOT / name, dirs_exist_ok=True)
    manifest_path = ROOT / 'evidence' / 'arm64_sysroot.json'
    if manifest_path.exists():
        old = json.loads(manifest_path.read_text(encoding='utf-8'))
        records = [x for x in old['packages'] if x['package'] not in selected] + records
        links = [x for x in old.get('unresolved_links', []) if x not in links] + links
    manifest = {'suite': 'Debian 13 trixie ARM64', 'packages': records,
                'unresolved_links': links, 'sysroot': str(SYSROOT)}
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    print(f'sysroot ready: {SYSROOT}; unresolved links: {len(links)}', flush=True)

if __name__ == '__main__':
    main()
