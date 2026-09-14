# TS / TP / TC Markdown 产物兼容契约

> 面向替换 Explore、测试规格分析或 Design 生成流程的扩展包开发者。
> 基线：`develop` 提交 `7bab4dcefa7301ffe536ce49d139c1e79803c4ec`，核对日期 2026-09-14。
> 本文记录当前已落地的格式和消费行为，不把工具侧分支或讨论中的新方案当作当前接口。只要保持本契约，生成算法、提示词、Agent 编排可以替换；JSON 提取及 Archive 无须因 Markdown 格式变化而改造。

## 1. 替换边界

需要同时兼容三类消费者：

| 消费者 | 读取对象 | 必须保持 |
|---|---|---|
| `build_tr_json.py` | 测试规格 Markdown 的固定表格区、`tr_info.json` | TR 行名、TS 列顺序、章节锚点、需求归属 |
| `build_tp_tc_json.py` | 同一 TS 的 design / cases Markdown | 固定元信息行名、TP/TC 列顺序、配对文件名 |
| Archive 对象阶段 / 文档阶段 | JSON、catalog、状态 / Markdown 固定叙述标题 | 稳定对象键、父子引用、JSON 路径 / 非空章节与固定标题 |

**JSON 能生成，不代表 Archive 一定兼容。** 表头改名可能未被脚本发现；叙述标题缺失可能只在在线文档同步阶段报错；悬空的 TP 引用可能直到归档才失败。替换方必须自行完成第 9 节验收。

本文不要求保留原有 Agent 数量或分析算法；如果连 Init / Explore 上下文也替换，必须另行满足 `tr_info.json`、`cida_info.json`、`platform_ts.json`、`tr_ts.json` 和 `ts_catalog.json` 的接口。仅输出三份 Markdown、缺少这些配套文件，不能直接进入现有完整链路。

## 2. 生成位置与命名

所有路径相对**扩展包仓库根目录** `<root>`，不是执行脚本时的任意工作目录。

| 产物 | 标准位置 | 当前生成职责 |
|---|---|---|
| TS 测试规格 Markdown（整 TR 一份） | `.design_output/<design_task_id>/TR_<tr_id>/test_specs/<TR名称>测试规格.md` | Explore → `test-spec-analysis` |
| TR / 普通 TS JSON | 同目录 `test_specs/tr_ts.json` | Explore 确认后 → `build_tr_json.py` |
| 平台 TS 查询快照 | 同目录 `test_specs/platform_ts.json` | Explore 保存查询结果 |
| 统一稳定 TS 编号目录 | 同目录 `test_specs/ts_catalog.json` | `build_ts_catalog.py` |
| TP 设计 Markdown（每 TS 一份） | `test_design/ts_<NN>_test_design.md` | Design → `test-design` |
| TC Markdown（每 TS 一份） | `test_design/ts_<NN>_test_cases.md` | Design → `test-design` |
| TP / TC JSON | `test_design/ts_<NN>_tp.json`、`test_design/ts_<NN>_tc.json` | `build_tp_tc_json.py` |
| 归档状态 | 同 TR 目录 `archive/archive_state.json` | Explore TS-only / Archive |

表中 `test_design/` 完整前缀均为 `.design_output/<design_task_id>/TR_<tr_id>/`。

命名要求：

- TS 规格不是每 TS 一份独立文件；整 TR 的普通 TS 和平台 DFX 规格放在同一份 Markdown。
- TR 名称需做路径安全处理；不适合文件名时用 `tr_no`，但正文和元信息中的真实 `tr_name` 不得改写。
- `NN` 来自 `ts_catalog.json.items[].ts_key`，例如 `TS_01` → `ts_01_test_design.md`；不得用真实平台 ID 生成 `ts_38490_...`。
- 当前 TP/TC 脚本文件名正则为 `^ts_(\d{2})_test_design\.md$`：只识别两位序号。超过 99 个 TS 是当前脚本的兼容边界，不能仅修改文件名解决。
- design 与 cases 必须同目录、同序号成对存在。缺 cases 时批量扫描会警告并跳过该 TS。
- 禁止写入扩展包根目录、`corespec/changes/`、旧版按需求编号分目录的结构或自定义输出目录。

稳定编号由 catalog 按“平台 DFX 在前、普通 TS 在后”顺序建立。普通 TS 的 `tr_ts_index` 为 `tr_ts.json.test_specs[]` 的 **0 基索引**；DFX 的规格按 `platform_ts_id` 定位。设计期间不得重新编号或重排 catalog，否则历史归档状态和对象键会错位。

## 3. 通用 Markdown 编码和表格规则

