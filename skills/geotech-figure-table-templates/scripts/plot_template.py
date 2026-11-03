"""Render explicit, ordered series. No fitting, normalization, sorting or data invention."""
import argparse
import json
import math
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
import numpy as np

KINDS={'response','parametric','depth-profile','cyclic','interaction','parity','gradation','threshold-history'}
COLORS=['#222222','#0072B2','#D55E00','#009E73','#9467BD','#777777']
MARKERS=['o','s','^','D','v','P']
LINES=['-','--','-.',':']

def numbers(values, label):
    if not isinstance(values,list) or not values:
        raise ValueError(f'{label} must be a nonempty list')
    result=[]
    for v in values:
        if v is None:
            result.append(np.nan)
        elif isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(v):
            result.append(float(v))
        else:
            raise ValueError(f'{label} contains a non-finite or non-numeric value')
    return np.array(result)

def validate(spec):
    if spec.get('schema_version')!=1 or spec.get('kind') not in KINDS:
        raise ValueError('Unsupported schema_version or kind')
    if not isinstance(spec.get('synthetic'),bool) or not str(spec.get('provenance','')).strip():
        raise ValueError('Explicit synthetic boolean and provenance are required')
    panels=spec.get('panels')
    if not isinstance(panels,list) or not panels:
        raise ValueError('At least one panel is required')
    for p in panels:
        if not p.get('xlabel') or not p.get('ylabel') or not p.get('series'):
            raise ValueError('Each panel needs labels and series')
        for s in p['series']:
            if not s.get('label') or s.get('role','series') not in {'observation','model','series'}:
                raise ValueError('Each series needs label and supported role')
            x,y=numbers(s['x'],'x'),numbers(s['y'],'y')
            if len(x)!=len(y) or not np.any(np.isfinite(x)&np.isfinite(y)):
                raise ValueError('Series lengths differ or contain no paired numeric points')
            for key,arr in [('x',x),('y',y)]:
                scale=p.get(key+'scale','linear')
                if scale not in {'linear','log'}:
                    raise ValueError('Only linear and log scales are supported')
                if scale=='log' and np.any(arr[np.isfinite(arr)]<=0):
                    raise ValueError(f'Nonpositive {key} value on log axis; no values were removed')
            if 'yerr' in s:
                err=numbers(s['yerr'],'yerr')
                if len(err)!=len(y) or np.any(err[np.isfinite(err)]<0):
                    raise ValueError('yerr must match data and be nonnegative')
        for line in p.get('reference_lines',[]):
            if line.get('axis') not in {'x','y'} or not isinstance(line.get('value'),(int,float)) or not math.isfinite(line['value']):
                raise ValueError('Invalid reference line')
    return spec

def render(spec, output):
    validate(spec)
    available={f.name for f in font_manager.fontManager.ttflist}
    fonts=[f for f in ['Times New Roman','SimSun','Noto Serif CJK SC','DejaVu Serif'] if f in available]
    plt.rcParams.update({'font.family':fonts,'font.size':spec.get('font_size',9),
                         'axes.linewidth':0.7,'lines.linewidth':1.1,
                         'xtick.direction':'in','ytick.direction':'in',
                         'svg.fonttype':'none','axes.unicode_minus':False})
    n=len(spec['panels']);cols=min(int(spec.get('columns',2 if n>1 else 1)),n)
    if cols<1: raise ValueError('columns must be positive')
    rows=math.ceil(n/cols)
    size=spec.get('size_mm',[170 if n>1 else 85,82*rows])
    if len(size)!=2 or min(size)<=0: raise ValueError('size_mm requires positive width and height')
    fig,axes=plt.subplots(rows,cols,figsize=(size[0]/25.4,size[1]/25.4),squeeze=False,layout='constrained')
    for idx,(ax,p) in enumerate(zip(axes.flat,spec['panels'])):
        for i,s in enumerate(p['series']):
            role=s.get('role','series');color=s.get('color',COLORS[i%len(COLORS)] if spec.get('style','mono')=='color' else '#222222')
            line=s.get('linestyle','None' if role=='observation' else LINES[i%len(LINES)])
            marker=s.get('marker',MARKERS[i%len(MARKERS)] if role!='model' else 'None')
            kw=dict(label=s['label'],color=color,linestyle=line,marker=marker,
                    markersize=4,markerfacecolor='white',markeredgewidth=0.7)
            x,y=numbers(s['x'],'x'),numbers(s['y'],'y')
            if 'yerr' in s:
                ax.errorbar(x,y,yerr=numbers(s['yerr'],'yerr'),capsize=2,**kw)
            else:
                ax.plot(x,y,markevery=s.get('markevery',1),**kw)
        for ri,ref in enumerate(p.get('reference_lines',[])):
            method=ax.axvline if ref['axis']=='x' else ax.axhline
            label=f'{ref["label"]} = {ref["value"]:g}' if ref.get('label') else '_nolegend_'
            method(ref['value'],ls=ref.get('linestyle',LINES[(ri+1)%len(LINES)]),lw=.8,color='#777777',label=label)
        ax.set(xlabel=p['xlabel'],ylabel=p['ylabel'],xscale=p.get('xscale','linear'),yscale=p.get('yscale','linear'))
        if p.get('xlim') is not None: ax.set_xlim(p['xlim'])
        if p.get('ylim') is not None: ax.set_ylim(p['ylim'])
        if p.get('invert_y'): ax.invert_yaxis()
        if p.get('x_on_top'):
            ax.xaxis.tick_top();ax.xaxis.set_label_position('top')
        if p.get('identity_line'):
            lo=min(ax.get_xlim()[0],ax.get_ylim()[0]);hi=max(ax.get_xlim()[1],ax.get_ylim()[1])
            ax.plot([lo,hi],[lo,hi],ls='--',lw=.8,color='#777777',label='1:1')
        if p.get('equal_aspect'): ax.set_aspect('equal',adjustable='box')
        if p.get('grid'): ax.grid(color='#dddddd',lw=.4)
        if n>1 or p.get('title'):
            ax.set_title((f'({chr(97+idx)}) ' if n>1 else '')+p.get('title',''),loc='left',fontsize=spec.get('font_size',9))
        if p.get('legend',True): ax.legend(frameon=False,fontsize=spec.get('font_size',9)-1,loc=p.get('legend_loc','best'))
    for ax in list(axes.flat)[n:]: ax.remove()
    if spec['synthetic']: fig.suptitle('SYNTHETIC DEMO - NOT RESEARCH DATA',fontsize=8,color='#a34b22')
    output=Path(output);output.parent.mkdir(parents=True,exist_ok=True)
    for ext in ['png','svg']: fig.savefig(output.with_suffix('.'+ext),dpi=300,facecolor='white')
    plt.close(fig)
    output.with_suffix('.json').write_text(json.dumps(spec,ensure_ascii=False,indent=2),encoding='utf-8')
    return {'output':str(output),'panels':n,'fonts':fonts,'synthetic':spec['synthetic']}

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input',type=Path);parser.add_argument('--out',required=True,type=Path)
    args=parser.parse_args()
    try:
        print(json.dumps(render(json.loads(args.input.read_text(encoding='utf-8')),args.out),ensure_ascii=False))
    except ValueError as exc:
        parser.exit(2,f'Input error: {exc}\n')
