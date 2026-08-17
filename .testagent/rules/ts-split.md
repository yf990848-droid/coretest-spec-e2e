# TR/TS 拆分与命名规则

本文件定义测试规格的**内容规则**：TS 四类定义、拆分原则、命名约定、描述写法、TR 段字段填法。

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
- 每条 TS 须标明其覆盖的 SR 编号（填入 `requirement_ids` 列）；一条 TS 可覆盖一个或多个 SR。
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

测试规格 md 的 TR 段须填写以下 6 个字段。占位符：`IR编号` 取自需求 ID；`SR数` 为本 TR 覆盖的 SR 总数。

| 字段 | 填法 |
|------|------|
| `tr_name` | 取 IR 标题，纯中文，不带 `TR-IR...` 编号前缀 |
| `description` | `本TR对应需求{IR编号}，整合该需求下全部{SR数}个SR的测试内容，组织为测试规格。` |
| `resolve_description` | `依据需求{IR编号}的实现设计，对其下{SR数}个SR逐项开展测试验证。` |
| `requirement_ids` | 本 TR 覆盖的全部 SR 编号，英文逗号分隔、不含空格（如 `SR20260110000656,SR20260110000657`）。取自 sr_specs 的 SR 清单 |
| `function_numbers` | 取自命令 `--function-numbers` 参数值，原样填入（英文逗号分隔串）；命令未传则填占位 `<PENDING-coretest-init>`。不得用 IR/SR 编号充数 |
| `feature_numbers` | 本期固定留空（空字符串） |

**不在本段填写的两个平台字段**：`design_task_id` 与 `creator` 不写入 md，由提取脚本在写平台时补全——`design_task_id` 来自命令 `--design-task-id` 参数（CloudSpider 页面 dtId），`creator` 来自运行环境的工号。模型无需、也不应在 md 中提供这两项。