- 输出可读 UTF-8，建议无 BOM；现有读取脚本兼容 UTF-8 BOM。
- 固定锚点使用原文、指定标题级别，独占一行。不得改名、增加编号前缀或放入代码块。
- 固定章节只出现一次；章节下第一张表必须是指定表格，不能先放摘要表。
- 表头、列数、列顺序必须不变；数据行逐格填写，一条对象一行。
- 表格数据行之间不插空行、注释或非表格文本；现有解析器遇到这些内容会结束读取。
- 单元格禁止原始 `|`。解析器直接按 `|` 切分，Markdown 的 `\|` 并不能解决；用其他标点替代。
- 固定表内不要使用跨行单元格。TP description 和 TC 的 preparation / test_step / expect_output / DesignNote 支持 `<br>`，脚本转成换行；其他字段没有同样的还原保证。
- 多值 `raw_factors` 使用英文逗号，无空格；需求编号列表也统一使用英文逗号。
- 不把本文示例、代码围栏或模板占位行当作真实产物。模板中的业务值必须由实际输入替换。

## 4. TS 测试规格 Markdown

### 4.1 叙述区：在线文档接口

必须按下列固定标题生成，每个标题下有真实非空内容：

```markdown
## 概述
### 被测对象概述
### 测试方案概述

## 测试设计策略
### 特性风险分析（RBT）
### 测试重点难点分析
### 分层测试策略
### 底层硬件/组网差异测试策略分析
### 网元形态差异测试策略分析

## 场景分析
## 测试类型分析
## 特性交互分析
## 功能交互分析
## 设计约束分析
```

设计任务同步读取 7 个三级叶子章节；TR 同步读取上述最后 5 个二级章节。不是只要有“概述”或“测试设计策略”父标题即可。补充分析应放入相关章节正文或使用不重复的新标题，不得替换固定标题。文档解析器会拒绝重复的标题文字。

### 4.2 普通 TS 固定表格区

文件末尾必须且只能有一个 `## 平台写入数据`，内部保留 `### TR` 与 `### TS 清单`：

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

字段来源：

| 字段 | 权威来源 / 生成方式 |
|---|---|
| TR `tr_name` / `description` / `resolve_description` | `tr_info.json` 对应字段，逐字一致，不重新总结 |
| TR `requirement_ids` | `tr_info.requirements[].requirement_number` 按原顺序去重的全集 |
| TR `function_numbers` / `feature_numbers` | `tr_info.relation_function` / `relation_feature`，规范化为逗号列表 |
| TS `ts_name` | 基于当前 TR 的整套 SR 规格，按 TS 拆分规则生成 |
| TS `ts_type` | 仅 `scene/function/feature/constraint` |
| TS `requirement_ids` | 当前 TR 直接关联需求的非空子集，不得引用其他 TR |
| TS `description` | 当前 TS 测试范围、目标与边界 |
| TS `resolve_description` | 当前 TS 测试重点、约束和设计方向 |

分析输入为 `tr_info.json`、`sr_specs/_index.md` 与全部 SR 文件、`platform_ts.json`；拆分规则来自仓库根目录 `.testagent/rules/analysis-guide.md` 与 `.testagent/rules/ts-split.md`。不能用 CIDA 首条需求替代 TR 的完整需求集合。

`build_tr_json.py` 从 Markdown 读普通 TS，从 `tr_info.json` 注入 TR 的 design_task_id、tr_id、tr_no、creator 等字段。输出为 `{_meta, tr, test_specs}`，其中 `_meta.tr_mode=existing`。它校验 TR 三个文本字段及需求全集一致性；TS 非空需求子集等业务要求也必须由生成方保证，不能假设脚本已做全量校验。TR 既有对象只复用，不创建。

### 4.3 平台 DFX 的独立规格

平台查询中排除 `scene/function/feature/constraint` 后的 DFX，每条按实际平台 ID 生成以下结构，放在普通平台写入章节**之前**：

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

`## DFX TS 测试规格` 只出现一次；每个有效 `platform_ts_id` 对应唯一三级标题。名称、类型和平台 ID 来自查询快照；需求集合来自当前 TR；描述由当前 TR 上下文生成。DFX 不写入 `### TS 清单` 或 `tr_ts.json.test_specs[]`，否则可能重复创建已有质量属性 TS。Design 按 ID 精确取规格；Archive 复用平台 ID。

## 5. TP 设计 Markdown

### 5.1 叙述标题、dimension 和来源值

根据 catalog 当前条目的来源/类型选择适用维度，只生成适用的标题且正文非空：

