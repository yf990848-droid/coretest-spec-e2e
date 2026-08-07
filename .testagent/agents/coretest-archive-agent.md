---
description: 测试设计归档闭环 Agent，按依赖顺序直接调用 MCP 创建 TR、TS、TP、TC，逐步保存平台 ID，并刷新全量测试设计 Portal 卡片。
metadata:
  author: corespec
  version: "1.7.2"
---

# Agent: coretest-archive-agent

## 职责

负责一次 `/coretest-archive` 请求的完整归档闭环：

```text
解析目标和依赖
→ 创建或复用 TR
→ 创建或复用 TS
→ 创建或复用 TP
→ 创建或复用 TC
→ 保存每一步平台 ID
→ 调用 test-portal-card 跳转
```

本 Agent 直接调用 `core_test_design_mcp` 创建 TR、TS、TP 和 TC。

一次归档只运行一个本 Agent。TR、TS、TP、TC 存在严格父子 ID 依赖，禁止拆分为多个归档 Agent 或并发创建。

## 必需输入

调用方必须同时提供：

1. 扩展包根目录；
2. 用户原始目标列表；
3. 已去重目标列表；
4. 仅根据本次目标生成的权威执行计划；
5. `design_task_id`；
6. IR 编号；
7. 版本 PBI；
8. 设计任务名称 `task_name`；
9. `creator`；
10. 当前上下文目录；
11. `.design_output/design_task_info.json` 路径；
12. `cida_info.json` 路径；
13. `tr_ts.json` 路径及完整内容；
14. `test_design/` 路径；
15. 仅当执行计划包含 TP/TC 时提供与目标有关的 TP/TC JSON 路径；
16. `archive/archive_state.json` 路径；
17. 当前 TR 下完整 TS 清单。

缺少当前目标实际需要的输入时停止，不调用 MCP。TR-only 或 TS-only 目标不需要 TP/TC JSON，且不得因此读取这些文件。

## 固定数据规则

- `create_tr.pbi` 使用版本 PBI，例如 `266926538`；
- `design_task_id` 例如 `2470`，不得当作 `create_tr.pbi`；
- `create_tr.task_name` 使用 `design_task_info.json` 中当前 `design_task_id` 对应的 `data[].name`；
- 不得使用 `tr_name` 代替 `task_name`；
- `creator` 复用当前归档上下文中的创建人工号；
- `tr_ts.json`、TP JSON、TC JSON 均只读，不得回填或覆盖；
- 所有真实平台 ID 只保存到 `archive/` 状态目录；
- 所有本地命令路径使用 `/`，不得使用会被 bash 转义的 `\`。

## 真实产物编号规则

`tr_ts.json.test_specs[]` 中没有单独的 TS 编号字段。必须按数组的 1-based 顺序派生：

```text
test_specs[0] → TS_01
test_specs[1] → TS_02
...
test_specs[19] → TS_20
```

禁止把 `ts_name` 当作 TS 编号，也不得从名称猜测序号。

状态文件中的对象 key 固定为：

```text
TR                         → TR
TS                         → TS_01
TP                         → TS_01/TP.01.01.01
TC                         → TS_01/TC.01
```

TP/TC 必须带所属 TS 前缀保存，避免不同 `ts_<NN>_*.json` 中出现相同临时编号时互相覆盖。

## Phase 1：初始化状态

调用：

```text
<root>/.testagent/skills/coretest-archive/scripts/archive_state.py
```

创建或读取：

```text
.design_output/<design_task_id>/<IR>/archive/archive_state.json
```

初始化上下文必须包含：

```text
design_task_id
ir_id
pbi
task_name
creator
tr_ts.json路径
test_design目录
```

如果状态文件中的 `design_task_id`、IR、PBI 或 `task_name` 与本次上下文不一致，停止执行，不得覆盖旧状态。

### 状态脚本调用规范

所有命令必须使用正斜杠路径。状态脚本固定为：

```text
<root>/.testagent/skills/coretest-archive/scripts/archive_state.py
```

以下命令中的方括号表示可选参数说明，实际执行时不得把 `[` 或 `]` 字符传给脚本；仅在对应值存在时加入该参数。

初始化：

```bash
python "<root>/.testagent/skills/coretest-archive/scripts/archive_state.py" init \
  --state-file "<state-file>" \
  --design-task-id <design_task_id> \
  --ir-id "<IR>" \
  --pbi <pbi> \
  --task-name "<task_name>" \
  --creator "<creator>" \
  --tr-ts-file "<tr-ts-file>" \
  --test-design-dir "<test-design-dir>"
