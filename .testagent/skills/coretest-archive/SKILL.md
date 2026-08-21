---
name: coretest-archive
description: 按 TS、TP 或 TC 目标归档测试设计产物，复用平台 DFX TS，并可通过 --document 将任务、TR 和 TS 的设计文字覆盖写入在线文档。
metadata:
  author: corespec
  version: "2.6.0"
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
/coretest-archive <tr_id> [归档目标...] [--document]
```

示例：

```text
/coretest-archive 3863 TS
/coretest-archive 3863 TS_01 TS_02
/coretest-archive 3863 TP
/coretest-archive 3863 TS_01/TP.01.03.01
/coretest-archive 3863 TC
/coretest-archive 3863 --document
/coretest-archive 3863 TC --document
```

层级关键字含义：

| 输入 | 归档范围 |
|---|---|
| `TS` | 全部 TS |
| `TP` | 全部 TS 和全部 TP |
| `TC` | 全部 TS、全部 TP 和全部 TC |

不支持 `TR` 归档目标。输入 `/coretest-archive <tr_id> TR` 时必须停止并说明 TR 仅复用、不归档。

指定对象规则：

- TS 编号和来源只从 Explore 生成的 `ts_catalog.json.items[]` 读取；
- `source=platform_dfx` 的 TS 复用 `platform_ts_id`，不得调用 `create_ts`；
- `source=explore` 的 TS 沿用现有创建或状态复用逻辑；
- TP 推荐使用 `TS_<NN>/<tp_id_temp>`；裸 `tp_id_temp` 仅在全部 TP JSON 中唯一时允许；
- TC 推荐使用 `TS_<NN>/<tc_id_temp>`；裸 `tc_id_temp` 或 `case_id` 仅在全部 TC JSON 中唯一时允许；
- 裸 TP/TC 标识匹配到多个对象时停止并列出带 TS 前缀的候选；
- 支持多个目标，保持用户输入顺序并去重；
- 指定对象只向上补齐父级依赖，绝不向下展开子级对象；
- `TS_01` 只归档该 TS，不包含其下 TP 或 TC。

## Phase 0：解析输入

1. 第一个位置参数必须是纯数字 `tr_id`；
2. 其后至少提供一个归档目标或 `--document`；
3. 仅识别 `TS`、`TP`、`TC` 三个全量层级关键字；
4. 拒绝 `TR` 目标；
5. `--document` 是独立布尔参数，不得放入对象执行计划；
6. 其他参数作为指定对象标识，与产物内容精确匹配；
7. 对重复目标去重，但保持输入顺序。

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
test_specs/ts_catalog.json
test_design/ts_*_tp.json
test_design/ts_*_tc.json
archive/archive_state.json
```

只做必要检查：

- TR 目录及 `tr_info.json`、`cida_info.json`、`test_specs/tr_ts.json`、`test_specs/ts_catalog.json` 存在；
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

每次调用都必须根据本次用户参数重新生成计划，并将完整计划作为 Agent 输入。主 Skill 不调用 `archive_state.py`，也不自行记录或重试执行计划；状态初始化和计划落盘统一由 `coretest-archive-agent` 完成。状态中的旧计划不得改变本次范围。

计划包含 TP/TC 时，所有目标 TP 的 `tpSourceType` 必须为 `tp-tc-design-logic.md` 中的非空合法值；为空或非法时在调用 Agent 前停止，不再记录为 skipped。

## Phase 3：初始化归档状态

状态文件固定为：

```text
.design_output/<design_task_id>/TR_<tr_id>/archive/archive_state.json
```

Agent 调用状态脚本初始化时必须传入：

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
9. `ts_catalog.json` 路径及完整内容；
10. `test_design/` 路径；
11. 仅当计划包含 TP/TC 时提供相关 JSON；
12. `archive/archive_state.json` 路径；
13. 当前 TR 下完整 TS 清单；
14. 是否启用 `--document`，以及 `design_task_info.json` 路径。

Agent 负责：

- 初始化状态并保存完整 TR 信息；
- 将完整计划写入 `archive/request_plan.json`，通过 `--request-file` 一次性记录并回读校验；
- 严格遍历状态文件中的执行计划，禁止从源 JSON 扩大执行范围；
- 复用 `archive_state.json.tr.platform_id` 作为父 TR ID；
- 只调用 `create_ts`、`create_tp`、`create_tc`；
- 每次 MCP 成功后立即保存真实平台 ID 和原始响应；
- 复用已成功状态，处理失败、blocked 和断点续跑；
- 完成后调用 `test-portal-card` Skill；
- `--document` 启用时，在对象归档完成后通过 `coretool` Skill 写入在线文档；
- 返回归档结果汇总。

## Phase 5：在线文档写入

未指定 `--document` 时跳过。指定后写入范围固定为当前设计任务、当前 TR 和 `ts_catalog.json` 中全部 TS，不受对象归档目标筛选影响，本次不写 TP 测试因子分析。

- 仅 `--document`：不创建任何 TS/TP/TC；普通 TS 必须已在状态中存在有效平台 ID；
- 与 TS/TP/TC 目标组合：先完成对象归档，再解析全部 TS 的平台 ID；
- 任一源章节、平台 ID 或在线 topic 缺失时，在第一次 `source-data write` 前整体停止；
- 使用稳定 `source_value_uuid` 覆盖更新，禁止每次生成随机 UUID；
- 具体章节、topic 和 UUID 规则由 `coretest-archive-agent` 执行。

## Phase 6：汇总

输出：

- 用户请求目标、计划 TS/TP/TC 数量和实际状态 TS/TP/TC 数量；
- 实际执行计划与状态数量不一致时明确报告；
- `TR <tr_id>：复用 Init 上下文，未执行归档`；
- TS 成功、失败、复用和 blocked 列表；
- TP 成功、失败、复用和 blocked 列表；
- TC 成功、失败、复用和 blocked 列表；
- `archive_state.json` 路径；
- Portal 卡片刷新与最终跳转结果。
- 在线文档预检、写入和覆盖更新结果。

主 Skill 不得在 Agent 返回后补做任何 MCP 创建调用。

## 错误处理

| 场景 | 处理 |
|---|---|
| 未提供 `tr_id`，或既无归档目标也无 `--document` | 停止并提示正确格式 |
| `ts_catalog.json` 缺失或非法 | 停止并提示重新执行 Explore |
| 输入 `TR` 目标 | 停止，说明 TR 不归档 |
| 找不到或找到多个 TR 上下文 | 报告候选并停止 |
| 指定对象不存在或不唯一 | 停止，不调用 MCP |
| Agent 调用失败 | 保留已写入的归档状态并报告 |
| Portal 卡片失败 | 保留平台对象和状态，不重建已成功对象 |

## Guardrails

- TR 只从 Init 的 `tr_info.json` 复用，禁止调用 `create_tr`；
- `request.execution_plan.tr` 必须为空；
- 不修改 `tr_info.json`、`tr_ts.json`、TP JSON 或 TC JSON；
- 不修改 `ts_catalog.json`，不重新查询并改变 TS 编号；
- 真实平台 ID 只保存到 `archive/` 状态目录；
- TC 以 `create_tc` 返回 `success=true` 为成功，不要求平台 ID；
- 主 Skill 不直接调用创建 MCP；
- 一次归档只调用一个 `coretest-archive-agent`；
- Agent 内顺序处理父子依赖；
- 已成功对象不得重复创建；
- 卡片失败时不得重做 MCP 写入；
- Portal 卡片必须通过 `test-portal-card` Skill 更新。
