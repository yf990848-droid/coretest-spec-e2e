---
name: coretest-archive
description: 按 TR、TS、TP 或 TC 目标归档测试设计产物，调用单个 coretest-archive-agent 顺序完成依赖创建、状态保存和 Portal 卡片跳转。
metadata:
  author: corespec
  version: "2.4.2"
---

# CoreTest Archive Skill

## 目标

根据用户指定的 TR、TS、TP 或 TC 归档目标，定位 `.design_output/<design_task_id>/<IR>/` 下已经完成 explore/design 的上下文，并调用一个 `coretest-archive-agent` 完成完整归档闭环。

归档依赖顺序固定为：

```text
TR → TS → TP → TC
```

本 Skill 只负责入口解析、上下文定位、输入校验和 Agent 调度，不直接调用 `create_tr`、`create_ts`、`create_tp`、`create_tc` MCP，也不直接刷新 Portal 卡片。

## 使用方式

### 按层级归档全部对象

```text
/coretest-archive TR
/coretest-archive TS
/coretest-archive TP
/coretest-archive TC
```

含义：

| 输入 | 归档范围 |
|---|---|
| `TR` | 当前 TR |
| `TS` | 当前 TR 和全部 TS |
| `TP` | 当前 TR、全部 TS 和全部 TP |
| `TC` | 当前 TR、全部 TS、全部 TP 和全部 TC |

### 归档指定对象

```text
/coretest-archive TS_01
/coretest-archive TS_01 TS_02
/coretest-archive TS_01/<tp_id_temp>
/coretest-archive TS_01/<tc_id_temp>
```

规则：

- `tr_ts.json.test_specs[]` 没有独立 TS 编号，按 1-based 顺序派生：`test_specs[0] → TS_01`；
- TP 推荐使用 `TS_<NN>/<tp_id_temp>`；裸 `tp_id_temp` 仅在全部 TP JSON 中唯一时允许；
- TC 推荐使用 `TS_<NN>/<tc_id_temp>`；裸 `tc_id_temp` 或 `case_id` 仅在全部 TC JSON 中唯一时允许；
- 裸 TP/TC 标识匹配到多个对象时停止并列出带 TS 前缀的候选，不得自行选择；
- TP/TC 的编号格式以实际 JSON 为准，不在入口中写死；
- 支持多个目标，保持用户输入顺序并去重；
- 指定对象只向上补齐其父级依赖，绝不向下展开其子级对象；
- `TS_01` 的范围固定为当前 TR 和 `TS_01`，不得包含 `TS_01` 下的任何 TP 或 TC；
- 不传参数时停止执行，提示用户指定 TR、TS、TP 或 TC；
- 不再使用 IR 作为归档参数。

## Phase 0：解析输入

保留用户输入的原始目标列表，并完成以下检查：

1. 参数不能为空；
2. 识别 `TR`、`TS`、`TP`、`TC` 四个全量层级关键字；
3. 其他参数作为指定对象标识，稍后与产物内容精确匹配；
4. 对重复目标去重，但不得改变用户输入顺序；
5. 不得根据编号外观猜测不存在的对象。

## Phase 1：定位归档上下文

先检查公共文件：

```text
.design_output/design_task_info.json
```

再且只能先用以下模式发现候选上下文：

```text
.design_output/*/*/test_specs/tr_ts.json
```

从每个匹配结果中解析：

```text
.design_output/<design_task_id>/<IR>/
```

只有解析出实际的 `design_task_id` 和 `IR` 后，才能组装并检查同一上下文中的：

```text
.design_output/<design_task_id>/<IR>/cida_info.json
.design_output/<design_task_id>/<IR>/test_design/ts_*_tp.json
.design_output/<design_task_id>/<IR>/test_design/ts_*_tc.json
```

一个有效归档上下文必须同时存在：

```text
.design_output/<design_task_id>/<IR>/cida_info.json
.design_output/<design_task_id>/<IR>/test_specs/tr_ts.json
```

仅当目标计划包含 TP 或 TC 时，才额外要求 `.design_output/<design_task_id>/<IR>/test_design/` 下存在对应的 `ts_*_tp.json` 或 `ts_*_tc.json`。

定位规则：

