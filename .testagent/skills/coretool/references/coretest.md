# CoreTest 领域参考

CoreTest 是华为 CoreTool 的测试执行领域，支持 InFactory、Script、Pipeline、TestResult、LCM、TestDesign、Common 七大平台。

所有命令统一使用 `coretool coretest` 调用，通过 Bash 工具执行。所有查询命令支持 `--output table|json` 控制输出格式。

## 平台总览

| 平台 | 说明 |
|------|------|
| `coretool coretest infactory` | InFactory 任务、环境、Runner 管理 |
| `coretool coretest script` | Script 执行器、用例、日志管理 |
| `coretool coretest pipeline` | Pipeline 用例筛选、导入、运行、状态查询 |
| `coretool coretest testresult` | 测试结果、AI 分析、日志、历史、重执行、DTS提单、环境修复 |
| `coretool coretest lcm` | LCM 环境查询、锁定、解锁 |
| `coretool coretest testdesign` | 测试设计（组合、资产、任务、TR/TS/TP/TC） |
| `coretool coretest common` | 通用查询（版本PBI、CIDA配置） |

---

## InFactory 平台

### 任务管理（task）

#### 创建 InFactory 任务

参数按页面分为 4 类 JSON 传入，`--basic-info` 必填，其余可选。

```bash
coretool coretest infactory task create --basic-info '<基础信息JSON>' [--case-filter '<入厂用例筛选JSON>'] [--mr-config '<创建MR JSON>'] [--script-refresh '<自定义刷新脚本字段JSON>']
```

**--basic-info（基础信息，必填）**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `inFactoryTaskName` | string | 是 | 任务名称 |
| `productLineName` | string | 是 | 产品线名称 |
| `projectName` | string | 是 | 项目名称 |
| `codehubHttpAddress` | string | 是 | 代码仓HTTP地址 |
| `sourceCodehubBranchName` | string | 是 | 源分支名 |
| `destCodehubBranchName` | string | 是 | 目标分支名 |
| `groupId` | string | 否 | 用户所在组ID |
| `creator` | string | 否 | 创建人（默认从登录用户取） |
| `cVersionName` | string | 否 | C版本名称 |
| `bVersionName` | string | 否 | B版本名称 |
| `factoryType` | string | 否 | 入场类型（如 Hutaf） |
| `executorType` | string | 否 | 执行器类型（如 CLOUD_SPIDER） |
| `isAuto` | string | 否 | 是否自动（`"1"`=自动，`"0"`=手动，默认`"1"`） |
| `envVersion` | string | 否 | 环境版本 |
| `topoName` | string | 否 | 网络拓扑名称 |
| `sourceCodehubCheckBranchName` | string | 否 | 源分支检查分支名 |
| `sourceCodehubMrBranchName` | string | 否 | 源分支MR分支名 |

**--case-filter（入厂用例筛选，可选）**

| 字段 | 类型 | 说明 |
|------|------|------|
| `envList` | string | 环境列表JSON字符串（如 `"[]"`） |
| `tepList` | string | 执行器列表JSON字符串 |
| `policyName` | string | 策略名称（如 `"只入厂"`） |
| `assuranceCaseIds` | string | 保障用例ID |
| `fileNames` | array | 入厂用例文件列表 |

`fileNames` 每项字段：`id`（序号）、`fileName`（文件名）、`caseNumber`（用例编号）、`isConfig`（0=用例，1=配置）

**--mr-config（创建MR，可选）**

| 字段 | 类型 | 说明 |
|------|------|------|
| `templateName` | string | MR模板名称（如 `"test_finish"`） |
| `mrTitle` | string | MR标题 |
| `templateDesc` | string | MR描述/模板说明 |
| `isNeedVerifyBeforeMergeIntoMaster` | int | MR合入前是否检查（0=否，1=是） |
| `merger` | string[] | 合并人列表 |
| `reviewer` | string[] | 审核人列表 |
| `committer` | string[] | 检视人列表 |
| `approvers` | string[] | 批准人列表 |
| `mrRelationNumber` | string | E2E关联编号 |

**--script-refresh（自定义刷新脚本字段，可选）**

| 字段 | 类型 | 说明 |
|------|------|------|
| `killerScriptConfigBeforeId` | int | 入场前killer脚本配置ID |
| `killerScriptConfigAfterId` | int | 入场后killer脚本配置ID |
| `customParams` | string | 自定义参数JSON字符串 |
| `customFieldInfo` | string | 自定义字段配置JSON字符串 |
| `deployTemplateId` | string | 部署模板ID |

