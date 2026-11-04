"""Incrementally inventory local PDFs without changing existing IDs or source bytes.

--added-date filters only new paths by file creation date in Asia/Shanghai.
Existing records are retained exactly and their source hashes are checked first.
Use --exclude-dir with an explicit source-relative review-output directory.
"""
from __future__ import annotations

import argparse
from datetime import date, datetime, timedelta, timezone
import hashlib
import json
import os
from pathlib import Path
import re

import fitz


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT.parent / 'literature'
WORK = ROOT / '.work'
LOCAL_TIMEZONE = timezone(timedelta(hours=8), 'Asia/Shanghai')
RENDER_DPI = 144


def source_files(source: Path, excluded_dirs=()):
    """Exclude only explicitly named relative subtrees, never filename patterns."""
    excluded = []
    for value in excluded_dirs:
        relative = Path(value)
        if relative.is_absolute() or '..' in relative.parts or not relative.parts:
            raise ValueError(f'--exclude-dir must name a source-relative directory: {value}')
        excluded.append(relative)
    return sorted((p for p in source.rglob('*') if p.is_file()
                   and not any(p.relative_to(source).is_relative_to(item) for item in excluded)),
                  key=lambda p: str(p).lower())


def created_date(path: Path) -> date:
    stat = path.stat()
    stamp = getattr(stat, 'st_birthtime', None)
    if stamp is None:
        if os.name != 'nt':
            raise ValueError('File creation time is unavailable; --added-date must not use modification time')
        stamp = stat.st_ctime
    return datetime.fromtimestamp(stamp, LOCAL_TIMEZONE).date()


def page_render_hashes(path: Path) -> list[str]:
    hashes = []
    with fitz.open(path) as doc:
        for page in doc:
            pix = page.get_pixmap(dpi=RENDER_DPI, colorspace=fitz.csRGB, alpha=False)
            header = f'{pix.width},{pix.height},{pix.n};'.encode('ascii')
            hashes.append(hashlib.sha256(header + pix.samples).hexdigest())
    return hashes


def extract(path: Path, ident: str, work: Path) -> dict:
    with fitz.open(path) as doc:
        texts = [page.get_text(sort=True) for page in doc]
        result = {'status': 'extracted', 'pages': len(doc),
                  'characters': sum(map(len, texts)), 'title_metadata': doc.metadata.get('title', ''),
                  'low_text_pages': [i + 1 for i, text in enumerate(texts) if len(text.strip()) < 80],
                  'text_sha256': hashlib.sha256(re.sub(r'\s+', '', ''.join(texts)).encode()).hexdigest()}
    work.mkdir(parents=True, exist_ok=True)
    (work / f'{ident}.txt').write_text('\n\n'.join(f'=== PDF PAGE {i + 1} ===\n{text}'
                                               for i, text in enumerate(texts)), encoding='utf-8')
    (work / f'{ident}.pages.json').write_text(json.dumps(texts, ensure_ascii=False), encoding='utf-8')
    return result


def inventory(source: Path, work: Path, previous: list[dict], added_date=None, excluded_dirs=()):
    """Return an appended inventory; old records, IDs and ordering are immutable."""
    records = [dict(row) for row in previous]
    by_path, by_id, by_hash, by_text = {}, {}, {}, {}
    for row in records:
        if row['path'] in by_path:
            raise ValueError(f"Repeated source path: {row['path']}")
        by_path[row['path']] = row
        path = source / row['path']
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != row['sha256']:
            raise ValueError(f"Existing source missing or changed; reconcile manually: {row['path']}")
        if row.get('id'):
            ident = row['id']
            if not re.fullmatch(r'P\d+', ident) or ident in by_id or row['sha256'] in by_hash:
                raise ValueError(f'Invalid/repeated unique-byte ID or hash: {ident}')
            by_id[ident], by_hash[row['sha256']] = row, ident
            if row.get('text_sha256') and row.get('characters', 0) > 0:
                by_text.setdefault(row['text_sha256'], []).append(ident)
    for row in records:
        if not row.get('id') and (row.get('duplicate_of') not in by_id
                                 or row['sha256'] != by_id[row['duplicate_of']]['sha256']):
            raise ValueError(f"Invalid historical byte duplicate: {row['path']}")
    next_number = max((int(ident[1:]) for ident in by_id), default=0) + 1
    renders = {}
    for path in source_files(source, excluded_dirs):
        relative = path.relative_to(source).as_posix()
        if path.suffix.lower() != '.pdf' or relative in by_path:
            continue
        if added_date is not None and created_date(path) != added_date:
            continue
        content_hash = hashlib.sha256(path.read_bytes()).hexdigest()
        row = {'path': relative, 'sha256': content_hash, 'bytes': path.stat().st_size}
        if content_hash in by_hash:
            row.update(status='byte_duplicate', duplicate_of=by_hash[content_hash])
        else:
            ident = f'P{next_number:03d}'
            next_number += 1
            row['id'] = ident
            try:
                row.update(extract(path, ident, work))
            except Exception as exc:
                row.update(status='unreadable', error=str(exc))
            # Text equality alone cannot establish that figures or tables are identical.
            candidates = by_text.get(row.get('text_sha256'), []) if row.get('characters', 0) > 0 else []
            for target in candidates:
                target_row = by_id[target]
                if row['pages'] != target_row.get('pages'):
                    continue
                try:
                    if ident not in renders:
                        renders[ident] = page_render_hashes(path)
                    if target not in renders:
                        renders[target] = page_render_hashes(source / target_row['path'])
                except Exception as exc:
                    row['duplicate_comparison_error'] = str(exc)
                    continue
                if renders[ident] == renders[target]:
                    row.update(status='content_duplicate', duplicate_of=target,
                               content_duplicate_evidence={
                                   'method': 'normalized_text_and_page_pixels',
                                   'render_dpi': RENDER_DPI, 'colorspace': 'RGB', 'alpha': False,
                                   'source_sha256': content_hash, 'target_sha256': target_row['sha256'],
                                   'page_render_sha256': renders[ident],
                                   'target_page_render_sha256': renders[target]})
                    break
            by_id[ident], by_hash[content_hash] = row, ident
            if row.get('text_sha256') and row.get('characters', 0) > 0:
                by_text.setdefault(row['text_sha256'], []).append(ident)
        records.append(row)
        by_path[relative] = row
    return records


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--added-date', type=date.fromisoformat, metavar='YYYY-MM-DD',
                        help='append only new paths created on this date in Asia/Shanghai; retain all existing rows')
    parser.add_argument('--exclude-dir', action='append', default=[],
                        help='explicit source-relative review-output directory to skip (repeatable)')
    args = parser.parse_args(argv)
    manifest = ROOT / 'corpus' / 'file_manifest.json'
    previous = json.loads(manifest.read_text(encoding='utf-8')) if manifest.exists() else []
    records = inventory(SOURCE, WORK, previous, args.added_date, args.exclude_dir)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    temporary = manifest.with_suffix('.json.tmp')
    temporary.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding='utf-8')
    temporary.replace(manifest)
    for row in records[len(previous):]:
        print(row.get('id', '-'), row['status'], row.get('pages'), row['path'])
    print('TOTAL FILES', len(records), 'UNIQUE BYTES', sum(bool(row.get('id')) for row in records),
          'APPENDED', len(records) - len(previous))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
