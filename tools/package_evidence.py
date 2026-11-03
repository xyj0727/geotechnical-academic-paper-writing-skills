"""Package original reading notes; never copy source PDFs, extracted text or images.

Run from any directory: python tools/package_evidence.py [--strict]
Inputs are corpus/file_manifest.json and .work/readings/P*.{md,json}.
The local literature directory is inventoried by filename only for non-PDF files.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / '.work' / 'readings'
SOURCE = ROOT.parent / 'literature'
SKILLS = {
    'writing': 'geotech-paper-writing',
    'figures': 'geotech-figure-table-templates',
}
TRANSLATIONS = {'P016': 'P015', 'P074': 'P046'}
for start, canonical in [(17, 9), (21, 10), (25, 11), (29, 12), (33, 13), (37, 14)]:
    TRANSLATIONS.update({f'P{number:03d}': f'P{canonical:03d}' for number in range(start, start + 4)})
EXCLUDED = {'P044': '非论文电子发票；只记录排除状态，不复制正文或个人/交易信息。'}
STATUS_ZH = {
    'read_complete': '阅读覆盖已记录',
    'read_partial': '阅读记录不完整',
    'pending': '待完成',
    'excluded_nonpaper': '非论文排除',
}


def read_json(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def write(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(content, encoding='utf-8', newline='\n')
    temporary.replace(path)


def digest(content: str) -> str:
    return hashlib.sha256(content.encode('utf-8')).hexdigest()


def cell(value) -> str:
    return str(value if value is not None else '未确定').replace('|', '\\|').replace('\n', ' ')


def page_ranges(pages) -> str:
    pages = sorted(set(pages))
    if not pages:
        return '无'
    groups, start, last = [], pages[0], pages[0]
    for number in pages[1:]:
        if number == last + 1:
            last = number
        else:
            groups.append(str(start) if start == last else f'{start}–{last}')
            start = last = number
    groups.append(str(start) if start == last else f'{start}–{last}')
    return ', '.join(groups)


def sections(note: str):
    """Keep entire level-two blocks, including nested headings and PDF locators."""
    matches = list(re.finditer(r'^## (.+)$', note, flags=re.M))
    if not matches:
        return note, []
    result = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(note)
        result.append((match.group(1), note[match.start():end].rstrip()))
    return note[:matches[0].start()].rstrip(), result


def route(heading: str) -> set[str]:
    # Shared qualifications come first: do not strip them from either skill.
    if any(word in heading for word in ['迁移', '限制', '边界', '覆盖', '文献类型', '处理决定']):
        if '写作' not in heading:
            return {'writing', 'figures'}
    if any(word in heading for word in ['写作', '结构', '论证', '文献构成', '全文链条']):
        return {'writing'}
    if any(word in heading for word in ['图', '曲线', '表格', '面板']):
        return {'figures'}
    # Preserve an unfamiliar block in both cards rather than lose evidence.
    return {'writing', 'figures'}


def normalize_pages(data: dict, key: str, total: int, ident: str) -> list[int]:
    values = data.get(key, [])
    if not isinstance(values, list) or any(type(p) is not int or not 1 <= p <= total for p in values):
        raise ValueError(f'{ident}: invalid {key}: expected PDF page integers within 1..{total}')
    return sorted(set(values))


def make_source(row: dict) -> tuple[dict, str]:
    ident = row['id']
    common = {
        'id': ident, 'canonical_id': ident, 'source_path': row['path'],
        'source_sha256': row['sha256'], 'pages': row.get('pages', 0),
        'composite_source': ident == 'P063',
    }
    if ident in EXCLUDED:
        return {**common, 'title': '非论文电子发票（已排除）', 'year': None,
                'kind': '非论文', 'reading_status': 'excluded_nonpaper',
                'exclusion_reason': EXCLUDED[ident]}, ''
    md_path, json_path = INPUT / f'{ident}.md', INPUT / f'{ident}.json'
    if not md_path.exists() or not json_path.exists():
        missing = [p.name for p in [md_path, json_path] if not p.exists()]
        return {**common, 'title': row.get('title_metadata') or ident, 'year': None,
                'kind': '待补阅读记录', 'reading_status': 'pending',
                'missing_note_files': missing, 'read_text_pages': [], 'visual_pages': [],
                'read_visual_text_pages': [], 'blank_or_separator_pages': [],
                'unaccounted_pages': list(range(1, common['pages'] + 1)),
                'limitations': ['阅读笔记或覆盖记录尚未完整提供。']}, ''
    data, note = read_json(json_path), md_path.read_text(encoding='utf-8')
    if data.get('id') != ident:
        raise ValueError(f'{json_path}: ID does not match filename')
    if not note.strip():
        raise ValueError(f'{md_path}: empty reading note')
    pages = {key: normalize_pages(data, key, common['pages'], ident) for key in
             ['read_text_pages', 'visual_pages', 'read_visual_text_pages', 'blank_or_separator_pages']}
    accounted = set(pages['read_text_pages']) | set(pages['read_visual_text_pages']) | set(pages['blank_or_separator_pages'])
    unaccounted = sorted(set(range(1, common['pages'] + 1)) - accounted)
    status = 'read_complete' if not unaccounted else 'read_partial'
    return {**common, **data, **pages, 'reading_status': status,
            'unaccounted_pages': unaccounted,
            'note_sha256': digest(note), 'coverage_record_sha256': digest(json_path.read_text(encoding='utf-8')),
            'complete_note': f'papers/{ident}.md'}, note


def card(source: dict, note: str, kind: str) -> tuple[str, list[dict]]:
    ident = source['id']
    label = '写作证据卡' if kind == 'writing' else '图表证据卡'
    lines = [f'# {ident} — {label}', '', f"题名：{source['title']}",
             f"年份：{source.get('year') or '未确定'}。类别：{source['kind']}。",
             f"原始来源 ID：{ident}；本地文献相对路径：`{source['source_path']}`。",
             f"来源 PDF：{source['pages']} 页；以下定位均为 PDF 页序。",
             f"阅读状态：{STATUS_ZH[source['reading_status']]}。",
             f"文本阅读：{page_ranges(source.get('read_text_pages', []))}（{len(source.get('read_text_pages', []))} 页）；"
             f"图像中的文字另读：{page_ranges(source.get('read_visual_text_pages', []))}；"
             f"实际图表视觉检查：{page_ranges(source.get('visual_pages', []))}（{len(source.get('visual_pages', []))} 页）。",
             f"空白/分隔页：{page_ranges(source.get('blank_or_separator_pages', []))}；"
             f"尚未说明覆盖的页：{page_ranges(source.get('unaccounted_pages', []))}。", '',
             '[返回本 skill 来源索引](../source-atlas.md)', '',
             '本卡由同一份原创阅读笔记生成。共同的书目信息、阅读范围与限制在两个 skill 中保留，支持各自独立复制安装；未复制原始论文、提取全文或截图。', '']
    if source['reading_status'] == 'pending':
        lines += ['## 待完成', '', '缺少：' + ', '.join(source['missing_note_files']) + '。本卡不声称已精读。', '']
        return '\n'.join(lines), []
    intro, blocks = sections(note)
    # Reuse the original introduction, excluding only its level-one title.
    intro = re.sub(r'^# .+\n?', '', intro, count=1).strip()
    if intro:
        lines += ['## 原笔记的来源与阅读说明', '', intro, '']
    routes = []
    for heading, block in blocks:
        destinations = route(heading)
        routes.append({'heading': heading, 'destinations': sorted(destinations)})
        if kind in destinations:
            lines += [block, '']
    if not blocks:
        lines += ['## 保留的原始笔记内容', '', re.sub(r'^# .+\n?', '', note, count=1).strip(), '']
    if kind == 'figures':
        lines += ['## 关键图表定位记录', '']
        entries = [('图', item) for item in source.get('key_figures', [])]
        entries += [('表', item) for item in source.get('key_tables', [])]
        if not entries:
            lines += ['记录中没有关键图表项；以以上原笔记对“未设图表/不适用”的说明为准。', '']
        else:
            lines += ['| 类别 | 原文标号 | PDF 页 | 用途 |', '|---|---|---|---|']
            for item_kind, item in entries:
                lines.append(f"| {item_kind} | {cell(item.get('label'))} | {cell(item.get('page'))} | {cell(item.get('purpose'))} |")
            lines.append('')
    limits = source.get('limitations', [])
    if limits:
        lines += ['## 覆盖记录中的限制', '']
        lines += [f'- {item}' for item in limits]
        lines.append('')
    lines += [f"生成依据：完整原创笔记 SHA-256 `{source['note_sha256']}`。", '']
    return '\n'.join(lines), routes


def auxiliary_record(path: Path, source_rows: dict) -> dict:
    relative = path.relative_to(SOURCE).as_posix()
    lowered = relative.lower()
    canonical, reason = None, '辅助文件，不作为新增论文；仅登记文件身份，未声称重新核对其中全部内容。'
    for number, ident in [('020-01254-0','P009'), ('020-01534-9','P010'), ('022-02075-z','P011'),
                          ('023-02421-9','P012'), ('024-02757-w','P013'), ('024-02822-4','P014'),
                          ('024-03048-0','P015')]:
        if number in lowered:
            canonical = ident
            break
    if 'babu2025' in lowered:
        canonical = 'P015'
    if 'bienen' in lowered:
        canonical = 'P046'
    if 'sakr2020' in lowered:
        canonical = 'P061'
    suffix = path.suffix.lower()
    category = {'.txt':'extracted_text', '.csv':'derived_curve_data', '.png':'figure_or_page_image',
                '.log':'process_log', '.jsonl':'translation_intermediate', '.md':'supporting_note',
                '.g3x':'external_project'}.get(suffix, 'auxiliary_file')
    if path.name.lower() == 'idea.docx':
        category = 'research_proposal'
        reason = '主代理已使用 OfficeCLI 确认为研究设想；不是新增论文，不计入论文精读数量。'
    elif suffix == '.g3x':
        reason = '外部项目文件，不是论文；未运行或验证项目内容。'
    elif canonical:
        reason = f'文件名/所在目录映射到 {canonical} 的派生材料；不作为独立来源，未据此重复计数。'
    return {'path': relative, 'format': suffix.lstrip('.'), 'bytes': path.stat().st_size,
            'canonical_id': canonical, 'processing_status': 'auxiliary_not_paper',
            'category': category, 'mapping_basis': 'filename_or_directory' if canonical else 'not_applicable',
            'reason': reason}


def atlas(kind: str, sources: list[dict], summary: dict) -> str:
    label = '写作技巧' if kind == 'writing' else '图表模板'
    lines = [f'# {label}来源索引', '',
             '下列卡片全部位于本 skill 内，可随 skill 独立复制安装。来源 ID 指原始字节文件，译文及重复副本不增加来源数。', '',
             f"本次登记 {summary['paper_report_thesis_source_files']} 份论文/报告/学位来源；"
             f"覆盖记录完整 {summary['reading_complete_sources']} 份，待完成 {len(summary['pending_ids'])} 份，"
             f"覆盖记录不完整 {len(summary['partial_ids'])} 份。P063 含原文、讨论及作者答复，不能把来源文件数当作严格的文章篇数。", '',
             '文本列为 `read_text_pages` 数量，图像文字列为另行视觉阅读的文字页数量，视觉列为实际检查的图表页面数量；三者可能重叠，不可相加当作不同页面。所有定位使用 PDF 页序。', '',
             '| ID / 证据卡 | 题名 | 年份 | 类别 | 文本页 | 图像文字页 | 视觉页 | 状态 |',
             '|---|---|---|---|---:|---:|---:|---|']
    for source in sources:
        if source['id'] in EXCLUDED:
            continue
        lines.append(f"| [{source['id']}](papers/{source['id']}.md) | {cell(source['title'])} | {cell(source.get('year'))} | "
                     f"{cell(source['kind'])} | {len(source.get('read_text_pages', []))} | {len(source.get('read_visual_text_pages', []))} | "
                     f"{len(source.get('visual_pages', []))} | {STATUS_ZH[source['reading_status']]} |")
    lines += ['', '原文中的参数、阈值、拟合关系和规范版本均不能作为通用默认值。图表视觉核对不表示重推所有公式；参考文献表未逐条做外部核实。', '']
    return '\n'.join(lines)


def catalog(sources: list[dict], files: list[dict], summary: dict) -> str:
    lines = ['# 来源与逐文件处理目录', '',
             f"已登记 {summary['pdf_files']} 个 PDF、{summary['unique_pdf_byte_files']} 个独立字节文件；"
             f"其中译文/翻译中间 PDF {summary['translation_derivative_byte_files']} 个，原始来源 {summary['original_source_byte_files']} 个。"
             f"排除非论文发票 {summary['excluded_nonpaper_source_files']} 个，剩余 {summary['paper_report_thesis_source_files']} 份论文/报告/学位来源。", '',
             'P063 是原文与讨论/作者答复的拼接文件，因此这里报告来源文件数，不宣称严格的文章总篇数。', '',
             '## 原始来源及完整笔记', '',
             '| ID | 题名 | 年份 | 类别 | PDF页 | 文本/图像文字/视觉页数 | 状态 |',
             '|---|---|---|---|---:|---|---|']
    for source in sources:
        ident = source['id']
        ref = ident if ident in EXCLUDED else f'[{ident}](papers/{ident}.md)'
        count = f"{len(source.get('read_text_pages', []))}/{len(source.get('read_visual_text_pages', []))}/{len(source.get('visual_pages', []))}"
        lines.append(f"| {ref} | {cell(source['title'])} | {cell(source.get('year'))} | {cell(source['kind'])} | {source['pages']} | {count} | {STATUS_ZH[source['reading_status']]} |")
    lines += ['', '## PDF 文件逐项映射', '',
             '字节重复沿清单中的 `duplicate_of` 追溯，译文再映射到对应原文；译文或重复项只继承原文阅读状态，不声称逐份重新阅读。', '',
             '| 文件键 | 源目录相对路径 | 字节文件 ID | 原文 ID | 处理状态 | 原文阅读状态 |',
             '|---|---|---|---|---|---|']
    for item in files:
        if item['format'] != 'pdf':
            continue
        lines.append(f"| {item['file_key']} | `{cell(item['path'])}` | {item['byte_source_id']} | {item['canonical_id']} | {item['processing_status']} | {STATUS_ZH[item['canonical_reading_status']]} |")
    lines += ['', '## 非 PDF 辅助文件', '',
             '下表逐文件登记；无对应原文 ID 的研究设想、项目文件或跨来源记录明确记为“不适用”。这些文件不增加论文数。', '',
             '| 文件键 | 源目录相对路径 | 类别 | 原文 ID | 状态/处理依据 |',
             '|---|---|---|---|---|']
    for item in files:
        if item['format'] == 'pdf':
            continue
        lines.append(f"| {item['file_key']} | `{cell(item['path'])}` | {item['category']} | {item['canonical_id'] or '不适用'} | {cell(item['reason'])} |")
    lines += ['', '## 未完成或需补充的记录', '']
    attention = [s for s in sources if s['reading_status'] in ['pending', 'read_partial']]
    if not attention:
        lines.append('没有缺失的成对笔记，也没有未说明覆盖的 PDF 页面。此结论只指逐页阅读记录完整，不表示全部图表均已逐图视觉审查。')
    for source in attention:
        lines.append(f"- {source['id']}：{STATUS_ZH[source['reading_status']]}；尚未说明覆盖页 {page_ranges(source.get('unaccounted_pages', []))}；缺少文件 {', '.join(source.get('missing_note_files', [])) or '无'}。")
    lines.append('')
    return '\n'.join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--strict', action='store_true', help='return nonzero for pending notes or unaccounted PDF pages')
    args = parser.parse_args()
    inventory = read_json(ROOT / 'corpus' / 'file_manifest.json')
    byte_rows = {row['id']: row for row in inventory if row.get('id')}
    if len(byte_rows) != sum(bool(row.get('id')) for row in inventory):
        raise ValueError('Duplicate unique-byte IDs in file_manifest.json')
    unknown = set(TRANSLATIONS) - set(byte_rows)
    if unknown or set(TRANSLATIONS.values()) - set(byte_rows):
        raise ValueError(f'Translation mapping does not match file inventory: {sorted(unknown)}')
    source_ids = sorted(set(byte_rows) - set(TRANSLATIONS))
    sources, notes = [], {}
    for ident in source_ids:
        source, note = make_source(byte_rows[ident])
        sources.append(source)
        notes[ident] = note
    by_id = {source['id']: source for source in sources}
    files = []
    for row in inventory:
        byte_id = row.get('id') or row.get('duplicate_of')
        if byte_id not in byte_rows:
            raise ValueError(f"Unknown duplicate target: {row['path']}")
        if row.get('duplicate_of') and row['sha256'] != byte_rows[byte_id]['sha256']:
            raise ValueError(f"Byte duplicate hash mismatch: {row['path']}")
        canonical = TRANSLATIONS.get(byte_id, byte_id)
        reading_status = by_id[canonical]['reading_status']
        status = ('byte_duplicate_mapped' if row.get('duplicate_of') else
                  'translation_derivative_mapped' if byte_id in TRANSLATIONS else
                  'excluded_nonpaper' if canonical in EXCLUDED else 'original_' + reading_status)
        files.append({'path': row['path'], 'format': 'pdf', 'bytes': row['bytes'], 'sha256': row['sha256'],
                      'byte_source_id': byte_id, 'canonical_id': canonical,
                      'processing_status': status, 'canonical_reading_status': reading_status,
                      'relation_chain': [byte_id] if byte_id == canonical else [byte_id, canonical],
                      'byte_duplicate': bool(row.get('duplicate_of')),
                      'translation_derivative': byte_id in TRANSLATIONS,
                      'pages': byte_rows[byte_id].get('pages')})
    if not SOURCE.exists():
        raise FileNotFoundError(f'Local source directory is required for complete auxiliary inventory: {SOURCE}')
    source_pdf_paths = {p.relative_to(SOURCE).as_posix() for p in SOURCE.rglob('*') if p.is_file() and p.suffix.lower() == '.pdf'}
    if source_pdf_paths != {row['path'] for row in inventory}:
        raise ValueError('PDF filenames changed since inventory; refresh and reconcile file_manifest first')
    for path in sorted(SOURCE.rglob('*'), key=lambda p: str(p).lower()):
        if path.is_file() and path.suffix.lower() != '.pdf':
            files.append(auxiliary_record(path, byte_rows))
    for index, item in enumerate(files, 1):
        item['file_key'] = f'F{index:03d}'
    papers = [s for s in sources if s['id'] not in EXCLUDED]
    summary = {
        'pdf_files': len(inventory), 'unique_pdf_byte_files': len(byte_rows),
        'byte_duplicate_pdf_files': sum(bool(r.get('duplicate_of')) for r in inventory),
        'translation_derivative_byte_files': len(TRANSLATIONS),
        'original_source_byte_files': len(sources), 'excluded_nonpaper_source_files': len(EXCLUDED),
        'paper_report_thesis_source_files': len(papers),
        'reading_complete_sources': sum(s['reading_status'] == 'read_complete' for s in papers),
        'pending_ids': [s['id'] for s in papers if s['reading_status'] == 'pending'],
        'partial_ids': [s['id'] for s in papers if s['reading_status'] == 'read_partial'],
        'total_source_pdf_pages': sum(s['pages'] for s in papers),
        'text_pages_recorded': sum(len(s.get('read_text_pages', [])) for s in papers),
        'visual_text_pages_recorded': sum(len(s.get('read_visual_text_pages', [])) for s in papers),
        'visual_pages_recorded': sum(len(s.get('visual_pages', [])) for s in papers),
        'blank_or_separator_pages_recorded': sum(len(s.get('blank_or_separator_pages', [])) for s in papers),
        'auxiliary_files': len(files) - len(inventory), 'all_files': len(files),
        'auxiliary_formats': dict(sorted(Counter(f['format'] for f in files if f['format'] != 'pdf').items())),
    }
    for source in papers:
        ident, note = source['id'], notes[source['id']]
        if note:
            write(ROOT / 'corpus' / 'papers' / f'{ident}.md', note)
        else:
            write(ROOT / 'corpus' / 'papers' / f'{ident}.md', f"# {ident} — 待完成\n\n尚缺完整阅读笔记：{', '.join(source['missing_note_files'])}。\n")
        for kind, skill in SKILLS.items():
            content, routes = card(source, note, kind)
            source['section_routes'] = routes
            write(ROOT / 'skills' / skill / 'references' / 'papers' / f'{ident}.md', content)
        # Every level-two block must be preserved without rewriting in at least one skill.
        if note:
            cards = [(ROOT / 'skills' / skill / 'references' / 'papers' / f'{ident}.md').read_text(encoding='utf-8') for skill in SKILLS.values()]
            for heading, block in sections(note)[1]:
                if not any(block in candidate for candidate in cards):
                    raise AssertionError(f'{ident}: dropped section {heading}')
    manifest = {
        'schema_version': 1, 'scope': 'local_source_files_and_original_reading_notes',
        'page_numbering': 'one_based_pdf_pages', 'summary': summary,
        'translation_to_original': TRANSLATIONS,
        'counting_note': '55份论文/报告/学位原始来源文件；P063包含原文及讨论答复，来源数不等于严格文章篇数。',
        'coverage_note': 'read_complete只表示文本/图像文字/空白分隔页已解释全部PDF页；visual_pages另记实际图表检查，不表示重推全部公式或核实全部参考文献。',
        'sources': sources, 'files': files,
    }
    write(ROOT / 'corpus' / 'reading_manifest.json', json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    write(ROOT / 'corpus' / 'source_catalog.md', catalog(sources, files, summary))
    for kind, skill in SKILLS.items():
        write(ROOT / 'skills' / skill / 'references' / 'source-atlas.md', atlas(kind, sources, summary))
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 1 if args.strict and (summary['pending_ids'] or summary['partial_ids']) else 0


if __name__ == '__main__':
    raise SystemExit(main())