| TS 来源/类型 | 必需叙述区二级标题 |
|---|---|
| `source=platform_dfx` | `## 测试类型交互设计`、`## 基于业务内部实现的设计` |
| `function/feature` | `## 功能交互设计`、`## 基于业务内部实现的设计` |
| `scene` | `## 基于业务场景的设计`、`## 基于业务内部实现的设计` |
| `constraint` | `## 基于业务内部实现的设计` |

固定映射来自 `.testagent/rules/tp-tc-design-logic.md`：

| 叙述标题 | TP dimension | tpType | tpSourceType |
|---|---|---|---|
| 基于业务场景的设计 | 基于业务场景 | BusinessSceneAnalysis | 基于业务场景设计—场景因子 |
| 基于业务内部实现的设计 | 基于业务内部实现 | SceneAnalysis | 基于业务内部实现设计—测试因子 |
| 功能交互设计 | 功能交互设计 | RequirementAnalysis | 功能交互设计-功能与测试因子 |
| 测试类型交互设计 | 测试类型交互设计 | RequirementAnalysis | 测试类型交互设计—测试因子 |

这三套文本不相同：例如不能将“基于业务内部实现的设计”直接写入 `dimension`。中文来源值里的 `—` 与 `-` 按表原样保留；不能把 CLI 参数枚举替换进现有 Markdown/MCP JSON。没有关联因子也必须填写合法非空 `tpSourceType`。

### 5.2 末尾固定区与字段来源

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

| 字段 | 来源 / 填写要求 |
|---|---|
| 元信息 `tr_name` | `tr_ts.json.tr.tr_name`，逐字一致 |
| 元信息 `ts_name/ts_type` | 当前 catalog 条目；普通 TS 与其 `tr_ts_index` 指向的规格一致，DFX 与查询规格一致 |
| `tp_id_temp` | 生成方分配稳定本地编号，如 `TP.01.01.01`，同一 TS 内唯一 |
| `tpName` | 当前 TS 适用维度展开出的具体测试点名称 |
| `description` | 测试点目标、条件和验证范围，与叙述区一致 |
| `resolveDescription` | 当前规则留空 |
| `rank` | Level 的数字部分，Level1 → `1`，范围 0–4 |
| `tsId/parentTrId` | 均填字面量 `<PENDING>`；真实父级 ID 在 Archive 使用 |
| `tpType/tpSourceType/dimension` | 严格使用第 5.1 节映射，不留空、不填 PENDING |
| `requirement_ids` | 当前 TP 表规则留空；不等同于 TS 层必须填写的需求关联 |
| `raw_factors` | 当前设计选定的关联因子原始标识列表，英文逗号分隔；无因子留空，不编造 |

元信息仅在 design 文件中维护一份；TC JSON 也从它读取，cases 文件不能作为另一套权威元信息。

当前转换脚本只是把 `raw_factors` 拆成数组写入 `_raw_factors`，**不会查询图谱、补齐因子对象或把编码解析成平台 ID**。现有对象归档将其用于因子名称参数，编码/名称的实际约定须与现有归档输入一致；不能因为表格可解析，就认定任意编码均可正确关联。结构化 TS 因子池、CLI relations 等新增方案须另行落地，不能仅加 Markdown 字段而期待当前脚本消费。

## 6. TC Markdown

前段展示方式可以调整，但必须与固定表内容一致。每个 TP 至少对应一个 TC，不能跳过低优先级 TP。末尾固定区：

```markdown
## 平台写入数据 - TC

| tc_id_temp | tp_id_temp | name | rank | preparation | test_step | expect_output | case_id | TestType | AutoType | envtype | DesignNote |
|---|---|---|---|---|---|---|---|---|---|---|---|
| TC.01 | TP.01.01.01 | [0101]重选次数边界控制 | 1 | 1. 系统运行正常<br>2. 配置最小重选次数 | 1. 注入链路故障<br>2. 观察重选次数 | 1. 重选次数符合配置<br>2. 超限后停止重选 | UPCF_RESELECT_01_01 | 1 | 0 | | 验证链路故障后系统按次数边界约束执行并停止重选 |
```

