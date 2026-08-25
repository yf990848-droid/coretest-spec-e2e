---
name: coretest-document-sync
description: 在 CoreTest 对象归档阶段结束后，按已核验的文档范围同步设计任务、TR 和 TS 在线文档，执行章节提取、topic 预检、稳定 UUID 覆盖写入和节点级失败隔离，并生成终态 document_plan.json。由 coretest-archive-agent 在 coretest-object-archive 之后、Portal 刷新之前调用。
---

# CoreTest Document Sync

## 职责

在对象归档全部处理结束后同步在线文档：

```text
设计任务 → TR → 文档范围中的 TS
```

只写设计任务、TR、TS 文档，不写 TP 测试因子分析或 TC 文档。文档失败不得回滚或改写对象状态。

## 必需输入

- 扩展包根目录；
- `design_task_id`、PBI、`user_id`；
- `tr_info.json` 及当前 `tr_id/tr_name`；
- `.design_output/design_task_info.json`；
- 测试规格 Markdown；
- `ts_catalog.json`；
- `test_design/`；
- 对象归档完成后的 `archive_state.json`；
- 调用方已核验的文档范围；
- `archive/document_plan.json` 输出路径。

文档范围格式：

```json
{
  "task": ["<design_task_id>"],
  "tr": ["<tr_id>"],
  "ts": ["TS_01"]
}
```

任一有效请求必须且只能包含当前任务和当前 TR。TS 按 `ts_catalog.json.items[]` 顺序去重；TR-only 的 `ts` 为空。

## 初始化文档计划

执行任何外部命令前，按“任务 → TR → TS”生成全部预期节点并写入 `document_plan.json`。节点初始状态为 `pending`，计划至少包含：

```text
schema_version
status
expected_nodes
nodes[].node_type
nodes[].node_id
nodes[].status
nodes[].activities
nodes[].error
```

后续每次节点状态变化都立即覆盖保存。Skill 返回时不得存在 `pending`。

## 解析 CoreTool 和 IDP 文档

先读取 `<root>/.testagent/skills/coretool/SKILL.md`，按其环境准备流程解析并校验绝对路径 `<coretool_cmd>`。所有命令复用该路径，禁止执行裸 `coretool`。

从 `design_task_info.json` 读取当前任务的 `idp_doc_id`。本地没有时调用：

```bash
"<coretool_cmd>" coretest testdesign task list --version-pbi <pbi> --output json
```

只接受 `id=<design_task_id>` 的唯一任务记录。公共 `idp_doc_id` 缺失时，将所有预期节点分别记录为 `failed`，不得直接结束而遗留 pending。

普通 TS 的真实 ID 从成功归档状态读取；DFX TS 使用 catalog 的 `platform_ts_id` 并与状态核对。TS 缺少真实 ID或发生冲突时只将该 TS 节点记为失败，继续其他节点。

## 提取固定章节

从测试规格 Markdown 提取：

- 任务 `概述`：合并 `被测对象概述`、`测试方案概述`；
- 任务 `测试设计策略`：合并 `特性风险分析（RBT）`、`测试重点难点分析`、`分层测试策略`、`底层硬件/组网差异测试策略分析`、`网元形态差异测试策略分析`；
- TR：`场景分析`、`测试类型分析`、`特性交互分析`、`功能交互分析`、`设计约束分析`。

从每个目标 `ts_<NN>_test_design.md` 提取：

| 来源/类型 | 必需章节 |
|---|---|
| 平台 DFX | `测试类型交互设计`、`基于业务内部实现的设计` |
| `function` / `feature` | `功能交互设计`、`基于业务内部实现的设计` |
| `scene` | `基于业务场景的设计`、`基于业务内部实现的设计` |
| `constraint` | `基于业务内部实现的设计` |

标题存在但正文为空同样视为缺失。不得使用相似标题、平台写入表格或临时总结替代源章节。节点章节不完整时记录失败并继续下一节点。

## 按节点预检 topic

使用 `"<coretool_cmd>" coretest testdesign idp topic list` 查询每个活动：

- 任务：使用 `idp_doc_id`、`user_id`、`activity_name`，不传父节点参数；
- TR：增加 `parent-activity-id=<tr_id>`、`parent-activity-name=<tr_name>`、`parent-activity-type=TR`；
- TS：增加真实 `tsId`、`ts_name`、`parent-activity-type=TS`。

每个活动必须唯一解析到非空 `topic_id`。每个节点独立完成源章节、平台 ID 和全部 topic 预检；一个节点失败不得阻止其他节点。

## 稳定覆盖写入

使用 UUIDv5 URL namespace，name 固定为：

```text
coretest-idp|<idp_doc_id>|<TASK|TR|TS>|<节点ID>|<活动名称>
```

重复执行必须得到完全相同的 `source_value_uuid`。为每个活动生成 UTF-8 请求 JSON，并调用：

```bash
"<coretool_cmd>" coretest testdesign idp source-data write --data-file <payload.json>
```

请求体固定包含：

```text
display_type=3
title=<活动名称>
text_content=<源章节正文>
topic_id=<预检结果>
user_id=<user_id>
source_value_uuid=<稳定UUID>
```

逐项保存原始响应并立即更新计划。节点内任一活动失败时：

- 当前节点标记为 `failed`；
- 尚未执行的活动标记为 `not_executed`；
- 已成功活动保持成功；
- 继续下一个节点；
- 不更换 UUID 重试。

## 返回门禁

返回前必须确保：

- `expected_nodes` 与输入文档范围完全一致；
- 每个预期节点恰好出现一次；
- 不存在 `pending`；
- 节点状态只包含 `succeeded`、`failed`、`not_executed`；
- 顶层 `status` 为：
  - 全部成功：`succeeded`；
  - 成功和失败并存：`partial`；
  - 全部失败：`failed`。

Skill 自身异常也必须尽可能将剩余 pending 节点落为 `failed`，错误写入节点和顶层摘要。

## Guardrails

- 不调用 `create_tr/create_ts/create_tp/create_tc`；
- 不修改 `archive_state.json` 的对象状态；
- 不扫描文档范围以外的 TS；
- 不写 TP/TC 文档；
- 不因单节点失败停止全部文档；
- 不调用 Portal Skill；
- 不输出最终归档成功结论。
