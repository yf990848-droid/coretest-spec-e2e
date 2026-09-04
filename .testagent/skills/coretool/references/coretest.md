# CoreTest 领域参考

CoreTest 是华为 CoreTool 的测试执行领域，支持 InFactory、Script、Pipeline、TestResult、LCM、TestDesign、Common 七大平台。

所有命令统一使用 `coretool-cli coretest` 调用，通过 Bash 工具执行。所有查询命令支持 `--output table|json` 控制输出格式。

## 平台总览

| 平台 | 说明 |
|------|------|
| `coretool-cli coretest infactory` | InFactory 任务、环境、Runner 管理 |
| `coretool-cli coretest script` | Script 执行器、用例、日志管理 |
| `coretool-cli coretest pipeline` | Pipeline 用例筛选、导入、运行、状态查询 |
| `coretool-cli coretest testresult` | 测试结果、AI 分析、日志、历史、重执行、DTS提单、环境修复、分析任务查询、执行任务失败用例查询 |
| `coretool-cli coretest lcm` | LCM 环境查询、锁定、解锁 |
| `coretool-cli coretest testdesign` | 测试设计（组合、资产、任务、TR/TS/TP/TC、CIDA、归档） |
| `coretool-cli coretest common` | 通用查询（版本PBI、CIDA配置） |

---

## InFactory 平台

### 任务管理（task）

#### 创建 InFactory 任务

参数按页面分为 4 类 JSON 传入，`--basic-info` 必填，其余可选。

```bash
coretool-cli coretest infactory task create --basic-info '<基础信息JSON>' [--case-filter '<入厂用例筛选JSON>'] [--mr-config '<创建MR JSON>'] [--script-refresh '<自定义刷新脚本字段JSON>'] [--executor-ip <执行机IP>] [--env-name <环境名称>]
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

**--executor-ip / --env-name（环境自动查询，可选）**

通过执行机 IP 或环境名称自动查询 InFactory 环境信息并填充 `envList`，无需手动在 `--case-filter` 中拼接 `envList` JSON。

| Flag | 类型 | 说明 |
|------|------|------|
| `--executor-ip` | string | 执行机 IP（如 `7.197.108.14`），按 IP 查询环境 |
| `--env-name` | string | 环境名称（如 `DOCKER_UAMF_INTER-27-29@UAMF_GY_VPC04`），按名称查询环境 |

- `--basic-info` 中必须包含 `groupId`，用于鉴权查询环境
- 两个 flag 互斥，同时传入时 `--executor-ip` 优先
- 查询到 0 个环境时报错，查到多个环境时提示缩小范围，查到 1 个环境时自动填充 `envList`
- 传入 `--executor-ip` 或 `--env-name` 时，会覆盖 `--case-filter` 中已有的 `envList`

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
coretool-cli coretest infactory task create \
  --basic-info '{"inFactoryTaskName":"task_test_20260818","productLineName":"CSP","projectName":"CSP 26.1.0","codehubHttpAddress":"https://codehub-dg-y.huawei.com/CSPAutoTest/AITestForCSP.git","sourceCodehubBranchName":"personal/w00455952/master","destCodehubBranchName":"personal/w00455952/master_ruchang","cVersionName":"CSP 26.1.0","bVersionName":"CSP 26.1.0_用例预入场","factoryType":"Hutaf","executorType":"CLOUD_SPIDER","isAuto":"0","groupId":"1052","creator":"r30073095"}' \
  --case-filter '{"envList":"[]","tepList":"[{\"id\":\"3085993856910165504\",\"type\":\"CLOUD_SPIDER\",\"name\":\"10.44.175.156:8090\",\"version\":\"1.1.57\",\"status\":\"idle\",\"network\":\"yellow\"}]","policyName":"只入厂","fileNames":[{"id":"","fileName":"test_TC_CSP_ALM_MML_024.py","caseNumber":"test_TC_CSP_ALM_MML_024","isConfig":0}]}' \
  --mr-config '{"templateName":"test_finish","mrTitle":"task_test_20260818","templateDesc":"1. test finish","isNeedVerifyBeforeMergeIntoMaster":1,"merger":[],"reviewer":[],"committer":[],"approvers":[]}' \
  --script-refresh '{"killerScriptConfigBeforeId":42,"killerScriptConfigAfterId":45,"customParams":"{\"configPath\":\"/home/executor/JavaEnvCfg\",\"packageName\":\"TestforCSPDFPPython-22.1.0.tar\",\"serviceName\":\"TestforCSPDFPPython\",\"version\":\"22.1.0\",\"product\":\"csp\",\"executorType\":\"CLOUD_SPIDER\",\"purePython\":\"true\",\"customCmd\":\"pytest -v\"}","customFieldInfo":"[{\"fieldName\":\"\",\"tmssFieldValue\":\"\",\"fieldNameOptions\":[],\"tmssFieldValueOptions\":[]}]"}'

# 示例：仅基础信息（最少参数）
coretool-cli coretest infactory task create \
  --basic-info '{"inFactoryTaskName":"构建验证","productLineName":"Cloud","projectName":"CoreTool","codehubHttpAddress":"https://codehub.huawei.com/CoreTool.git","sourceCodehubBranchName":"feature/test","destCodehubBranchName":"master"}'

# 示例：通过执行机IP自动查询环境填充envList
coretool-cli coretest infactory task create \
  --basic-info '{"inFactoryTaskName":"task_test_20260826","productLineName":"UAMF","projectName":"UNC UAMF 27.0.0","codehubHttpAddress":"https://szv-open.codehub.huawei.com/TestCode/CloudCore/5gcore-test/AutoFac-ps/uamf.git","sourceCodehubBranchName":"personal/h00452815","destCodehubBranchName":"uamf27.0.0_release","groupId":"1065","creator":"h00980767","cVersionName":"UNC UAMF 27.0.0","bVersionName":"UNC UAMF 27.0.RC1.B003","factoryType":"CloudExpress","executorType":"CLOUD_SPIDER","isAuto":"0","topoName":"DOCKER_UAMF_INTER"}' \
  --case-filter '{"tepList":"[]","policyName":"仅入厂","fileNames":[{"id":"","fileName":"TC_DNN_CONVERT_001_001_021.py","caseNumber":"TC_DNN_CONVERT_001_001_021","isConfig":0}]}' \
  --executor-ip 7.197.108.14

# 示例：通过环境名称自动查询环境填充envList
coretool-cli coretest infactory task create \
  --basic-info '{"inFactoryTaskName":"task_test_20260826","productLineName":"UAMF","projectName":"UNC UAMF 27.0.0","codehubHttpAddress":"https://szv-open.codehub.huawei.com/TestCode/CloudCore/5gcore-test/AutoFac-ps/uamf.git","sourceCodehubBranchName":"personal/h00452815","destCodehubBranchName":"uamf27.0.0_release","groupId":"1065","creator":"h00980767","cVersionName":"UNC UAMF 27.0.0","bVersionName":"UNC UAMF 27.0.RC1.B003","factoryType":"CloudExpress","executorType":"CLOUD_SPIDER","isAuto":"0","topoName":"DOCKER_UAMF_INTER"}' \
  --case-filter '{"tepList":"[]","policyName":"仅入厂","fileNames":[{"id":"","fileName":"TC_DNN_CONVERT_001_001_021.py","caseNumber":"TC_DNN_CONVERT_001_001_021","isConfig":0}]}' \
  --env-name "DOCKER_UAMF_INTER-27-29@UAMF_GY_VPC04"
```

#### 查询任务列表

```bash
coretool-cli coretest infactory task list --group-id <组ID> [--creator <工号>] [--id <任务ID>] [--result <结果>]
# 示例
coretool-cli coretest infactory task list --group-id 1052
coretool-cli coretest infactory task list --group-id 1052 --creator w30020094
```

`--group-id` 为 int64 类型（必填）。支持分页：`--page`（默认1）、`--page-size`（默认10）。

输出字段：`id`、`name`、`creator`、`source_branch`、`dest_branch`、`state`、`create_time`、`exec_task_ids`（JSON数组，用于 retry 的 `inFactoryExecTaskId`）。

#### 刷新任务状态

```bash
coretool-cli coretest infactory task refresh <task-id> --scope <status|detail>
# 示例：刷新状态
coretool-cli coretest infactory task refresh 35324 --scope status
# 示例：刷新详情（需指定 group-id）
coretool-cli coretest infactory task refresh 35324 --scope detail --group-id 1052
```

#### 重试失败任务

参数按页面分为 4 类 JSON 传入，与 create 格式一致。`--basic-info` 必填（须包含 `inFactoryTaskId` 和 `inFactoryExecTaskId`），其余可选。

```bash
coretool-cli coretest infactory task retry --basic-info '<基础信息JSON>' [--case-filter '<入厂用例筛选JSON>'] [--mr-config '<创建MR JSON>'] [--script-refresh '<自定义刷新脚本字段JSON>'] [--executor-ip <执行机IP>] [--env-name <环境名称>]
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

其余字段同 create 的 `--basic-info`、`--case-filter`、`--mr-config`、`--script-refresh`。`--executor-ip` / `--env-name` 用法同 create。

```bash
# 示例：重试任务（最少参数）
coretool-cli coretest infactory task retry \
  --basic-info '{"inFactoryTaskId":35324,"inFactoryExecTaskId":50938}'

# 示例：重试任务（带完整4类参数，同 create 格式）
coretool-cli coretest infactory task retry \
  --basic-info '{"inFactoryTaskId":35324,"inFactoryExecTaskId":50938,"inFactoryTaskName":"task_test_20260818","productLineName":"CSP","projectName":"CSP 26.1.0","codehubHttpAddress":"https://codehub-dg-y.huawei.com/CSPAutoTest/AITestForCSP.git","sourceCodehubBranchName":"personal/w00455952/master","destCodehubBranchName":"personal/w00455952/master_ruchang","cVersionName":"CSP 26.1.0","bVersionName":"CSP 26.1.0_用例预入场","factoryType":"Hutaf","executorType":"CLOUD_SPIDER","isAuto":"0","groupId":"1052","creator":"r30073095"}' \
  --case-filter '{"envList":"[]","tepList":"[{\"id\":\"3085993856910165504\",\"type\":\"CLOUD_SPIDER\",\"name\":\"10.44.175.156:8090\",\"version\":\"1.1.57\",\"status\":\"idle\",\"network\":\"yellow\"}]","policyName":"只入厂","fileNames":[{"id":"","fileName":"test_TC_CSP_ALM_MML_024.py","caseNumber":"test_TC_CSP_ALM_MML_024","isConfig":0}]}' \
  --mr-config '{"templateName":"test_finish","mrTitle":"task_test_20260818","templateDesc":"1. test finish","isNeedVerifyBeforeMergeIntoMaster":1,"merger":[],"reviewer":[],"committer":[],"approvers":[]}' \
  --script-refresh '{"killerScriptConfigBeforeId":42,"killerScriptConfigAfterId":45,"customParams":"{\"configPath\":\"/home/executor/JavaEnvCfg\",\"packageName\":\"TestforCSPDFPPython-22.1.0.tar\",\"serviceName\":\"TestforCSPDFPPython\",\"version\":\"22.1.0\",\"product\":\"csp\",\"executorType\":\"CLOUD_SPIDER\",\"purePython\":\"true\",\"customCmd\":\"pytest -v\"}","customFieldInfo":"[{\"fieldName\":\"\",\"tmssFieldValue\":\"\",\"fieldNameOptions\":[],\"tmssFieldValueOptions\":[]}]"}'

