#!/usr/bin/env python3
"""Install this skill only; explicit updates retain a full backup."""
import argparse, hashlib, json, os, shutil, tempfile, uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANAGED = ('SKILL.md', 'agents', 'references', 'scripts')

def install(target, update=False):
    target = Path(target).expanduser().absolute()
    if target.is_symlink():
        raise ValueError('Refusing to replace a symlink; choose a separate installation directory.')
    target = target.resolve()
    if target == ROOT or ROOT in target.parents or target in ROOT.parents:
        raise ValueError('Installation target must not overlap this source repository.')
    if target.exists() and not update:
        raise FileExistsError('Target exists. Inspect local edits, then use --update to preserve a backup.')
    if target.exists() and not target.is_dir():
        raise ValueError('Target is not a directory.')
    for name in MANAGED:
        if not (ROOT / name).exists():
            raise FileNotFoundError(ROOT / name)
    target.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix='.pfr-install-', dir=target.parent))
    backup = None
    try:
        for name in MANAGED:
            src, dst = ROOT / name, stage / name
            if src.is_dir():
                shutil.copytree(src, dst, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
            else:
                shutil.copy2(src, dst)
        files = [p for p in stage.rglob('*') if p.is_file()]
        for p in files:
            original = ROOT / p.relative_to(stage)
            if hashlib.sha256(p.read_bytes()).digest() != hashlib.sha256(original.read_bytes()).digest():
                raise RuntimeError('Staged copy mismatch: ' + str(p))
        if target.exists():
            backup_root = target.parent.parent / 'skill-backups'
            backup_root.mkdir(parents=True, exist_ok=True)
            stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
            backup = backup_root / (target.name + '-' + stamp + '-' + uuid.uuid4().hex[:8])
            target.rename(backup)
        try:
            stage.rename(target)
        except Exception:
            if backup is not None and not target.exists():
                backup.rename(target)
            raise
        return {'installed': str(target), 'backup': str(backup) if backup else None, 'files': len(files)}
    finally:
        if stage.exists():
            shutil.rmtree(stage)  # Only our temporary staging directory.

if __name__ == '__main__':
    default = Path(os.environ.get('CODEX_HOME', str(Path.home() / '.codex'))) / 'skills/paper-figure-reconstruction'
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target', type=Path, default=default)
    parser.add_argument('--update', action='store_true')
    args = parser.parse_args()
    try:
        print(json.dumps(install(args.target, args.update), indent=2))
    except (ValueError, FileExistsError, FileNotFoundError) as error:
        parser.exit(1, str(error) + '\n')