| 字段 | 来源 / 填写要求 |
|---|---|
| `tc_id_temp` | 生成方分配，同一 TS 内唯一；跨 TS 通过 TS 键区分 |
| `tp_id_temp` | 精确引用同一 TS 的 TP 表编号，不能引用另一 TS |
| `name` | 当前 TP 展开的具体用例名称 |
| `rank` | 用例 Level 数字部分，0–4 |
| `preparation` | 当前用例的预置条件，编号条目用 `<br>` 连接 |
| `test_step` | 当前用例可执行步骤，体现 TP 指定的参数和范围 |
| `expect_output` | 对应步骤的可验证预期结果 |
| `case_id` | 完整稳定用例编号，建议保留 `前缀_NN_NN` 后缀结构；不可只填前缀 |
| `TestType` | 按测试目标及 `tp-tc-output.md` 编码表选择；无法识别填字符串 `1` |
| `AutoType` | 明确自动化填 `1`；非自动化或无法识别填 `0` |
| `envtype` | 当前规则留空 |
| `DesignNote` | 生成一句真实测试目的/验证内容描述，非空，不直接复制用例名称 |

`TestType/AutoType/envtype/DesignNote` 不得填写 `<PENDING>`，其中 envtype 按当前规则空串。完整 TestType 码表以公共规则文件为准，不在本文复制第二套枚举。

## 7. Markdown → JSON 与归档映射

### 7.1 当前脚本调用

从 `<root>` 执行，明确指定单个稳定 TS 序号：

```bash
python .testagent/skills/test-spec-analysis/scripts/build_tr_json.py \
  ".design_output/<design_task_id>/TR_<tr_id>/test_specs/<TR名称>测试规格.md" \
  --tr-info ".design_output/<design_task_id>/TR_<tr_id>/tr_info.json"

python .testagent/skills/coretest-explore/scripts/build_ts_catalog.py \
  --platform-json ".design_output/<design_task_id>/TR_<tr_id>/test_specs/platform_ts.json" \
  --tr-ts-json ".design_output/<design_task_id>/TR_<tr_id>/test_specs/tr_ts.json" \
  --output ".design_output/<design_task_id>/TR_<tr_id>/test_specs/ts_catalog.json"

python .testagent/skills/coretest-design/scripts/build_tp_tc_json.py \
  ".design_output/<design_task_id>/TR_<tr_id>/test_design" \
  --design-task-id <design_task_id> --ts 01
```

TP/TC 转换的 `creator` 来自环境变量 `USERNAME`，为空时脚本停止；必须由调用环境保证身份正确，不要在表格追加 creator 列。design_task_id 来自上下文目录/命令参数，不得硬编码沙盒 ID。脚本注释中仍有旧路径示例，正式产物位置以第 2 节和现有主流程为准。

### 7.2 JSON 字段形状

| 输出字段 | 当前转换行为 |
|---|---|
| TP/TC 顶层 | 均为 `tr_name/ts_name/ts_type`；分别包含 `tps[]` / `tcs[]` |
| TP 普通字段 | 表格对应值直接传递，rank 等保持字符串 |
| TP 注入字段 | `designTaskId` 为命令参数、`creator` 为 USERNAME |
| TP 内部字段 | `dimension` → `_dimension`；`raw_factors` → `_raw_factors` 数组 |
| TP 父级占位 | `<PENDING>` → `<TODO:tsId>`、`<TODO:parentTrId>` |
| TC 编号派生 | case_id 至少有两个下划线时用 `rsplit("_",2)[0]` 得到 `case_id_prefix`；`case_id_start_value=0`、`case_id_number="1"` |
| TC 注入字段 | `creator=USERNAME`、`owner=""`、小写 `auto_type=0` |
| TC 父级占位 | `tp_id="<TODO:tp_id_after_create_tp>"`、`tr_id="<TODO:tr_id>"` |

大写 `AutoType` 是卡片上报字段，小写 `auto_type` 是现有 create_tc 归档字段，不能合并或互相替代。TC JSON 保留完整 `case_id`。

### 7.3 Archive 消费关系

- TR 从 Init 上下文/状态复用；普通 TS 通过 catalog 的 tr_ts_index 读取 tr_ts.json；平台 DFX 复用 platform_ts_id。
- TP 对象键为 `TS_<NN>/<tp_id_temp>`；TC 为 `TS_<NN>/<tc_id_temp>`，并通过同 TS 下 tp_id_temp 找真实父级 TP。
- 对象归档使用 JSON 与 archive_state 中的真实父级 ID，不要求提前向 Markdown 写入平台 ID；不回写或修改设计输入 JSON。
- 成功 TS/TP 的真实 ID 即时保存在 `archive/archive_state.json`，响应保存在 `archive/responses/`；TC 成功不要求返回平台 ID。
- 在线文档同步读取 TS 规格的固定任务/TR 章节及 design 文件适用维度正文；当前不写 TP/TC 自身在线文档。
- TC JSON 还被测试用例卡片适配消费，产出位于 TR 根目录的 `ts_<NN>_test_case.json`。仅替换 Markdown 生成流程时，保留原有后续 JSON 与卡片调用。

