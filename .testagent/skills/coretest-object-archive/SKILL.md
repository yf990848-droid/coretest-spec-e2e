---
name: coretest-object-archive
description: 串行执行已锁定的 CoreTest 对象计划，创建或复用 TS、TP、TC 并即时保存 archive_state.json；Explore TS-only 模式仅创建或复用普通 TS，不处理平台 DFX TS。
---

# CoreTest Object Archive

## 职责

严格执行 Archive Agent 或 Explore 已锁定并写入 `archive_state.json.request.execution_plan` 的对象归档计划：

```text
复用既有 TR → 创建或复用 TS → 创建或复用 TP → 创建或复用 TC
```

一次调用完成全部对象阶段。调用来源允许：

- `archive`：由 Archive Agent 执行完整对象计划；
- `explore_ts_only`：由 Explore 执行全部普通 TS 的 TS-only 计划，此时 `tr/tp/tc` 必须为空，且计划不得包含 `source=platform_dfx`。

禁止调用在线文档同步或 Portal Skill，禁止自行扩大计划。

## 必需输入

- 扩展包根目录；
- `tr_id`、`design_task_id`、PBI、`creator`；
- `tr_info.json`、`tr_ts.json`、`ts_catalog.json` 路径及内容；
- `test_design/` 路径；Explore TS-only 只记录该标准路径，不得读取其中产物；
- `archive/archive_state.json` 路径；
- 调用来源 `archive` 或 `explore_ts_only`；
- 仅当计划包含 TP/TC 时提供对应的 TP/TC JSON 和每个相关 TS 的
  `test_design/ts_<NN>_factor_plan.json`；TP 计划缺少因子计划时禁止创建 TP。

缺少当前计划实际需要的输入时停止对象阶段，不调用创建 CLI。TS-only 不得读取 TP/TC JSON。

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

对象开始前调用 `mark-in-progress`。TS/TC 的 CLI 脚本将命令、退出码、stdout/stderr 和确认结果保存为证据；每对象固定使用同一路径：

```text
archive/cli/<entity>_<safe-key>.json
```

TP 的证据路径继续使用 factor_archive.py 的返回值。然后使用 `--response-file` 调用 `record-success` 或 `record-failure`。禁止通过 `--response-json` 传递响应。每条状态命令都必须检查 `success`；真实父级 ID 未成功落盘时不得继续子节点。

## TR：只复用

直接使用状态中的 `tr.platform_id` 作为：

```text
ts --tr-id
tp --parent-tr-id
TC 的 TR 上下文仍由归档计划保存
```

不得调用 `create_tr`，不得修改 TR 状态。TR-only 请求允许 TS/TP/TC 计划全部为空，本 Skill 完成 TR 校验后返回。

## TS：创建或复用

按 `execution_plan.ts` 顺序处理。TS 编号和来源只读取 `ts_catalog.json.items[]`。

- 状态已为 `succeeded` 且有有效 `platform_id`：直接复用；
- `source=platform_dfx`：仅允许在 `archive` 调用来源中校验并复用 `platform_ts_id`；`explore_ts_only` 计划出现 DFX 时必须停止，禁止写入状态或调用 `create_ts`；
- `source=explore`：通过 `tr_ts_index` 精确读取 `tr_ts.json.test_specs[]` 并通过下述脚本调用 CLI `ts create-by-name`；
- 其他来源：记录当前 TS 失败。

先使用 `coretool-cli` Skill 确定 CLI 绝对路径。执行：

```bash
python "<root>/.testagent/skills/coretest-object-archive/scripts/object_cli.py" ts \
  --cli "<coretool_cmd>" --input-file "<tr_ts.json>" --ts-index <catalog.tr_ts_index> \
  --design-task-id <design_task_id> --tr-id <TR平台ID> --creator "<creator>" \
  --response-file "<archive/cli/ts_<safe-key>.json>"
```

脚本保持 `tsName/ts_name`、`tsType/ts_type`、description、resolveDescription/resolve_description；
将 sceneSelecteds/functionSelecteds/featureSelecteds 映射为 --scene-names/--function-names/--feature-names，
requirement_ids 映射为 --requirement-ids。缺少可选字段时不编造关联。
检查退出码为 0、`success=true` 和有效 `id`，使用该 ID 调用
`archive_state.py record-success --state-file <archive_state.json> --entity ts --key <TS_NN> --parent-key TR --parent-id <TR平台ID> --platform-id <id> --response-file <绝对证据路径>`。
失败时记录失败。不要使用 `ts get` 中空白的关系概要字段推断关系不存在。

