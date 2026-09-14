# TS、TP、TC Markdown 文件说明

替换生成流程时，按下面的位置和格式输出文件即可。标题、表头和列顺序不要改；示例中的业务内容换成实际内容。文件使用 UTF-8，表格单元格不要包含竖线，表格数据行之间不要插空行。

## 一、TS：测试规格文件

### 文件位置

相对扩展包根目录：

```text
.design_output/<design_task_id>/TR_<tr_id>/test_specs/<TR名称>测试规格.md
```

一个 TR 只生成一份，里面包含全部普通 TS 和平台已有的 DFX TS。TR 名称不适合做文件名时，使用 TR 编号，但正文中的 TR 名称保持原值。

### Markdown 格式

前半部分按下面的标题写分析内容。每个标题下都要有正文，不能只写标题，因为归档时会读取这些内容。

```markdown
## 概述
### 被测对象概述
填写被测产品和本次需求的范围。

### 测试方案概述
填写整体测试思路。

## 测试设计策略
### 特性风险分析（RBT）
填写主要风险。

### 测试重点难点分析
填写测试重点和难点。

### 分层测试策略
填写各层分别验证什么。

### 底层硬件/组网差异测试策略分析
填写硬件和组网差异需要怎样覆盖。

### 网元形态差异测试策略分析
填写不同网元形态需要怎样覆盖。

## 场景分析
填写业务场景分析。

## 测试类型分析
填写性能、可靠性等测试方向。

## 特性交互分析
填写与其他特性的交互。

## 功能交互分析
填写与其他功能的交互。

## 设计约束分析
填写参数、边界和其他约束。
```

有平台 DFX TS 时，在后面补充以下部分。总标题只写一次，每个 DFX TS 按真实平台 ID 各写一段。DFX 不放进下面的“TS 清单”。

```markdown
## DFX TS 测试规格

### DFX TS：38058

| 字段 | 内容 |
|---|---|
| platform_ts_id | 38058 |
| ts_name | 性能测试 |
| ts_type | performance |
| requirement_ids | IR001,SR002 |
| description | 当前TR的性能验证范围与目标 |
| resolve_description | 性能验证重点和约束 |
```

文件最后放固定表格：

```markdown
## 平台写入数据

### TR

| 字段 | 值 |
|---|---|
| tr_name | 链路容灾功能补齐 |
| description | 当前TR的原始描述 |
| resolve_description | 当前TR的原始解决描述 |
| requirement_ids | IR001,SR002 |
| function_numbers | FUNC001 |
| feature_numbers | FEATURE001 |

### TS 清单

| ts_name | ts_type | requirement_ids | description | resolve_description |
|---|---|---|---|---|
| 链路故障后的重选控制 | constraint | IR001 | 验证重选次数和周期约束 | 覆盖边界、定时和失败处理 |
```

“TS 清单”每行是一个普通 TS，只允许 `scene/function/feature/constraint` 四种类型。

### 字段来源

| 字段或内容 | 从哪里来 |
|---|---|
| 前半部分的分析正文 | 根据当前 TR 的需求及 `sr_specs/` 下的 SR 规格生成 |
| TR 表 `tr_name` | `tr_info.json.tr_name`，照原文填写 |
| TR 表 `description` | `tr_info.json.description`，照原文填写 |
| TR 表 `resolve_description` | `tr_info.json.resolve_description`，照原文填写 |
| TR 表 `requirement_ids` | `tr_info.json.requirements[].requirement_number` 的全部需求编号，去重后用英文逗号连接 |
| TR 表 `function_numbers` | `tr_info.json.relation_function` |
| TR 表 `feature_numbers` | `tr_info.json.relation_feature` |
| 普通 TS `ts_name` | 根据需求拆分出的测试规格名称 |
| 普通 TS `ts_type` | 根据规格内容选择 scene、function、feature 或 constraint |
| 普通 TS `requirement_ids` | 这个 TS 对应的当前 TR 需求编号，至少一个，用英文逗号连接 |
| 普通 TS `description` | 生成这个 TS 的测试范围和目标 |
| 普通 TS `resolve_description` | 生成这个 TS 的测试重点和约束 |
| DFX `platform_ts_id/ts_name/ts_type` | `test_specs/platform_ts.json` 中的平台查询结果 |
| DFX `requirement_ids` | 当前 TR 的全部直接关联需求编号 |
| DFX `description/resolve_description` | 结合当前 TR 需求，生成该 DFX 的范围、目标和重点 |

TS 拆分按 [ts-split.md](../.testagent/rules/ts-split.md) 填写，详细格式以 [测试规格生成规则](../.testagent/skills/test-spec-analysis/SKILL.md) 为准。

## 二、TP：测试点设计文件

### 文件位置

```text
.design_output/<design_task_id>/TR_<tr_id>/test_design/ts_<NN>_test_design.md
```

每个 TS 一份。`NN` 是 `test_specs/ts_catalog.json` 中的稳定序号，例如 `TS_01` 对应 `ts_01_test_design.md`，不是平台 TS ID。当前文件名使用两位序号。

### Markdown 格式

前半部分按 TS 类型选择标题，标题下写具体测试点设计，不要留空，也不要增加当前 TS 不适用的设计标题。

| TS 类型 | 要写的二级标题 |
|---|---|
| 平台 DFX | `## 测试类型交互设计`、`## 基于业务内部实现的设计` |
| function / feature | `## 功能交互设计`、`## 基于业务内部实现的设计` |
| scene | `## 基于业务场景的设计`、`## 基于业务内部实现的设计` |
| constraint | `## 基于业务内部实现的设计` |

文件最后放元信息和 TP 表，每个测试点一行：