## 8. 可以替换与不能单独更改的内容

| 可以替换 | 必须保留 |
|---|---|
| 分析模型、提示词、检索算法、Agent 编排 | 当前 TR/TS 来源与职责边界 |
| 叙述正文、解释层次、图表、补充内容 | 被在线文档读取的固定非空标题，不重复标题文字 |
| TP/TC 具体业务内容与展示样式 | 固定表格中字段、顺序、合法取值及正文一致性 |
| 本地编号分配算法 | 同 TS 唯一、TC 引用正确、重跑稳定、catalog 文件序号映射一致 |
| 生成实现语言 | 标准文件位置、UTF-8、配对文件名 |

不能单独更改：章节锚点、表头、列顺序、camelCase/snake_case、中文枚举、文件前缀/后缀、目录层级、catalog 稳定键、JSON 顶层形状。需要更改这些接口时，必须同时修改消费者、迁移历史产物/状态并增加回归测试；不属于“只替换生成流程”。

新增字段不得直接插入 TP/TC 固定表。可先放在不影响固定标题的附加叙述中，但现有 JSON/Archive 不会自动读取；如需机器消费，另行定义并实现版本化接口。

## 9. 替换方验收清单

先在隔离目录运行转换/校验，不调用平台创建或在线文档写入；确认无误后再在明确授权的测试对象上执行归档。

- [ ] TR 上下文唯一，所有产物位于标准 TR 目录，没有使用旧按需求编号分目录路径。
- [ ] TS 规格固定章节和 7 个任务叶子章节正文非空，无重复标题。
- [ ] TR 固定表与 tr_info 三个文本字段、需求全集一致，function/feature 列表来自源值。
- [ ] 普通 TS 类型合法、需求关联非空且属于当前 TR；DFX 不混入普通清单。
- [ ] DFX 规格按平台 ID 唯一可定位；catalog 按规定建立，重跑没有静默改变稳定键。
- [ ] 每个 TS 的 design/cases 文件成对，文件序号匹配 catalog；适用设计标题非空、不增加不适用维度。
- [ ] TP/TC 固定表锚点、表头、列数、列顺序逐项匹配公共规则；无原始竖线、跨行单元格或中途空行。
- [ ] TP 来源及 dimension/tpType 映射正确；TC DesignNote 非空，TestType/AutoType 按规则生成。
- [ ] 本地 TP/TC 编号唯一，所有 TC 的 tp_id_temp 都命中同一 TS 的 TP；每 TP 至少一个 TC。
- [ ] 使用原脚本生成 JSON，核对对象数量、顶层元信息、raw_factors 拆分和父级 TODO 占位。
- [ ] 同一输入重跑，路径、稳定键和本地引用不漂移；JSON 结构与原消费者一致。
- [ ] 后续测试覆盖普通 scene/function/feature/constraint、平台 DFX、无因子、多条 TP/TC、多行步骤等场景。
- [ ] 授权归档验证同时检查对象、在线文档、状态与卡片；不能只凭转换退出码或 Portal 成功判断兼容。

当前解析器不是通用 Markdown 库，也不会完整检查表头内容、TP/TC 引用、编号唯一性或全部业务枚举。契约验收必须补足这些检查。

## 10. 依据文件

以下相对链接指向当前仓库实现；接口变化时，应同时更新本文：

- [测试规格生成规则](../.testagent/skills/test-spec-analysis/SKILL.md)
- [TR/TS Markdown 转 JSON](../.testagent/skills/test-spec-analysis/scripts/build_tr_json.py)
- [Explore 上下文与输出结构](../.testagent/skills/coretest-explore/SKILL.md)
- [稳定 TS 编号构建](../.testagent/skills/coretest-explore/scripts/build_ts_catalog.py)
- [Design 输出与编排](../.testagent/skills/coretest-design/SKILL.md)
- [单 TS 设计闭环](../.testagent/agents/test-design-agent.md)
- [TP/TC 固定表格规则](../.testagent/rules/tp-tc-output.md)
- [TP/TC 维度与枚举规则](../.testagent/rules/tp-tc-design-logic.md)
- [TP/TC Markdown 转 JSON](../.testagent/skills/coretest-design/scripts/build_tp_tc_json.py)
- [对象归档消费者](../.testagent/skills/coretest-object-archive/SKILL.md)
- [Archive 入口及范围](../.testagent/skills/coretest-archive/SKILL.md)
- [在线文档同步](../.testagent/skills/coretest-document-sync/scripts/document_sync.py)
