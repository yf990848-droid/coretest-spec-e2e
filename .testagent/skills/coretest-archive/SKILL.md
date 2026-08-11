---
name: coretest-archive
description: 按 TS、TP 或 TC 目标归档测试设计产物，复用 Init 拉取的既有 TR，调用单个 coretest-archive-agent 顺序完成依赖创建、状态保存和 Portal 卡片跳转。
metadata:
  author: corespec
  version: "2.5.0"
---

# CoreTest Archive Skill

## 目标

根据用户指定的 TR ID 和 TS、TP 或 TC 归档目标，定位 `.design_output/<design_task_id>/TR_<tr_id>/` 下已完成 Explore/Design 的上下文，并调用一个 `coretest-archive-agent` 完成归档闭环。

TR 已由 Init 从平台拉取，Archive 只复用 TR，不创建、不归档 TR。归档依赖顺序固定为：

```text
既有 TR → TS → TP → TC
```

本 Skill 只负责入口解析、上下文定位、输入校验和 Agent 调度，不直接调用 `create_ts`、`create_tp`、`create_tc` MCP，也不直接刷新 Portal 卡片。

## 使用方式

```text
/coretest-archive <tr_id> <归档目标...>
```

示例：

```text
/coretest-archive 3863 TS
/coretest-archive 3863 TS_01 TS_02
/coretest-archive 3863 TP
/coretest-archive 3863 TS_01/TP.01.03.01
/coretest-archive 3863 TC
```

层级关键字含义：

| 输入 | 归档范围 |
|---|---|
| `TS` | 全部 TS |
| `TP` | 全部 TS 和全部 TP |
| `TC` | 全部 TS、全部 TP 和全部 TC |

不支持 `TR` 归档目标。输入 `/coretest-archive <tr_id> TR` 时必须停止并说明 TR 仅复用、不归档。

指定对象规则：

- `tr_ts.json.test_specs[]` 没有独立 TS 编号，按 1-based 顺序派生：`test_specs[0] → TS_01`；
- TP 推荐使用 `TS_<NN>/<tp_id_temp>`；裸 `tp_id_temp` 仅在全部 TP JSON 中唯一时允许；
- TC 推荐使用 `TS_<NN>/<tc_id_temp>`；裸 `tc_id_temp` 或 `case_id` 仅在全部 TC JSON 中唯一时允许；
- 裸 TP/TC 标识匹配到多个对象时停止并列出带 TS 前缀的候选；
- 支持多个目标，保持用户输入顺序并去重；
- 指定对象只向上补齐父级依赖，绝不向下展开子级对象；
- `TS_01` 只归档该 TS，不包含其下 TP 或 TC。

## Phase 0：解析输入

1. 第一个位置参数必须是纯数字 `tr_id`；
2. 其后至少提供一个归档目标；
3. 仅识别 `TS`、`TP`、`TC` 三个全量层级关键字；
4. 拒绝 `TR` 目标；
5. 其他参数作为指定对象标识，与产物内容精确匹配；
6. 对重复目标去重，但保持输入顺序。

## Phase 1：定位归档上下文

根据 `tr_id` 只使用文件匹配定位：

```text
.design_output/*/TR_<tr_id>/tr_info.json
```

找到唯一结果后，解析：

```text
.design_output/<design_task_id>/TR_<tr_id>/
```

使用同一上下文中的：

```text
tr_info.json
cida_info.json
test_specs/tr_ts.json
test_design/ts_*_tp.json
test_design/ts_*_tc.json
archive/archive_state.json
```

只做必要检查：

- TR 目录及 `tr_info.json`、`cida_info.json`、`test_specs/tr_ts.json` 存在；
- 测试规格中能找到指定 TS；
- 归档 TP/TC 时，对应 JSON 存在且指定对象能唯一匹配；
- 找到多个同一 `tr_id` 上下文时列出候选并停止。

仅当本次计划包含 TP 或 TC 时读取相应 TP/TC JSON。不得读取或写入任何 `corespec/changes/` 目录。

## Phase 2：生成执行计划

TR 永远不进入执行计划：

```json
{
  "tr": [],
  "ts": ["TS_01"],
  "tp": [],
  "tc": []
}
```

范围规则：

```text
TS_01           → TS_01
TS              → 全部 TS
TS_01/TP.xxx    → 所属 TS + 指定 TP
TP              → 全部 TS + 全部 TP
TS_01/TC.xxx    → 所属 TS + 所属 TP + 指定 TC
TC              → 全部 TS + 全部 TP + 全部 TC
```