# 示例：重试任务（通过执行机IP自动查询环境）
coretool-cli coretest infactory task retry \
  --basic-info '{"inFactoryTaskId":35324,"inFactoryExecTaskId":50938,"groupId":"1052"}' \
  --executor-ip 10.44.175.156
```

> **提示**：`inFactoryTaskId` 对应 task list 输出的 `id` 字段，`inFactoryExecTaskId` 对应 task list 输出的 `exec_task_ids` 字段（JSON 数组，取第一个值即可）。

### 环境管理（environment）

#### 查询可用环境

```bash
coretool-cli coretest infactory environment list --project <项目> --product-line <产品线> --group-id <组ID>
# 示例
coretool-cli coretest infactory environment list --project "CSP 23.1.0" --product-line CSP --group-id 1052
coretool-cli coretest infactory environment list --project "CSP 23.1.0" --product-line CSP --group-id 1052 --status available
```

必填：`--project`、`--product-line`、`--group-id`（int）。可选筛选：`--name`、`--version`、`--status`。分页：`--page`（默认1）、`--page-size`（默认10）。

### Runner 管理（runner）

#### 查询可用 Runner

```bash
coretool-cli coretest infactory runner list --project <项目> --product-line <产品线> --group-id <组ID>
# 示例
coretool-cli coretest infactory runner list --project "CSP 23.1.0" --product-line CSP --group-id 1052
coretool-cli coretest infactory runner list --project "CSP 23.1.0" --product-line CSP --group-id 1052 --status idle --type CLOUD_SPIDER
coretool-cli coretest infactory runner list --project "CSP 23.1.0" --product-line CSP --group-id 1052 --page 2 --page-size 20
```

必填：`--project`、`--product-line`、`--group-id`（int）。可选筛选：`--network`（可多次）、`--type`（可多次）、`--status`（可多次）、`--version`、`--location`、`--ip`。分页：`--page`（默认1）、`--page-size`（默认10）。

---

## Script 平台

### 执行器管理（script executor）

#### 查询执行器连接信息

```bash
coretool-cli coretest script executor list [--user-id <工号>] [--name <环境名>]
# 示例：默认查当前登录用户名下的执行器
coretool-cli coretest script executor list
# 示例：指定用户
coretool-cli coretest script executor list --user-id w30020094
```

不传 `--user-id` 时自动从登录信息填充当前工号。`--name` 默认为空（返回用户默认执行器配置）。

### 用例执行（script case）

#### 远程运行测试用例

```bash
coretool-cli coretest script case run --file <用例文件路径>
# 示例：通过后端查询执行器（默认）
coretool-cli coretest script case run --file tests/test_login.py
# 示例：指定后端查询参数
coretool-cli coretest script case run --file tests/test_login.py --user-id w30020094 --env-name env01 --version-branch branch_new
# 示例：直传执行器信息（跳过后端查询）
coretool-cli coretest script case run --file tests/test_login.py \
  --executor-ip 10.90.120.56 --ssh-user root --ssh-password 'xxxx'