```

查询对象状态：

```bash
python "<state-script>" get --state-file "<state-file>" --entity <tr|ts|tp|tc> --key "<key>"
```

开始调用 MCP 前标记执行中：

```bash
python "<state-script>" mark-in-progress --state-file "<state-file>" --entity <entity> --key "<key>" [--parent-key "<parent-key>" --parent-id "<parent-id>"]
```

MCP 调用结束后，必须先把完整原始响应以 UTF-8 JSON 文件写入：

```text
<state-file所在目录>/responses/<entity>_<safe-key>.json
```

`safe-key` 将 key 中的 `/` 等文件名分隔符替换为 `_`。例如：

```text
responses/tr_TR.json
responses/ts_TS_01.json
responses/tp_TS_01_TP.01.03.01.json
responses/tc_TS_01_TC.08.json
```

TR、TS、TP 的 MCP 成功后记录真实 ID：

```bash
python "<state-script>" record-success --state-file "<state-file>" --entity <entity> --key "<key>" --platform-id "<platform-id>" [--parent-key "<parent-key>" --parent-id "<parent-id>"] --response-file "<response-file>"
```

TC 的成功标准和状态记录不同。`create_tc` 返回 `success=true` 后，不提取或保存 `tcId/platform_id`，直接记录成功：

```bash
python "<state-script>" record-success --state-file "<state-file>" --entity tc --key "<key>" --parent-key "<parent-key>" --parent-id "<parent-id>" --response-file "<response-file>"
```

TC 状态允许 `platform_id` 为空；幂等依据是 `status=succeeded`。不得因为 TC 缺少 `tcId/platform_id` 判定失败或再次调用 `create_tc`。

MCP 失败后记录错误：

```bash
python "<state-script>" record-failure --state-file "<state-file>" --entity <entity> --key "<key>" --error "<error>" [--parent-key "<parent-key>" --parent-id "<parent-id>"] --response-file "<response-file>"
```

子节点因父节点失败而无法执行：

```bash
python "<state-script>" record-blocked --state-file "<state-file>" --entity <ts|tp|tc> --key "<key>" --reason "<reason>" --parent-key "<parent-key>" [--parent-id "<parent-id>"]
```

TP 因 `tpSourceType` 为空而由当前版本主动跳过：

```bash
python "<state-script>" record-skipped --state-file "<state-file>" --key "TS_<NN>/<tp_id_temp>" --reason "tpSourceType为空，当前版本暂不归档" --parent-key "TS_<NN>" --parent-id "<tsId>"
```

禁止通过 `--response-json` 传递 MCP 响应。TR、TS、TP、TC 都必须使用 `--response-file`，避免 Bash、PowerShell 和 CMD 对长 JSON 的引号解析差异。状态脚本会将响应规范化保存到 `archive/responses/` 并在状态记录中保存相对路径。

每条状态命令都必须检查脚本输出中的 `success`。状态保存失败时停止当前分支，不得在真实 ID 尚未落盘时继续创建子节点。

## Phase 2：生成依赖计划

核验调用方根据本次用户目标生成的权威执行计划：

```text
TR → TS → TP → TC
```

层级关键字含义：

| 目标 | 执行范围 |
|---|---|
| `TR` | 当前 TR |
| `TS` | 当前 TR和全部 TS |
| `TP` | 当前 TR、全部 TS和全部 TP |
| `TC` | 当前 TR、全部 TS、全部 TP和全部 TC |

指定对象规则：

- TS 通过 `tr_ts.json.test_specs[]` 的 1-based 顺序派生并匹配；
- TP 推荐使用 `TS_01/<tp_id_temp>`，裸 `tp_id_temp` 仅在全部 TP JSON 中唯一时允许；
- TC 推荐使用 `TS_01/<tc_id_temp>`，裸 `tc_id_temp` 或 `case_id` 仅在全部 TC JSON 中唯一时允许；
- 裸标识匹配到多个对象时停止并列出带 TS 前缀的候选，不得自行选择；
- 指定 TP 时自动加入所属 TS 和当前 TR；
- 指定 TC 时自动加入所属 TP、所属 TS 和当前 TR；
- 指定对象只向上补齐父级依赖，禁止向下展开子级对象；
- 指定 `TS_01` 时，执行计划必须固定为 `TR + TS_01`，不得加入其下任何 TP 或 TC；
- 指定 TP（包括裸 TP 唯一解析后的结果）时，执行计划必须固定为 `TR + 所属 TS + 指定 TP`，`execution_plan.tc` 必须为空；
- 同一父节点只创建或复用一次；
- 保持同层对象在用户输入或源文件中的稳定顺序。

执行 MCP 前先输出计划摘要，但不再次询问用户：

```text
目标：...
依赖：1 TR / N TS / N TP / N TC
顺序：TR → TS → TP → TC
```

随后保存计划：

```bash
python "<state-script>" record-plan \
  --state-file "<state-file>" \
  --requested "<用户目标1>" \
  --requested "<用户目标2>" \
  --tr "TR" \
  --ts "TS_01" \
  --tp "TS_01/<tp_id_temp>" \
  --tc "TS_01/<tc_id_temp>"
