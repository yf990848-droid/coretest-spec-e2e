# TP/TC 设计逻辑规则

> 本文件定义不同 TS 的设计维度、TP 的 `tpType` / `tpSourceType` 取值，以及 TP 到 TC 的覆盖规则。

## 一、TS → TP：按类型选择维度

| TS 来源/类型 | 必须生成的设计维度 |
|---|---|
| 平台 DFX（`source=platform_dfx`） | 测试类型交互设计、基于业务内部实现 |
| `function` / `feature` | 功能交互设计、基于业务内部实现 |
| `scene` | 基于业务场景、基于业务内部实现 |
| `constraint` | 基于业务内部实现 |

每个维度分别提取 TP。每个 TP 必须包含名称、描述、Level（0-4）、关联测试因子（如有）和所属维度。禁止为当前 TS 生成表中未列出的其他维度。

## 二、TP 的 tpType / tpSourceType

| 维度 | tpType | tpSourceType |
|---|---|---|
| 基于业务场景 | `BusinessSceneAnalysis` | `基于业务场景设计—场景因子` |
| 基于业务内部实现 | `SceneAnalysis` | `基于业务内部实现设计—测试因子` |
| 功能交互设计 | `RequirementAnalysis` | `功能交互设计-功能与测试因子` |
| 测试类型交互设计 | `RequirementAnalysis` | `测试类型交互设计—测试因子` |

所有生成的 TP 都必须填写非空 `tpSourceType`，不得再以空值表示尚未接入测试因子。

平台真实合法值还包括以下预留来源，本流程当前不主动生成：

- `测试类型交互设计—测试设计准则`
- `测试类型交互设计—模式库`

因子选择独立保存在当前 TS 的 `ts_<NN>_factor_plan.json`，由归档阶段按 ID
构造 TP `--relations`，不再按名称映射 `sceneFactorNames/testFactorNames`。

- `scene` TS/TP 可同时使用 SceneFactor 与 TestFactor；
- `function`、`feature`、`constraint`、平台 DFX TS/TP 仅使用 TestFactor；
- 先根据完整 TS 规格选择 TS 因子，再让每个 TP 从该集合中选择子集；
- TS 因子必须至少被一个 TP 使用；每 TS 默认最多 5 个，每 TP 默认最多 3 个，两类因子合并计数；
- 无匹配因子时保留空数组并继续，不编造因子；
- TestFactor 的 `testFactorId` 必须是因子 UUID（图谱 `test_factor_id`，平台查询的
  `test_factor_id`），不得使用 TS 因子关系行的数字 `id`；
- `_raw_factors` 保持现有 Markdown 表格格式，用于设计展示；归档只读取经校验的因子计划。

## 三、TP → TC：覆盖展开

每个 TP 必须至少生成 1 个 TC，TP→TC 覆盖率为 100%。每个 TC 必须包含用例名称、Level、预置条件、测试步骤、预期结果和用例编号。不得跳过低优先级 TP。