- 指定 TS 时，根据 `tr_ts.json.test_specs[]` 的 1-based 顺序匹配；指定 TP 或 TC 时，根据带 TS 前缀的选择器和对应 JSON 实际内容匹配上下文；
- 输入层级关键字 `TR`、`TS`、`TP`、`TC` 时，只能在唯一有效上下文中执行；
- 只匹配到一个上下文时使用该上下文；
- 没有匹配上下文时停止并报告已检查的目标；
- 匹配到多个上下文时停止并列出候选 `<design_task_id>/<IR>`，不得按修改时间或目录顺序静默选择；
- 候选枚举完成前，不得使用未解析的路径变量构造后续路径；
- 禁止发出 `.design_output///...` 或仍包含 `<design_task_id>`、`<IR>` 占位符的工具调用；
- 上下文发现只使用文件匹配，不使用 `dir`、`ls` 或 Bash/PowerShell 命令探测目录；
- 不读取或写入任何 `corespec/changes/` 目录。

## Phase 2：校验上下文

读取 `.design_output/design_task_info.json`，根据上下文目录中的 `design_task_id` 精确匹配：

```text
data[].design_task_id
```

必须取得：

```text
pbi       = design_task_info.json 顶层 pbi
task_name = 当前 design_task_id 对应的 data[].name
```

注意：

- `create_tr.pbi` 使用顶层版本 PBI，例如 `266926538`；
- `design_task_id` 例如 `2470`，用于后续 `create_ts.designTaskId` 和 `create_tp.designTaskId`；
- 不得把 `design_task_id` 当作 `create_tr.pbi`；
- 不得使用 `tr_name` 代替 `task_name`。

同时校验：

1. `cida_info.json` 可读取；
2. `tr_ts.json` 中存在完整 TR 和 TS 数据；
3. 指定 TS 存在于 `tr_ts.json`；
4. 指定 TP 存在于某个 `ts_<NN>_tp.json`；
5. 指定 TC 存在于某个 `ts_<NN>_tc.json`；
6. 指定 TP/TC 能唯一解析其所属 TS/TP；
7. `creator` 不为空；
8. 仅当目标或其上游依赖计划实际包含 TP/TC 时，校验对应 TP/TC JSON 文件存在。

目标范围必须严格遵守：

```text
TR              → TR
TS_01           → TR + TS_01
TS              → TR + 全部 TS
TS_01/TP.xxx    → TR + 所属 TS + 指定 TP
TP              → TR + 全部 TS + 全部 TP
TS_01/TC.xxx    → TR + 所属 TS + 所属 TP + 指定 TC
TC              → TR + 全部 TS + 全部 TP + 全部 TC
```

依赖只能向上补齐父节点，禁止从 TR、指定 TS 或指定 TP 向下推导、读取或归档子级对象。TS-only 目标不得要求、读取或传递 `ts_*_tp.json`、`ts_*_tc.json`；指定 TP 目标不得要求、读取或传递 `ts_*_tc.json`。

精确 TP 目标（包括裸 TP 唯一解析后的结果）的执行计划必须固定为：

```json
{
  "tr": ["TR"],
  "ts": ["TS_01"],
  "tp": ["TS_01/TP.01.03.01"],
  "tc": []
}
```

生成计划后、保存计划和启动 Agent 前必须执行范围校验：如果本次用户目标中不存在 TC 目标或全量 `TC`，但 `execution_plan.tc` 非空，立即停止并报告计划生成错误；不得调用 `record-plan`、不得启动 Agent、不得调用任何创建 MCP。

每次调用都必须只根据本次用户参数重新生成当前执行计划。`archive_state.json.request.execution_plan` 是上一次请求的历史记录，不是本次计划来源；不得根据其中残留的 TP/TC 生成待办、续跑任务或 Agent 提示词。本次计划生成后，必须通过 `record-plan` 覆盖该历史计划。

`tpSourceType` 字段必须存在，但当前版本允许值为空。入口不得因 `tpSourceType` 为空而停止整个归档，也不得补写或猜测其值；由 Agent 将对应 TP 记录为 skipped，并将其下 TC 记录为 blocked。

任一校验失败时，不得启动 Agent，也不得调用 MCP。