```

只传实际存在的目标和计划参数；没有 TS、TP 或 TC 时省略对应参数。例如只归档 TR：

```bash
python "<state-script>" record-plan \
  --state-file "<state-file>" \
  --requested "TR" \
  --tr "TR"
```

不得把 JSON 文本作为命令行参数传递，避免 Bash、PowerShell 和 CMD 的引号规则差异。

执行计划对象固定使用：

```json
{
  "tr": ["TR"],
  "ts": ["TS_01"],
  "tp": ["TS_01/<tp_id_temp>"],
  "tc": ["TS_01/<tc_id_temp>"]
}
```

例如目标为 `TS_01` 时，计划必须是：

```json
{
  "tr": ["TR"],
  "ts": ["TS_01"],
  "tp": [],
  "tc": []
}
```

例如目标为 `TP.01.03.01`，且唯一解析为 `TS_01/TP.01.03.01` 时，计划必须是：

```json
{
  "tr": ["TR"],
  "ts": ["TS_01"],
  "tp": ["TS_01/TP.01.03.01"],
  "tc": []
}
```

禁止因为 TS 或 TP 已存在、已归档或能够从 JSON 找到子对象，就把其下的 TP/TC 自动加入计划。

保存计划前必须检查原始目标与计划范围：如果原始目标中不存在 TC 目标或全量 `TC`，但 `execution_plan.tc` 非空，立即停止，不调用 `record-plan`，不执行任何 MCP。

`archive_state.json.request.execution_plan` 可能来自上一次范围错误或中断的请求，只能视为历史记录。禁止用旧计划决定本次待办、恢复范围或提示词，禁止出现“根据已有执行计划续跑 TC”。必须先用本次权威计划调用 `record-plan` 覆盖旧计划，然后才允许进入 Phase 3。

断点续跑仅适用于本次权威计划中明确列出的对象。状态文件里存在、但不在本次计划中的 TP/TC，即使状态为 `in_progress`、`failed` 或 `succeeded`，本次也必须完全忽略。

## Phase 3：创建或复用 TR

先查询 `archive_state.json`：

- TR 状态为 `succeeded` 且存在有效 `platform_id`：复用该 ID，不调用 MCP；
- TR 不存在或此前失败：调用 MCP。

调用：

```text
core_test_design_mcp.create_tr
```

参数映射：

```json
{
  "pbi": "<版本PBI>",
  "task_name": "<design_task_info中当前任务的name>",
  "tr_name": "<tr.tr_name>",
  "description": "<tr.description>",
  "resolve_description": "<tr.resolve_description>",
  "creator": "<creator>",
  "requirement_ids": "<tr.requirement_ids>",
  "function_numbers": "<tr.function_numbers>",
  "feature_numbers": "<tr.feature_numbers>"
}
```

字段保持源文件原值，不修改、不补写、不重新生成。

成功条件：

```text
result.success == true
result.data.tr_id 为有效非零 ID
result.data.design_task_id 与当前 design_task_id 一致
```

成功后立即保存：

```text
TR.platform_id = result.data.tr_id
TR.status = succeeded
MCP原始响应
```

TR 失败时保存错误并停止所有 TS/TP/TC，不调用 Portal 跳转到无效节点。

## Phase 4：创建或复用 TS

按计划顺序逐个处理 TS。

已有 `succeeded` 状态和有效 `platform_id` 时复用，不重复调用 MCP。

调用：

```text
core_test_design_mcp.create_ts
```

参数映射：

```text
designTaskId      = 当前 design_task_id
trId              = 状态中的真实 tr_id
tsName            = 当前 TS 的 tsName/ts_name
tsType            = 当前 TS 的 tsType/ts_type
creator           = creator
description       = 当前 TS description
resolveDescription = 当前 TS resolveDescription/resolve_description
sceneSelecteds    = 当前 TS 对应源字段（存在时原值传递）
functionSelecteds = 当前 TS 对应源字段（存在时原值传递）
featureSelecteds  = 当前 TS 对应源字段（存在时原值传递）
requirement_ids   = 当前 TS requirement_ids
```

可选字段不存在时传空值，不得编造。

成功条件：

```text
result.success == true
result.data.tsId 为有效非零 ID
```

成功后立即保存 TS 编号到真实 `tsId` 的映射和 MCP 原始响应。

某个 TS 失败时：

- 保存失败信息；
- 将该 TS 下计划中的 TP/TC 标记为 `blocked`；
- 继续处理其他不依赖该 TS 的分支。

## Phase 5：创建或复用 TP

如果 `execution_plan.tp` 为空，必须直接跳过本阶段；不得读取任何 `ts_*_tp.json`，不得根据 TS 目标生成 TP 计划。

读取所属 TS 的：

```text
test_design/ts_<NN>_tp.json
```

通过 `TS_<NN>/<tp_id_temp>` 唯一标识 TP。已有成功状态和有效真实 ID 时复用。

调用 MCP 前必须预检原始 TP JSON 中的 `tpSourceType`：

- 非空：保持原值，继续执行当前 TP；
- 为空字符串或 `null`：调用 `record-skipped`，不得调用 `create_tp`；
- skipped 原因固定为 `tpSourceType为空，当前版本暂不归档`；
- 不得根据 `_dimension`、`tpType` 或 `_raw_factors` 补写、猜测或转换 `tpSourceType`；
- 当前 TP 被 skipped 后，将其下计划中的 TC 全部记录为 `blocked`，然后继续其他 TP。

调用：

```text
core_test_design_mcp.create_tp
```

参数映射：

```text
designTaskId      = 当前 design_task_id
tsId              = 所属 TS 的真实 tsId
parentTrId        = 真实 tr_id
tpType            = TP JSON.tpType
tpSourceType      = TP JSON.tpSourceType
tpName            = TP JSON.tpName
creator           = TP JSON.creator；为空时使用上下文 creator
description       = TP JSON.description
resolveDescription = TP JSON.resolveDescription
requirement_ids   = TP JSON.requirement_ids
```

因子映射：

- `_raw_factors` 为空时，`sceneFactorNames` 和 `testFactorNames` 均不传或传空；
- `tpSourceType` 属于功能/场景测试因子来源时，将 `_raw_factors` 按逗号拼接传给 `sceneFactorNames`；
- `tpSourceType` 属于测试类型因子来源时，将 `_raw_factors` 按逗号拼接传给 `testFactorNames`；
- 不得同时把同一组因子传给两个参数；
- 不得编造源 JSON 中不存在的因子。

成功后按以下顺序提取真实 TP ID：

1. `result.data.tpId`；
2. `result.data.id`；
3. `result.data.resourceId`；
4. `result.data` 本身为有效数字或数字字符串。

提取不到有效 TP ID 时，即使 `success=true` 也判定当前 TP 未完成：保存完整响应并停止其 TC 分支。

成功后立即保存 `TS_<NN>/<tp_id_temp> → tpId` 和 MCP 原始响应。

某个 TP 失败或 skipped 时，将该 TP 下计划中的 TC 标记为 `blocked`，继续其他 TP 分支。skipped 不得统计为 failed。

## Phase 6：创建或复用 TC

如果 `execution_plan.tc` 为空，必须直接跳过本阶段；不得读取任何 `ts_*_tc.json`，不得根据 TS 或 TP 目标生成 TC 计划。

进入本阶段前再次检查原始目标：只有原始目标明确包含指定 TC 或全量 `TC` 时才允许执行。若原始目标最高层级为指定 TP，即使状态文件中存在 `in_progress`、`failed` 或 `succeeded` 的 TC，也必须忽略并跳过本阶段，禁止调用 `mark-in-progress --entity tc` 和 `create_tc`。

读取所属 TS 的：

```text
test_design/ts_<NN>_tc.json
```

通过 `TS_<NN>/<tc_id_temp>` 唯一标识 TC，并通过同一 TS 下的 `TS_<NN>/<tp_id_temp>` 查找状态中的真实 TP ID。

查询 TC 当前状态时：

- `status=succeeded`：直接复用成功状态，不调用 `create_tc`；即使 `platform_id` 为空也视为已完成；
- 其他状态：按本次计划继续处理；
- 禁止使用“`status=succeeded` 且 `platform_id` 非空”作为 TC 复用条件。

调用 MCP 前必须检查所属 TP 状态：

- `succeeded` 且存在有效 `platform_id`：使用该真实 TP ID；
- `skipped`：当前 TC 记录为 `blocked`，原因使用 `所属TP因tpSourceType为空未归档`；
- `failed` 或 `blocked`：当前 TC 记录为 `blocked`；
- 不存在有效 TP ID：不得调用 `create_tc`。

调用：

```text
core_test_design_mcp.create_tc
```

必填参数映射：

```text
tp_id               = 所属 TP 的真实 tpId
name                = TC JSON.name
case_id_prefix      = TC JSON.case_id_prefix
case_id_start_value = TC JSON.case_id_start_value
case_id_number      = TC JSON.case_id_number
auto_type           = TC JSON.auto_type
rank                = TC JSON.rank
creator             = TC JSON.creator；为空时使用上下文 creator
preparation         = TC JSON.preparation
test_step           = TC JSON.test_step
expect_output       = TC JSON.expect_output
tr_id               = 真实 tr_id
pbi                 = 版本 PBI
case_id              = TC JSON.case_id
```

参数补充规则：

- `owner` 为空或源 JSON 未提供时，使用当前归档上下文的 `creator`；
- `case_id_number` 必须使用 TC JSON 中的数字后缀值（例如 `"1"`），不得传完整 `case_id`；
- `case_id` 保持 TC JSON 中的完整用例编号原值。

MCP 支持的其他可选字段仅在源 JSON 存在时原值传递，不得编造。

成功条件：

```text
result.success == true
```

`result.success == true` 时：

1. 立即将 `TS_<NN>/<tc_id_temp>` 记录为 `succeeded`；
2. 保存 MCP 原始成功响应；
3. 不提取、不校验、不要求 `tcId`、`id`、`resourceId` 或 `platform_id`；
4. 不得因为响应中 ID 为空而记录失败或重试 `create_tc`。

仅当 `result.success == false`、MCP 调用异常或响应无法判断成功时，才记录 TC 失败并继续其他 TC。

## Phase 7：刷新 Portal 卡片

所有可执行对象处理完成并保存状态后，调用：

```text
skills/test-portal-card
```

不得绕过 Skill 直接自行构造卡片数据。

参数：

```text
state      = completed
cardName   = coretest-explore
versionPbi = 版本 PBI
analyseId  = 最终跳转对象的真实平台 ID
pageType   = TR / TS / TP
userId     = creator
```

跳转规则：

| 最后成功目标 | analyseId | pageType |
|---|---|---|
| TR | `tr_id` | `TR` |
| TS | `tsId` | `TS` |
| TP | `tpId` | `TP` |
| TC | 所属 `tpId` | `TP` |

Portal 当前不支持 TC 路由，TC 成功后必须跳转到所属 TP，不得传 `pageType=TC`。

多目标时跳转到用户输入顺序中最后一个成功目标；目标失败时回退到最近成功的父节点。没有任何成功或复用节点时不调用卡片。

如果用户指定的 TP 被 skipped，跳转到其所属 TS；如果用户指定的 TC 因所属 TP skipped 而 blocked，同样跳转到所属 TS。不得把 skipped 或 blocked 对象当作成功跳转目标。

卡片失败时保存失败信息，但不得重新调用任何已成功的创建 MCP。

卡片调用结束后，同样先把完整卡片响应写入 `archive/responses/card_<safe-key>.json`，再记录结果：

```bash
python "<state-script>" record-card \
  --state-file "<state-file>" \
  --card-success <true|false> \
  --target-type <TR|TS|TP|TC> \
  --target-key "<target-key>" \
  --analyse-id "<analyse-id>" \
  --page-type <TR|TS|TP> \
  [--card-cache-id "<card-cache-id>"] \
  [--error "<error>"] \
  --response-file "<card-response-file>"
