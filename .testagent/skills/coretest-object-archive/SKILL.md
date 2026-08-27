---
name: coretest-object-archive
description: 串行执行已锁定的 CoreTest 对象计划，创建或复用 TS、TP、TC 并即时保存 archive_state.json；可由 Archive Agent 调用完整计划，也可由 Explore 调用 TS-only 计划。
---

# CoreTest Object Archive

## 职责

严格执行 Archive Agent 或 Explore 已锁定并写入 `archive_state.json.request.execution_plan` 的对象归档计划：

```text
复用既有 TR → 创建或复用 TS → 创建或复用 TP → 创建或复用 TC
```

一次调用完成全部对象阶段。调用来源允许：

- `archive`：由 Archive Agent 执行完整对象计划；
- `explore_ts_only`：由 Explore 执行全量 TS-only 计划，此时 `tp/tc` 必须为空。

禁止调用在线文档同步或 Portal Skill，禁止自行扩大计划。

## 必需输入

- 扩展包根目录；
- `tr_id`、`design_task_id`、PBI、`creator`；
- `tr_info.json`、`tr_ts.json`、`ts_catalog.json` 路径及内容；
- `test_design/` 路径；Explore TS-only 只记录该标准路径，不得读取其中产物；
- `archive/archive_state.json` 路径；
- 调用来源 `archive` 或 `explore_ts_only`；
- 仅当计划包含 TP/TC 时提供对应的 TP/TC JSON。

缺少当前计划实际需要的输入时停止对象阶段，不调用创建 MCP。TS-only 不得读取 TP/TC JSON。

## 状态与计划

状态脚本固定为：

```text
<root>/.testagent/skills/coretest-archive/scripts/archive_state.py
```

所有本地路径使用 `/`。开始前必须回读 `archive_state.json` 并验证：

- `context.tr_id/design_task_id/pbi/creator` 与输入一致；
- `tr.status=succeeded`、`tr.platform_id=<tr_id>`；
- `tr.source=init`、`tr.archive_action=reused`；
- `request.execution_plan` 只包含 `tr/ts/tp/tc`，且 `tr=[]`。

TS、TP、TC 只能按状态文件中的计划顺序遍历。历史状态只用于复用当前计划内对象，不得触发计划外续跑。

对象开始前调用 `mark-in-progress`。MCP 返回后先将完整原始响应写入：

```text
archive/responses/<entity>_<safe-key>.json
```

然后使用 `--response-file` 调用 `record-success` 或 `record-failure`。禁止通过 `--response-json` 传递响应。每条状态命令都必须检查 `success`；真实父级 ID 未成功落盘时不得继续子节点。

## TR：只复用

直接使用状态中的 `tr.platform_id` 作为：

```text
create_ts.trId
create_tp.parentTrId
create_tc.tr_id
```

不得调用 `create_tr`，不得修改 TR 状态。TR-only 请求允许 TS/TP/TC 计划全部为空，本 Skill 完成 TR 校验后返回。

## TS：创建或复用

按 `execution_plan.ts` 顺序处理。TS 编号和来源只读取 `ts_catalog.json.items[]`。

- 状态已为 `succeeded` 且有有效 `platform_id`：直接复用；
- `source=platform_dfx`：校验 `platform_ts_id`，保存 catalog 条目作为响应，并以该 ID 记录成功；禁止调用 `create_ts`；
- `source=explore`：通过 `tr_ts_index` 精确读取 `tr_ts.json.test_specs[]` 并调用 `core_test_design_mcp.create_ts`；
- 其他来源：记录当前 TS 失败。

`create_ts` 参数映射：

```text
designTaskId       = design_task_id
trId               = tr.platform_id
tsName             = tsName/ts_name
tsType             = tsType/ts_type
creator            = creator
description        = description
resolveDescription = resolveDescription/resolve_description
sceneSelecteds     = 源值（存在时）
functionSelecteds  = 源值（存在时）
featureSelecteds   = 源值（存在时）
requirement_ids    = requirement_ids
```

可选字段不存在时传空值，不得编造。成功必须同时满足：

```text
result.success == true
result.data.tsId 为有效非零 ID
```

TS 失败时，将该 TS 下计划内 TP/TC 记录为 `blocked`，继续其他 TS 分支。

## TP：创建或复用

`execution_plan.tp` 为空时直接跳过，不得读取 `ts_*_tp.json`。通过 `TS_<NN>/<tp_id_temp>` 唯一定位 TP。

状态已为 `succeeded` 且有有效 `platform_id` 时直接复用。创建前要求所属 TS 成功且有真实 ID，否则记录 `blocked`。

