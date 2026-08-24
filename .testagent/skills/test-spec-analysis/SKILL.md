---
name: test-spec-analysis
description: 基于 init 保存的当前已有 TR 完整上下文和整套 sr_specs 进行测试规格与 TS 分析；TR 元数据及直接需求范围来自 tr_info.json，不创建新 TR，不追加平台已有质量属性 TS。
metadata:
  version: "0.3"
---

# 测试规格分析

## 1. 输入与职责

必需输入：

```yaml
tr_info: <tr_dir>/tr_info.json
sr_specs: <tr_dir>/sr_specs/
platform_ts: <tr_dir>/test_specs/platform_ts.json
output_dir: <tr_dir>/test_specs/
```

完整读取：

- `tr_info.json`；
- `sr_specs/_index.md`；
- `sr_specs/` 下全部 SR 文件；
- `platform_ts.json`。

本 Skill 面向平台已存在的当前 TR：

- 不创建、不修改 TR；
- 不从环境变量、任务级文件或其他 TR 补充 TR 字段；
- 只生成一份测试规格 Markdown，不直接生成 JSON；
- 在同一 Markdown 中生成平台 DFX 的独立测试规格，但不把 DFX 写入普通 TS 清单。

分析方法见 [rules/analysis-guide.md](../../rules/analysis-guide.md)，TS 拆分、命名与描述规则见 [rules/ts-split.md](../../rules/ts-split.md)。

## 2. 上下文校验

开始分析前：

1. 校验 `tr_info.tr_id`、`design_task_id`、`tr_name` 存在；
2. 从 `tr_info.requirements[]` 按顺序提取并去重 `requirement_number`；
3. 该集合是当前 TR 的直接关联需求全集，不能为空；
4. `_index.md` 的“当前 TR 直接关联需求”必须覆盖相同集合；
5. `sr_specs/` 至少包含一个有效 SR 文件；
6. 存在未处理的高优先级解析冲突时停止并提示确认；
7. `platform_ts.json` 必须是合法 JSON；过滤 `scene/function/feature/constraint` 后的 DFX 条目必须具有唯一、非空的 `platform_ts_id`。

不得使用 `cida_info.json` 的首条需求代替完整需求集合。

## 3. 分析过程

测试规格前段必须包含以下固定标题，标题文字不得改写；标题下必须有非空正文，供 Archive 写入在线文档：

```markdown
## 概述
### 被测对象概述
### 测试方案概述

## 测试设计策略
### 特性风险分析（RBT）
### 测试重点难点分析
### 分层测试策略
### 底层硬件/组网差异测试策略分析
### 网元形态差异测试策略分析

## 场景分析
## 测试类型分析
## 特性交互分析
## 功能交互分析
## 设计约束分析
```

“概述”和“测试设计策略”的子标题内容分别合并写入对应任务节点；其余五个二级标题分别写入同名 TR 节点。直接关联需求、SR 覆盖、测试场景拆分依据和文档冲突影响必须归入上述最相关章节，不再创建同义标题。

每条 TS 必须能够回溯到当前 TR 的一个或多个直接关联需求；`requirement_ids` 必须是 TR 需求全集的非空子集。不得引用其他 TR 的需求。

## 4. DFX TS 测试规格

对 `platform_ts.json` 中过滤 `scene/function/feature/constraint` 后的每条平台 DFX，按原顺序生成一条规格：

```markdown
## DFX TS 测试规格

### DFX TS：<platform_ts_id>

| 字段 | 内容 |
|---|---|
| platform_ts_id | <平台 TS ID> |
| ts_name | <TS 名称> |
| ts_type | <平台 TS 类型> |
| requirement_ids | <当前 TR 直接关联需求全集> |
| description | <结合当前 TR 总结的 DFX 测试范围和目标> |
| resolve_description | <测试重点、约束和设计方向> |
```

`## DFX TS 测试规格` 只出现一次，每个 `platform_ts_id` 只对应一个三级标题。该章节必须位于 `## 平台写入数据` 之前；不得按名称或类型代替 `platform_ts_id` 定位，不得把 DFX 行写入平台普通 TS 清单。

## 5. 平台写入数据

在 Markdown 末尾写入且只写入一个 `## 平台写入数据` 章节：

````markdown
## 平台写入数据

> 本章为固定格式，由 build_tr_json.py 校验并生成已有 TR JSON。

### TR

| 字段 | 值 |
|---|---|
| tr_name | <tr_info.tr_name> |
| description | <tr_info.description> |
| resolve_description | <tr_info.resolve_description> |
| requirement_ids | <tr_info.requirements[] 的全部需求编号，英文逗号分隔> |
| function_numbers | <tr_info.relation_function> |
| feature_numbers | <tr_info.relation_feature> |

### TS 清单

| ts_name | ts_type | requirement_ids | description | resolve_description |
|---|---|---|---|---|
| <中文 TS 名> | <scene/function/feature/constraint> | <当前TR需求子集> | <按规则填写> | <按规则填写> |
````

TR 表字段必须直接映射 `tr_info.json`，不得重新总结或改写。`requirement_ids` 必须与 `requirements[]` 去重全集完全一致，建议保持原顺序。

TS 规则：

- `ts_type` 仅为 `scene`、`function`、`feature`、`constraint`；
- `requirement_ids` 使用英文逗号分隔；
- 每个需求编号必须属于当前 TR；
- 不生成 `performance`、`reliability` 等平台已有质量属性 TS；
- 中文字段必须为可读 UTF-8 内容。

## 6. 输出

输出唯一文件：

```text
<tr_dir>/test_specs/<TR名称>测试规格.md
```

文件名中的 TR 名称须进行路径安全处理；若名称不适合作为文件名，使用 `tr_no`，仍不得改写 Markdown 中的真实 `tr_name`。

完成后汇总 TR ID、直接需求数、SR 数、普通 TS 数、DFX TS 数、各 TS 类型数及尚待确认的审计项。

`tr_ts.json` 由 Explore 确认后调用：

```bash
python .testagent/skills/test-spec-analysis/scripts/build_tr_json.py \
  "<测试规格.md>" \
  --tr-info "<tr_dir>/tr_info.json"
```

脚本负责再次校验 TR 元数据、需求全集和 TS 子集关系，并生成 `_meta.tr_mode=existing` 的 JSON。
