# 输入契约

## 曲线 JSON（schema_version=1）

```json
{
  "schema_version": 1,
  "kind": "response",
  "synthetic": false,
  "provenance": "实际数据文件、工况和列的说明",
  "style": "mono",
  "size_mm": [85, 75],
  "panels": [{
    "xlabel": "Displacement (mm)",
    "ylabel": "Load (kN)",
    "series": [{
      "label": "Test A",
      "role": "observation",
      "x": [0, 1, 2],
      "y": [0, 3, 5]
    }]
  }]
}
```

上述数值仅说明JSON语法，不能拿来充当实验。

- `kind`：response、parametric、depth-profile、cyclic、interaction、parity、gradation、threshold-history；图型语义由选定的真实数据保证。
- `synthetic`：演示数据必须true，图上会显示SYNTHETIC DEMO。`provenance`必填；真实数据应写明文件/工况/处理方式。
- `size_mm`：完整图版宽高；`columns`控制面板列数；`font_size`默认9。
- `role`：observation（仅点）、model（线）、series（线+点）。`color`、`marker`、`linestyle`、`markevery`可覆盖；同组跨面板需指定相同样式。
- `x/y`：同长数字数组；允许成对或单侧null表示缺测，曲线会断开。拒绝NaN/Inf字符串和非有限数值。不会自动排序。
- `yerr`：可选同长非负误差；没有重复试验/误差定义则不填。
- 面板可设 `xscale/yscale` 为linear或log；对数轴非正值会明确报错，要求回到数据/定义处理。
- `xlim/ylim`显式两数；`invert_y`、`x_on_top`、`equal_aspect`可选。不自动判断深度符号。标记正好落在显式边界时按Matplotlib规则裁切；若需要完整端点标记，应在不误导量程的前提下留少量坐标余量，脚本不擅自改用户范围。
- `reference_lines`：`axis`为x/y、`value`、`label`，只绘制有依据的参考线。
- `identity_line`：明确设true绘制y=x；不要在单位不同的坐标上使用。
- `grid`可选false/true；`title`是简短面板题；`legend`可设置false隐藏重复图例。

脚本保留数据顺序和缺测断点，不做拟合/插值/积分/归一化/峰值识别。所有此类处理须先在当前任务中明确定义，保存原始量及处理方法。

## 表格 JSON

顶层 `tables`数组，每表包含 `id`、`caption`、`columns`、`rows`和`note`。每行列数应一致。空结构预览设置 `template: true`；填入数据后设false或省略，页头不再称空模板。`rows`中的“待填”或“未提供”是空模板提示；真实交付时由用户数据替换，未提供不能改0。

预览HTML支持中文、三线表、长文本换行；输出不含外部资源，可离线打开。此预览不构成Word分页验证。