```markdown
## 平台写入数据 - 元信息

| 字段 | 值 |
|---|---|
| tr_name | 链路容灾功能补齐 |
| ts_name | 链路故障后的重选控制 |
| ts_type | constraint |

## 平台写入数据 - TP

| tp_id_temp | tpName | description | resolveDescription | rank | tsId | parentTrId | tpType | tpSourceType | requirement_ids | dimension | raw_factors |
|---|---|---|---|---|---|---|---|---|---|---|---|
| TP.01.01.01 | 重选次数边界控制 | 验证最大值和最小值对应的重选行为 | | 1 | <PENDING> | <PENDING> | SceneAnalysis | 基于业务内部实现设计—测试因子 | | 基于业务内部实现 | |
```

### 字段来源

| 字段 | 从哪里来 / 怎样填 |
|---|---|
| 元信息 `tr_name` | `test_specs/tr_ts.json.tr.tr_name` |
| 元信息 `ts_name` | 当前 TS 在 `ts_catalog.json` 中的名称 |
| 元信息 `ts_type` | 当前 TS 在 `ts_catalog.json` 中的类型 |
| `tp_id_temp` | 生成一个稳定的本地测试点编号，同一个 TS 内不能重复 |
| `tpName` | 根据当前 TS 规格生成具体测试点名称 |
| `description` | 生成测试点的条件、目标和验证范围；换行用 `<br>` |
| `resolveDescription` | 当前留空 |
| `rank` | 测试点的 Level 数字，例如 Level1 填 `1`，范围 0–4 |
| `tsId` | 固定填 `<PENDING>` |
| `parentTrId` | 固定填 `<PENDING>` |
| `tpType/tpSourceType/dimension` | 按下面的设计维度表填写，不能留空 |
| `requirement_ids` | 当前 TP 表留空 |
| `raw_factors` | 当前设计选中的关联因子原始列表，用英文逗号连接；没有因子就留空。现有归档用于因子名称参数，不要自行换成平台 ID |

设计维度取值：

| 正文标题 | dimension | tpType | tpSourceType |
|---|---|---|---|
| 基于业务场景的设计 | 基于业务场景 | BusinessSceneAnalysis | 基于业务场景设计—场景因子 |
| 基于业务内部实现的设计 | 基于业务内部实现 | SceneAnalysis | 基于业务内部实现设计—测试因子 |
| 功能交互设计 | 功能交互设计 | RequirementAnalysis | 功能交互设计-功能与测试因子 |
| 测试类型交互设计 | 测试类型交互设计 | RequirementAnalysis | 测试类型交互设计—测试因子 |

普通 TS 的设计内容来自 `tr_ts.json` 中对应规格；DFX 的设计内容来自 TS Markdown 中按平台 ID 对应的 DFX 规格。设计正文和 TP 表的内容要一致。

## 三、TC：测试用例文件

### 文件位置

```text
.design_output/<design_task_id>/TR_<tr_id>/test_design/ts_<NN>_test_cases.md
```

每个 TS 一份，和 TP 文件在同一目录、使用同一个两位序号。例如 `ts_01_test_design.md` 必须配套 `ts_01_test_cases.md`。

### Markdown 格式

前半部分可以按测试点分组展示用例，说明用例名称、等级、预置条件、步骤和预期结果。文件最后放固定 TC 表，每个用例一行：

```markdown
## 平台写入数据 - TC

| tc_id_temp | tp_id_temp | name | rank | preparation | test_step | expect_output | case_id | TestType | AutoType | envtype | DesignNote |
|---|---|---|---|---|---|---|---|---|---|---|---|
| TC.01 | TP.01.01.01 | [0101]重选次数边界控制 | 1 | 1. 系统运行正常<br>2. 配置最小重选次数 | 1. 注入链路故障<br>2. 观察重选次数 | 1. 重选次数符合配置<br>2. 超限后停止重选 | UPCF_RESELECT_01_01 | 1 | 0 | | 验证链路故障后系统按次数边界约束执行并停止重选 |
```

每个 TP 至少生成一个 TC。`tp_id_temp` 必须引用同一个 TS 的 TP 表中已有的编号。TC 文件不用重复填写 TR/TS 元信息，生成 JSON 时会从对应 TP 文件读取。

### 字段来源

| 字段 | 从哪里来 / 怎样填 |
|---|---|
| `tc_id_temp` | 生成一个稳定的本地用例编号，同一个 TS 内不能重复 |
| `tp_id_temp` | 对应 TP 文件里的 `tp_id_temp`，原样填写 |
| `name` | 根据对应 TP 的验证目标生成具体用例名称 |
| `rank` | 用例的 Level 数字，范围 0–4 |
| `preparation` | 生成执行用例前需要满足的条件 |
| `test_step` | 生成具体可执行的操作步骤，覆盖 TP 指定的参数和范围 |
| `expect_output` | 生成对应步骤的可检查结果 |
| `case_id` | 生成完整用例编号，例如 `UPCF_RESELECT_01_01`，保留末尾两段数字 |
| `TestType` | 根据用例验证目标选择测试类型编码，无法判断填 `1` |
| `AutoType` | 明确自动化填 `1`；非自动化或无法判断填 `0` |
| `envtype` | 当前留空 |
| `DesignNote` | 根据测试目的生成一句简短描述，不能留空，也不要直接复制用例名称 |

预置条件、步骤和预期结果中的多条内容用 `1. 内容<br>2. 内容` 连接。表格内容要和前面的用例说明一致。

TP/TC 的完整填写规则见 [tp-tc-output.md](../.testagent/rules/tp-tc-output.md)，设计维度与来源取值见 [tp-tc-design-logic.md](../.testagent/rules/tp-tc-design-logic.md)。不要在固定表格里新增或删除列。
