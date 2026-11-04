# Geotechnical Academic Paper Writing Skills

岩土工程学术论文撰写技能仓库。基于 `D:/Pile/literature` 的本地文献，包含两个可独立使用的 Codex skill。内容以中文说明为主，附英文论文句段和图轴示例。

## 两个 skill

| Skill | 作用 | 入口 |
|---|---|---|
| `geotech-paper-writing` | 引言、方法、验证、机理讨论、摘要与结论；把论断限定在已有证据内 | [SKILL.md](skills/geotech-paper-writing/SKILL.md) |
| `geotech-figure-table-templates` | 函数曲线、多面板、深度剖面、循环响应、包络及论文表格 | [SKILL.md](skills/geotech-figure-table-templates/SKILL.md) |

先看 [图表模板预览](skills/geotech-figure-table-templates/assets/gallery.html) 或 [八类表格预览](skills/geotech-figure-table-templates/assets/table-preview.html)。预览HTML可离线打开；曲线均为明确标注的演示数据。

## 本地文献覆盖

截至 2026-11-04，本库登记112个PDF：按字节哈希为87个不同文件；将26份译本/翻译中间件及2份同内容版本对应到原文，得到59份原始来源，其中1份非学术文件排除，58份学术来源有逐篇阅读记录。来源包含期刊论文、接收稿、学位论文及技术报告；P063还含原文后的讨论/答复，因此来源文件数不等于严格的期刊文章篇数。

本轮按2026-11-03本地创建日期核对7个PDF：2个已收录，5个新字节文件对应3篇新来源；新增写作方法、2个组合图样和2类表格。范围及去重证据见 [本轮更新记录](corpus/updates/2026-11-04.md)。今天目录中新出现但尚未收录的来源明确列在阅读清单，不混入本轮覆盖统计。

- [文献与文件对应清单](corpus/source_catalog.md)：每个PDF的归属、重复/译本处理与阅读记录。
- [阅读覆盖与方法说明](corpus/README.md)：全文文字、视觉核对、扫描/OCR及引用核验范围。
- [完整逐篇笔记](corpus/papers)：结构、写作方法、图/表观察、适用边界和原文核验线索。
- [机器可读清单](corpus/reading_manifest.json)：页码、图号、表号和覆盖状态。

主要共性已提炼到两个skill的按需参考文件。每个skill另带自己的逐篇证据卡，不依赖仓库外路径。图表卡和写作卡由同一完整笔记生成，共同的来源/限制段有意保留，保证单独分发时仍能追溯。

## 使用示例

在当前聊天明确指出本地 `SKILL.md` 路径即可要求读取并使用；全局发现需要另行安装。示例请求：

> 使用 geotech-paper-writing，根据已有试验与计算资料修改结果讨论，保留原有数值和适用范围。

> 使用 geotech-figure-table-templates，为我的真实荷载—位移数据生成试验/计算对比图，并列出绘图基准。

从图表skill目录运行（需要Python、NumPy、Matplotlib）：

```powershell
python scripts/plot_template.py assets/examples/response.json --out output/response
python scripts/plot_template.py assets/examples/depth-profile.json --out output/depth-profile
python scripts/render_table.py assets/table-templates.json --out output/tables.html
```

提供8种基础图型、10个可编辑JSON/PNG/SVG图样，以及8种表格结构。新增模式矩阵和理论/离散样本包络对照；分组表头按条件组织成对方法列。绘图脚本保留输入顺序、缺测断点和显式坐标；不做自动拟合、平滑、归一化或结果外推。替换数据时更新 `provenance` 与 `synthetic` 状态。

## 文件与工具约定

Office文件使用OfficeCLI；Word/PowerPoint公式编辑使用MathType MCP并做工具验证及视觉检查。CJGE格式依用户项目要求应用，不能覆盖用户明确指定的目标期刊或已有模板。此仓库不提供物理参数默认值，也不执行有限元计算。

仓库保存原创笔记、模板和脚本。原始PDF、全文提取和原文页面截图未纳入版本库；本地审阅中间件位于被忽略的 `.work/`。已有论文、项目AGENTS及全局配置未修改。

## 维护

`tools/inventory_corpus.py` 增量清点同级 `literature` 并提取本地审阅文本，保留已有ID及记录，可用 `--added-date YYYY-MM-DD` 限定新文件；`tools/render_review.py`用于审阅原文页；`tools/package_evidence.py`汇编已完成人工阅读的笔记；`tools/build_examples.py`重建演示图。自动提取不等于阅读，新增文献须补独立笔记及实际视觉记录后才能标为完成。

GitHub仓库：[xyj0727/geotechnical-academic-paper-writing-skills](https://github.com/xyj0727/geotechnical-academic-paper-writing-skills)，创建时设为私有。源码 checkout 与全局安装分开管理。仓库未提供 plugin 安装方式，按 Codex 兼容的 npx 流程安装两个 skill：

```powershell
npx --yes skills add https://github.com/xyj0727/geotechnical-academic-paper-writing-skills -g -a codex -y --copy
```

私有仓库需已有 GitHub 访问权限。npx 安装不会自动更新，后续使用 `npx skills update -g`；安装/更新后重启 Codex 加载。不要手动复制到全局目录或自行包装本地插件源绕过安装流程。

验证记录见 [VALIDATION.md](VALIDATION.md)。
