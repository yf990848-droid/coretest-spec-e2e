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

因子参数映射：

- `基于业务场景设计—场景因子`、`功能交互设计-功能与测试因子` → `sceneFactorNames`；
- `基于业务内部实现设计—测试因子`、`测试类型交互设计—测试因子` → `testFactorNames`；
- `_raw_factors` 为空时两个因子参数均不传或传空；
- 同一组因子不得同时传给两个参数。

## 三、TP → TC：覆盖展开

每个 TP 必须至少生成 1 个 TC，TP→TC 覆盖率为 100%。每个 TC 必须包含用例名称、Level、预置条件、测试步骤、预期结果和用例编号。不得跳过低优先级 TP。
