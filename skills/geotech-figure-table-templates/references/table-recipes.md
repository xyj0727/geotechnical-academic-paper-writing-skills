# 表格结构与样式

本库常见三线或少量水平分组线，但并非所有来源都没有竖线：P077/P082的部分Géotechnique表有竖向列线，P070表1为完整网格。选择目标期刊风格，不将样本文献的排版说成通用标准。

## 八种可复用结构

| 结构 | 建议字段 | 来源及用途 |
|---|---|---|
| material-parameters | 参数、符号、单位、各材料值、来源/获取方法 | P010 Tables1–2；P013 Table1；P015 Tables1–2 |
| case-matrix | 工况ID、固定条件、变化参数、加载/阶段、目的 | P013 Table2；P051；P014 Table5 |
| validation | 数据集、尺度/土类、标定或验证、比较量、范围/误差、限制 | P075 Tables4–5；P077 |
| response-summary | 工况、评价点、绝对响应、相对基线、停止/缺测状态 | P015 Tables4–5；P004 |
| literature-matrix | 来源、方法/条件、研究变量、发现、评述/缺口 | P009 Tables2–3 |
| stage-sequence | 阶段号、事件、已激活构件/荷载、重置量/输出基准 | P012 Table2；P069 |
| grouped-method-comparison | 行条件、列条件分组、组内参考/预测方法成对值 | P086 Table1 p8；说明归一化与方法身份 |
| paired-response | 基线/修改方案/相对变化三行、对应响应或测点为列 | P085 Tables1–2 p5；绝对值与变化方向同读 |

字段按当前任务删改。非参数表不必强塞单位列；字符较多的解释列左对齐，数值列按精度一致对齐。

新增两类表格的原文观察与实现边界见 [mode-envelope-styles.md](mode-envelope-styles.md)。分组线只跨所属子列；稀疏工况的变量水平列表不能误读为已完成全部交叉组合（P083 Table2 p2）。

## 三线表实现

顶线/底线0.75pt、表头下线0.5pt；不用背景色、竖线和每行横线。多级表头可以有短分组线，但不要穿过无关列。表题在上、注释在下；符号、单位、统计口径、基线与缺测原因放在表头/脚注。

中文CJGE使用宋体9pt、英文数字Times New Roman9pt，表头不加粗，14pt行距；单栏宽不超过8.5cm、通栏按版心选择至17cm。重复表头，行不拆分，但允许表格自然跨页。不要用空白段或整体keep-with-next制造大空白。

## 数字和不适用项

精度应匹配测量或计算可信度，不能为整齐增加虚假有效位。0、未测、未报告、不适用分开；只有在表注定义后使用“—”。比例给出分母，保留负增益；同一评价点的绝对量与增幅可相邻排列。旋转宽表是原文选项（P013 Table3），新稿优先考虑拆分分组或通栏，避免为了容纳全部字段缩至不可读。

## OfficeCLI落地

需要原生Office时先运行当前安装版本的帮助，核对表格、行和单元格属性：

```powershell
officecli help docx table
officecli help docx row
officecli help docx cell
officecli help batch
```

按JSON模板的字段和数据创建原生表格，用OfficeCLI回读数据与边框，再按其默认流程验证/预览。已有稿件不要全局覆盖字体和排版。若含真正数学公式，用MathType MCP写入并完成两遍检查；不能把公式图片当可编辑MathType对象。

本仓库的 `render_table.py` 只做HTML样式预览，不生成或读取Office文件。