## Phase 3：调用 coretest-archive-agent

只启动一个：

```text
agents/coretest-archive-agent
```

不得按 TR、TS、TP 或 TC 拆分多个 Agent，不得并发启动归档 Agent。

调用 Agent 时必须提供：

1. 扩展包根目录；
2. 用户原始目标列表；
3. 已去重的目标列表；
4. 仅根据本次目标生成的权威执行计划；
5. `design_task_id`；
6. IR 编号；
7. PBI；
8. `task_name`；
9. `creator`；
10. 当前上下文目录；
11. `design_task_info.json` 路径；
12. `cida_info.json` 路径；
13. `tr_ts.json` 路径及完整内容；
14. `test_design/` 路径；
15. 仅当执行计划包含 TP/TC 时提供与目标有关的 TP/TC JSON 路径；
16. `.design_output/<design_task_id>/<IR>/archive/archive_state.json` 路径；
17. 当前 TR 下完整 TS 清单。

如果本次最高目标是指定 TP，传给 Agent 的 `execution_plan.tc` 必须为空，并且不得提供 TC JSON 路径或 TC 详细数据。

Agent 负责：

- 核验并保存本次权威执行计划，不得复用状态文件中的旧计划；
- 直接调用 `core_test_design_mcp.create_tr/create_ts/create_tp/create_tc`；
- TR、TS、TP 的 MCP 成功后立即保存真实平台 ID 和原始响应；
- TC 的 MCP 返回 `success=true` 后立即保存 `succeeded` 状态和原始响应，不要求返回或保存 `tcId/platform_id`；
- TC 已有 `status=succeeded` 时直接复用成功状态，不得因缺少 `platform_id` 重复调用 `create_tc`；
- 复用已成功保存的 ID，避免重复创建；
- 处理 skipped、失败、blocked 分支和断点续跑；
- 所有可执行对象处理完成后调用 `test-portal-card` Skill；
- 返回归档结果汇总。

## Phase 4：汇总

等待 `coretest-archive-agent` 完成后输出：

- 用户请求目标；
- 实际依赖计划；
- TR 成功/失败及 `tr_id`；
- TS 成功、失败、复用和 blocked 列表；
- TP 成功、失败、复用、skipped 和 blocked 列表；
- TC 成功、失败、复用和 blocked 列表；
- `archive_state.json` 路径；
- Portal 卡片刷新与最终跳转结果。

主 Skill 不得在 Agent 返回后补做任何 MCP 创建调用。

## 错误处理

| 场景 | 处理 |
|---|---|
| 未提供归档目标 | 停止，提示指定 TR、TS、TP 或 TC |
| 找不到有效上下文 | 停止并报告 |
| 找到多个上下文 | 列出候选并停止 |
| design_task_info 缺少匹配任务 | 停止，不调用 MCP |
| 指定对象不存在或不唯一 | 停止，不调用 MCP |
| Agent 调用失败 | 保留已写入的归档状态并报告 |
| Portal 卡片失败 | 保留平台对象和状态；禁止重新创建已成功对象 |

## Guardrails

- 不再接受 IR 作为归档目标；
- 不修改 `tr_ts.json`、`ts_<NN>_tp.json` 或 `ts_<NN>_tc.json`；
- 不在入口阶段拒绝 `tpSourceType` 空值，不补写或转换该字段；
- 真实平台 ID 只保存到 `archive/` 状态目录；
- TC 不以平台 ID 作为成功条件；`create_tc` 返回 `success=true` 即成功；
- TC 幂等以 `status=succeeded` 为准，不得要求 TC 同时存在 `platform_id`；
- 主 Skill 不直接调用四个创建 MCP；
- 旧 `execution_plan` 只能作为历史记录读取，不得据此创建“续跑 TP/TC”待办或改变本次目标；
- 一次归档只调用一个 `coretest-archive-agent`；
- Agent 内必须顺序处理依赖，不得并发创建存在父子关系的平台对象；
- 已成功且状态中存在真实 ID 的对象不得重复创建；
- 卡片失败时不得重做 MCP 写入；
- 不使用 `coretest-aexplore`；
- Portal 卡片必须通过 `test-portal-card` Skill 更新。
