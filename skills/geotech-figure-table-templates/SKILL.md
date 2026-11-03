---
name: geotech-figure-table-templates
description: "Create source-grounded geotechnical paper figures and tables: load-displacement and validation curves, parameter panels, depth profiles, cyclic histories, interaction envelopes, gradation curves and three-line tables. Use with real data or for clearly labeled reusable templates; preserve units, normalization, loading order and missing data."
---

# 岩土论文函数曲线与表格模板

先选表达问题，再选图型。模板借鉴本地论文的视觉语法，不复制原图或原数据；预设字号、线宽、配色是本仓库的可调实现，不是测得的期刊强制标准。

## 按任务读取

- 选择图型及文献依据：[figure-recipes.md](references/figure-recipes.md)。
- 表格结构、三线表和多级表头：[table-recipes.md](references/table-recipes.md)。
- 数据输入和脚本使用：[data-contract.md](references/data-contract.md)。
- 查找某篇样式：[source-atlas.md](references/source-atlas.md)，然后按需读证据卡。

## 绘图流程

确认数据文件、物理量、单位、测点、基线、归一化式、加载顺序及目标版宽。资料已给出的直接使用。缺少真实数据时可制作标明“演示数据”的模板，不把演示曲线当研究结果。

1. 按问题选择响应、剖面、循环、参数矩阵、包络或验证图。不同土类/加载路径优先分面；同一组跨图保持相同颜色与符号。
2. 实测数据用符号，计算/解析曲线用线，必要时叠加；图例说明来源。误差棒只来自真实重复试验或已定义的不确定度。
3. 保留数据顺序。滞回环和包络不能按x自动排序；缺失点断开；提前停止不外推；不为“平滑”移动峰值或生成未测点。
4. 量纲写在轴或列头；无量纲量注明分母。深度通常向下但按数据约定确认，负高程不能再盲目倒轴。对数轴不得吞掉零/负值。
5. 在最终版宽检查标签、图例、黑白辨识、面板量程和线条清晰度；检查图题所说变量与轴相符。

## 可直接运行的资源

依赖 Python、NumPy、Matplotlib。从 skill 目录运行：

```powershell
python scripts/plot_template.py assets/examples/response.json --out output/response
python scripts/plot_template.py assets/examples/depth-profile.json --out output/depth-profile
python scripts/render_table.py assets/table-templates.json --out output/tables.html
```

绘图输出PNG、SVG和原样输入旁车JSON。其他图型示例见 `assets/examples/`；[gallery.html](assets/gallery.html) 可离线预览。替换示例时更新 `provenance` 并确认 `synthetic` 状态；脚本不做拟合、归一化、插值或统计推断。

可沿用用户指定的 Origin、MATLAB 等后端，转用同一数据契约与视觉参数；不要为了本模板强行替换工作流。

## 表格与 Office

表格模板提供字段与展示结构；HTML是样式预览，JSON是可编辑数据，不冒充原生Word文件。需要 Word/Excel/PowerPoint 时用 OfficeCLI读取、生成与检查；不要用 Python Office 库绕过。CJGE表格使用9pt宋体/TNR、顶底0.75pt、表头0.5pt、无竖线、上置双语表题；用户或目标期刊模板优先。公式编辑仅用 MathType MCP并进行工具和视觉两遍检查。

## 完成检查

核对数据条数、系列/工况对应、坐标方向、单位、归一化基准及端点；检查导出图和表格预览。交付可编辑输入、图文件、来源说明及必要的未确认项。无需把未授权的数据数字化、模型求解或论文改写扩展到当前任务。