```

必填：`--file`（`-f`）。

**后端查询模式**（不传 `--executor-ip` 时）：从后端 API 查询执行器连接信息。可选：`--context`（`-c`）、`--env-name`（默认空）、`--user-id`（默认当前登录工号）、`--version-branch`（`branch_old` 或 `branch_new`，默认 `branch_old`）。

**直传模式**（传 `--executor-ip` 时）：跳过后端查询，直接使用命令行提供的连接信息。参数：`--executor-ip`（必填）、`--ssh-user`（默认 `root`）、`--ssh-port`（默认 `22`）、`--ssh-password`、`--case-root`（默认 `/tmp`）、`--execute-mode`（默认 `CloudSpider`）。

### 日志管理（script log）

#### 从日志提取元数据

```bash
coretool-cli coretest script log extract-metadata --content <日志内容>
# 示例：直接传内容
coretool-cli coretest script log extract-metadata --content "data:{'caseId': 'TC001', 'startTime': 1704067200, 'endTime': 1704153600}"
# 示例：从文件读取
coretool-cli coretest script log extract-metadata --content-file /tmp/test.log
```

`--content` 和 `--content-file` 二选一。从日志中正则提取 `caseId`、`startTime`、`endTime`，并查询后端关联 `groupId` 和 `testResultId`。

---

## Pipeline 平台

### 用例管理（pipeline case）

#### 按条件筛选用例

```bash
coretool-cli coretest pipeline case filter --condition <JSON条件>
# 示例
coretool-cli coretest pipeline case filter --condition '{"field":"priority","op":"eq","value":"P0"}' --scope-paths /project/module
```

也可用 `--condition-file <文件路径>`。可选：`--scope-paths`（可多次）、`--type`（默认 `TestCase`）、`--current-children`、`--need-short-uri`

#### 按条件导入用例到目标版本

```bash
coretool-cli coretest pipeline case import --source-path <源版本路径> --dest-path <目标路径> --condition <JSON条件>
# 示例
coretool-cli coretest pipeline case import --source-path /v1/modules --dest-path /v2/modules --condition '{"field":"priority","op":"eq","value":"P0"}'
```

必填：`--source-path`、`--dest-path`。也可用 `--condition-file`。可选：`--scope-paths`

### Pipeline 操作（pipeline operation）

#### 查询操作执行结果

```bash
coretool-cli coretest pipeline operation get --operation-uri <操作URI>
# 示例
coretool-cli coretest pipeline operation get --operation-uri /operations/import-20260817-001
```

### Pipeline 运行（pipeline run）

#### 创建并触发 Pipeline

```bash
coretool-cli coretest pipeline run --c-version-uri <C版本URI> --c-version-name <C版本名> --b-version-uri <B版本URI> --b-version-name <B版本名>
# 示例
coretool-cli coretest pipeline run --c-version-uri /versions/c-v1.0 --c-version-name "C v1.0" --b-version-uri /versions/b-v1.0 --b-version-name "B v1.0" --is-parallel true --pipeline-param '{"pipelineId":1,"caseId":"TC001"}'
```

必填：`--c-version-uri`、`--c-version-name`、`--b-version-uri`、`--b-version-name`。`--is-parallel` 默认 `true`。`--pipeline-param` 可多次指定，或用 `--pipeline-param-file <文件路径>`。

### Pipeline 状态（pipeline status）

#### 查询 Pipeline 执行步骤状态

```bash
coretool-cli coretest pipeline status --pipeline-id <ID1> [--pipeline-id <ID2>]
# 示例
coretool-cli coretest pipeline status --pipeline-id 1 --pipeline-id 2 --latest-record true
```

`--pipeline-id` 为 int64Slice（必填，可多次指定）。可选 `--latest-record`。

### 测试策略（pipeline strategy）

#### 查询测试策略列表

```bash
coretool-cli coretest pipeline strategy list --group-id <组ID>
# 示例
coretool-cli coretest pipeline strategy list --group-id 1032
coretool-cli coretest pipeline strategy list --group-id 1032 --name 冒烟 --type 0 --c-version "V5.0"
```

必填 `--group-id`（string）。可选：`--name`（模糊筛选）、`--type`（0=C版本，1=B版本）、`--c-version`（C版本名称筛选）、`--page`（默认1）、`--page-size`（默认10）。

#### 创建测试策略

```bash
coretool-cli coretest pipeline strategy create --group-id <组ID> --name <名称> --c-version <C版本名> --data <JSON>
# 示例
coretool-cli coretest pipeline strategy create --group-id 1032 --name "冒烟测试策略" --c-version "V5.0" --data-file content.json
# 示例：用 c-version-id 自动解析（互斥 --c-version）
coretool-cli coretest pipeline strategy create --group-id 1032 --name "冒烟测试策略" --c-version-id 789 --data-file content.json
```

必填 `--group-id`、`--name`、`--data` 或 `--data-file`。`--c-version` 与 `--c-version-id` 二选一（`--c-version-id` 自动解析为 c-version name）。

### 策略模板（pipeline strategy-template）

#### 查询策略模板列表

```bash
coretool-cli coretest pipeline strategy-template list --group-id <组ID>
# 示例
coretool-cli coretest pipeline strategy-template list --group-id 1032 --page 1 --page-size 10
```

必填 `--group-id`（string）。可选：`--name`（模糊筛选）、`--type`（0=PDU，1=product）、`--page`、`--page-size`。

#### 创建策略模板

```bash
coretool-cli coretest pipeline strategy-template create --group-id <组ID> --name <名称> --type <类型>
# 示例：用 ID 指定分类
coretool-cli coretest pipeline strategy-template create --group-id 1032 --name "PDU策略模板" --type 0 --must-ids 101,102 --optional-ids 201
# 示例：用名称解析分类（互斥 --must-ids/--optional-ids）
coretool-cli coretest pipeline strategy-template create --group-id 1032 --name "PDU策略模板" --type 0 --must-names 功能测试,性能测试 --optional-names 安全测试
```

必填 `--group-id`、`--name`。`--must-ids` 与 `--must-names` 互斥；`--optional-ids` 与 `--optional-names` 互斥。名称自动解析为分类 ID。可选 `--desc`。

#### 查询策略小分类

```bash
coretool-cli coretest pipeline strategy-template category list --group-id <组ID>
# 示例
coretool-cli coretest pipeline strategy-template category list --group-id 1032
```

必填 `--group-id`（string）。

### 传递版本（pipeline transfer-version）

#### 查询传递版本列表

```bash
coretool-cli coretest pipeline transfer-version list --group-id <组ID>
# 示例
coretool-cli coretest pipeline transfer-version list --group-id 1032
```

必填 `--group-id`（string）。

#### 添加传递版本

```bash
coretool-cli coretest pipeline transfer-version add --group-id <组ID> --data <JSON>
# 示例
coretool-cli coretest pipeline transfer-version add --group-id 1032 --data-file version.json
```

必填 `--group-id`。`--data` 或 `--data-file` 二选一。

### 测试任务（pipeline test-task）

#### 查询测试任务列表

```bash
coretool-cli coretest pipeline test-task list --group-id <组ID>
# 示例
coretool-cli coretest pipeline test-task list --group-id 1032
```

必填 `--group-id`（string）。可选：`--page`、`--page-size`。

#### 创建测试任务

```bash
coretool-cli coretest pipeline test-task create --group-id <组ID> --name <名称> --version-id <版本ID>
# 示例
coretool-cli coretest pipeline test-task create --group-id 1032 --name "冒烟测试" --version-id 5
# 示例：用名称解析版本（互斥 --version-id）
coretool-cli coretest pipeline test-task create --group-id 1032 --name "冒烟测试" --version-name "V5.0"
# 示例：用名称解析负责人（互斥 --person）
coretool-cli coretest pipeline test-task create --group-id 1032 --name "冒烟测试" --version-id 5 --person-name 张三
```

必填 `--group-id`、`--name`。`--version-id` 与 `--version-name` 互斥；`--person` 与 `--person-name` 互斥。也可用 `--data` / `--data-file` 传完整 JSON。

#### 更新测试任务（触发流水线）

```bash
coretool-cli coretest pipeline test-task update --group-id <组ID> --task-id <任务ID>
# 示例
coretool-cli coretest pipeline test-task update --group-id 1032 --task-id 7523 --auto-execute
# 示例：用名称解析任务ID（互斥 --task-id）
coretool-cli coretest pipeline test-task update --group-id 1032 --task-name "冒烟测试" --auto-execute
```

必填 `--group-id`、`--task-id`。`--task-id` 与 `--task-name` 互斥。可选 `--auto-execute`（自动执行策略）、`--group-execute`（组执行策略）。也可用 `--data` / `--data-file`。

#### 提交测试任务

```bash
coretool-cli coretest pipeline test-task deliver --group-id <组ID> --data <JSON>
# 示例
coretool-cli coretest pipeline test-task deliver --group-id 1032 --data-file deliver.json
```

必填 `--group-id`。`--data` 或 `--data-file` 二选一。

#### 查询测试任务详情

```bash
coretool-cli coretest pipeline test-task detail --group-id <组ID> --task-id <任务ID>
# 示例
coretool-cli coretest pipeline test-task detail --group-id 1032 --task-id 7523
```

必填 `--group-id`（string）、`--task-id`（int）。

### 任务模板（pipeline template）

#### 查询任务模板列表

```bash
coretool-cli coretest pipeline template list --group-id <组ID>
# 示例
coretool-cli coretest pipeline template list --group-id 1032 --page 1 --page-size 5
```

必填 `--group-id`（string）。可选 `--page`、`--page-size`。

#### 创建任务模板

```bash
coretool-cli coretest pipeline template create --group-id <组ID> --data <JSON>
# 示例
coretool-cli coretest pipeline template create --group-id 1032 --data-file template.json
```

必填 `--group-id`。`--data` 或 `--data-file` 二选一。

### 辅助查询（pipeline helper）

#### 查询 C 版本下拉选项

```bash
coretool-cli coretest pipeline helper c-version list --group-id <组ID>
# 示例
coretool-cli coretest pipeline helper c-version list --group-id 1032
```

#### 查询 B 版本下拉选项

```bash
coretool-cli coretest pipeline helper b-version list --group-id <组ID>
# 示例
coretool-cli coretest pipeline helper b-version list --group-id 1032
```

#### 查询用户下拉选项

```bash
coretool-cli coretest pipeline helper user list --group-id <组ID>
# 示例
coretool-cli coretest pipeline helper user list --group-id 1032
```

#### 查询 CodeHub 项目下拉选项

```bash
coretool-cli coretest pipeline helper codehub list --group-id <组ID>
# 示例
coretool-cli coretest pipeline helper codehub list --group-id 1032
coretool-cli coretest pipeline helper codehub list --group-id 1032 --project-id PID
```

可选 `--project-id`（传入后查询该项目的分支列表）。

### 流水线记录（pipeline record）

#### 查询流水线记录列表

```bash
coretool-cli coretest pipeline record list --group-id <组ID>
# 示例
coretool-cli coretest pipeline record list --group-id 1032 --page 1 --page-size 10
```

必填 `--group-id`（int）。可选 `--page`、`--page-size`。

#### 查询流水线记录详情

```bash
coretool-cli coretest pipeline record detail --record-id <记录ID>
# 示例
coretool-cli coretest pipeline record detail --record-id 6fdfdb781a5d4efaaf99d268af723a28
```

必填 `--record-id`（string）。

#### 查询工厂任务详情

```bash
coretool-cli coretest pipeline record factory-detail --record-id <记录ID>
# 示例
coretool-cli coretest pipeline record factory-detail --record-id 6fdfdb781a5d4efaaf99d268af723a28
```

必填 `--record-id`（string）。任务未执行到工厂阶段时提示 "No factory task detail available"。

---

## TestResult 平台

### AI 分析（testresult analysis）

#### 获取失败用例的 RAG 检索结果

```bash
coretool-cli coretest testresult analysis get --test-result-id <结果ID>
# 示例
coretool-cli coretest testresult analysis get --test-result-id 334463562
coretool-cli coretest testresult analysis get --test-result-id 334463562 --with-dts-status
```

`--test-result-id`（`-t`）为 int 类型（必填）。可选 `--with-dts-status`。

#### 回填 AI 分析结论到 CTR

```bash
coretool-cli coretest testresult analysis update --test-result-id <结果ID> --big-type <大类> --sub-type <子类> --analyse-state <状态>
# 示例
coretool-cli coretest testresult analysis update --test-result-id 334463562 --big-type "脚本问题" --sub-type "脚本问题" --analysis-desc "脚本检查点不正确" --analyse-state 2 --modify-type AI_FILL
# 示例：指定分析人
coretool-cli coretest testresult analysis update --test-result-id 334463562 --big-type "脚本问题" --sub-type "脚本问题" --analysis-desc "脚本检查点不正确" --analyse-state 2 --analyst w30020094
```

`--test-result-id`（`-t`）为 int 类型（必填）。可选参数：`--big-type`、`--sub-type`、`--dts-number`、`--issue-url`、`--analysis-desc`、`--analyse-state`（0=未开始，1=进行中，2=已完成）、`--change-state`、`--change-details`、`--is-determine-case`（`1`=是，`2`=否）、`--modify-type`（`AI_FILL`、`AI_BATCH`、`一键确认`）、`--analyst`（分析人，不传则默认当前登录用户）。`source` 字段自动填充为 `CLI`。

### 日志分析（testresult log-analysis）

#### 获取失败用例的 AI 日志清洗结果

```bash
coretool-cli coretest testresult log-analysis get --test-result-id <结果ID>
# 示例
coretool-cli coretest testresult log-analysis get --test-result-id 334463562
```

`--test-result-id`（`-t`）为 int 类型（必填）。

### 日志下载（testresult log）

#### 下载测试用例日志

```bash
coretool-cli coretest testresult log download --test-result-id <结果ID>
# 示例
coretool-cli coretest testresult log download --test-result-id 334463562
```

`--test-result-id`（`-t`）为 int 类型（必填）。

### 历史结果（testresult history）

#### 查询用例的历史执行结果

```bash
coretool-cli coretest testresult history list --case-id <用例ID>
# 示例
coretool-cli coretest testresult history list --case-id TC_UPF_VVIP_QOSEXP_FUNC_240809_00001 --is-last
# 示例：按任务ID过滤
coretool-cli coretest testresult history list --case-id TC_UPF_VVIP_QOSEXP_FUNC_240809_00001 --task-id 1042
```

`--case-id`（`-c`）为 string 类型（必填）。可选筛选：`--case-result`（可多次）、`--start-time`、`--end-time`（ms 时间戳）、`--executor-ip`、`--product-version`、`--dts-number`、`--c-version`、`--analyse-state`（0/1/2/99，默认99=all）、`--task-id`（任务ID过滤）。支持分页。

JSON 输出中额外包含 AI 分析字段（有值时才显示）：`is_determine_case`（是否确定性问题）、`intelligent_big_type_desc`（AI大类描述）、`intelligent_sub_type_desc`（AI子类描述）、`confidence`（置信度）。

### 最近成功（testresult latest-success）

#### 获取失败用例最后一次成功执行的信息

```bash
coretool-cli coretest testresult latest-success get --test-result-id <结果ID>
# 示例
coretool-cli coretest testresult latest-success get --test-result-id 334463562
coretool-cli coretest testresult latest-success get --test-result-id 334463562 --c-version "UDG 27.0.RC1.3.B006"
```

`--test-result-id`（`-t`）为 int 类型（必填）。可选 `--c-version`（省略时自动检测）。

### 失败重执行（testresult rerun）

#### 重执行失败用例

```bash
coretool-cli coretest testresult rerun --test-result-id <结果ID>
# 示例：自动查找执行器重执行
coretool-cli coretest testresult rerun --test-result-id 334463562
# 示例：指定执行器
coretool-cli coretest testresult rerun --test-result-id 334463562 --executor-ip 10.113.175.208
# 示例：指定操作者
coretool-cli coretest testresult rerun --test-result-id 334463562 --user-id w30020094
```

`--test-result-id`（`-t`）为 int 类型（必填）。可选 `--executor-ip`（`-e`，默认自动查找原始失败环境）、`--user-id`（`-u`，默认当前登录用户）。

### DTS-GPT 提单（testresult dts-gpt-ticket）

#### 为失败用例创建 DTS-GPT 问题单

```bash
coretool-cli coretest testresult dts-gpt-ticket --test-result-id <结果ID> --brief-desc <简要描述>
# 示例
coretool-cli coretest testresult dts-gpt-ticket --test-result-id 334463562 --brief-desc "脚本检查点不正确导致用例失败"
# 示例：简化版问题单
coretool-cli coretest testresult dts-gpt-ticket --test-result-id 334463562 --brief-desc "脚本检查点不正确" --simplified
```

`--test-result-id`（`-t`）为 int 类型（必填），`--brief-desc`（`-d`）为 string 类型（必填）。可选 `--simplified`。

### 环境修复（testresult env-repair）

#### 检测并修复环境配置残留

```bash
coretool-cli coretest testresult env-repair --executor-ip <IP> --group-id <群组ID>
# 示例：修复单个执行器
coretool-cli coretest testresult env-repair --executor-ip 10.113.175.208 --group-id 1042
# 示例：修复多个执行器
coretool-cli coretest testresult env-repair --executor-ip 10.113.175.208 --executor-ip 10.113.162.67 --group-id 1042
# 示例：关联测试结果ID
coretool-cli coretest testresult env-repair --executor-ip 10.113.175.208 --group-id 1042 --test-result-id 334463562
```

`--executor-ip`（`-e`）可多次指定（必填），`--group-id`（`-g`）为 int 类型（必填）。可选 `--test-result-id`（`-t`，int64Slice，可多次）、`--user-id`（`-u`，默认当前登录用户）。

### 分析任务查询（testresult analyse-task）

#### 查询分析任务关联的执行任务 ID

```bash
coretool-cli coretest testresult analyse-task task-ids get <analyse-task-id>
# 示例
coretool-cli coretest testresult analyse-task task-ids get 55162
# JSON 输出
coretool-cli coretest testresult analyse-task task-ids get 55162 -o json
```

`<analyse-task-id>` 为 int 类型位置参数（必填）。返回关联的执行任务 ID 列表，ID 以字符串形式输出避免大数精度丢失。后端接口：`GET /openapi/v1/analyseTask/taskIds?analyseTaskId={id}`。

#### 查询分析任务关联的 nonflaky 失败用例 ID

```bash
coretool-cli coretest testresult analyse-task nonflaky-ids get <analyse-task-id>
# 示例
coretool-cli coretest testresult analyse-task nonflaky-ids get 55156
# JSON 输出
coretool-cli coretest testresult analyse-task nonflaky-ids get 55156 -o json
```

`<analyse-task-id>` 为 int 类型位置参数（必填）。返回 nonflaky（非随机失败）的失败用例 test_result_id 列表，ID 以字符串形式输出。后端接口：`GET /openapi/v1/analyseTask/flakyFailedTestResultIds?analyseTaskId={id}`。

### 执行任务查询（testresult task）

#### 查询执行任务关联的失败用例 ID

```bash
coretool-cli coretest testresult task failed-ids get <task-id>
# 示例
coretool-cli coretest testresult task failed-ids get 3964856420500766722
# JSON 输出
coretool-cli coretest testresult task failed-ids get 3964856420500766722 -o json
```

`<task-id>` 为 string 类型位置参数（必填），因执行任务 ID 可能超出 int64 范围。返回 case_result 为 FAIL 的 test_result_id 列表，ID 以字符串形式输出。后端接口：`GET /openapi/v1/testResult/failedTestResultIds?taskId={id}`。

---

## LCM 平台

### 环境查询（lcm environment）

#### 查询个人 LCM 环境

```bash
coretool-cli coretest lcm environment list --scope personal --test-result-id <结果ID>
# 示例
coretool-cli coretest lcm environment list --scope personal --test-result-id 334801349
```

`--scope personal` 时 `--test-result-id` 为 int 类型（必填）。可选筛选：`--name`、`--version`、`--status`。支持分页。`user` 字段自动从当前登录用户填充，无需手动指定。

#### 查询公共 LCM 环境

```bash
coretool-cli coretest lcm environment list --scope public --lcm-server <服务器URL> --group-id <群组ID>
# 示例
coretool-cli coretest lcm environment list --scope public --lcm-server https://autofac-ccn.lcm.huawei.com/factory --group-id 1042
```

`--scope public` 时 `--lcm-server` 和 `--group-id`（int）均必填。`--lcm-server` 传原始 URL 即可（适配器内部自动编码）。可选筛选：`--name`、`--version`、`--status`。支持分页。

### 环境锁定/解锁（lcm lock/unlock）

#### 锁定 LCM 环境

```bash
coretool-cli coretest lcm lock --executor-ip <执行器IP>
# 示例
coretool-cli coretest lcm lock --executor-ip 10.113.175.184
```

`--executor-ip`（`-e`）为 string 类型（必填）。

#### 解锁 LCM 环境

```bash
coretool-cli coretest lcm unlock --executor-ip <执行器IP>
# 示例
coretool-cli coretest lcm unlock --executor-ip 10.113.175.184
```

`--executor-ip`（`-e`）为 string 类型（必填）。

---

## TestDesign 平台

TestDesign 是 CoreTest 的测试设计平台，支持资产库查询、设计工作流（TR→TS→TP→TC）等功能。

### 资产库（testdesign asset）

#### 查询版本关联的资产库配置

```bash
coretool-cli coretest testdesign asset list --version-pbi <版本PBI>
# 示例
coretool-cli coretest testdesign asset list --version-pbi 266926538 --type all
```

`--type`：`scene`=场景库，`feature`=特性库，`function`=功能库，`all`=全部（默认 all）。查询 `function` 时需加 `--user-id`。

#### 查询资产关系

```bash
coretool-cli coretest testdesign asset relation list --alm-id <ALM ID> --category <关系类别>
# 示例
coretool-cli coretest testdesign asset relation list --alm-id 1200734448940248896 --category feature
```

`--alm-id` 和 `--category` 均为 stringArray（必填，可多次指定）。

#### 查询 TR 关联的场景

```bash
coretool-cli coretest testdesign asset scene list --tr-id <TR ID>
# 示例
coretool-cli coretest testdesign asset scene list --tr-id 3611
```

`--tr-id` 为 int 类型（必填）。

#### 查询 TR 关联的特性

```bash
coretool-cli coretest testdesign asset feature list --pbi <版本PBI> --tr-id <TR ID>
# 示例
coretool-cli coretest testdesign asset feature list --pbi 266926538 --tr-id 3611
```

`--pbi` 为 string 类型（必填），`--tr-id` 为 int 类型（必填）。

#### 查询 TR 关联的功能

```bash
coretool-cli coretest testdesign asset function list --tr-id <TR ID>
# 示例
coretool-cli coretest testdesign asset function list --tr-id 3611
```

`--tr-id` 为 int 类型（必填）。

#### 查询 TS 关联的测试因子

```bash
coretool-cli coretest testdesign asset factor list --ts-id <TS ID>
# 示例
coretool-cli coretest testdesign asset factor list --ts-id 35792
```

`--ts-id` 为 int 类型（必填）。

#### 添加测试因子关系到 TS

```bash
coretool-cli coretest testdesign asset factor create --ts-id <TS ID> --pbi <版本PBI> --factor-type <因子类型> --asso-act-type <关联活动类型> --factor '<因子JSON数组>'
# 示例
coretool-cli coretest testdesign asset factor create --ts-id 38058 --pbi 266926538 --factor-type BusinessInterImplAnalysis --asso-act-type SceneAnalysis --factor '[{"number":"CLI_TEST_001","name":"CLI测试因子","type":0,"assoActType":"SceneAnalysis","sourceType":"TestFactorLibrary"}]'
```

必填：`--ts-id`（int）、`--pbi`（string）、`--factor-type`（string）、`--asso-act-type`（stringArray，可多次指定）。

`--factor-type` 枚举值：

| 值 | 说明 |
|----|------|
| `TSFunctionInteractionAnalysis` | 功能交互设计 |
| `BusinessInterImplAnalysis` | 基于业务内部实现设计 |
| `TestTypeInteractionAnalysis` | 测试类型交互设计 |

因子数据：`--factor <JSON数组>` 或 `--factor-file <文件路径>`（二选一）。

因子项字段：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `number` | string | 是 | 因子编号 |
| `name` | string | 是 | 因子名称 |
| `type` | int | 是 | 因子类别：0=动作因子，1=数据因子 |
| `assoActType` | string | 是 | 关联活动类型，可选值见下表。影响查询过滤，不传则 factor list 查不到 |
| `sourceType` | string | 是 | 来源类型，可选值见下表。影响查询过滤，不传则 factor list 查不到 |
| `pbi` | string | 否 | 版本PBI |
| `creator` | string | 否 | 创建人 |
| `testFactorId` | string | 否 | 因子唯一标识，未提供时自动生成 |
| `customType` | int | 否 | 是否自定义：0=否，1=是 |
| `customTestFactorId` | int64 | 否 | 自定义因子ID |
| `customTestFactorCode` | string | 否 | 自定义因子编号 |
| `description` | string | 否 | 描述 |
| `status` | string | 否 | 状态 |
| `validValues` | string | 否 | 有效值 |
| `invalidValues` | string | 否 | 无效值 |
| `variableName` | string | 否 | 变量名 |
| `variableType` | string | 否 | 变量类型 |
| `logicDescription` | string | 否 | 逻辑描述 |
| `operation` | string | 否 | 操作描述 |
| `precondition` | string | 否 | 预置条件 |
| `expectedResult` | string | 否 | 预期结果 |
| `modeNumber` | string | 否 | 模式编号 |
| `designSpecificationNumber` | string | 否 | 设计准则编号 |
| `source` | string | 否 | 来源 |
| `temporary` | int | 否 | 是否临时因子：0=否，1=是 |
| `realNumber` | string | 否 | 真实因子编号 |

`assoActType` 枚举值：

| 值 | 说明 |
|----|------|
| `RequirementAnalysis` | 测试需求分析 |
| `SceneAnalysis` | 场景分析 |
| `FeatureInteractionAnalysis` | 特性交互分析 |
| `TRFunctionInteractionAnalysis` | TR功能交互分析 |
| `TSFunctionInteractionAnalysis` | TS功能交互分析 |
| `TestTypeInteractionAnalysis` | 测试类型交互分析 |
| `TestFactorAnalysis` | 测试因子分析 |

`sourceType` 枚举值：

| 值 | 说明 |
|----|------|
| `TestFactorLibrary` | 测试因子库 |
| `SceneFactorLibrary` | 场景因子库 |

#### 查询 TS 关联的模式库

```bash
coretool-cli coretest testdesign asset model list --ts-id <TS ID> --activity-type <活动类型>
# 示例
coretool-cli coretest testdesign asset model list --ts-id 35792 --activity-type SceneAnalysis
```

`--ts-id` 为 int 类型（必填），`--activity-type` 为 string 类型（必填，可选值：`RequirementAnalysis`、`SceneAnalysis`、`FeatureInteractionAnalysis`、`TRFunctionInteractionAnalysis`、`TSFunctionInteractionAnalysis`、`TestTypeInteractionAnalysis`、`TestFactorAnalysis`）。

#### 查询 TS 节点的测试设计准则

```bash
coretool-cli coretest testdesign asset principle list --ts-id <TS ID>
# 示例
coretool-cli coretest testdesign asset principle list --ts-id 38059
```

必填：`--ts-id`（int）。自动查询 TS 详情获取 `tsType` 和 `pbi`，`tsType` 映射为中文名称（如 `reliability`→`可靠性`、`performance`→`性能`）后拼入 API 路径。

输出字段：`CRITERIA_ID`、`CRITERIA_NAME`、`MODE_NAME`、`MODE_DIR`、`INVOLVED`、`STATUS`、`TOPIC_NAME`、`CREATOR`。

#### 更新 TS 节点的测试设计准则

```bash
# 单条更新
coretool-cli coretest testdesign asset principle update --ts-id <TS ID> --criteria-id <准则ID> --idp-doc-id <IDP文档ID> [--involved <是否涉及>] [--analysis-description <说明>] [--conclusion-source-type <来源>]
# 示例：单条更新
coretool-cli coretest testdesign asset principle update --ts-id 38058 --criteria-id 391122b3fc9a435783d7180d181f7f5c --involved 1 --analysis-description "需求描述中提到了PCF组件工作量变化" --conclusion-source-type "AI推荐" --idp-doc-id 5dcdfe1e-9114-48c7-8abd-aa5222f6312f

