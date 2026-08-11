---
name: test-spec-analysis
description: 基于 init 保存的当前已有 TR 完整上下文和整套 sr_specs 进行测试规格与 TS 分析；TR 元数据及直接需求范围来自 tr_info.json，不创建新 TR，不追加平台已有质量属性 TS。
metadata:
  version: "0.2"
---

# 测试规格分析

## 1. 输入与职责

必需输入：

```yaml
tr_info: <tr_dir>/tr_info.json
sr_specs: <tr_dir>/sr_specs/
output_dir: <tr_dir>/test_specs/
```

完整读取：

- `tr_info.json`；
- `sr_specs/_index.md`；
- `sr_specs/` 下全部 SR 文件。

本 Skill 面向平台已存在的当前 TR：

- 不创建、不修改 TR；
- 不调用 `create-tr`；
- 不从环境变量、任务级文件或其他 TR 补充 TR 字段；
- 不自动追加 9 条质量属性 TS，避免与平台已有 TS 重复；
- 只生成一份测试规格 Markdown，不直接生成 JSON。

分析方法见 [rules/analysis-guide.md](../../rules/analysis-guide.md)，TS 拆分、命名与描述规则见 [rules/ts-split.md](../../rules/ts-split.md)。

## 2. 上下文校验

开始分析前：

1. 校验 `tr_info.tr_id`、`design_task_id`、`tr_name` 存在；
2. 从 `tr_info.requirements[]` 按顺序提取并去重 `requirement_number`；
3. 该集合是当前 TR 的直接关联需求全集，不能为空；
4. `_index.md` 的“当前 TR 直接关联需求”必须覆盖相同集合；
5. `sr_specs/` 至少包含一个有效 SR 文件；
6. 存在未处理的高优先级解析冲突时停止并提示确认。

不得使用 `cida_info.json` 的首条需求代替完整需求集合。

## 3. 分析过程

测试规格前段至少包含：

1. 被测对象与当前 TR 概述；
2. 直接关联需求和 SR 分解覆盖；
3. RBT 风险、重点难点、分层策略；
4. 硬件、组网、网元形态差异；
5. 测试场景拆分依据与覆盖映射；
6. 文档来源冲突对测试设计的影响。

每条 TS 必须能够回溯到当前 TR 的一个或多个直接关联需求；`requirement_ids` 必须是 TR 需求全集的非空子集。不得引用其他 TR 的需求。

## 4. 平台写入数据

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

## 5. 输出

输出唯一文件：

```text
<tr_dir>/test_specs/<TR名称>测试规格.md
```

文件名中的 TR 名称须进行路径安全处理；若名称不适合作为文件名，使用 `tr_no`，仍不得改写 Markdown 中的真实 `tr_name`。

完成后汇总 TR ID、直接需求数、SR 数、TS 数、各 TS 类型数及尚待确认的审计项。

`tr_ts.json` 由 Explore 确认后调用：

```bash
python .testagent/skills/test-spec-analysis/scripts/build_tr_json.py \
  "<测试规格.md>" \
  --tr-info "<tr_dir>/tr_info.json"
```

脚本负责再次校验 TR 元数据、需求全集和 TS 子集关系，并生成 `_meta.tr_mode=existing` 的 JSON。
