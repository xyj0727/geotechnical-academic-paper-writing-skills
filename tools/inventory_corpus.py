"""Inventory local PDFs, extract page-delimited text and keep source bytes untouched."""
from pathlib import Path
import hashlib, json, re
import fitz

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT.parent / 'literature'
WORK = ROOT / '.work'
WORK.mkdir(exist_ok=True)
records, seen = [], {}
for p in sorted(SOURCE.rglob('*.pdf'), key=lambda p: str(p).lower()):
    relative = p.relative_to(SOURCE).as_posix()
    digest = hashlib.sha256(p.read_bytes()).hexdigest()
    record = {'path': relative, 'sha256': digest, 'bytes': p.stat().st_size}
    if digest in seen:
        record.update({'status': 'byte_duplicate', 'duplicate_of': seen[digest]})
    else:
        ident = f'P{len(seen)+1:03d}'
        seen[digest] = ident
        record['id'] = ident
        try:
            doc = fitz.open(p)
            page_texts = [page.get_text(sort=True) for page in doc]
            record.update({'status': 'extracted', 'pages': len(doc), 'characters': sum(map(len,page_texts)), 'title_metadata': doc.metadata.get('title',''), 'low_text_pages': [i+1 for i,t in enumerate(page_texts) if len(t.strip())<80]})
            record['text_sha256'] = hashlib.sha256(re.sub(r'\s+', '', ''.join(page_texts)).encode()).hexdigest()
            (WORK / f'{ident}.txt').write_text('\n\n'.join(f'=== PDF PAGE {i+1} ===\n{t}' for i,t in enumerate(page_texts)),encoding='utf-8')
            (WORK / f'{ident}.pages.json').write_text(json.dumps(page_texts,ensure_ascii=False),encoding='utf-8')
            doc.close()
        except Exception as exc:
            record.update({'status':'unreadable', 'error':str(exc)})
    records.append(record)
(ROOT/'corpus'/'file_manifest.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
for r in records:
    if r.get('id'):
        print(r['id'],r['status'],r.get('pages'),r.get('characters'),r['path'])
print('TOTAL FILES',len(records),'UNIQUE BYTES',len(seen))