```bash
# 示例：完整4类参数
coretool coretest infactory task create \
  --basic-info '{"inFactoryTaskName":"task_test_20260818","productLineName":"CSP","projectName":"CSP 26.1.0","codehubHttpAddress":"https://codehub-dg-y.huawei.com/CSPAutoTest/AITestForCSP.git","sourceCodehubBranchName":"personal/w00455952/master","destCodehubBranchName":"personal/w00455952/master_ruchang","cVersionName":"CSP 26.1.0","bVersionName":"CSP 26.1.0_用例预入场","factoryType":"Hutaf","executorType":"CLOUD_SPIDER","isAuto":"0","groupId":"1052","creator":"r30073095"}' \
  --case-filter '{"envList":"[]","tepList":"[{\"id\":\"3085993856910165504\",\"type\":\"CLOUD_SPIDER\",\"name\":\"10.44.175.156:8090\",\"version\":\"1.1.57\",\"status\":\"idle\",\"network\":\"yellow\"}]","policyName":"只入厂","fileNames":[{"id":"","fileName":"test_TC_CSP_ALM_MML_024.py","caseNumber":"test_TC_CSP_ALM_MML_024","isConfig":0}]}' \
  --mr-config '{"templateName":"test_finish","mrTitle":"task_test_20260818","templateDesc":"1. test finish","isNeedVerifyBeforeMergeIntoMaster":1,"merger":[],"reviewer":[],"committer":[],"approvers":[]}' \
  --script-refresh '{"killerScriptConfigBeforeId":42,"killerScriptConfigAfterId":45,"customParams":"{\"configPath\":\"/home/executor/JavaEnvCfg\",\"packageName\":\"TestforCSPDFPPython-22.1.0.tar\",\"serviceName\":\"TestforCSPDFPPython\",\"version\":\"22.1.0\",\"product\":\"csp\",\"executorType\":\"CLOUD_SPIDER\",\"purePython\":\"true\",\"customCmd\":\"pytest -v\"}","customFieldInfo":"[{\"fieldName\":\"\",\"tmssFieldValue\":\"\",\"fieldNameOptions\":[],\"tmssFieldValueOptions\":[]}]"}'

# 示例：仅基础信息（最少参数）
coretool coretest infactory task create \
  --basic-info '{"inFactoryTaskName":"构建验证","productLineName":"Cloud","projectName":"CoreTool","codehubHttpAddress":"https://codehub.huawei.com/CoreTool.git","sourceCodehubBranchName":"feature/test","destCodehubBranchName":"master"}'
```

#### 查询任务列表

```bash
coretool coretest infactory task list --group-id <组ID> [--creator <工号>] [--id <任务ID>] [--result <结果>]
# 示例
coretool coretest infactory task list --group-id 1052
coretool coretest infactory task list --group-id 1052 --creator w30020094
```

`--group-id` 为 int64 类型（必填）。支持分页：`--page`（默认1）、`--page-size`（默认10）。

输出字段：`id`、`name`、`creator`、`source_branch`、`dest_branch`、`state`、`create_time`、`exec_task_ids`（JSON数组，用于 retry 的 `inFactoryExecTaskId`）。

#### 刷新任务状态

```bash
coretool coretest infactory task refresh <task-id> --scope <status|detail>
# 示例：刷新状态
coretool coretest infactory task refresh 35324 --scope status
# 示例：刷新详情（需指定 group-id）
coretool coretest infactory task refresh 35324 --scope detail --group-id 1052
```

#### 重试失败任务

参数按页面分为 4 类 JSON 传入，与 create 格式一致。`--basic-info` 必填（须包含 `inFactoryTaskId` 和 `inFactoryExecTaskId`），其余可选。

```bash
coretool coretest infactory task retry --basic-info '<基础信息JSON>' [--case-filter '<入厂用例筛选JSON>'] [--mr-config '<创建MR JSON>'] [--script-refresh '<自定义刷新脚本字段JSON>']
```

**--basic-info（基础信息，必填）**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `inFactoryTaskId` | int | 是 | 入场任务ID（从 task list 的 id 字段获取） |
| `inFactoryExecTaskId` | int | 是 | 入场执行任务ID（从 task list 的 exec_task_ids 字段获取） |
| `productLineName` | string | 否 | 产品线名称 |
| `projectName` | string | 否 | 项目名称 |
| `codehubHttpAddress` | string | 否 | 代码仓HTTP地址 |
| `sourceCodehubBranchName` | string | 否 | 源分支名 |
| `destCodehubBranchName` | string | 否 | 目标分支名 |
| `reRunExecTaskId` | int | 否 | 重跑时关联的原执行任务ID |

其余字段同 create 的 `--basic-info`、`--case-filter`、`--mr-config`、`--script-refresh`。

```bash
# 示例：重试任务（最少参数）
coretool coretest infactory task retry \
  --basic-info '{"inFactoryTaskId":35324,"inFactoryExecTaskId":50938}'

# 示例：重试任务（带完整4类参数，同 create 格式）
coretool coretest infactory task retry \
  --basic-info '{"inFactoryTaskId":35324,"inFactoryExecTaskId":50938,"inFactoryTaskName":"task_test_20260818","productLineName":"CSP","projectName":"CSP 26.1.0","codehubHttpAddress":"https://codehub-dg-y.huawei.com/CSPAutoTest/AITestForCSP.git","sourceCodehubBranchName":"personal/w00455952/master","destCodehubBranchName":"personal/w00455952/master_ruchang","cVersionName":"CSP 26.1.0","bVersionName":"CSP 26.1.0_用例预入场","factoryType":"Hutaf","executorType":"CLOUD_SPIDER","isAuto":"0","groupId":"1052","creator":"r30073095"}' \
  --case-filter '{"envList":"[]","tepList":"[{\"id\":\"3085993856910165504\",\"type\":\"CLOUD_SPIDER\",\"name\":\"10.44.175.156:8090\",\"version\":\"1.1.57\",\"status\":\"idle\",\"network\":\"yellow\"}]","policyName":"只入厂","fileNames":[{"id":"","fileName":"test_TC_CSP_ALM_MML_024.py","caseNumber":"test_TC_CSP_ALM_MML_024","isConfig":0}]}' \
  --mr-config '{"templateName":"test_finish","mrTitle":"task_test_20260818","templateDesc":"1. test finish","isNeedVerifyBeforeMergeIntoMaster":1,"merger":[],"reviewer":[],"committer":[],"approvers":[]}' \
  --script-refresh '{"killerScriptConfigBeforeId":42,"killerScriptConfigAfterId":45,"customParams":"{\"configPath\":\"/home/executor/JavaEnvCfg\",\"packageName\":\"TestforCSPDFPPython-22.1.0.tar\",\"serviceName\":\"TestforCSPDFPPython\",\"version\":\"22.1.0\",\"product\":\"csp\",\"executorType\":\"CLOUD_SPIDER\",\"purePython\":\"true\",\"customCmd\":\"pytest -v\"}","customFieldInfo":"[{\"fieldName\":\"\",\"tmssFieldValue\":\"\",\"fieldNameOptions\":[],\"tmssFieldValueOptions\":[]}]"}'
```