# 批量更新
coretool-cli coretest testdesign asset principle update --ts-id <TS ID> --idp-doc-id <IDP文档ID> --items '<JSON数组>'
# 示例：批量更新两条准则
coretool-cli coretest testdesign asset principle update --ts-id 38058 --idp-doc-id 5dcdfe1e-9114-48c7-8abd-aa5222f6312f --items '[{"testDesignCriteriaId":"391122b3fc9a435783d7180d181f7f5c","involved":"1","analysisDescription":"描述1","conclusionSourceType":"AI推荐"},{"testDesignCriteriaId":"3d1728b5942e44f8a53a110499b0ab86","involved":"1","analysisDescription":"描述2","conclusionSourceType":"AI推荐"}]'
```

必填：`--ts-id`（int）、`--idp-doc-id`（string，IDP文档ID）。单条模式必填 `--criteria-id`；批量模式使用 `--items <JSON数组>` 或 `--items-file <文件路径>`。

单条模式可选变更字段：`--involved`（是否涉及）、`--analysis-description`（说明）、`--conclusion-source-type`（来源）。

批量模式 items 项字段：`testDesignCriteriaId`（必填）、`involved`、`analysisDescription`、`conclusionSourceType`。

执行流程：自动查询 relativeTr 获取 `parentTrId`，查询 principle list 回填 `modeName`/`modeDescription`/`criteriaName` 等字段，合并用户变更后 POST 全量数组。

#### 查询 TS 关联的场景因子

```bash
coretool-cli coretest testdesign asset scene-factor list --ts-id <TS ID>
# 示例
coretool-cli coretest testdesign asset scene-factor list --ts-id 38490
```

必填：`--ts-id`（int）。

输出字段：

| 字段 | 说明 |
|------|------|
| `id` | 关系ID |
| `ts_id` | TS ID |
| `scene_factor_code` | 场景因子编码 |
| `custom_scene_factor_id` | 自定义场景因子ID |
| `custom_scene_factor_code` | 自定义场景因子系统编号 |
| `custom_type` | 是否自定义 |
| `asso_act_type` | 关联活动类型 |
| `source_type` | 来源类型 |
| `name` | 因子名称 |
| `description` | 描述 |
| `data_type` | 数据类型 |
| `pbi` | 版本PBI |
| `status` | 状态 |
| `creator` | 创建人 |
| `create_time` | 创建时间 |
| `modifier` | 修改人 |
| `update_time` | 修改时间 |

#### 添加场景因子关系到 TS

```bash
coretool-cli coretest testdesign asset scene-factor create --ts-id <TS ID> --pbi <版本PBI> --source-type <来源类型> --asso-act-type <关联活动类型> --scene-factor '<场景因子JSON数组>'
# 示例
coretool-cli coretest testdesign asset scene-factor create --ts-id 35792 --pbi 266926538 --source-type scene --asso-act-type SceneAnalysis --scene-factor '[{"factorCode":"TEST_002","factorName":"CLI测试因子v2"}]'
```

必填：`--ts-id`（int）、`--pbi`（string）、`--source-type`（string）、`--asso-act-type`（string）。

因子数据：`--scene-factor <JSON数组>` 或 `--scene-factor-file <文件路径>`（二选一）。

场景因子项字段：

| 字段 | 类型 | 说明 |
|------|------|------|
| `factorCode` | string | 因子编号 |
| `factorName` | string | 因子名称 |
| `factorDesc` | string | 描述 |
| `factorDataType` | string | 数据类型 |
| `variableName` | string | 变量名 |
| `dataValidValue` | string | 数据有效值 |
| `dataInvalidValue` | string | 数据无效值 |
| `factorStatus` | string | 状态 |
| `remark` | string | 备注 |
| `parentCode` | string | 父节点编号 |

### 设计任务（testdesign task）

#### 查询版本下的测试设计任务

```bash
coretool-cli coretest testdesign task list --version-pbi <版本PBI>
# 示例
coretool-cli coretest testdesign task list --version-pbi 266926538
```

### 测试需求 TR（testdesign tr）

#### 查询设计任务下的 TR 列表

```bash
coretool-cli coretest testdesign tr list --design-task-id <设计任务ID>
# 示例
coretool-cli coretest testdesign tr list --design-task-id 2342
```

`--design-task-id` 为 int 类型（必填）。

#### 创建测试需求 TR

```bash
coretool-cli coretest testdesign tr create --version-pbi <版本PBI> --design-task-id <设计任务ID> --name <TR名称> --idp-doc-id <IDP文档ID> --resource-type <资源类型>
# 示例
coretool-cli coretest testdesign tr create --version-pbi 266926538 --design-task-id 2342 --name "登录功能测试需求" --idp-doc-id 5dcdfe1e-9114-48c7-8abd-aa5222f6312f --resource-type featureLib
```

必填：`--version-pbi`（string）、`--design-task-id`（string）、`--name`（string）、`--idp-doc-id`（string，从 `task list` 返回的 `idp_doc_id` 字段获取）、`--resource-type`（可选值：`custom`、`sceneLib`、`functionLib`、`featureLib`）。

可选参数：`--requirement-type`（`IR`/`SR`）、`--description`、`--resolve-description`、`--requirement-id`（可多次指定）。

高级输入：`--data <JSON>` 或 `--data-file <文件路径>`（与独立 flag 互斥）。

### 测试规格 TS（testdesign ts）

#### 查询 TR 关联的 TS 类型

```bash
coretool-cli coretest testdesign ts list-types --tr-id <TR ID>
# 示例
coretool-cli coretest testdesign ts list-types --tr-id 3611
```

`--tr-id` 为 int 类型（必填）。

#### 查询单个 TS

```bash
coretool-cli coretest testdesign ts get --ts-id <TS ID>
# 示例
coretool-cli coretest testdesign ts get --ts-id 38059
```

`--ts-id` 为 int 类型（必填）。返回单个 TS 详情，包含 `id`、`ts_no`、`ts_type`、`ts_name`、`status`、`pbi`、`owner`、`creator`、`create_time` 等字段。

#### 查询 TS 所属的父 TR ID

```bash
coretool-cli coretest testdesign ts get-relative-tr --ts-id <TS ID>
# 示例
coretool-cli coretest testdesign ts get-relative-tr --ts-id 38058
```

`--ts-id` 为 int 类型（必填）。调用 `GET /test_design/api/v1/ts/relativeTr?tsId={id}`，返回 TS 所属的父 TR ID。输出字段：`TR_ID`。

#### 查询 TR 下的 TS 列表

```bash
coretool-cli coretest testdesign ts query-by-type --tr-id <TR ID> [--ts-type <类型>] [--status <状态>] [--feature-tree-type <特性树类别>]
# 示例：查询 TR 下所有 TS（不传类型默认查全部）
coretool-cli coretest testdesign ts query-by-type --tr-id 3611
# 示例：按类型筛选
coretool-cli coretest testdesign ts query-by-type --tr-id 3611 --ts-type scene --ts-type function
```

`--tr-id` 为 int 类型（必填）。可选：`--ts-type`（stringArray，可多次指定，不传则查全部）、`--status`（string，筛选状态）、`--feature-tree-type`（string，特性树类别，查询关联特性资源时必填）。

输出字段：`ID`、`TS_NO`、`TYPE`、`NAME`、`STATUS`、`OWNER`、`CREATOR`。

#### 创建测试规格 TS

```bash
coretool-cli coretest testdesign ts create --version-pbi <版本PBI> --tr-id <TR ID> --type <TS类型> --name <TS名称> --idp-doc-id <IDP文档ID>
# 示例
coretool-cli coretest testdesign ts create --version-pbi 266926538 --tr-id 3611 --type scene --name "登录功能测试规格" --idp-doc-id 5dcdfe1e-9114-48c7-8abd-aa5222f6312f
```

必填：`--version-pbi`（string）、`--tr-id`（int）、`--type`（可选值：`scene`、`function`、`feature`、`constraint`、`reliability`、`performance`、`compatibility`、`security`、`toughness`、`om`、`lifecycle`、`upgradepatch`、`inheritance`、`documentation`、`tool`、`customized`、`usability`、`serviceability`、`ai`、`funcSafety`、`testability`）、`--name`（string）、`--idp-doc-id`（string，从 `task list` 返回的 `idp_doc_id` 字段获取）。

可选参数：`--description`、`--resolve-description`。

高级输入：`--data <JSON>` 或 `--data-file <文件路径>`（与独立 flag 互斥）。

### 测试要点 TP（testdesign tp）

#### 查询 TS 关联的 TP 列表

```bash
coretool-cli coretest testdesign tp list --ts-id <TS ID>
# 示例
coretool-cli coretest testdesign tp list --ts-id 35792
```

`--ts-id` 为 int 类型（必填）。

#### 创建测试点 TP

```bash
coretool-cli coretest testdesign tp create --version-pbi <版本PBI> --ts-id <TS ID> --tp-type <TP类型> --tp-source-type <TP资源类型> --parent-tr-id <父TR ID> --name <TP名称> --creator <创建者> --idp-doc-id <IDP文档ID>
# 示例
coretool-cli coretest testdesign tp create --version-pbi 266926538 --ts-id 38058 --tp-type TestTypeInteractionAnalysis --tp-source-type test_type_test_factor_type --parent-tr-id 4029 --name "CLI测试TP" --creator w30020094 --idp-doc-id 5dcdfe1e-9114-48c7-8abd-aa5222f6312f
# 创建 TP 并关联测试因子和场景因子
coretool-cli coretest testdesign tp create --version-pbi 266926538 --ts-id 38490 --tp-type SceneAnalysis --tp-source-type scene --parent-tr-id 4029 --name "CLI测试TP" --creator w30020094 --idp-doc-id 5dcdfe1e-9114-48c7-8abd-aa5222f6312f --relations '{"testFactorIdList":[{"testFactorId":"28880","name":"所有的消息，都必须记录EDR","assoActType":"SceneAnalysis","sourceType":"TestFactorLibrary","number":"Flow_03_01","type":0,"pbi":"266926538"}],"sceneFactorIdList":[{"sceneFactorCode":"TFACTOR20240301001828","factorName":"产品环境IP类型","assoActType":"SceneAnalysis","sourceType":"scene","pbi":"266926538"}]}'
```

**Query 参数**（拼接在 URL 上）：

| 字段 | JSON key | 类型 | 必填 | 说明 |
|------|----------|------|------|------|
| `--version-pbi` | `pbi` | string | 是 | 版本 PBI |
| `--ts-id` | — | int | 是 | 所属 TS ID |
| `--tp-type` | — | string | 是 | 产生 TP 的活动页面类型 |
| `--tp-source-type` | — | string | 是 | 活动页面的资源类型 |
| `--parent-tr-id` | — | int | 是 | 父 TR ID（通过 `ts get-relative-tr` 获取） |

**Body 参数**（JSON 请求体）：

| 字段 | JSON key | 类型 | 必填 | 说明 |
|------|----------|------|------|------|
| `--name` | `tpName` | string | 是 | TP 名称 |
| `--creator` | `creator` | string | 是 | 创建者 |
| `--idp-doc-id` | `idpDocId` | string | 是 | IDP 文档 ID |
| `--tr-name` | `trName` | string | 否 | TR 名称 |
| `--description` | `description` | string | 否 | 描述 |
| `--resolve-description` | `resolveDescription` | string | 否 | 分解描述 |
| — | `pbi` | string | 否 | 版本 PBI（与 query 参数重复，自动填充） |
| `--relations` | — | JSON object | 否 | 关联列表（见下方） |

**`--relations` JSON 字段**（可选，不传则所有列表为空数组）：

| JSON key | 类型 | 说明 |
|----------|------|------|
| `testFactorIdList` | object[] | 测试因子对象列表（见下方字段） |
| `sceneFactorIdList` | object[] | 场景因子对象列表（见下方字段） |
| `testDesignCriteriaIdList` | object[] | 测试设计准则对象列表 |
| `functionIdList` | object[] | 功能对象列表 |
| `modelDataList` | object[] | 模式库对象列表 |
| `tpAssociationRequirementAlmIdList` | string[] | 关联需求 ALM ID 列表 |
| `funcReqFRAndTestSpecFTList` | object[] | 功能需求 FR & 测试规格 FT 对象列表 |
| `securityConfigIdList` | string[] | 安全配置 ID 列表 |
| `speiIdList` | string[] | SPEI ID 列表 |

**`testFactorIdList` 项字段**（后端 `TestFactorBaseDomain`）：

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | long | 自增主键 |
| `assoActType` | string | 关联活动类型 |
| `sourceType` | string | 来源类型 |
| `testFactorId` | string | 测试因子 ID |
| `customTestFactorId` | long | 自定义测试因子唯一标识 |
| `customTestFactorCode` | string | 自定义测试因子系统编号 |
| `customType` | int | 是否自定义 |
| `name` | string | 因子名称 |
| `number` | string | 因子编码 |
| `description` | string | 描述 |
| `type` | int | 因子类型 |
| `pbi` | string | 版本 PBI |
| `status` | string | 测试因子状态 |
| `validValues` | string | 有效值 |
| `invalidValues` | string | 无效值 |
| `variableName` | string | 变量名 |
| `variableType` | string | 变量类型 |
| `logicDescription` | string | 因子逻辑描述（动作因子） |
| `operation` | string | 因子操作描述（动作因子） |
| `precondition` | string | 预置条件（动作因子） |
| `expectedResult` | string | 预期结果描述（动作因子） |
| `modeNumber` | string | 模式编号 |
| `designSpecificationNumber` | string | 设计准则编号 |
| `source` | string | 来源 |
| `temporary` | int | 是否临时因子（0否/1是） |
| `realNumber` | string | 因子编码 |
| `creator` | string | 创建人 |
| `createTime` | string | 创建时间 |
| `modifier` | string | 修改人 |
| `updateTime` | string | 修改时间 |
| `deleted` | int | 是否删除（0否/1是） |

**`sceneFactorIdList` 项字段**（后端 `SceneFactorBaseDomain`）：

| 字段 | 类型 | 说明 |
|------|------|------|
| `sceneFactorCode` | string | 场景因子 ID |
| `customSceneFactorId` | long | 自定义场景因子 ID |
| `customSceneFactorCode` | string | 自定义场景因子系统编号 |
| `customType` | int | 是否自定义场景因子 |
| `assoActType` | string | 关联活动类型 |
| `sourceType` | string | 来源类型 |
| `factorCode` | string | 场景因子编号 |
| `factorName` | string | 场景因子名称 |
| `factorDesc` | string | 场景因子描述 |
| `factorDataType` | string | 场景因子数据类型 |
| `variableName` | string | 场景因子变量名称 |
| `dataValidValue` | string | 场景因子数据有效值 |
| `dataInvalidValue` | string | 场景因子数据无效值 |
| `factorStatus` | string | 场景因子状态 |
| `remark` | string | 场景因子备注 |
| `pbi` | string | 版本 PBI |
| `status` | string | 状态 |
| `creator` | string | 创建人 |
| `createTime` | string | 创建时间 |
| `modifier` | string | 修改人 |
| `updateTime` | string | 修改时间 |
| `deleted` | int | 是否删除（0否/1是） |

**`testDesignCriteriaIdList` 项字段**（后端 `TpTestDesignCriteriaRelation`）：

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | long | 主键 |
| `tpId` | long | TP ID |
| `testDesignCriteriaId` | string | 测试准则唯一标识 |
| `testDesignCriteriaName` | string | 测试设计准则名字 |
| `pbi` | string | 版本 PBI |
| `modeDir` | string | 目录信息 |
| `modeDescription` | string | 模式说明 |
| `modeNumber` | string | 模式编号 |
| `status` | string | 状态（draft/submitted） |
| `applicableProduct` | string | 适用产品 |
| `applicableObject` | string | 适用对象 |
| `customDataSourceType` | string | 准则来源分类 |
| `customDataTestExecMethod` | string | 执行分析方案 |
| `customDataTestAnalyseMethod` | string | 执行分析方法 |
| `creator` | string | 创建人 |
| `createTime` | string | 创建时间 |
| `modifier` | string | 修改人 |
| `updateTime` | string | 修改时间 |
| `deleted` | int | 是否删除（0否/1是） |

**`functionIdList` 项字段**（后端 `FunctionBaseDomain`）：

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | long | 自增主键 |
| `assoActType` | string | 关联活动类型 |
| `sourceType` | string | 来源类型 |
| `customFunctionId` | long | 自定义功能 ID |
| `almCode` | string | ALM 编码 |
| `almId` | string | ALM ID |
| `name` | string | 名称 |
| `keyId` | string | Key ID |
| `status` | string | 状态 |
| `involved` | string | 是否涉及 |
| `notInvolvedReason` | string | 不涉及原因 |
| `path` | string | 目录信息 |
| `category` | string | 类型 |
| `description` | string | 描述 |
| `input` | string | 输入 |
| `process` | string | 处理 |
| `output` | string | 输出 |
| `functionConstraint` | string | 约束 |
| `resModifier` | string | 资源最近变更人 |
| `resUpdateTime` | string | 资源最近变更时间 |
| `pbi` | string | 版本 PBI |
| `functionDomainId` | string | 功能域 ID |
| `creator` | string | 创建人 |
| `createTime` | string | 创建时间 |
| `modifier` | string | 修改人 |
| `updateTime` | string | 修改时间 |
| `deleted` | int | 是否删除（0否/1是） |

**`modelDataList` 项字段**（后端 `ModelInfo`）：

| 字段 | 类型 | 说明 |
|------|------|------|
| `modeType` | string | 模式类型（resilience/security/reliability） |
| `modeId` | string | 模式唯一标识 |
| `name` | string | 模式名字 |
| `number` | string | 模式编号 |
| `description` | string | 模式说明 |
| `pbi` | string | 版本 PBI |
| `technologyType` | string | 技术类型 |
| `relevance` | string | 相关性 |
| `applicableProduct` | string | 模式适用产品 |
| `attackerAccessLocation` | string | 攻击者接入位置 |
| `attackComplexity` | string | 攻击复杂度 |
| `attackImpactDegree` | string | 攻击影响程度 |
| `riskAssessment` | string | 风险评估 |
| `modePrerequisites` | string | 模式预置条件 |
| `modeOperation` | string | 模式操作 |
| `defense` | string | 防御 |
| `detection` | string | 检测 |
| `respond` | string | 响应 |
| `restore` | string | 恢复 |
| `creator` | string | 创建人 |
| `createTime` | string | 创建时间 |
| `modifier` | string | 修改人 |
| `updateTime` | string | 修改时间 |
| `deleted` | int | 是否删除（0否/1是） |

**`funcReqFRAndTestSpecFTList` 项字段**（后端 `Ft`）：

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | long | 主键 ID |
| `ftNo` | string | 功能测试编号 |
| `ftUniqueNo` | string | 功能测试唯一编号 |
| `ftName` | string | 功能测试名称 |
| `ftDesc` | string | 功能测试描述 |
| `ftTestTag` | string | 功能测试标签 |
| `ftPurpose` | string | 功能测试目的 |
| `ftTestTool` | string | 功能测试工具 |
| `ftTestType` | string | 功能测试类型 |
| `ftParentTestNo` | string | 功能测试父测试编号 |
| `publicCaseNo` | string | 公共用例编号 |
| `ruleNo` | string | 规则编号 |
| `parentRuleNo` | string | 父规则编号 |
| `relatedRuleNo` | string | 相关规则编号 |
| `ruleUniqueNo` | string | 规则唯一编号 |
| `ruleName` | string | 规则名称 |
| `ruleTag` | string | 规则标签 |
| `ruleRange` | string | 规则范围 |
| `speiId` | string | SPEI ID |
| `deleted` | string | 是否删除 |
| `creator` | string | 创建者 |
| `createTime` | string | 创建时间 |
| `modifier` | string | 修改者 |
| `updateTime` | string | 修改时间 |

**--tp-type 枚举全集**（后端 NodeType 枚举，表示产生 TP 的活动页面）：

| 值 | 含义 |
|---|---|
| `RequirementAnalysis` | 测试需求分析 |
| `SceneAnalysis` | 场景分析 |
| `FeatureInteractionAnalysis` | 特性交互分析 |
| `TRFunctionInteractionAnalysis` | 功能交互分析(TR级) |
| `TSFunctionInteractionAnalysis` | TS功能交互分析 |
| `TestTypeInteractionAnalysis` | 测试类型交互分析 |
| `TestFactorAnalysis` | 测试因子分析 |
| `BusinessInterImplAnalysis` | 业务内部实现分析 |
| `BusinessSceneAnalysis` | 业务场景分析 |
| `TestTypeAnalysis` | 测试类型分析 |
| `DesignConstraintAnalysis` | 设计约束分析 |
| `TestabilityAnalysis` | 可测试性分析 |

**--tp-source-type 枚举全集**（后端 TpResourceType 枚举，区分活动页面的哪种资源产生 TP）：

| 值 | 含义 |
|---|---|
| `function_and_test_factor_type` | 功能交互设计-功能与测试因子 |
| `business_test_factor_type` | 基于业务内部实现设计-测试因子 |
| `business_scenario_factor` | 基于业务场景设计-场景因子 |
| `test_type_test_design_principle` | 测试类型交互设计-测试设计准则 |
| `test_type_test_factor_type` | 测试类型交互设计-测试因子 |
| `test_type_model_lib` | 测试类型交互设计-模式库 |

> **提示**：`--parent-tr-id` 可通过 `ts get-relative-tr --ts-id <TS ID>` 获取。`--idp-doc-id` 可从 `task list` 返回的 `idp_doc_id` 字段获取。

### TP→TC 数据组合算法（testdesign combination）

从 TP 的因子和取值生成 TC 组合用例。支持正交（全覆盖）和 PairWise（两两覆盖）两种算法。

#### 根据因子和混合力度获取组合结果

```bash
coretool-cli coretest testdesign combination result --parameter <因子JSON> --order <混合力度>
# 示例：正交组合（全覆盖，--order 0）
coretool-cli coretest testdesign combination result --parameter '{"OS":["Windows","Linux"],"Browser":["Chrome","Firefox"]}' --order 0
# 示例：PairWise组合（两两覆盖，--order 2，默认）
coretool-cli coretest testdesign combination result --parameter '{"OS":["Windows","Linux"],"Browser":["Chrome","Firefox"],"Network":["WiFi","4G"]}' --order 2
```

`--parameter` 为 stringArray（可多次指定）。也可用 `--parameter-file <文件路径>`（`-` 表示 stdin）。`--order`：0=正交，2=PairWise（默认2）。

#### 根据因子和约束获取组合结果

```bash
coretool-cli coretest testdesign combination result-with-constraints --parameter <因子JSON> --constraint <约束条件> --order <混合力度>
# 示例
coretool-cli coretest testdesign combination result-with-constraints --parameter '{"OS":["Windows","Linux"],"Browser":["Chrome","Firefox"]}' --constraint 'OS=Windows => Browser=Chrome' --order 2
```

`--constraint` 为 stringArray（可多次指定）。也可用 `--constraint-file <文件路径>`（`-` 表示 stdin）。

### 测试用例 TC（testdesign tc）

#### 查询 TP 下的 TC 列表

```bash
coretool-cli coretest testdesign tc list --version-pbi <版本PBI> --tp-id <TP ID>
# 示例
coretool-cli coretest testdesign tc list --version-pbi 266926538 --tp-id 18288
```

`--tp-id` 为 int 类型（必填），`--version-pbi` 为 string 类型（必填）。

#### 创建测试用例 TC

```bash
coretool-cli coretest testdesign tc create --tp-id <TP ID> --version-pbi <版本PBI> --name <用例名称> --case-id <用例ID> --creator <创建者> --owner <责任人>
# 示例：基础创建
coretool-cli coretest testdesign tc create --tp-id 18288 --version-pbi 266926538 --name "Windows+Chrome登录验证" --case-id TC_SKILL_001 --creator w30020094 --owner w30020094
# 示例：带可选参数 + AI生成标识
coretool-cli coretest testdesign tc create --tp-id 24830 --version-pbi 266926538 --name "AI生成用例验证" --case-id PCF_E2E_03_01 --creator w30020094 --owner w30020094 --atg-flag 3 --auto-type 1 --rank 1 --apply-version "V27.0.0" --precondition "系统已部署" --test-step "1. 执行验证" --expected-output "验证成功"
```

**参数**（CLI flag 对应后端 JSON key）：

| CLI flag | JSON key | 类型 | 必填 | 说明 |
|----------|----------|------|------|------|
| `--tp-id` | — | int | 是 | TP ID（URL 参数） |
| `--version-pbi` | `pbi` | string | 是 | 版本 PBI |
| `--name` | `name` | string | 是 | 用例名称 |
| `--case-id` | `caseId` | string | 是 | 用例编号（仅字母数字下划线） |
| — | `caseIdPrefix` | string | 否 | 用例编号前缀（自动从 caseId 拆分） |
| — | `caseIdConnSign` | string | 否 | 用例编号连接符（自动从 caseId 拆分） |
| — | `caseIdNumber` | string | 否 | 用例编号起始值（自动从 caseId 拆分） |
| `--creator` | `creator` | string | 是 | 创建者 |
| — | `modifier` | string | 否 | 修改者（自动填 creator） |
| `--owner` | `owner` | string | 是 | 责任人 |
| `--description` | `description` | string | 否 | 用例描述 |
| `--test-type` | `testCaseType` | string | 否 | 用例类型 |
| `--test-activity` | `testCaseActivity` | string | 否 | 测试活动 |
| `--rank` | `rank` | string | 否 | 用例等级（`0`=Level0, `1`=Level1, `2`=Level2, `3`=Level3, `4`=Level4, `5`=LevelT） |
| `--precondition` | `preparation` | string | 否 | 预置条件 |
| `--test-step` | `testStep` | string | 否 | 测试步骤 |
| `--expected-output` | `expectOutput` | string | 否 | 预期结果 |
| `--post-process` | `postProcess` | string | 否 | 后置条件 |
| `--case-id-type` | `caseIdType` | string | 否 | 用例编号取值类型：`input_begin` 或 `end_begin` |
| `--auto-type` | `autoType` | int | 否 | 自动化类型（0=手动，1=自动） |
| `--status` | `status` | string | 否 | 状态：`archived` / `notArchived` / `draft` |
| `--apply-version` | `applyVersion` | string | 否 | 使用版本 |
| `--operation-type` | `operationType` | string | 否 | 操作类型 |
| `--case-remark` | `caseRemark` | string | 否 | 备注 |
| `--atg-flag` | `atgFlag` | string | 否 | ATG 生成标识：`0`=非AI生成、`1`=AI TP生成、`2`=AI Factor生成、`3`=AI生成 |
| `--test-env-id` | `testEnvironmentId` | string | 否 | 测试环境 ID |
| `--test-env-type` | `testEnvironmentType` | string | 否 | 测试环境类型 |
| `--execution-platform` | `executionPlatform` | string | 否 | 执行平台 |
| `--test-case-feature` | `testCaseFeature` | string | 否 | 用例特性 |
| `--test-case-author` | `testCaseAuthor` | string | 否 | 用例作者 |
| `--applied-market` | `appliedMarket` | string | 否 | 适用市场 |
| `--threshold-flag` | `thresholdFlag` | string | 否 | 门槛标识 |
| `--vbs-flag` | `vbsFlag` | string | 否 | 精选用例标识 |

#### 更新单条测试用例 TC

```bash
coretool-cli coretest testdesign tc update --id <TC ID> --name <用例名称> --precondition <预置条件> --test-step <测试步骤> --expected-output <预期结果>
# 示例：flag 模式（更新基本信息 + AI标识）
coretool-cli coretest testdesign tc update --id 144337 --name "AI生成用例验证" --precondition "系统已部署" --test-step "1. 执行验证" --expected-output "验证成功" --atg-flag 3 --auto-type 1 --apply-version "V27.0.0" --post-process "清理环境"
# 示例：--data JSON 模式
coretool-cli coretest testdesign tc update --data '{"id":144337,"name":"AI生成用例验证_JSON","preparation":"新预置条件","testStep":"新测试步骤","expectOutput":"新预期结果","atgFlag":"3","autoType":1,"applyVersion":"V27.0.0"}'
# 示例：--data-file 文件模式
coretool-cli coretest testdesign tc update --data-file tc_update.json
```

支持两种输入模式（互斥）：
- **flag 模式**：通过独立 CLI flag 传参
- **JSON 模式**：`--data <JSON>` 或 `--data-file <文件路径>` 直接传完整请求体

**Body 参数**（flag 模式对应 CLI flag，JSON 模式对应 JSON key）：

| CLI flag | JSON key | 类型 | 必填 | 说明 |
|----------|----------|------|------|------|
| `--id` | `id` | int | 是 | TC ID |
| `--case-id` | `caseId` | string | 否* | 用例编号（仅字母数字下划线） |
| — | `caseIdPrefix` | string | 否 | 用例编号前缀（自动从 caseId 拆分） |
| — | `caseIdNumber` | string | 否 | 用例编号起始值（自动从 caseId 拆分） |
| `--name` | `name` | string | 是* | 用例名称 |
| `--description` | `description` | string | 否 | 用例描述（始终写入，即使为空） |
| `--test-type` | `testCaseType` | string | 否 | 用例类型 |
| `--test-activity` | `testCaseActivity` | string | 否 | 测试活动 |
| `--apply-version` | `applyVersion` | string | 否 | 使用版本 |
| `--test-env-id` | `testEnvironmentId` | string | 否 | 测试环境 ID |
| `--test-env-type` | `testEnvironmentType` | string | 否 | 测试环境类型 |
| `--execution-platform` | `executionPlatform` | string | 否 | 执行平台 |
| `--test-case-feature` | `testCaseFeature` | string | 否 | 用例特性 |
| `--test-case-author` | `testCaseAuthor` | string | 否 | 用例作者 |
| `--operation-type` | `operationType` | string | 否 | 操作类型 |
| `--auto-type` | `autoType` | int | 否 | 自动化类型（0=手动，1=自动） |
| `--rank` | `rank` | string | 否 | 用例等级（`0`=Level0, `1`=Level1, `2`=Level2, `3`=Level3, `4`=Level4, `5`=LevelT） |
| `--precondition` | `preparation` | string | 是* | 预置条件 |
| `--test-step` | `testStep` | string | 是* | 测试步骤 |
| `--expected-output` | `expectOutput` | string | 是* | 预期结果 |
| `--post-process` | `postProcess` | string | 否 | 后置条件 |
| `--status` | `status` | string | 否 | 状态：`archived` / `notArchived` / `draft` |
| `--case-remark` | `caseRemark` | string | 否 | 备注（始终写入，即使为空） |
| `--applied-market` | `appliedMarket` | string | 否 | 适用市场 |
| `--threshold-flag` | `thresholdFlag` | string | 否 | 门槛标识 |
| `--vbs-flag` | `vbsFlag` | string | 否 | 精选用例标识 |
| `--atg-flag` | `atgFlag` | string | 否 | ATG 生成标识：`0`=非AI生成、`1`=AI TP生成、`2`=AI Factor生成、`3`=AI生成 |

> *标记"是*"的字段为后端校验必填：`id`、`name`、`preparation`、`testStep`、`expectOutput` 缺一则返回校验错误。flag 模式下这 5 个字段必须同时传入。JSON 模式下请求体需包含全部 5 个字段。后端 MyBatis 动态 SQL 仅更新非空字段（`description` 和 `caseRemark` 除外，始终写入）。

JSON 模式：`--data <JSON>` 或 `--data-file <文件路径>`（与 flag 模式互斥）。JSON 字段使用后端 camelCase（如 `preparation`、`testStep`、`expectOutput`）。

> **注意**：后端校验 `name`、`preparation`（预置条件）、`testStep`（测试步骤）、`expectOutput`（预期结果）不能为空。flag 模式下这四个字段必须同时传入。后端 MyBatis 动态 SQL 仅更新非空字段（`description` 和 `caseRemark` 除外，始终写入）。

### IDP 文档（testdesign idp）

#### 查询 IDP 文档章节

```bash
coretool-cli coretest testdesign idp topic list --idp-doc-id <IDP文档ID> --user-id <用户ID> --activity-name <活动名称>
# 示例
coretool-cli coretest testdesign idp topic list --idp-doc-id 5dcdfe1e-9114-48c7-8abd-aa5222f6312f --user-id w30020094 --activity-name 场景分析 --parent-activity-id 3861 --parent-activity-name "Nsmf/Nupf链路容灾功能补齐-5GC-UPCF" --parent-activity-type TR
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
coretool-cli coretest testdesign idp source-data write --topic-id <章节ID> --user-id <用户ID> --display-type row-table --title <数据标题>
# 示例：新增表格
coretool-cli coretest testdesign idp source-data write --topic-id bfeb5299-ff2c-4db3-a6af-a71da527788e --user-id w30020094 --display-type row-table --title "测试类型交互设计"