依赖只能向上补齐父节点。TS-only 目标不得要求、读取或传递 TP/TC JSON；指定 TP 目标不得要求、读取或传递 TC JSON。

每次调用都必须根据本次用户参数重新生成计划，并通过 `record-plan` 覆盖状态文件中的历史计划。状态中的旧计划不得改变本次范围。

`tpSourceType` 为空时入口不停止；由 Agent 将 TP 记录为 `skipped`，其下 TC 记录为 `blocked`。

## Phase 3：初始化归档状态

状态文件固定为：

```text
.design_output/<design_task_id>/TR_<tr_id>/archive/archive_state.json
```

调用状态脚本时必须传入：

```text
--tr-info-file "<TR目录>/tr_info.json"
```

状态脚本读取完整 `tr_info.json`，将既有 TR 预置为：

```json
{
  "key": "TR",
  "status": "succeeded",
  "platform_id": 3863,
  "source": "init",
  "archive_action": "reused",
  "tr_info": {}
}
```

其中 `tr_info` 必须完整保存 Init 生成的原始对象，`platform_id` 使用 `tr_info.tr_id`。重复初始化时刷新 `tr_info`，保留已经归档的 TS、TP、TC 和卡片状态。

本次 `request.execution_plan.tr` 必须始终为空。

## Phase 4：调用 coretest-archive-agent

只启动一个：

```text
agents/coretest-archive-agent
```

不得按 TS、TP 或 TC 拆分多个 Agent，不得并发启动归档 Agent。

调用 Agent 时提供：

1. 扩展包根目录；
2. 用户原始目标列表及去重后的目标列表；
3. 本次权威执行计划；
4. `tr_id`、`design_task_id`、IR 编号、PBI、`task_name`、`creator`；
5. 当前 `TR_<tr_id>` 上下文目录；
6. `tr_info.json` 路径及完整内容；
7. `cida_info.json` 路径；
8. `tr_ts.json` 路径及完整内容；
9. `test_design/` 路径；
10. 仅当计划包含 TP/TC 时提供相关 JSON；
11. `archive/archive_state.json` 路径；
12. 当前 TR 下完整 TS 清单。

Agent 负责：

- 初始化状态并保存完整 TR 信息；
- 复用 `archive_state.json.tr.platform_id` 作为父 TR ID；
- 只调用 `create_ts`、`create_tp`、`create_tc`；
- 每次 MCP 成功后立即保存真实平台 ID 和原始响应；
- 复用已成功状态，处理 skipped、失败、blocked 和断点续跑；
- 完成后调用 `test-portal-card` Skill；
- 返回归档结果汇总。

## Phase 5：汇总

输出：

- 用户请求目标和实际执行计划；
- `TR <tr_id>：复用 Init 上下文，未执行归档`；
- TS 成功、失败、复用和 blocked 列表；
- TP 成功、失败、复用、skipped 和 blocked 列表；
- TC 成功、失败、复用和 blocked 列表；
- `archive_state.json` 路径；
- Portal 卡片刷新与最终跳转结果。

主 Skill 不得在 Agent 返回后补做任何 MCP 创建调用。

## 错误处理

| 场景 | 处理 |
|---|---|
| 未提供 `tr_id` 或归档目标 | 停止并提示正确格式 |
| 输入 `TR` 目标 | 停止，说明 TR 不归档 |
| 找不到或找到多个 TR 上下文 | 报告候选并停止 |
| 指定对象不存在或不唯一 | 停止，不调用 MCP |
| Agent 调用失败 | 保留已写入的归档状态并报告 |
| Portal 卡片失败 | 保留平台对象和状态，不重建已成功对象 |

## Guardrails

- TR 只从 Init 的 `tr_info.json` 复用，禁止调用 `create_tr`；
- `request.execution_plan.tr` 必须为空；
- 不修改 `tr_info.json`、`tr_ts.json`、TP JSON 或 TC JSON；
- 真实平台 ID 只保存到 `archive/` 状态目录；
- TC 以 `create_tc` 返回 `success=true` 为成功，不要求平台 ID；
- 主 Skill 不直接调用创建 MCP；
- 一次归档只调用一个 `coretest-archive-agent`；
- Agent 内顺序处理父子依赖；
- 已成功对象不得重复创建；
- 卡片失败时不得重做 MCP 写入；
- Portal 卡片必须通过 `test-portal-card` Skill 更新。