> **提示**：`inFactoryTaskId` 对应 task list 输出的 `id` 字段，`inFactoryExecTaskId` 对应 task list 输出的 `exec_task_ids` 字段（JSON 数组，取第一个值即可）。

### 环境管理（environment）

#### 查询可用环境

```bash
coretool coretest infactory environment list --project <项目> --product-line <产品线> --group-id <组ID>
# 示例
coretool coretest infactory environment list --project "CSP 23.1.0" --product-line CSP --group-id 1052
coretool coretest infactory environment list --project "CSP 23.1.0" --product-line CSP --group-id 1052 --status available
```

必填：`--project`、`--product-line`、`--group-id`（int）。可选筛选：`--name`、`--version`、`--status`。分页：`--page`（默认1）、`--page-size`（默认10）。

### Runner 管理（runner）

#### 查询可用 Runner

```bash
coretool coretest infactory runner list --project <项目> --product-line <产品线> --group-id <组ID>
# 示例
coretool coretest infactory runner list --project "CSP 23.1.0" --product-line CSP --group-id 1052
coretool coretest infactory runner list --project "CSP 23.1.0" --product-line CSP --group-id 1052 --status idle --type CLOUD_SPIDER
coretool coretest infactory runner list --project "CSP 23.1.0" --product-line CSP --group-id 1052 --page 2 --page-size 20
```

必填：`--project`、`--product-line`、`--group-id`（int）。可选筛选：`--network`（可多次）、`--type`（可多次）、`--status`（可多次）、`--version`、`--location`、`--ip`。分页：`--page`（默认1）、`--page-size`（默认10）。

---

## Script 平台

### 执行器管理（script executor）

#### 查询执行器连接信息

```bash
coretool coretest script executor list [--user-id <工号>] [--name <环境名>]
# 示例：默认查当前登录用户名下的执行器
coretool coretest script executor list
# 示例：指定用户
coretool coretest script executor list --user-id w30020094
```

不传 `--user-id` 时自动从登录信息填充当前工号。`--name` 默认为空（返回用户默认执行器配置）。

### 用例执行（script case）

#### 远程运行测试用例

```bash
coretool coretest script case run --file <用例文件路径>
# 示例：通过后端查询执行器（默认）
coretool coretest script case run --file tests/test_login.py
# 示例：指定后端查询参数
coretool coretest script case run --file tests/test_login.py --user-id w30020094 --env-name env01 --version-branch branch_new
# 示例：直传执行器信息（跳过后端查询）
coretool coretest script case run --file tests/test_login.py \
  --executor-ip 10.90.120.56 --ssh-user root --ssh-password 'xxxx'
```

必填：`--file`（`-f`）。

**后端查询模式**（不传 `--executor-ip` 时）：从后端 API 查询执行器连接信息。可选：`--context`（`-c`）、`--env-name`（默认空）、`--user-id`（默认当前登录工号）、`--version-branch`（`branch_old` 或 `branch_new`，默认 `branch_old`）。

**直传模式**（传 `--executor-ip` 时）：跳过后端查询，直接使用命令行提供的连接信息。参数：`--executor-ip`（必填）、`--ssh-user`（默认 `root`）、`--ssh-port`（默认 `22`）、`--ssh-password`、`--case-root`（默认 `/tmp`）、`--execute-mode`（默认 `CloudSpider`）。

### 日志管理（script log）

#### 从日志提取元数据

```bash
coretool coretest script log extract-metadata --content <日志内容>
# 示例：直接传内容
coretool coretest script log extract-metadata --content "data:{'caseId': 'TC001', 'startTime': 1704067200, 'endTime': 1704153600}"
# 示例：从文件读取
coretool coretest script log extract-metadata --content-file /tmp/test.log
```

`--content` 和 `--content-file` 二选一。从日志中正则提取 `caseId`、`startTime`、`endTime`，并查询后端关联 `groupId` 和 `testResultId`。

---

## Pipeline 平台

### 用例管理（pipeline case）

#### 按条件筛选用例

```bash
coretool coretest pipeline case filter --condition <JSON条件>
# 示例
coretool coretest pipeline case filter --condition '{"field":"priority","op":"eq","value":"P0"}' --scope-paths /project/module
```

也可用 `--condition-file <文件路径>`。可选：`--scope-paths`（可多次）、`--type`（默认 `TestCase`）、`--current-children`、`--need-short-uri`

#### 按条件导入用例到目标版本

```bash
coretool coretest pipeline case import --source-path <源版本路径> --dest-path <目标路径> --condition <JSON条件>
# 示例
coretool coretest pipeline case import --source-path /v1/modules --dest-path /v2/modules --condition '{"field":"priority","op":"eq","value":"P0"}'
```

