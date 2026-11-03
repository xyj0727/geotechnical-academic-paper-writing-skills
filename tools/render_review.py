"""Render selected source pages for visual review; originals never enter the repository."""
from pathlib import Path
import argparse, json
import pymupdf as fitz
from PIL import Image, ImageDraw

root = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('id')
parser.add_argument('--pages', help='1-based comma-separated pages or ranges; default all')
parser.add_argument('--width', type=int, default=1000)
parser.add_argument('--columns', type=int, default=3)
parser.add_argument('--sheet-size', type=int, default=12)
args = parser.parse_args()
manifest = json.loads((root/'corpus/file_manifest.json').read_text(encoding='utf-8'))
rec = next(r for r in manifest if r.get('id')==args.id)
doc = fitz.open(root.parent/'literature'/rec['path'])
pages = []
if args.pages:
    for term in args.pages.split(','):
        ends = list(map(int,term.split('-')))
        pages.extend(range(ends[0],ends[-1]+1))
else:
    pages = list(range(1,len(doc)+1))
out = root/'.work'/'renders'/args.id
out.mkdir(parents=True,exist_ok=True)
items=[]
for n in pages:
    page=doc[n-1]
    pix=page.get_pixmap(matrix=fitz.Matrix(args.width/page.rect.width,args.width/page.rect.width),alpha=False)
    p=out/f'page-{n:03d}.png'
    pix.save(p)
    items.append((n,p))
for start in range(0,len(items),args.sheet_size):
    batch=items[start:start+args.sheet_size]
    thumb_w=min(600,args.width)
    thumb_h=int(thumb_w*1.5)
    sheet=Image.new('RGB',(args.columns*thumb_w,((len(batch)+args.columns-1)//args.columns)*(thumb_h+30)),'#d8d8d8')
    draw=ImageDraw.Draw(sheet)
    for k,(n,p) in enumerate(batch):
        im=Image.open(p); im.thumbnail((thumb_w,thumb_h))
        x,y=(k%args.columns)*thumb_w,(k//args.columns)*(thumb_h+30)
        sheet.paste(im,(x,y+30));draw.text((x+8,y+8),f'{args.id} PDF page {n}',fill='black')
    sp=out/f'sheet-{start//args.sheet_size+1:02d}.jpg'
    sheet.save(sp,quality=88)
    print(sp)