# 文本写入（flags 模式）
coretool-cli coretest testdesign idp source-data write --topic-id <章节ID> --user-id <用户ID> --display-type text --title <数据标题>
# 示例：新增文本
coretool-cli coretest testdesign idp source-data write --topic-id bfeb5299-ff2c-4db3-a6af-a71da527788e --user-id w30020094 --display-type text --title "测试类型交互设计"

# --data JSON 模式：表格写入（含完整 table_content）
coretool-cli coretest testdesign idp source-data write --data '{"topic_id":"bfeb5299-ff2c-4db3-a6af-a71da527788e","user_id":"w30020094","display_type":2,"title":"测试表格","table_content":{"headers":[{"content":"参数","rowspan":1,"colspan":1},{"content":"值","rowspan":1,"colspan":1}],"rows":[[{"content":"模式","rowspan":1,"colspan":1},{"content":"自动化","rowspan":1,"colspan":1}]],"col_widths":["100","100"]}}'

# --data JSON 模式：文本写入
coretool-cli coretest testdesign idp source-data write --data '{"topic_id":"bfeb5299-ff2c-4db3-a6af-a71da527788e","user_id":"w30020094","display_type":3,"title":"测试类型交互设计","text_content":"这是通过CLI写入的文本内容"}'

# --data JSON 模式：覆盖写入（传入已有 source_value_uuid）
coretool-cli coretest testdesign idp source-data write --data '{"topic_id":"bfeb5299-ff2c-4db3-a6af-a71da527788e","user_id":"w30020094","display_type":3,"title":"测试类型交互设计","source_value_uuid":"e5d9e605-89b6-63d1-eb26-018865eed44f-1a03bfae182","text_content":"覆盖后的新内容"}'
```

flags 模式必填：`--topic-id`（string）、`--user-id`（string）、`--display-type`（可选值：`row-table`、`text`、`file`）、`--title`（string）。可选：`--source-value-uuid`（未提供时自动生成）。

`--data <JSON>` 或 `--data-file <文件路径>` 模式：直接传入完整请求体 JSON，与 flags 模式互斥。JSON 字段：`topic_id`、`user_id`、`display_type`（2=row-table, 3=text, 6=file）、`title`、`source_value_uuid`（可选，不传为新增，传已有值为覆盖）、`table_content`（display_type=2 时使用，含 headers/rows/col_widths）、`text_content`（display_type=3 时使用，纯文本字符串）、`file_content`（display_type=6 时使用，ECM 文件 ID）。

输出字段：`TOPIC_ID`、`SOURCE_VALUE_UUID`、`DISPLAY_TYPE`、`TITLE`、`WRITTEN`。

### CIDA 操作（testdesign cida）

CIDA 是 TMSS 的配置与目录管理平台，支持查询版本配置、浏览版本目录树、创建目录/用例实体。

**tmss-tenant 参数说明**：`--tmss-tenant` 必须使用 TMSS 映射名（如 `TMSS-SZV04`），由 `tmssAddress` 经后端 `TmssTenantConfig` 映射表推导。不能用租户 ID（如 `cloudCoreNetwork2022Auth`）。映射关系示例：`http://szvtms04.tmss.huawei.com` → `TMSS-SZV04`。