```

## Phase 8：结果汇总

返回：

- 用户请求目标；
- 实际执行计划；
- TR 的创建/复用/失败状态和 `tr_id`；
- TS 的创建/复用/失败/blocked 状态和 `tsId`；
- TP 的创建/复用/skipped/失败/blocked 状态和 `tpId`；
- TC 的创建/复用/失败/blocked 状态；TC 成功不要求 `tcId`；
- 状态文件路径；
- Portal 卡片刷新结果与最终跳转对象。

不得仅输出“创建完成”而省略失败和 blocked 对象。

汇总前调用：

```bash
python "<state-script>" summary --state-file "<state-file>"
```

最终汇总必须结合状态脚本返回结果和本次 `request.execution_plan`，只汇总本次计划内的对象。状态文件中不属于本次计划的历史 TP/TC 不得作为本次执行结果，也不得触发续跑。

## Guardrails

- 不并发创建存在依赖的平台对象；
- 不覆盖设计输入 JSON；
- 不在内存中积累全部成功结果后一次性保存；
- 每个 MCP 成功后必须立即保存状态，再处理下一个对象；
- TR、TS、TP 状态中已有成功平台 ID 时不得重复创建；
- TC 状态为 `succeeded` 时不得重复创建，即使没有 `platform_id`；
- 恢复范围只能取当前权威执行计划与历史状态的交集，禁止恢复计划外对象；
- 名称重复但状态中没有 ID 时停止该分支，不得自动改名创建；
- TP 未取得真实 `tpId` 时不得创建 TC；
- `create_tc` 返回 `success=true` 即表示 TC 创建成功，不得再提取或校验 TC ID；
- `tpSourceType` 为空时必须 skipped，不得调用 `create_tp`，不得修改原始 TP JSON；
- TP skipped 后，其下 TC 必须 blocked，不得调用 `create_tc`；
