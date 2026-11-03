"""Check portable skill references, corpus coverage, and immutable source hashes."""
from pathlib import Path
import json,re,hashlib
import yaml

root=Path(__file__).resolve().parents[1]
errors=[]
skills=sorted((root/'skills').iterdir())
if len(skills)!=2: errors.append('Expected exactly two skill directories')
links=0
for skill in skills:
    text=(skill/'SKILL.md').read_text(encoding='utf-8')
    front=yaml.safe_load(text.split('---',2)[1])
    if front.get('name')!=skill.name or not front.get('description'): errors.append(f'Invalid skill metadata: {skill.name}')
    ui=yaml.safe_load((skill/'agents/openai.yaml').read_text(encoding='utf-8'))
    if '$'+skill.name not in ui['interface']['default_prompt']: errors.append(f'Invocation mismatch: {skill.name}')
    for p in skill.rglob('*.md'):
        for target in re.findall(r'\]\(([^)]+)\)',p.read_text(encoding='utf-8')):
            if re.match(r'[a-zA-Z]+://',target) or target.startswith('#'): continue
            resolved=(p.parent/target.split('#')[0]).resolve()
            if not resolved.exists(): errors.append(f'Broken link {p.relative_to(root)} -> {target}')
            elif not resolved.is_relative_to(skill.resolve()): errors.append(f'External dependency {p.relative_to(root)} -> {target}')
            links+=1
manifest=json.loads((root/'corpus/file_manifest.json').read_text(encoding='utf-8'))
verified=0
for r in manifest:
    p=root.parent/'literature'/r['path']
    if not p.exists() or hashlib.sha256(p.read_bytes()).hexdigest()!=r['sha256']:
        errors.append(f'Source missing or changed: {r["path"]}')
    else: verified+=1
for p in root.rglob('*'):
    if '.git' in p.parts or '.work' in p.parts or '__pycache__' in p.parts: continue
    if any(ord(c)>127 for c in p.name): errors.append(f'New non-English filename: {p.relative_to(root)}')
    if p.suffix.lower()=='.pdf': errors.append(f'Unexpected original PDF in package: {p.relative_to(root)}')
print(json.dumps({'skill_count':len(skills),'skill_local_links_checked':links,'original_pdf_hashes_verified':verified,'errors':errors},ensure_ascii=False,indent=2))
raise SystemExit(bool(errors))