#### 查询 CIDA 版本配置

```bash
coretool-cli coretest testdesign cida get-config --version-pbi <版本PBI>
# 示例
coretool-cli coretest testdesign cida get-config --version-pbi 266926538
```

`--version-pbi`（`-p`）为 string（必填）。返回 CIDA 配置信息，包含 `pbi_version_name`、`tmss_address`、`cversion_path`、`requirement_domain_id`/`scene_domain_id`/`function_domain_id` 等域 ID，以及 `config_info`（嵌套 JSON，含 `tmssVersions`/`tmssUrl`/`sceneDomain`/`functionDomain` 等完整配置）。

`config_info.tmssVersions` 数组中每项含 `uri`（用作 `cida list` 的 `--version-uri`）、`cidaVersionUri`、`name`（版本名）、`path` 等字段。

输出字段：`ID`、`PBI_VERSION_NAME`、`TMSS_ADDRESS`、`C_VERSION_PATH`、`PROJECT_ID`。

#### 浏览 CIDA 版本目录树

```bash
coretool-cli coretest testdesign cida list --tmss-tenant <TMSS映射名> --version-uri <目录URI>
# 示例：浏览版本根目录
coretool-cli coretest testdesign cida list --tmss-tenant TMSS-SZV04 --version-uri 045n1149agtdb
# 示例：浏览子目录（递归）
coretool-cli coretest testdesign cida list --tmss-tenant TMSS-SZV04 --version-uri 045n1149agtdh
```

