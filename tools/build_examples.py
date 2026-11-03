"""Build explicitly synthetic examples, previews and an offline template gallery."""
from pathlib import Path
import json,math,sys
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
SKILL=ROOT/'skills'/'geotech-figure-table-templates'
sys.path.insert(0,str(SKILL/'scripts'))
from plot_template import render
from render_table import render as render_table
A=SKILL/'assets';EX=A/'examples';PRE=A/'previews'
EX.mkdir(parents=True,exist_ok=True);PRE.mkdir(exist_ok=True)

def series(label,x,y,role='series',**kw):
    return dict(label=label,x=np.asarray(x).tolist(),y=np.asarray(y).tolist(),role=role,**kw)
def panel(xlabel,ylabel,series,**kw): return dict(xlabel=xlabel,ylabel=ylabel,series=series,**kw)
def spec(kind,panels,size=(170,88),**kw):
    return dict(schema_version=1,kind=kind,synthetic=True,provenance='Analytic synthetic data generated only to demonstrate layout; not digitized, measured or computed research results.',style='mono',size_mm=list(size),panels=panels,**kw)

x=np.linspace(0,20,41); y=80*x/(x+8)
examples={}
examples['response']=spec('response',[
    panel('Displacement (mm)','Load (kN)',[series('Illustrative model',x,y,'model'),series('Illustrative observations',x[::5],y[::5]*np.array([1,1.03,.97,1.02,.99,1.03,.98,1.01,1]),'observation')],title='Response comparison'),
    panel('Displacement (mm)','Load (kN)',[series('Case A',x,y),series('Case B',x,1.3*y)],title='Same-displacement comparison',legend_loc='upper left',reference_lines=[dict(axis='x',value=10,label='Evaluation (mm)')])])
examples['parametric']=spec('parametric',[
    panel('Normalized displacement, y/D','Response ratio, H/Href',
          [series(f'Group {k+1}',x/100,(1+.25*k)*(j+1)*y/80) for k in range(3)],
          title=f'Fixed condition {j+1}',xlim=[0,.2],ylim=[0,4.5],legend=j==0)
    for j in range(4)],size=(170,135),columns=2)
z=np.linspace(0,1,21)
examples['depth-profile']=spec('depth-profile',[
    panel('Displacement, y/D','Depth, z/L',[series('Case A',.08*(1-z)*np.cos(2*z),z),series('Case B',.06*(1-z)*np.cos(2*z),z)],title='Displacement',invert_y=True,x_on_top=True,ylim=[0,1],reference_lines=[dict(axis='y',value=.4,label='Layer boundary')]),
    panel('Moment, M/Mref','Depth, z/L',[series('Case A',-np.sin(np.pi*z)*(1-z/2),z),series('Case B',-.8*np.sin(np.pi*z)*(1-z/2),z)],title='Moment',invert_y=True,x_on_top=True,ylim=[0,1]),
    panel('Soil reaction, p/pref','Depth, z/L',[series('Case A',np.cos(np.pi*z)*(.8+.2*z),z),series('Case B',.7*np.cos(np.pi*z),z)],title='Soil reaction',invert_y=True,x_on_top=True,ylim=[0,1])],size=(170,110),columns=3)
t=np.linspace(0,12*2*np.pi,650);N=np.arange(1,51)
examples['cyclic']=spec('cyclic',[
    panel('Displacement (mm)','Load (kN)',[series('Ordered history',.04*t+2*(1-np.cos(t)),12*(1-np.cos(t-.25)),'model')],title='Path retained'),
    panel('Cycle number, N','Normalized displacement, yN/y1',[series('Series A',N,1+.35*np.log(N),'model'),series('Series B',N,1+.5*np.log(N),'model')],title='Accumulation',xscale='log')])
theta=np.linspace(0,2*np.pi,101)
examples['interaction']=spec('interaction',[
    panel('Normalized horizontal load, H/Href','Normalized moment, M/Mref',[series('Condition A',np.cos(theta),.8*np.sin(theta),'model'),series('Condition B',.8*np.cos(theta),.6*np.sin(theta),'model')],equal_aspect=True,xlim=[-1.2,1.2],ylim=[-1,1],reference_lines=[dict(axis='x',value=0),dict(axis='y',value=0)])],size=(95,90))
obs=np.array([20,35,50,65,80,95]);pred=obs*np.array([1.1,.93,1.07,.96,1.02,.95])
examples['parity']=spec('parity',[
    panel('Observed response (kN)','Predicted response (kN)',[series('Independent pairs',obs,pred,'observation')],identity_line=True,equal_aspect=True,xlim=[0,110],ylim=[0,110])],size=(95,90))
d=np.logspace(-2,1,40)
examples['gradation']=spec('gradation',[
    panel('Particle diameter (mm)','Percent finer (%)',[series('Soil A',d,100/(1+(.3/d)**2),'model'),series('Soil B',d,100/(1+(.6/d)**2),'model')],xscale='log',ylim=[0,100],grid=True)],size=(110,80))
steps=np.linspace(0,20,201);saw=35+10*np.abs(np.sin(np.pi*steps))
examples['threshold-history']=spec('threshold-history',[
    panel('Event count','Measured force (N)',[series('Illustrative history',steps,saw,'model')],reference_lines=[dict(axis='y',value=48,label='Reference level'),dict(axis='y',value=42,label='Action threshold')],ylim=[30,52])],size=(140,80))