必填：`--source-path`、`--dest-path`。也可用 `--condition-file`。可选：`--scope-paths`

### Pipeline 操作（pipeline operation）

#### 查询操作执行结果

```bash
coretool coretest pipeline operation get --operation-uri <操作URI>
# 示例
coretool coretest pipeline operation get --operation-uri /operations/import-20260817-001
```

### Pipeline 运行（pipeline run）

#### 创建并触发 Pipeline

```bash
coretool coretest pipeline run --c-version-uri <C版本URI> --c-version-name <C版本名> --b-version-uri <B版本URI> --b-version-name <B版本名>
# 示例
coretool coretest pipeline run --c-version-uri /versions/c-v1.0 --c-version-name "C v1.0" --b-version-uri /versions/b-v1.0 --b-version-name "B v1.0" --is-parallel true --pipeline-param '{"pipelineId":1,"caseId":"TC001"}'
```

必填：`--c-version-uri`、`--c-version-name`、`--b-version-uri`、`--b-version-name`。`--is-parallel` 默认 `true`。`--pipeline-param` 可多次指定，或用 `--pipeline-param-file <文件路径>`。

### Pipeline 状态（pipeline status）

#### 查询 Pipeline 执行步骤状态

```bash
coretool coretest pipeline status --pipeline-id <ID1> [--pipeline-id <ID2>]
# 示例
coretool coretest pipeline status --pipeline-id 1 --pipeline-id 2 --latest-record true
```

`--pipeline-id` 为 int64Slice（必填，可多次指定）。可选 `--latest-record`。

---

## TestResult 平台

### AI 分析（testresult analysis）

#### 获取失败用例的 RAG 检索结果

```bash
coretool coretest testresult analysis get --test-result-id <结果ID>
# 示例
coretool coretest testresult analysis get --test-result-id 334463562
coretool coretest testresult analysis get --test-result-id 334463562 --with-dts-status
```

`--test-result-id`（`-t`）为 int 类型（必填）。可选 `--with-dts-status`。

#### 回填 AI 分析结论到 CTR

```bash
coretool coretest testresult analysis update --test-result-id <结果ID> --big-type <大类> --sub-type <子类> --analyse-state <状态>
# 示例
coretool coretest testresult analysis update --test-result-id 334463562 --big-type "脚本问题" --sub-type "脚本问题" --analysis-desc "脚本检查点不正确" --analyse-state 2 --modify-type AI_FILL
# 示例：指定分析人
coretool coretest testresult analysis update --test-result-id 334463562 --big-type "脚本问题" --sub-type "脚本问题" --analysis-desc "脚本检查点不正确" --analyse-state 2 --analyst w30020094
```

`--test-result-id`（`-t`）为 int 类型（必填）。可选参数：`--big-type`、`--sub-type`、`--dts-number`、`--issue-url`、`--analysis-desc`、`--analyse-state`（0=未开始，1=进行中，2=已完成）、`--change-state`、`--change-details`、`--is-determine-case`（`1`=是，`2`=否）、`--modify-type`（`AI_FILL`、`AI_BATCH`、`一键确认`）、`--analyst`（分析人，不传则默认当前登录用户）。`source` 字段自动填充为 `CLI`。

### 日志分析（testresult log-analysis）

#### 获取失败用例的 AI 日志清洗结果

```bash
coretool coretest testresult log-analysis get --test-result-id <结果ID>
# 示例
coretool coretest testresult log-analysis get --test-result-id 334463562
```

`--test-result-id`（`-t`）为 int 类型（必填）。

### 日志下载（testresult log）

#### 下载测试用例日志

```bash
coretool coretest testresult log download --test-result-id <结果ID>
# 示例
coretool coretest testresult log download --test-result-id 334463562
```

`--test-result-id`（`-t`）为 int 类型（必填）。

### 历史结果（testresult history）

#### 查询用例的历史执行结果

```bash
coretool coretest testresult history list --case-id <用例ID>
# 示例
coretool coretest testresult history list --case-id TC_UPF_VVIP_QOSEXP_FUNC_240809_00001 --is-last
# 示例：按任务ID过滤
coretool coretest testresult history list --case-id TC_UPF_VVIP_QOSEXP_FUNC_240809_00001 --task-id 1042
```

`--case-id`（`-c`）为 string 类型（必填）。可选筛选：`--case-result`（可多次）、`--start-time`、`--end-time`（ms 时间戳）、`--executor-ip`、`--product-version`、`--dts-number`、`--c-version`、`--analyse-state`（0/1/2/99，默认99=all）、`--task-id`（任务ID过滤）。支持分页。

JSON 输出中额外包含 AI 分析字段（有值时才显示）：`is_determine_case`（是否确定性问题）、`intelligent_big_type_desc`（AI大类描述）、`intelligent_sub_type_desc`（AI子类描述）、`confidence`（置信度）。

### 最近成功（testresult latest-success）

#### 获取失败用例最后一次成功执行的信息

```bash
coretool coretest testresult latest-success get --test-result-id <结果ID>
# 示例
coretool coretest testresult latest-success get --test-result-id 334463562
coretool coretest testresult latest-success get --test-result-id 334463562 --c-version "UDG 27.0.RC1.3.B006"
```

`--test-result-id`（`-t`）为 int 类型（必填）。可选 `--c-version`（省略时自动检测）。

### 失败重执行（testresult rerun）