`--tmss-tenant` 为 string（必填，TMSS 映射名如 `TMSS-SZV04`）、`--version-uri` 为 string（必填，来自 `cida get-config` 返回的 `config_info.tmssVersions[].uri` 或上级目录的 `real_uri`）。userId 从认证上下文自动获取。

输出字段：`NAME`、`RESOURCE_TYPE`（`Container`/`TestItem`/`TestCase`/`RMResource`/`Version`）、`REAL_URI`、`URI`、`IS_PARENT`。

递归浏览：将返回的 `REAL_URI` 作为下一次调用的 `--version-uri` 即可遍历子目录。

#### 创建 CIDA 实体

```bash
# flags 模式
coretool-cli coretest testdesign cida create --tmss-tenant <TMSS映射名> --parent-uri <父目录URI> --type <实体类型> --parent-path <父目录路径> --name <实体名称> [--number <用例编号>] [--rank <级别>] [--auto-type <自动化类型>] [--status <状态>]
# 示例：创建 test-item 目录
coretool-cli coretest testdesign cida create --tmss-tenant TMSS-SZV04 --parent-uri 045n1149agtdh --type test-item --parent-path "/00ysbq5reib/045n1149agtdb/045n1149agtdh/" --name "CLI-test-item"
# 示例：创建 test-case（需 --number）
coretool-cli coretest testdesign cida create --tmss-tenant TMSS-SZV04 --parent-uri 040h11ll2761d --type test-case --parent-path "/00ysbq5reib/045n1149agtdb/045n1149agtdh/040h11ll2761d/" --name "测试用例1" --number TC_001

# --data JSON 模式
coretool-cli coretest testdesign cida create --tmss-tenant TMSS-SZV04 --parent-uri 045n1149agtdh --data '{"typeName":"TestItem","parentPath":"/00ysbq5reib/045n1149agtdb/045n1149agtdh/","content":{"name":"CLI-test-item","type":"TestItem"}}'
```

