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

单个目标 TS：

-   ts_name
-   ts_type
-   requirement_ids
-   description
-   resolve_description

以及：

-   所属TR信息；
-   TR级背景素材；
-   当前TR完整TS列表；
-   调用方指定的输出目录。

## 输出目录约束

测试设计文件输出目录由调用方 `coretest-design` 指定。

默认格式：

    .design_output/<IR>/test_design/

必须输出：

    .design_output/<IR>/test_design/

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

## TP设计

按：

    ../../rules/tp-tc-design-logic.md

进行4维度展开。

每个TP必须：

-   有明确测试目标；
-   标注Level；
-   填写tpType/tpSourceType。

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
