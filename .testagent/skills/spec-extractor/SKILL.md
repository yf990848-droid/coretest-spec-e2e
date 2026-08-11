---
name: spec-extractor
description: 将一个或多个需求 Word 文档作为统一输入集合，抽取并合并为一份系统需求.md和一份功能设计.md，保留文档来源并记录字段冲突；供 coretest-explore 的 TR 级多需求流程使用，兼容单个 docx_path。
license: MIT
compatibility: 依赖 pandoc 命令行工具
metadata:
  author: corespec
  version: "0.2"
  generatedBy: manual
---

# Spec Extractor

## 输入

正式模式：

```yaml
docx_paths:
  - /absolute/path/A.docx
  - /absolute/path/B.docx
document_manifest: /absolute/path/design_doc/document_manifest.json
output_dir: /absolute/path/TR_<tr_id>
source_ids:
  - IR_A
  - SR_B
author: c00959281(via spec-extractor)
```

兼容模式允许传入单个 `docx_path` 和 `source_id`，内部必须规范化为单元素数组后执行同一流程。

约束：

- `docx_paths` 至少一项，按给定顺序处理；
- 每个文件必须存在、非空且后缀为 `.docx`；
- 正式模式下每个路径必须能在 `document_manifest` 中定位；
- 只读写 `output_dir` 及其 `design_doc/` 中的输入文件。

## 工作流

使用 `todowrite` 跟踪 6 步。

### 1. 校验输入

检查文件集合、清单、输出目录和 pandoc。路径重复时按解析后的绝对路径去重，保留首次顺序。

### 2. 独立转换

每份 Word 使用独立临时文件，禁止共用 `.tmp_docx.md`：

```text
<output_dir>/.spec-extractor-tmp/<顺序号>_<安全文件名>.md
```

逐一执行：

```bash
pandoc "<docx_path>" -o "<独立临时文件>" -t gfm
```

任一转换失败立即停止，并保留错误信息，不得基于部分文档产出最终文件。

### 3. 通读全部文档

先读完全部临时 Markdown，再组织输出。每段事实保留来源文档；相同内容合并时保留完整来源集合。

冲突处理：

- 编号、名称、数值指标、默认值或约束存在差异时不得猜测；
- 在对应字段正文中列出差异及来源；
- 优先级仅在原文明确版本或清单明确顺序时适用，并说明采用依据；
- 无法确定时标注“存在来源冲突，待确认”。

### 4. 生成系统需求.md

只生成一份 `<output_dir>/系统需求.md`，固定包含：文档与来源信息、引言、总体描述、功能需求、非功能需求、接口需求、数据需求、验收标准、来源冲突与合并说明。

功能行必须增加“来源文档”列。原文未覆盖的章节用明确说明标注，不得编造。

### 5. 生成功能设计.md

只生成一份 `<output_dir>/功能设计.md`，合并全部接口、MML、数据模型和设计约束。每个接口或设计段标注来源文档；同名接口存在差异时同时保留并进入冲突说明。

### 6. 验证与清理

验证两个最终文件存在且非空，报告输入文档数、功能数、接口数、冲突数及来源覆盖。成功后删除 `.spec-extractor-tmp/`；失败时保留临时文件用于排查。

## 输出原则

- 全部 Word 是同一个 TR 的统一权威输入集合；
- 不选择“最佳文档”代替其他有效文档；
- 不为每份 Word 分别生成最终 Markdown；
- 最终始终只有一份 `系统需求.md` 和一份 `功能设计.md`；
- 内容语言遵循原文，中文字段使用 UTF-8；
- 只重组、提炼和合并原文，不补充原文没有的业务事实。
