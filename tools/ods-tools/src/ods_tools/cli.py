from __future__ import annotations
import argparse, json
from pathlib import Path
from .parsers.lha import inspect

def repo_root() -> Path:
    p=Path.cwd()
    for candidate in [p,*p.parents]:
        if (candidate/'catalog'/'archives').is_dir(): return candidate
    raise SystemExit('ODS repository root not found')

def main() -> int:
    parser=argparse.ArgumentParser(prog='ods')
    sub=parser.add_subparsers(dest='command',required=True)
    inv=sub.add_parser('inventory',help='inventory an LHA archive')
    inv.add_argument('archive',type=Path)
    inv.add_argument('--json',type=Path)
    sub.add_parser('list-archives',help='list cataloged archives')
    sub.add_parser('validate',help='validate repository catalog invariants')
    args=parser.parse_args()
    if args.command=='inventory':
        result=inspect(args.archive)
        if args.json: args.json.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(result,indent=2)); return 0
    root=repo_root()
    manifests=[]
    for path in sorted((root/'catalog'/'archives').glob('*.json')):
        data=json.loads(path.read_text(encoding='utf-8')); manifests.append(data)
    if args.command=='list-archives':
        for d in manifests: print(f"{d['source_filename']}: {d['entry_count']} entries {d['source_sha256'][:12]}")
        return 0
    if args.command=='validate':
        seen=set()
        for d in manifests:
            assert d['entry_count']==len(d['entries']), d['source_filename']
            assert len(d['source_sha256'])==64
            assert d['source_filename'] not in seen
            seen.add(d['source_filename'])
            for e in d['entries']:
                assert not Path(e['path']).is_absolute()
                assert '..' not in Path(e['path']).parts
        print(f'OK: {len(manifests)} archives, {sum(d["entry_count"] for d in manifests)} entries')
        return 0
    return 2