tables={'schema_version':1,'template':True,'tables':[
 dict(id='material-parameters',caption='表1 材料参数及来源 / Table 1 Material parameters and sources',columns=['参数','符号','单位','材料A','材料B','来源/获取方法'],rows=[['弹性参数','E','MPa','待填','待填','试验/标定/引用，待说明'],['强度参数','按本构定义','kPa或°','待填','待填','不能从模板直接取值']],note='占位提示不是取值；有效应力/总应力、排水条件和本构需在表注或正文定义。'),
 dict(id='case-matrix',caption='表2 工况矩阵 / Table 2 Test and analysis matrix',columns=['工况ID','固定条件','变化参数','加载路径','研究目的'],rows=[['BASE','待填','基线','待填','对照'],['CASE-A','与基线一致项，待填','待填','待填','隔离单一因素']],note='编码是索引，不能替代可读参数。计算/试验的实际完成状态另列。'),
 dict(id='validation',caption='表3 标定与验证数据 / Table 3 Calibration and validation data',columns=['来源/数据集','尺度及条件','用途','比较量','误差定义及值','限制'],rows=[['待填','待填','标定','待填','未计算','不称独立验证'],['待填','待填','独立验证','待填','未计算','数据是否独立，待核']],note='没有独立数据时保留缺口，不能复制标定结果充当验证。'),
 dict(id='response-summary',caption='表4 响应及比较基准 / Table 4 Responses at defined evaluation points',columns=['工况','评价点/测点','绝对响应/单位','相对基线增幅/%','停止或缺测状态'],rows=[['BASE','待填','未提供','基线','待填'],['CASE-A','与基线同定义','未提供','未计算','待填']],note='未提供、未计算、0、不适用含义不同；增幅必须说明分母。'),
 dict(id='literature-matrix',caption='表5 文献对比 / Table 5 Literature comparison',columns=['来源','方法/条件','研究变量','原文发现','评述/局限'],rows=[['作者、年份，待核','土类、尺度、加载','待填','待据原文概括','与当前问题的关系'],['另一来源，待核','待填','待填','待据原文概括','区别原文结论与作者推断']],note='对比条件不一致时，不按单一增幅排名；历史空白不自动是当前空白。'),
 dict(id='stage-sequence',caption='表6 阶段与输出基准 / Table 6 Stages and output reference states',columns=['阶段','事件','荷载/构件状态','重置或增量基准','输出'],rows=[['INITIAL','初始状态','待填','待填','待填'],['STAGE-1','施工/加载事件','待填','继承/重置，待核','待填']],note='阶段号是离散事件；说明总量还是相对指定阶段的增量。')
]}
(A/'table-templates.json').write_text(json.dumps(tables,ensure_ascii=False,indent=2),encoding='utf-8')
(A/'table-preview.html').write_text(render_table(tables),encoding='utf-8')
names={'response':'响应与验证','parametric':'参数分面','depth-profile':'沿深度剖面','cyclic':'循环路径与累积','interaction':'相互作用包络','parity':'预测与观测','gradation':'颗粒级配','threshold-history':'过程与阈值'}
cards=[]
for name,s in examples.items():
    for p in s['panels']:
        if name=='depth-profile':
            p['ylim']=[-.025,1.025]
        for curve in p['series']:
            if curve.get('role')=='series' and len(curve['x'])>20:
                curve['markevery']=4
    (EX/f'{name}.json').write_text(json.dumps(s,ensure_ascii=False,indent=2),encoding='utf-8')
    print(render(s,PRE/name))
    cards.append(f'<article><h2>{names[name]}</h2><a href="previews/{name}.svg"><img src="previews/{name}.png" alt="{names[name]}：演示数据"></a><p><a href="examples/{name}.json">可编辑输入 JSON</a> · <a href="previews/{name}.svg">矢量 SVG</a></p></article>')
page='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>岩土论文图表模板</title><style>body{margin:0;background:#f4f3ef;color:#172c39;font:16px/1.7 system-ui,sans-serif}header,main{max-width:1180px;margin:auto;padding:30px}h1{font-size:34px;margin:0}header p{max-width:850px}a{color:#176d8b}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(400px,1fr));gap:22px;padding-top:0}article{background:white;padding:22px;border:1px solid #ddd}h2{font-size:20px;margin:0 0 14px}img{width:100%;height:auto}.tag{display:inline-block;padding:4px 12px;border:1px solid #c89a61;color:#7c4b13;font-size:13px;margin-bottom:18px}@media(max-width:500px){main{display:block}article{margin-bottom:20px}header,main{padding:20px}}</style><header><span class="tag">TEMPLATE LIBRARY · 演示数据</span><h1>岩土论文图表模板</h1><p>借鉴文献中的比较方式、坐标组织与图例编码。这里的曲线均为合成演示数据，不是论文原始数据或有限元结果。替换数据前，请阅读数据契约并确认单位、测点和归一化基准。</p><p><a href="table-preview.html">查看六类表格模板</a> · <a href="../references/figure-recipes.md">图型与文献依据</a></p></header><main>'''+''.join(cards)+'</main></html>'
(A/'gallery.html').write_text(page,encoding='utf-8')