#### 重执行失败用例

```bash
coretool coretest testresult rerun --test-result-id <结果ID>
# 示例：自动查找执行器重执行
coretool coretest testresult rerun --test-result-id 334463562
# 示例：指定执行器
coretool coretest testresult rerun --test-result-id 334463562 --executor-ip 10.113.175.208
# 示例：指定操作者
coretool coretest testresult rerun --test-result-id 334463562 --user-id w30020094
```

`--test-result-id`（`-t`）为 int 类型（必填）。可选 `--executor-ip`（`-e`，默认自动查找原始失败环境）、`--user-id`（`-u`，默认当前登录用户）。

### DTS-GPT 提单（testresult dts-gpt-ticket）

#### 为失败用例创建 DTS-GPT 问题单

```bash
coretool coretest testresult dts-gpt-ticket --test-result-id <结果ID> --brief-desc <简要描述>
# 示例
coretool coretest testresult dts-gpt-ticket --test-result-id 334463562 --brief-desc "脚本检查点不正确导致用例失败"
# 示例：简化版问题单
coretool coretest testresult dts-gpt-ticket --test-result-id 334463562 --brief-desc "脚本检查点不正确" --simplified
```

`--test-result-id`（`-t`）为 int 类型（必填），`--brief-desc`（`-d`）为 string 类型（必填）。可选 `--simplified`。

### 环境修复（testresult env-repair）

#### 检测并修复环境配置残留

```bash
coretool coretest testresult env-repair --executor-ip <IP> --group-id <群组ID>
# 示例：修复单个执行器
coretool coretest testresult env-repair --executor-ip 10.113.175.208 --group-id 1042
# 示例：修复多个执行器
coretool coretest testresult env-repair --executor-ip 10.113.175.208 --executor-ip 10.113.162.67 --group-id 1042
# 示例：关联测试结果ID
coretool coretest testresult env-repair --executor-ip 10.113.175.208 --group-id 1042 --test-result-id 334463562
```

`--executor-ip`（`-e`）可多次指定（必填），`--group-id`（`-g`）为 int 类型（必填）。可选 `--test-result-id`（`-t`，int64Slice，可多次）、`--user-id`（`-u`，默认当前登录用户）。

---

## LCM 平台

### 环境查询（lcm environment）

#### 查询个人 LCM 环境

```bash
coretool coretest lcm environment list --scope personal --test-result-id <结果ID>
# 示例
coretool coretest lcm environment list --scope personal --test-result-id 334801349
```

`--scope personal` 时 `--test-result-id` 为 int 类型（必填）。可选筛选：`--name`、`--version`、`--status`。支持分页。`user` 字段自动从当前登录用户填充，无需手动指定。

#### 查询公共 LCM 环境

```bash
coretool coretest lcm environment list --scope public --lcm-server <服务器URL> --group-id <群组ID>
# 示例
coretool coretest lcm environment list --scope public --lcm-server https://autofac-ccn.lcm.huawei.com/factory --group-id 1042
```

`--scope public` 时 `--lcm-server` 和 `--group-id`（int）均必填。`--lcm-server` 传原始 URL 即可（适配器内部自动编码）。可选筛选：`--name`、`--version`、`--status`。支持分页。

### 环境锁定/解锁（lcm lock/unlock）

#### 锁定 LCM 环境

```bash
coretool coretest lcm lock --executor-ip <执行器IP>
# 示例
coretool coretest lcm lock --executor-ip 10.113.175.184
```

`--executor-ip`（`-e`）为 string 类型（必填）。

#### 解锁 LCM 环境

```bash
coretool coretest lcm unlock --executor-ip <执行器IP>
# 示例
coretool coretest lcm unlock --executor-ip 10.113.175.184
```

`--executor-ip`（`-e`）为 string 类型（必填）。

---

## TestDesign 平台

TestDesign 是 CoreTest 的测试设计平台，支持资产库查询、设计工作流（TR→TS→TP→TC）等功能。

### 资产库（testdesign asset）

#### 查询版本关联的资产库配置

```bash
coretool coretest testdesign asset list --version-pbi <版本PBI>
# 示例
coretool coretest testdesign asset list --version-pbi 266926538 --type all
```

`--type`：`scene`=场景库，`feature`=特性库，`function`=功能库，`all`=全部（默认 all）。查询 `function` 时需加 `--user-id`。

#### 查询资产关系

```bash
coretool coretest testdesign asset relation list --alm-id <ALM ID> --category <关系类别>
# 示例
coretool coretest testdesign asset relation list --alm-id 1200734448940248896 --category feature
```

`--alm-id` 和 `--category` 均为 stringArray（必填，可多次指定）。

#### 查询 TR 关联的场景

```bash
coretool coretest testdesign asset scene list --tr-id <TR ID>
# 示例
coretool coretest testdesign asset scene list --tr-id 3611
```

`--tr-id` 为 int 类型（必填）。

#### 查询 TR 关联的特性

```bash
coretool coretest testdesign asset feature list --pbi <版本PBI> --tr-id <TR ID>
# 示例
coretool coretest testdesign asset feature list --pbi 266926538 --tr-id 3611
```

`--pbi` 为 string 类型（必填），`--tr-id` 为 int 类型（必填）。

#### 查询 TR 关联的功能

```bash
coretool coretest testdesign asset function list --tr-id <TR ID>
# 示例
coretool coretest testdesign asset function list --tr-id 3611
```

`--tr-id` 为 int 类型（必填）。