原始 TP JSON 的 `tpSourceType` 必须是以下非空值之一：

- `功能交互设计-功能与测试因子`
- `基于业务内部实现设计—测试因子`
- `基于业务场景设计—场景因子`
- `测试类型交互设计—测试因子`
- `测试类型交互设计—测试设计准则`
- `测试类型交互设计—模式库`

非法时记录当前 TP 失败，不调用 `create_tp`，不得根据 `_dimension`、`tpType` 或 `_raw_factors` 猜测或修改输入。

`create_tp` 参数映射：

```text
designTaskId       = design_task_id
tsId               = 所属 TS 真实 tsId
parentTrId         = tr.platform_id
tpType             = TP JSON.tpType
tpSourceType       = TP JSON.tpSourceType
tpName             = TP JSON.tpName
creator            = TP JSON.creator；为空时使用上下文 creator
description        = TP JSON.description
resolveDescription = TP JSON.resolveDescription
requirement_ids    = TP JSON.requirement_ids
```

因子映射：

- `_raw_factors` 为空时不传因子名称；
- 场景因子或功能交互来源传 `sceneFactorNames`；
- 内部实现或测试类型测试因子来源传 `testFactorNames`；
- 测试设计准则或模式库不传因子名称；
- 同一组因子不得同时传给两个参数。

真实 TP ID 按以下顺序提取：

1. `result.data.tpId`；
2. `result.data.id`；
3. `result.data.resourceId`；
4. `result.data` 本身为有效数字或数字字符串。

即使 `success=true`，提取不到有效 TP ID 也记录失败并阻断其 TC。TP 失败时将所属计划内 TC 记录为 `blocked`。

## TC：创建或复用

`execution_plan.tc` 为空时直接跳过，不得读取 `ts_*_tc.json`。只有原始目标明确包含指定 TC 或全量 `TC` 时才允许执行。

通过 `TS_<NN>/<tc_id_temp>` 唯一定位 TC，并在同一 TS 下使用 `TS_<NN>/<tp_id_temp>` 查找真实 TP ID。

- `status=succeeded`：直接复用，即使没有 `platform_id`；
- 所属 TP 失败、blocked 或没有有效 ID：记录 TC 为 `blocked`；
- 其他状态：调用 `core_test_design_mcp.create_tc`。

必填参数映射：

```text
tp_id               = 所属 TP 真实 tpId
name                = TC JSON.name
case_id_prefix      = TC JSON.case_id_prefix
case_id_start_value = TC JSON.case_id_start_value
case_id_number      = TC JSON.case_id_number
auto_type           = TC JSON.auto_type
rank                = TC JSON.rank
creator             = TC JSON.creator；为空时使用上下文 creator
owner               = TC JSON.owner；为空时使用上下文 creator
preparation         = TC JSON.preparation
test_step           = TC JSON.test_step
expect_output       = TC JSON.expect_output
tr_id               = tr.platform_id
pbi                 = PBI
case_id             = TC JSON.case_id
```

`case_id_number` 只传数字后缀，`case_id` 保持完整原值。其他可选字段仅在源 JSON 存在时原值传递。

`result.success == true` 即记录 TC 成功，不提取、不校验、不要求 TC 平台 ID。只有 `success=false`、调用异常或无法判断成功时记录失败。

## 返回门禁

返回调用方前必须重新读取状态，并只针对本次计划核验：

- 所有 TS/TP/TC 均为 `succeeded`、`failed` 或 `blocked`；
- 不存在 `in_progress`；
- 成功 TS/TP 有有效 `platform_id`；
- 成功 TC 不要求 `platform_id`；
- 计划数量和状态数量一致。

若仍有非终态节点，先记录明确失败或 blocked；状态无法保存时报告对象阶段失败。最后按调用来源输出：

- `archive`：
  ```text
  对象归档阶段已结束；必须继续调用 coretest-document-sync，当前结果不是最终归档结果。
  ```
- `explore_ts_only`：
  ```text
  Explore TS-only 归档阶段已结束；不得调用文档同步或 Portal，返回各 TS 的终态和真实平台 ID。
  ```

## Guardrails

- 不并发创建存在父子依赖的对象；
- 不修改设计输入 JSON 或 `ts_catalog.json`；
- 不从源文件追加计划外对象；
- 不在内存中累计全部结果后一次性保存；
- 不重复创建已成功对象；
- 不调用 CoreTool 文档命令；
- 不调用 `coretest-document-sync` 或 `test-portal-card`；
- `explore_ts_only` 模式要求计划覆盖 catalog 全部 TS，且 `tr/tp/tc` 均为空；
- 不输出最终归档成功结论。
