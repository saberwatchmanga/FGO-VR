"""Complete pinned external source copies without changing the original PC tree."""
import hashlib
import json
import os
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
source = ROOT.parent / 'source/AstroQuest/shadps4-arm64-main/externals'
target = ROOT / 'source/AstroQuest/shadps4-arm64-main/externals'
added = {}
for folder, directories, files in os.walk(source):
    directories[:] = [name for name in directories if name not in ('.git', 'build')]
    relative = Path(folder).relative_to(source)
    for name in files:
        if name == '.git': continue
        incoming = Path(folder) / name
        destination = target / relative / name
        if destination.exists(): continue
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(incoming, destination)
        added[destination.relative_to(target).as_posix()] = hashlib.sha256(destination.read_bytes()).hexdigest()
(ROOT / 'evidence/dependency_completion.json').write_text(json.dumps(added, indent=2), encoding='utf-8')
print(f'Added {len(added)} missing pinned dependency files; existing files preserved.')