#### 查询 TS 关联的测试因子

```bash
coretool coretest testdesign asset factor list --ts-id <TS ID>
# 示例
coretool coretest testdesign asset factor list --ts-id 35792
```

`--ts-id` 为 int 类型（必填）。

#### 添加测试因子关系到 TS

```bash
coretool coretest testdesign asset factor create --ts-id <TS ID> --pbi <版本PBI> --factor-type <因子类型> --asso-act-type <关联活动类型> --factor '<因子JSON数组>'
# 示例
coretool coretest testdesign asset factor create --ts-id 35792 --pbi 266926538 --factor-type BusinessInterImplAnalysis --asso-act-type SceneAnalysis --factor '[{"factorCode":"TEST_001","factorName":"CLI测试因子"}]'
```

必填：`--ts-id`（int）、`--pbi`（string）、`--factor-type`（可选值：`TSFunctionInteractionAnalysis`、`BusinessInterImplAnalysis`、`TestTypeInteractionAnalysis`）、`--asso-act-type`（stringArray，可多次指定）。

因子数据：`--factor <JSON数组>` 或 `--factor-file <文件路径>`（二选一）。

因子项字段：`factorCode`（因子编号，映射为后端 `number`）、`factorName`（因子名称，映射为后端 `name`）。可选字段：`variableName`、`variableType`、`validValues`、`invalidValues`、`logicDescription`、`operation`、`precondition`、`expectedResult`、`modeNumber`、`source`、`description`。`testFactorId` 未提供时自动生成。

#### 查询 TS 关联的模型

```bash
coretool coretest testdesign asset model list --ts-id <TS ID> --activity-type <活动类型>
# 示例
coretool coretest testdesign asset model list --ts-id 35792 --activity-type SceneAnalysis
```

`--ts-id` 为 int 类型（必填），`--activity-type` 为 string 类型（必填，可选值：`RequirementAnalysis`、`SceneAnalysis`、`FeatureInteractionAnalysis`、`TRFunctionInteractionAnalysis`、`TSFunctionInteractionAnalysis`、`TestTypeInteractionAnalysis`、`TestFactorAnalysis`）。

#### 查询 TS 节点的测试设计原则

```bash
coretool coretest testdesign asset principle list --version-pbi <版本PBI> --tree-node-id <节点ID> --type <原则类型>
# 示例
coretool coretest testdesign asset principle list --version-pbi 266926538 --tree-node-id 35792 --type SceneAnalysis
```

必填：`--version-pbi`（string）、`--tree-node-id`（int）、`--type`（可选值同 model list `--activity-type`）。

#### 添加场景因子关系到 TS

```bash
coretool coretest testdesign asset scene-factor create --ts-id <TS ID> --pbi <版本PBI> --source-type <来源类型> --asso-act-type <关联活动类型> --scene-factor '<场景因子JSON数组>'
# 示例
coretool coretest testdesign asset scene-factor create --ts-id 35792 --pbi 266926538 --source-type scene --asso-act-type SceneAnalysis --scene-factor '[{"factorCode":"TEST_002","factorName":"CLI测试因子v2"}]'
```

必填：`--ts-id`（int）、`--pbi`（string）、`--source-type`（string）、`--asso-act-type`（string）。

因子数据：`--scene-factor <JSON数组>` 或 `--scene-factor-file <文件路径>`（二选一）。

场景因子项字段：`factorCode`（因子编号）、`factorName`（因子名称）。可选字段：`factorDesc`（描述）、`factorDataType`（数据类型）、`variableName`（变量名称）、`dataValidValue`（数据有效值）、`dataInvalidValue`（数据无效值）、`factorStatus`（状态）、`remark`（备注）、`parentCode`（父节点编号）。

### 设计任务（testdesign task）

#### 查询版本下的测试设计任务

```bash
coretool coretest testdesign task list --version-pbi <版本PBI>
# 示例
coretool coretest testdesign task list --version-pbi 266926538
```

### 测试需求 TR（testdesign tr）

#### 查询设计任务下的 TR 列表

```bash
coretool coretest testdesign tr list --design-task-id <设计任务ID>
# 示例
coretool coretest testdesign tr list --design-task-id 2342
```

`--design-task-id` 为 int 类型（必填）。

#### 创建测试需求 TR

```bash
coretool coretest testdesign tr create --version-pbi <版本PBI> --design-task-id <设计任务ID> --name <TR名称> --idp-doc-id <IDP文档ID> --resource-type <资源类型>
# 示例
coretool coretest testdesign tr create --version-pbi 266926538 --design-task-id 2342 --name "登录功能测试需求" --idp-doc-id 5dcdfe1e-9114-48c7-8abd-aa5222f6312f --resource-type featureLib
```

必填：`--version-pbi`（string）、`--design-task-id`（string）、`--name`（string）、`--idp-doc-id`（string，从 `task list` 返回的 `idp_doc_id` 字段获取）、`--resource-type`（可选值：`custom`、`sceneLib`、`functionLib`、`featureLib`）。

可选参数：`--requirement-type`（`IR`/`SR`）、`--description`、`--resolve-description`、`--requirement-id`（可多次指定）。

高级输入：`--data <JSON>` 或 `--data-file <文件路径>`（与独立 flag 互斥）。

### 测试规格 TS（testdesign ts）

#### 查询 TR 关联的 TS 类型

```bash
coretool coretest testdesign ts list-types --tr-id <TR ID>
# 示例
coretool coretest testdesign ts list-types --tr-id 3611
```

