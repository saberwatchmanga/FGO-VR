"""Fetch a pinned public baseline and apply exactly one platform's complete patch."""
import argparse
from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser()
parser.add_argument('platform',choices=['pc','quest'])
parser.add_argument('destination',type=Path)
args=parser.parse_args()
destination=args.destination.resolve()
if destination.exists(): raise SystemExit('Use a new destination; existing work is preserved.')
def git(*values): subprocess.run(['git',*map(str,values)],check=True)
git('clone','--no-checkout','https://github.com/bigmak94/AstroQuest.git',destination)
git('-C',destination,'checkout','--detach','9f42c44d4e838e3a0df67913e350c4f098110862')
git('-C',destination,'submodule','update','--init','--recursive')
patch=ROOT/'patches'/f'fgo-resolution-{args.platform}-complete.patch'
git('-C',destination,'apply','--check',patch)
git('-C',destination,'apply',patch)
print('Prepared',args.platform,'at',destination)
