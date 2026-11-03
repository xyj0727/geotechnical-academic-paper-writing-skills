"""Render editable JSON table structures to offline HTML; does not operate Office files."""
import argparse,json,html
from pathlib import Path

def render(spec):
    sections=[]
    template=spec.get('template',False)
    intro='空模板展示：待填项不是研究数据。HTML用于结构和样式预览，Word分页须另用OfficeCLI检查。' if template else '表格预览：数据按输入JSON展示。来源和解释以各表注释为准；此预览不验证数据真实性或Word分页。'
    for t in spec['tables']:
        cols=t['columns']
        if not cols or any(len(row)!=len(cols) for row in t['rows']):
            raise ValueError(f'Column count mismatch in {t["id"]}')
        esc=lambda v:html.escape(str(v))
        head=''.join('<th>'+esc(c)+'</th>' for c in cols)
        body=''.join('<tr>'+''.join('<td>'+esc(v)+'</td>' for v in row)+'</tr>' for row in t['rows'])
        sections.append(f'<section id="{esc(t["id"])}"><h2>{esc(t["caption"])}</h2><div class="scroll"><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div><p class="note">{esc(t.get("note",""))}</p></section>')
    return '''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Geotechnical table templates</title><style>
body{max-width:1100px;margin:40px auto;padding:0 24px;background:#f4f3ef;color:#1f2933;font:16px/1.7 system-ui,sans-serif}h1{font-size:28px}h2{font:18px SimHei,serif;text-align:center;font-weight:normal}section{background:white;padding:24px;margin:26px 0;border:1px solid #e3e0d8}.scroll{overflow-x:auto}table{border-collapse:collapse;width:100%;border-top:.75pt solid black;border-bottom:.75pt solid black;font:12px/1.55 "Times New Roman",SimSun,serif}th{border-bottom:.5pt solid black;font-weight:normal}td,th{padding:8px 10px;text-align:center;vertical-align:top}td:first-child{text-align:left}.note{font-size:13px;color:#555}@media print{body{background:white}section{border:0}thead{display:table-header-group}tr{break-inside:avoid}}</style><h1>岩土论文表格预览</h1><p>'''+intro+'</p>'+''.join(sections)+'</html>'

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('input',type=Path);p.add_argument('--out',required=True,type=Path);a=p.parse_args()
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(render(json.loads(a.input.read_text(encoding='utf-8'))),encoding='utf-8');print(a.out)