必填：`--tmss-tenant`（string，TMSS 映射名）、`--parent-uri`（string，父目录的 realURI）、`--type`（可选值：`test-item`、`test-case`）、`--parent-path`（string，从版本根到父目录的完整路径）、`--name`（string，实体名称）。

`--type` 为 `test-case` 时 `--number` 必填。

可选：`--content-type`（默认同 `--type`，可选值：`test-item`、`test-case`）、`--rank`（可选值：`level0`、`level1`、`level2`、`level3`、`level4`、`level-t`）、`--auto-type`（可选值：`manual`、`auto`）、`--status`（可选值：`archived`、`not-archived`、`draft`）、`--author`、`--logic-case-owner`、`--design-note`、`--preparation`、`--test-step`、`--expect-output`。

高级输入：`--data <JSON>` 或 `--data-file <文件路径>`（与独立 flag 互斥）。

CLI 枚举在 adapter 层映射为后端值：`test-item`↔`TestItem`、`test-case`↔`TestCase`、`level0`→`6`/`level1`→`1`/`level2`→`2`/`level3`→`3`/`level4`→`4`/`level-t`→`5`、`manual`→`0`/`auto`→`1`、`not-archived`→`notArchived`。

输出字段：`NAME`、`NUMBER`、`TYPE`、`REAL_URI`、`VERSION_NAME`。

### 归档用例（testdesign archived-case）

将本地 TC 归档到 CIDA 平台，或查询已归档用例详情。

**前置步骤**：归档前需通过 `cida get-config` 获取配置参数，通过 `cida list` 找到或 `cida create` 创建目标 TestItem 目录作为归档目标。

**重要约束**：
- `--parent-uri` 必须是 TestItem 目录的 realURI，不能是 Cases 容器的 realURI（后端会报"不能添加测试用例到测试用例容器下"）
- `--ts-id` 必填，否则后端 `TreeNodeDao.getDesignTaskIdByTsId` 返回 null 致 NPE
- `--tmss-tenant` 必须使用 TMSS 映射名（如 `TMSS-SZV04`），不能用租户 ID

#### 归档测试用例到 CIDA

```bash
# flags 模式
coretool-cli coretest testdesign archived-case run --tmss-url <TMSS地址> --version-uri <版本URI> --parent-uri <父目录URI> --parent-path <父目录路径> --tr-id <TR ID> --tc-id <TC ID> [--tc-id <TC ID2>] --tmss-tenant <TMSS映射名> --ts-id <TS ID>
# 示例：归档单条 TC
coretool-cli coretest testdesign archived-case run --tmss-url "http://szvtms04.tmss.huawei.com" --version-uri 045n1149agtdb --parent-uri 040h11ll2761d --parent-path "/00ysbq5reib/045n1149agtdb/045n1149agtdh/040h11ll2761d/" --tr-id 3611 --tc-id 142617 --ts-id 38058 --project-id "2b88f0b325154c7582a71fa02b8cd322" --tmss-tenant TMSS-SZV04 --requirement-domain-id "2091981156" --scene-domain-id "1200734448940240896" --function-domain-id "1200734448940240896"

# --data JSON 模式
coretool-cli coretest testdesign archived-case run --tmss-tenant TMSS-SZV04 --parent-uri 040h11ll2761d --data '{"tmssUrl":"http://szvtms04.tmss.huawei.com","versionUri":"045n1149agtdb","parentUri":"040h11ll2761d","parentPath":"/00ysbq5reib/045n1149agtdb/045n1149agtdh/040h11ll2761d/","trId":3611,"tcIds":[142617],"projectId":"2b88f0b325154c7582a71fa02b8cd322","tmssTenant":"TMSS-SZV04","tsId":38058,"requirementDomainId":"2091981156","sceneDomainId":"1200734448940240896","functionDomainId":"1200734448940240896"}'
```

必填：`--tmss-url`（string，TMSS 服务器 URL，从 `cida get-config` 的 `tmss_address` 获取）、`--version-uri`（string，CIDA 版本 URI，从 `cida get-config` 的 `config_info.tmssVersions[].uri` 获取）、`--parent-uri`（string，目标 TestItem 目录的 realURI）、`--parent-path`（string，从版本根到目标目录的完整路径）、`--tr-id`（int64，TC 所属的 TR ID）、`--tc-id`（int64Slice，可多次指定，至少一个）、`--tmss-tenant`（string，TMSS 映射名）、`--ts-id`（int64，TC 所属的 TS ID，必填否则后端 NPE）。

可选：`--project-id`、`--tp-id`、`--requirement-domain-id`、`--scene-domain-id`、`--function-domain-id`（均来自 `cida get-config` 返回）。

高级输入：`--data <JSON>` 或 `--data-file <文件路径>`（与独立 flag 互斥，此时 `--tmss-tenant` 和 `--parent-uri` 仍需单独传入）。

输出字段：`RESULT`（OK/FAILED）、`TC_COUNT`、`FAILED`。

#### 查询已归档用例详情

```bash
# --uri 模式
coretool-cli coretest testdesign archived-case get --tmss-tenant <TMSS映射名> --uri <用例URI> [--uri <用例URI2>]
# 示例
coretool-cli coretest testdesign archived-case get --tmss-tenant TMSS-SZV04 --uri 04vh11lfqu10p --uri 04tp11lfqu18p

# --data JSON 模式（传入 URI 数组）
coretool-cli coretest testdesign archived-case get --tmss-tenant TMSS-SZV04 --data '["04vh11lfqu10p","04tp11lfqu18p"]'
```

必填：`--tmss-tenant`（string，TMSS 映射名）、`--uri`（stringArray，至少一个）或 `--data`/`--data-file`（JSON 字符串数组，与 `--uri` 互斥）。

输出字段：`URI`。

---

## Common 通用查询

跨平台通用查询接口，包含版本 PBI 查询和 CIDA 配置查询。

### 版本 PBI 查询（common version-pbi）

#### 通过 C 版本名称查询 versionPBI

```bash
coretool-cli coretest common version-pbi --name <版本名称>
# 示例
coretool-cli coretest common version-pbi --name "UPCF 27.0.0"
```

`--name`（`-n`）为 string（必填），传入 C 版本名称。

输出字段：`VERSION_PBI`（版本 PBI 编号，int64）。

服务端点：`https://coreaidi.inhuawei.com`，接口路径 `/versioninfo/v2/get_version_pbi_by_name?versionName=<名称>`，返回纯数字（非 WebReturn 信封）。

### CIDA 配置查询（common cida-config）

#### 通过 groupName 查询 CIDA 配置

```bash
coretool-cli coretest common cida-config --group-name <群组名称>
# 示例
coretool-cli coretest common cida-config --group-name "UPCF测试组"
```

`--group-name`（`-g`）为 string（必填），传入群组名称。后端先通过 groupName 查询 groupId，再返回该组下的 CIDA 配置列表。

输出字段：`ID`、`PRODUCT_NAME`、`TICC_SERVICE_ADDRESS`、`TMSS_SERVICE_ADDRESS`、`LCM_SERVICE_ADDRESS`、`GROUP_ID`。

服务端点：`https://coretestresult.cloudspider.rnd.huawei.com`，接口路径 `/api/v1/cidaConfig/getCidaConfigsByGroupName/<groupName>`，标准 WebReturn 信封。