TS 失败时，将该 TS 下计划内 TP/TC 记录为 `blocked`，继续其他 TS 分支。

### TS 因子（仅正式 Archive）

TS 成功创建或从状态复用后，若当前 TS 存在已完成的 TP JSON 和因子计划，
即使 TS 对象状态已为 `succeeded`，也必须执行因子同步。`explore_ts_only`
禁止读取设计产物和同步因子。尚未 Design 的 TS-only 归档可以先保存 TS ID，
待 Design 完成后在正式 Archive 补做因子同步。

使用 `coretool-cli` Skill 确定当前可用 CLI 的绝对路径，固定调用：

```bash
python "<root>/.testagent/skills/coretest-archive/scripts/factor_archive.py" sync-ts \
  --cli "<coretool-cli绝对路径>" --state-file "<archive_state.json>" \
  --plan-file "<test_design/ts_<NN>_factor_plan.json>" \
  --tp-file "<test_design/ts_<NN>_tp.json>" \
  --ts-key TS_<NN> --ts-type "<catalog.ts_type>" \
  --ts-id <真实tsId> --pbi <PBI>
```

脚本逐因子查询已有关系、必要时调用 CLI `asset factor create` 或
`asset scene-factor create`，随后查询确认。每个因子的请求、响应和独立终态
即时保存到 `archive_state.json.factor`；单个因子失败不阻断 TP/TC，最终汇总
必须逐项检查 `results[].status` 并报告失败的因子。脚本的 `success=true`
只表示批次执行结束，不表示全部因子成功。TS 的 `succeeded` 对象状态不能
代替因子状态。

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

新建 TP 时调用固定脚本，以参数数组执行 CLI `tp create --relations`：

```bash
python "<root>/.testagent/skills/coretest-archive/scripts/factor_archive.py" create-tp \
  --cli "<coretool-cli绝对路径>" --state-file "<archive_state.json>" \
  --plan-file "<test_design/ts_<NN>_factor_plan.json>" \
  --tp-file "<test_design/ts_<NN>_tp.json>" --ts-key TS_<NN> \
  --ts-type "<catalog.ts_type>" --ts-id <真实tsId> --pbi <PBI> \
  --tr-id <TR平台ID> --creator "<creator>" --idp-doc-id "<IDP文档ID>" \
  --tr-info-file "<tr_info.json>" --tp-id-temp "<tp_id_temp>"
```

脚本校验因子计划，保持 TP JSON 的 `tpType`、名称、描述、需求关联，
只在 CLI 调用边界把中文 `tpSourceType` 转成 CLI 枚举；`testFactorIdList`
使用因子 UUID（`test_factor_id`），`sceneFactorIdList` 使用场景因子编码。
禁止使用 TS 因子关系的数字 `id`，禁止回退到按名称推断因子。
脚本返回 `id`、`request_file`、`response_file`；先检查 `success=true` 和
有效非零 ID，再按原流程通过 `archive_state.py record-success --entity tp`
保存平台 ID 与原始响应。脚本返回的文件路径相对于 `archive/`，调用
`record-success/record-failure --response-file` 时先拼成绝对路径。返回失败时
用 `record-failure` 保存错误，所属 TC
保持原有 blocked 语义。已有成功 TP 直接复用，不补录旧 TP 因子。

真实 TP ID 按以下顺序提取：

1. 新 CLI 脚本输出的 `id`；
2. 历史已成功状态的 `platform_id`（仅复用，不再次创建）。

即使 `success=true`，提取不到有效 TP ID 也记录失败并阻断其 TC。TP 失败时将所属计划内 TC 记录为 `blocked`。

## TC：创建或复用

`execution_plan.tc` 为空时直接跳过，不得读取 `ts_*_tc.json`。只有原始目标明确包含指定 TC 或全量 `TC` 时才允许执行。

通过 `TS_<NN>/<tc_id_temp>` 唯一定位 TC，并在同一 TS 下使用 `TS_<NN>/<tp_id_temp>` 查找真实 TP ID。

TC 标识必须分开使用：入口允许唯一匹配的 `case_id`，但匹配后立即转换为 JSON 的 `tc_id_temp`。例如 `case_id=PCF_CLI_MIG_01_01` 对应 `tc_id_temp=TC.11.01` 时，执行计划和状态 key 均为 `TS_11/TC.11.01`，父 TP key 为 `TS_11/TP.11.01.01`。禁止把 case_id 或三级路径 `TS_11/TP.11.01.01/PCF_CLI_MIG_01_01` 写入 execution_plan.tc 或 TC 状态 key；case_id 只用于平台用例编号，不改写其值。

