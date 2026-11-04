---
name: geotech-paper-writing
description: "Draft and revise geotechnical research papers using source-grounded argument patterns from a local literature corpus. Use for introductions, methods, validation, mechanism discussion, abstracts and conclusions in Chinese or English; preserve quantitative conditions and distinguish experiments, numerical predictions and design implications."
---

# 岩土工程论文写作技巧

把研究证据组织成可核验的论证。这里总结的是文献的表达方法，不是材料参数、设计标准或可直接复制的论文结论。

## 工作入口

先明确用户正在写哪一部分、研究对象、土类/排水条件、加载路径、证据来源和目标语言。已有材料能回答的事项直接读取，不要求重复填表。只修改用户要求的范围。

- 组织全文或引言：读 [argument-patterns.md](references/argument-patterns.md)。
- 写方法、验证或机理：读 [evidence-and-comparisons.md](references/evidence-and-comparisons.md)。
- 写运动模式、组合荷载包络或改进方案对照：读 [mechanism-and-envelope-writing.md](references/mechanism-and-envelope-writing.md)。
- 改具体句段：读 [sentence-patterns.md](references/sentence-patterns.md)。
- 寻找相似论文：在 [source-atlas.md](references/source-atlas.md) 按研究类型选文，再读相应证据卡。
- 从零搭框架：使用 [manuscript-outline.md](assets/manuscript-outline.md)，按现有证据删改，不能把空位填成虚构结果。

不要一次加载所有文献卡。卡中的 P 编号只用于内部追溯；最终论文参考文献必须采用准确作者、题名、年份等书目信息，不能以 P 编号代替。

## 核心方法

1. **先定论证单位。** 每个结果段让读者知道比较对象、固定条件、变化指标、证据位置。若机理尚未直接测得，使用“与……一致”“可能与……有关”，不要把推测写成已证实因果。
2. **把比较基准写出来。** 同荷载比较变形、同变形比较抗力、同使用性能比较用材，分别回答不同问题。土类、加载高度、排水状态、尺度、定义或归一化分母不同的结果不可直接排名。
3. **让验证限定结论。** 标定用哪些数据、验证用哪些独立数据、比较了什么响应及其范围，要分开交代。整体荷载—位移吻合不能单独证明局部接触峰值、循环寿命或新工况。
4. **按证据推进机理。** 从总体曲线到剖面/构件分担，再到局部场或实测形态。只有总体曲线时，不虚构塑性区、土塞或被动楔体证据。
5. **结论回到研究边界。** 保留土类、几何域、加载路径、评价点及停止原因。“所考察组合中较优”不可改成普遍最优；计算末点不可自动称极限承载力。

## 改稿时的交付

交付用户需要的正文或修订稿，并简要标注影响结论的缺证据项。不要把每个普通写作请求都变成全面审计。参数或数据缺失时，可以完成有依据的段落，并准确指出缺口；不能通过润色补造事实。

中英文互改保留限定词、数值范围、正负号、数量级和来源。不要复制原文长句；例句为原创结构示例。历史综述的“研究空白”需要当次文献检索才能作为当前空白使用。

## 文件工具衔接

若任务涉及 Word/Excel/PowerPoint，遵守当前项目的 OfficeCLI 操作约定；公式编辑交 MathType MCP，须通过工具验证及逐式视觉检查。当前项目指定 CJGE 时按其格式规则执行；目标期刊或用户提供模板优先。纯文本写作无需启动 Office 工具，也不强制改排版。

作图与表格制作可配合 `$geotech-figure-table-templates`，但本 skill 可独立完成文字工作。
