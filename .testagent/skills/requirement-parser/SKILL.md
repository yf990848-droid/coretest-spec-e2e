---
name: requirement-parser
description: 将一个或多个需求 Word 文档作为统一权威输入集合，识别并合并全部 IR/SR/US，按 SR 生成唯一一套 sr_specs/，保留来源并审计字段冲突；兼容单个 docx_path。
metadata:
  version: "0.2"
---

# 需求文档解析器

## 输入契约

```yaml
docx_paths:
  - /absolute/path/A.docx
  - /absolute/path/B.docx
document_manifest: /absolute/path/design_doc/document_manifest.json
output_dir: /absolute/path/TR_<tr_id>
requirements:
  - requirement_number: IR_A
    requirement_id: "123"
```

兼容模式可传单个 `docx_path`，内部规范化为数组。

权威关系：

- 全部 `docx_paths` 共同构成权威输入，缺一不可；
- `系统需求.md`、`功能设计.md` 仅用于交叉校验、补充含糊字段和横切分摊；
- 辅助文件不得引入 Word 集合中不存在的需求；
- `requirements[]` 表示当前 TR 直接关联范围，用于索引和覆盖校验，不等同于文档内所有分解需求。

## 工作流程

使用 `todowrite` 跟踪 8 步。

### 0. 校验与读取辅助输入

校验全部 Word、`document_manifest.json` 及来源映射。读取 `系统需求.md`、`功能设计.md`（存在时）。

### 1. 独立转换全部 Word

每份 Word 转为独立临时 Markdown，文件名含顺序号与源文件名，禁止覆盖。任一转换失败时停止，不生成部分 `sr_specs/`。

### 2. 分文档识别

逐份识别 IR、SR、US、层次关系、关键功能、约束、依赖、非功能需求、接口、OM、资料设计和来源文档。

### 3. 合并需求对象

以需求编号为主键合并：

- 相同 SR 编号只形成一个逻辑对象和一个文件；
- 内容互补时合并，字段来源取并集；
- 相同字段内容不同，完整记录各来源值，不静默覆盖；
- 同一需求编号出现不同 ALM ID，记录为高优先级冲突并停止生成最终产物；
- 相同 US 只挂接一次；多个文档提供的层次关系冲突时进入审计。

### 4. 提取关键信息

IR：编号、标题、来源、问题、目标客户、业务价值、系统上下文及分解关系。

SR：编号、标题、利益相关方、描述、约束、规格、非功能需求、实现思路、输入/处理/输出、接口、OM、外部接口、资料设计及关联 US。

### 5. 横切信息归集

归集关键功能、约束、依赖、非功能需求、接口段和模块归属，并保存来源文档。

### 6. 确定性分摊

- 按实体名将关键功能、约束和依赖映射到相关 SR；
- 性能、可靠性、可测试性映射到对应验证类 SR；
- 接口或 MML 按同名实体映射；
- 无法确定的内容进入 `_index.md` 的“未分摊横切信息”；
- 利益相关者不强行分摊，模块归属由关联 US 承载。

### 7. 生成唯一产物并汇总

输出：

```text
<output_dir>/sr_specs/
├── _index.md
├── SR<编号1>.md
└── SR<编号2>.md
```

文件结构见 [references/output-templates.md](references/output-templates.md)。重复执行时按稳定排序覆盖本次生成的同名产物，不产生重复 SR 文件。

汇总当前 TR 直接关联需求数、识别 IR/SR/US 数、来源文档数、冲突数、未分摊项数及产物路径。

## 冲突与错误

- 文档集合为空、文件不可读或清单映射缺失：停止；
- 同一需求编号映射不同 ALM ID：停止；
- 同一 SR 字段存在内容差异：保留各值并写入审计，允许继续；
- 识别到 0 个 SR：警告并停止进入测试规格分析；
- 不得用后处理覆盖方式丢弃已解析来源。

## 注意事项

- 只读写 `<output_dir>` 及显式传入的 Word；
- 分摊采用稳定规则，不做无依据推断；
- 产物语言遵循原文，使用 UTF-8；
- `_index.md` 必须能追溯当前 TR 的直接需求、全部输入文档、合并结果与冲突处理。