`--tr-id` 为 int 类型（必填）。

#### 查询 TR 下的 TS 列表

```bash
coretool coretest testdesign ts query-by-type --tr-id <TR ID> [--ts-type <类型>] [--status <状态>] [--feature-tree-type <特性树类别>]
# 示例：查询 TR 下所有 TS（不传类型默认查全部）
coretool coretest testdesign ts query-by-type --tr-id 3611
# 示例：按类型筛选
coretool coretest testdesign ts query-by-type --tr-id 3611 --ts-type scene --ts-type function
```

`--tr-id` 为 int 类型（必填）。可选：`--ts-type`（stringArray，可多次指定，不传则查全部）、`--status`（string，筛选状态）、`--feature-tree-type`（string，特性树类别，查询关联特性资源时必填）。

输出字段：`ID`、`TS_NO`、`TYPE`、`NAME`、`STATUS`、`OWNER`、`CREATOR`。

#### 创建测试规格 TS

```bash
coretool coretest testdesign ts create --version-pbi <版本PBI> --tr-id <TR ID> --type <TS类型> --name <TS名称> --idp-doc-id <IDP文档ID>
# 示例
coretool coretest testdesign ts create --version-pbi 266926538 --tr-id 3611 --type scene --name "登录功能测试规格" --idp-doc-id 5dcdfe1e-9114-48c7-8abd-aa5222f6312f
```

必填：`--version-pbi`（string）、`--tr-id`（int）、`--type`（可选值：`scene`、`function`、`feature`、`constraint`、`reliability`、`performance`、`compatibility`、`security`、`toughness`、`om`、`lifecycle`、`upgradepatch`、`inheritance`、`documentation`、`tool`、`customized`、`usability`、`serviceability`、`ai`、`funcSafety`、`testability`）、`--name`（string）、`--idp-doc-id`（string，从 `task list` 返回的 `idp_doc_id` 字段获取）。

可选参数：`--description`、`--resolve-description`。

高级输入：`--data <JSON>` 或 `--data-file <文件路径>`（与独立 flag 互斥）。

### 测试要点 TP（testdesign tp）

#### 查询 TS 关联的 TP 列表

```bash
coretool coretest testdesign tp list --ts-id <TS ID>
# 示例
coretool coretest testdesign tp list --ts-id 35792
```

`--ts-id` 为 int 类型（必填）。

### TP→TC 数据组合算法（testdesign combination）

从 TP 的因子和取值生成 TC 组合用例。支持正交（全覆盖）和 PairWise（两两覆盖）两种算法。

#### 根据因子和混合力度获取组合结果

```bash
coretool coretest testdesign combination result --parameter <因子JSON> --order <混合力度>
# 示例：正交组合（全覆盖，--order 0）
coretool coretest testdesign combination result --parameter '{"OS":["Windows","Linux"],"Browser":["Chrome","Firefox"]}' --order 0
# 示例：PairWise组合（两两覆盖，--order 2，默认）
coretool coretest testdesign combination result --parameter '{"OS":["Windows","Linux"],"Browser":["Chrome","Firefox"],"Network":["WiFi","4G"]}' --order 2
```

`--parameter` 为 stringArray（可多次指定）。也可用 `--parameter-file <文件路径>`（`-` 表示 stdin）。`--order`：0=正交，2=PairWise（默认2）。

#### 根据因子和约束获取组合结果

```bash
coretool coretest testdesign combination result-with-constraints --parameter <因子JSON> --constraint <约束条件> --order <混合力度>
# 示例
coretool coretest testdesign combination result-with-constraints --parameter '{"OS":["Windows","Linux"],"Browser":["Chrome","Firefox"]}' --constraint 'OS=Windows => Browser=Chrome' --order 2
```

`--constraint` 为 stringArray（可多次指定）。也可用 `--constraint-file <文件路径>`（`-` 表示 stdin）。

### 测试用例 TC（testdesign tc）

#### 查询 TP 下的 TC 列表

```bash
coretool coretest testdesign tc list --version-pbi <版本PBI> --tp-id <TP ID>
# 示例
coretool coretest testdesign tc list --version-pbi 266926538 --tp-id 18288
```

`--tp-id` 为 int 类型（必填），`--version-pbi` 为 string 类型（必填）。

#### 创建测试用例 TC

```bash
coretool coretest testdesign tc create --tp-id <TP ID> --version-pbi <版本PBI> --name <用例名称> --case-id <用例ID> --creator <创建者> --owner <责任人>
# 示例
coretool coretest testdesign tc create --tp-id 18288 --version-pbi 266926538 --name "Windows+Chrome登录验证" --case-id TC_SKILL_001 --creator w30020094 --owner w30020094
```

必填：`--tp-id`（int）、`--version-pbi`（string）、`--name`（string）、`--case-id`（string）、`--creator`（string）、`--owner`（string）。

可选参数：`--description`、`--test-type`、`--test-activity`、`--rank`、`--precondition`、`--test-step`、`--expected-output`、`--case-id-type`（`input_begin` 或 `end_begin`）

### IDP 文档（testdesign idp）

#### 查询 IDP 文档章节

```bash
coretool coretest testdesign idp topic list --idp-doc-id <IDP文档ID> --user-id <用户ID> --activity-name <活动名称>
# 示例
coretool coretest testdesign idp topic list --idp-doc-id 5dcdfe1e-9114-48c7-8abd-aa5222f6312f --user-id w30020094 --activity-name 场景分析 --parent-activity-id 3861 --parent-activity-name "Nsmf/Nupf链路容灾功能补齐-5GC-UPCF" --parent-activity-type TR
```

