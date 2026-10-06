"""Check new ARM64 core dependencies and symbol versions against the bundled runtime."""
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
READELF = ROOT / 'tools/android/ndk/android-ndk-r27d/toolchains/llvm/prebuilt/windows-x86_64/bin/llvm-readelf.exe'
CORE = ROOT / 'build/arm64/shadps4'
RUNTIME = ROOT / 'build/probes/runtime/host'
EVIDENCE = ROOT / 'evidence'

def read(path):
    data = path.read_bytes()[:20]
    if data[:5] != b'\x7fELF\x02' or int.from_bytes(data[18:20], 'little') != 183:
        raise RuntimeError(f'Not ELF64 AArch64: {path}')
    return subprocess.check_output([str(READELF), '-h', '-d', '-V', str(path)], text=True, encoding='utf-8')

output = read(CORE)
(EVIDENCE / 'fgo_core_elf.txt').write_text(output, encoding='utf-8')
needed = re.findall(r'\(NEEDED\).*Shared library: \[([^\]]+)\]', output)
requirements = {}
library = None
in_needs = False
for line in output.splitlines():
    if line.startswith('Version needs section'): in_needs = True
    if not in_needs: continue
    match = re.search(r'File: (\S+)', line)
    if match:
        library = match[1]
        requirements[library] = set()
    match = re.search(r'Name: (\S+)', line)
    if match and library: requirements[library].add(match[1])
report = {'core': str(CORE), 'architecture': 'ELF64 AArch64', 'needed': needed, 'libraries': {}, 'passed': True}
for name in needed:
    path = RUNTIME / name
    if not path.is_file():
        report['libraries'][name] = {'missing': True}
        report['passed'] = False
        continue
    library_output = read(path)
    definitions = library_output.split('Version definition section', 1)
    provided = set()
    if len(definitions) > 1:
        provided = set(re.findall(r'Name: (\S+)', definitions[1].split('Version needs section', 1)[0]))
    missing = sorted(requirements.get(name, set()) - provided)
    report['libraries'][name] = {'required_versions': sorted(requirements.get(name, set())), 'missing_versions': missing}
    if missing: report['passed'] = False
(EVIDENCE / 'elf_runtime_compatibility.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report, indent=2))
if not report['passed']: raise SystemExit(1)