每条 TC 按同一标准 key 查询状态；已成功则复用，否则先 mark-in-progress，再调用 object_cli.py，最后用同一 key record-success/record-failure。`--tc-id-temp` 必须传 JSON 的 `TC.11.01`，不能传平台 case_id。发现锁定计划使用错误标识时返回计划错误，不得为迁就错误计划继续创建或保存非标准 key。

- `status=succeeded`：直接复用，即使没有 `platform_id`；
- 所属 TP 失败、blocked 或没有有效 ID：记录 TC 为 `blocked`；
- 其他状态：使用下述脚本调用 CLI `tc create`，保持完整 `case_id`。

```bash
python "<root>/.testagent/skills/coretest-object-archive/scripts/object_cli.py" tc \
  --cli "<coretool_cmd>" --input-file "<test_design/ts_<NN>_tc.json>" \
  --tc-id-temp "<tc_id_temp>" --tp-id <所属TP真实ID> --pbi <PBI> \
  --creator "<上下文creator>" --response-file "<archive/cli/tc_<safe-key>.json>"
```

safe-key 必须含 TS 编号及对象临时 ID，替换路径分隔符，避免不同 TS 的 TC.01 共用证据。
脚本以参数数组调用 CLI，不拼接 Shell 命令；从原 JSON 精确选择 TC，映射：

| JSON | CLI |
|---|---|
| case_id | --case-id，原值保留全部数字段及前导零 |
| preparation | --precondition |
| test_step / expect_output | --test-step / --expected-output |
| creator / owner | --creator / --owner；为空时分别使用上下文 creator |
| auto_type / rank | --auto-type / --rank，保持 0 值 |
| test_case_type / test_case_activity | --test-type / --test-activity |
| test_environment_id / test_environment_type | --test-env-id / --test-env-type |

其余原有 snake_case 可选参数按对应 flag 传递；status 固定 notArchived，case_id_type 默认 input_begin。
不使用旧 case_id_prefix/start_value/number 重新拼装编号，不把卡片列 TestType、AutoType、envtype、DesignNote 改写为归档字段。

CLI 的空 `message` 不代表失败。脚本创建前后使用 `tc list --tp-id` 查询，按完整 case_id 唯一匹配并核对名称、PBI、owner、rank、auto_type、status。
仅退出码为 0、`success=true` 且有有效 `id` 时，使用 `record-success --state-file <archive_state.json> --entity tc --key <TS_NN/tc_id_temp> --parent-key <TS_NN/tp_id_temp> --parent-id <TP平台ID> --platform-id <id> --response-file <绝对证据路径>` 保存本次新对象。
历史 succeeded TC 仍允许没有平台 ID，并按原规则复用。

脚本在写入平台前独占保存 `.request.json`，相同对象重试只能确认已创建结果，不能盲目重复创建。
若结果不确定、同编号冲突或读回不一致，记录失败，保留证据并人工核查平台与状态；不得删除证据后自动重试。
脚本输入校验失败可能没有响应文件，此时使用 `record-failure --error` 保存脚本错误，不伪造成功响应。

当前标准 TC JSON 没有因子关联字段；TS 因子与 TP 因子关联保持现有流程。
如自定义 TC 带非空 action_factor_names/data_factor_names 或结构化因子，脚本明确失败，禁止静默丢弃；
需 CLI 支持“完整 case_id + 因子关联”并验证后再扩展，不以 create-by-name 重组编号替代。

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
  Explore TS-only 归档阶段已结束；不得调用文档同步或 Portal，返回各普通 TS 的终态和真实平台 ID，并报告未归档的 DFX 数量。
  ```

## Guardrails

- 不并发创建存在父子依赖的对象；
- 不修改设计输入 JSON 或 `ts_catalog.json`；
- 不从源文件追加计划外对象；
- 不在内存中累计全部结果后一次性保存；
- 不重复创建已成功对象；
- 不调用 CoreTool 文档命令；
- 不调用 `coretest-document-sync` 或 `test-portal-card`；
- `explore_ts_only` 模式要求计划按 catalog 顺序覆盖全部且仅覆盖 `source=explore` 的普通 TS，`tr/tp/tc` 均为空，DFX 不得进入计划；
- 不输出最终归档成功结论。