必填：`--idp-doc-id`（string，从 `task list` 返回的 `idp_doc_id` 字段获取）、`--user-id`（string）、`--activity-name`（string）。

可选：`--parent-activity-id`（int）、`--parent-activity-name`（string）、`--parent-activity-type`（string，如 TR/TS/TP）。

输出字段：`TOPIC_ID`、`TOPIC_NAME`。

#### 写入 IDP 文档源数据

支持三种类型：表格（row-table/display_type=2）、文本（text/display_type=3）、文件（file/display_type=6）。

- 不传 `source_value_uuid`：新增数据源，IDP 自动分配 UUID
- 传入已有的 `source_value_uuid`：覆盖该 UUID 对应的已有内容

```bash
# 表格写入（flags 模式）
coretool coretest testdesign idp source-data write --topic-id <章节ID> --user-id <用户ID> --display-type row-table --title <数据标题>
# 示例：新增表格
coretool coretest testdesign idp source-data write --topic-id bfeb5299-ff2c-4db3-a6af-a71da527788e --user-id w30020094 --display-type row-table --title "测试类型交互设计"

# 文本写入（flags 模式）
coretool coretest testdesign idp source-data write --topic-id <章节ID> --user-id <用户ID> --display-type text --title <数据标题>
# 示例：新增文本
coretool coretest testdesign idp source-data write --topic-id bfeb5299-ff2c-4db3-a6af-a71da527788e --user-id w30020094 --display-type text --title "测试类型交互设计"

# --data JSON 模式：表格写入（含完整 table_content）
coretool coretest testdesign idp source-data write --data '{"topic_id":"bfeb5299-ff2c-4db3-a6af-a71da527788e","user_id":"w30020094","display_type":2,"title":"测试表格","table_content":{"headers":[{"content":"参数","rowspan":1,"colspan":1},{"content":"值","rowspan":1,"colspan":1}],"rows":[[{"content":"模式","rowspan":1,"colspan":1},{"content":"自动化","rowspan":1,"colspan":1}]],"col_widths":["100","100"]}}'

# --data JSON 模式：文本写入
coretool coretest testdesign idp source-data write --data '{"topic_id":"bfeb5299-ff2c-4db3-a6af-a71da527788e","user_id":"w30020094","display_type":3,"title":"测试类型交互设计","text_content":"这是通过CLI写入的文本内容"}'

# --data JSON 模式：覆盖写入（传入已有 source_value_uuid）
coretool coretest testdesign idp source-data write --data '{"topic_id":"bfeb5299-ff2c-4db3-a6af-a71da527788e","user_id":"w30020094","display_type":3,"title":"测试类型交互设计","source_value_uuid":"e5d9e605-89b6-63d1-eb26-018865eed44f-1a03bfae182","text_content":"覆盖后的新内容"}'
```

flags 模式必填：`--topic-id`（string）、`--user-id`（string）、`--display-type`（可选值：`row-table`、`text`、`file`）、`--title`（string）。可选：`--source-value-uuid`（未提供时自动生成）。

`--data <JSON>` 或 `--data-file <文件路径>` 模式：直接传入完整请求体 JSON，与 flags 模式互斥。JSON 字段：`topic_id`、`user_id`、`display_type`（2=row-table, 3=text, 6=file）、`title`、`source_value_uuid`（可选，不传为新增，传已有值为覆盖）、`table_content`（display_type=2 时使用，含 headers/rows/col_widths）、`text_content`（display_type=3 时使用，纯文本字符串）、`file_content`（display_type=6 时使用，ECM 文件 ID）。

输出字段：`TOPIC_ID`、`SOURCE_VALUE_UUID`、`DISPLAY_TYPE`、`TITLE`、`WRITTEN`。

---

## Common 通用查询

跨平台通用查询接口，包含版本 PBI 查询和 CIDA 配置查询。

### 版本 PBI 查询（common version-pbi）

#### 通过 C 版本名称查询 versionPBI

```bash
coretool coretest common version-pbi --name <版本名称>
# 示例
coretool coretest common version-pbi --name "UPCF 27.0.0"
```

`--name`（`-n`）为 string（必填），传入 C 版本名称。

输出字段：`VERSION_PBI`（版本 PBI 编号，int64）。

服务端点：`https://coreaidi.inhuawei.com`，接口路径 `/versioninfo/v2/get_version_pbi_by_name?versionName=<名称>`，返回纯数字（非 WebReturn 信封）。

### CIDA 配置查询（common cida-config）

#### 通过 groupName 查询 CIDA 配置

```bash
coretool coretest common cida-config --group-name <群组名称>
# 示例
coretool coretest common cida-config --group-name "UPCF测试组"
```

`--group-name`（`-g`）为 string（必填），传入群组名称。后端先通过 groupName 查询 groupId，再返回该组下的 CIDA 配置列表。

输出字段：`ID`、`PRODUCT_NAME`、`TICC_SERVICE_ADDRESS`、`TMSS_SERVICE_ADDRESS`、`LCM_SERVICE_ADDRESS`、`GROUP_ID`。

服务端点：`https://coretestresult.cloudspider.rnd.huawei.com`，接口路径 `/api/v1/cidaConfig/getCidaConfigsByGroupName/<groupName>`，标准 WebReturn 信封。
