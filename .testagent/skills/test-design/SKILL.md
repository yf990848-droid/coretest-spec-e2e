---
description: 基于TS展开TP和TC设计。输入单个目标TS，同时接收完整TS列表作为边界参考，只生成指定TS内容，避免TS之间重复覆盖。
name: test-design
---

# 测试设计 Skill

## 核心概念

  层级   含义
  ------ ----------
  TR     测试需求
  TS     测试规格
  TP     测试点
  TC     测试用例

## 输入

单个目标 TS 按来源提供：

-   `source=explore`：`ts_name`、`ts_type`、`requirement_ids`、`description`、`resolve_description` 和 `tr_ts_index`；
-   `source=platform_dfx`：`ts_key`、`ts_name`、`ts_type`、`platform_ts_id`，以及 Explore 按该 ID 生成的 DFX 完整规格；DFX 不要求 `tr_ts_index`。

以及：

-   所属TR信息；
-   调用方精确提取的当前 TS 规格内容；
-   当前TR完整TS列表；
-   调用方指定的输出目录。

## 输出目录约束

测试设计文件输出目录由调用方 `coretest-design` 指定。

默认格式：

    .design_output/<design_task_id>/TR_<tr_id>/test_design/

必须输出：

    .design_output/<design_task_id>/TR_<tr_id>/test_design/

    ts_<NN>_test_design.md
    ts_<NN>_test_cases.md

禁止：

-   输出到扩展包根目录；
-   输出到当前工作目录；
-   自行创建其他测试设计输出目录。

## TS边界约束（最高优先级）

本 Skill 由 `coretest-design` 并行调用时，每个 SubAgent 必须接收：

1.  当前负责生成的目标 TS；
2.  当前 TR 下完整 TS 列表。

完整 TS 列表仅用于：

-   理解测试范围；
-   判断测试内容归属；
-   避免不同 TS 重复设计。

### 生成规则

必须：

-   只生成目标 TS 对应的 TP/TC；
-   只覆盖目标 TS 职责范围内的测试内容。

禁止：

-   根据完整 TS 列表展开其他 TS 的 TP；
-   将其他 TS 的测试点合并到当前 TS；
-   因为看到其他 TS 信息而扩展额外测试范围。

判断原则：

如果一个测试点同时涉及多个 TS：

-   根据测试点主要职责归属选择 TS；
-   按 TS 名称、职责描述、requirement_ids 判断归属；
-   不属于当前 TS 的内容留给对应 TS。

## 必读文件

  文件                                用途
  ----------------------------------- --------------------------
  ../../rules/tp-tc-design-logic.md   4维度展开、TP/TC设计规则
  ../../rules/tp-tc-output.md         固定表格区格式

## 固定表格区约束

两个文件末尾必须包含：

design文件：

    ## 平台写入数据 - 元信息
    ## 平台写入数据 - TP

cases文件：

    ## 平台写入数据 - TC

锚点、表头、列顺序必须严格按照：

    ../../rules/tp-tc-output.md

不得修改。

只读取调用方明确传入的文件和上述两个公共规则文件。不得因 DFX 缺少普通 TS 字段而扫描 TR、`test_specs`、`test_design`、references 或历史样例，也不得读取其他 TS 产物。

## TP设计

按：

    ../../rules/tp-tc-design-logic.md

进行4维度展开。

叙述区标题、TP 表 `dimension` 和 `tpSourceType` 是不同字段，必须分别按规则填写。例如：

| 叙述区标题 | `dimension` | `tpSourceType` |
|---|---|---|
| `基于业务内部实现的设计` | `基于业务内部实现` | `基于业务内部实现设计—测试因子` |

`dimension` 只能使用 `tp-tc-output.md` 定义的四类值：`基于业务场景`、`基于业务内部实现`、`功能交互设计`、`测试类型交互设计`。生成固定 TP 表后、执行 JSON 提取前必须逐行校验，不得直接复制带“的设计”的标题名称。

每个TP必须：

-   有明确测试目标；
-   标注Level；
-   填写合法的 `dimension`、`tpType` 和 `tpSourceType`。

## TC生成

规则：

-   TP→TC必须100%覆盖；
-   每个TP必须生成对应TC；
-   测试步骤必须体现测试点指定参数、条件和范围；
-   不允许套用无关固定模板。

## Guardrails

-   不生成其他TS内容；
-   不跨TS扩展测试范围；
-   不修改其他TS产物；
-   固定表格区不可修改；
-   不生成测试脚本；
-   只负责测试设计阶段产物。
