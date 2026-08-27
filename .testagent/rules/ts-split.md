# TR/TS 拆分与命名规则

本文件定义已有 TR 模式测试规格的**内容规则**：TS 四类定义、拆分原则、命名约定、描述写法、TR 段字段填法。

负责生成测试规格 markdown 的助手须先读取本文件，据此把最终的 **TR 段**与 **TS 清单**写入测试规格 md 的固定章节（章节的位置与表格格式见 `test-spec-analysis` SKILL）。本文件只决定"写什么内容"；测试规格 JSON 的结构、字段名、字段顺序、以及写入平台的动作，由提取脚本与流程统一保证，**不在本文件配置范围内**。

业务方调整测试规格的拆分或命名时，只需修改本文件，无需改动 skill 或脚本。

---

## 一、TS 四类（ts_type）

每条 TS 必须归入下列四类之一，填入 TS 清单的 `ts_type` 列。判类看"测的是什么形态"，四选一：

| ts_type | 含义 |
|---------|------|
| `scene` | 场景：一条端到端使用流程，在真实情境里从头走到尾。 |
| `function` | 功能：单个功能点能否正确工作。 |
| `feature` | 特性：一整块能力，比单个功能粗一层。 |
| `constraint` | 约束：边界、规格限制、非功能要求——"不能超过 / 必须满足"这类归此。 |

## 二、拆分原则

模型读取各 SR 内容，按第一节四类定义把测试场景拆成若干 TS：

- 一个 SR 可拆出一条或多条 TS，条数由模型按内容判断，不强求一一对应。
- 每条 TS 只归一类。
- 拆分分析须记录每条 TS 覆盖的 SR 内容，但 SR 编号不得直接填入平台 `requirement_ids`。
- 平台 `requirement_ids` 必须取自 `tr_info.json requirements[].requirement_number`，且每条 TS 使用当前 TR 直接关联需求全集的非空子集；根据 `sr_specs` 的来源覆盖关系完成 SR 到直接需求的回溯。
- 拆分以"覆盖全部 SR 的测试意图"为目标：所有 SR 的测试点都应落到某条 TS 上，不遗漏。

## 三、命名约定（ts_name）

ts_name 为纯中文名称。命名要求：

- 看名字能识别"测的是什么"，必要时带上被测特性（TR 名）以免脱离上下文。
- 简洁，不含编号前缀。
- 例（TR 名＝Logo联动保障）：`Logo联动保障_异常logo拦截`、`Logo联动保障端到端流程`。

## 四、TS 描述写法（description / resolve_description）

每条 TS 除 `ts_name`、`ts_type`、`requirement_ids` 外，还有 `description` 与 `resolve_description` 两个字段，按下列通用模板套具体值填写。`{ts_name}` 取该条 TS 名，`{测试意图}` 为模型对该 TS 所测内容的一句话概括。

- `description`：`验证{ts_name}所涉及的测试内容的正确性。`
- `resolve_description`：`针对{ts_name}设计测试，覆盖其{测试意图}的输入、行为与预期结果。`

## 五、TR 段字段填法

正式流程复用平台已有 TR，`tr_info.json` 是 TR 元数据和直接关联需求的唯一权威来源。测试规格 md 的 TR 段须填写以下 6 个字段，禁止重新总结或改写：

| 字段 | 填法 |
|------|------|
| `tr_name` | 原样使用 `tr_info.tr_name` |
| `description` | 原样使用 `tr_info.description` |
| `resolve_description` | 原样使用 `tr_info.resolve_description` |
| `requirement_ids` | 按顺序提取并去重 `tr_info.requirements[].requirement_number`，英文逗号分隔；不得填写 sr_specs 中的 SR 编号，除非该 SR 本身就是 TR 的直接关联需求 |
| `function_numbers` | 原样使用 `tr_info.relation_function`，按平台写入格式规范化为英文逗号分隔 |
| `feature_numbers` | 原样使用 `tr_info.relation_feature`，按平台写入格式规范化为英文逗号分隔 |

`design_task_id` 与 `creator` 不写入 Markdown TR 表，由提取脚本直接从 `tr_info.json` 补全。平台 DFX TS 和普通 TS 的 `requirement_ids` 均遵循当前 TR 直接关联需求子集规则；SR 仅用于测试内容拆分和覆盖审计。
