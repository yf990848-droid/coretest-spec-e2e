---
name: test-spec-analysis
description: 进行软件测试规格分析工作。适用于：(1)分析被测对象概述和测试规格概述，(2)进行测试设计策略分析（RBT风险分析、测试重点难点、分层测试策略、底层硬件/组网差异、网元形态差异），(3)基于已有TR进行测试需求分析并建立TR与版本需求对应关系，(4)进行测试场景分析(TS)。当用户需要设计测试策略、分析测试需求、分解测试场景时使用此技能。TR使用用户选择的已有TR，不在此技能中创建新的TR；规则文件位于本 skill 目录上两级的 .opencode/rules/ 下（不在本 skill 目录内）：分析方法见 ../../rules/analysis-guide.md，拆分、命名与描述规则见 ../../rules/ts-split.md。
---

# 测试分析

## 角色与产物

本 skill 产出**一份测试规格 markdown**：`test_specs/<中文需求名>测试规格.md`，分两段：

- **前段（自由）**：分析过程，供人工评审。分析方法与参考资料**全部见 [rules/analysis-guide.md](../../rules/analysis-guide.md)**，本 skill 不重述。
- **后段（固定）**：标题 `## 平台写入数据` 的章节，承载 TR 段与 TS 清单，格式严格固定，由提取脚本 `build_tr_json.py` 读取生成平台 JSON。内容规则见 **[rules/ts-split.md](../../rules/ts-split.md)**。

两份 rules 是内容与方法的唯一来源；业务调整分析方法、拆分或命名时只改 rules，本 skill 与脚本不动。**本 skill 不产出任何 JSON。**

当前测试规格分析依赖已有 TR 上下文信息。TR 信息由 `coretest-explore` 阶段生成的：

```text
.design_output/<design_task_id>/<requirement_id>/tr_context.json
```

提供。本 skill 使用该文件中的已有 TR 信息，不重新创建 TR。

## 前段：分析过程

按 [rules/analysis-guide.md](../../rules/analysis-guide.md) 开展分析，将结论写入 md 前段。前段须涵盖：

1. 被测对象概述、测试规格概述
2. 测试设计策略（RBT 风险、重点难点、分层、硬件/组网差异、网元形态差异）
3. 测试需求分析（基于已有 TR 分析测试需求覆盖范围，并建立 TR 与版本需求对应关系）
4. 测试场景分析（按四类拆分的定性分析）

前段只写分析结论，**不在此编排 TS 清单**——TS 清单一律落入后段固定章节。

## 后段：平台写入数据（固定格式）

在 md 末尾追加 `## 平台写入数据` 章节，**严格按下列骨架填写**，本章只放两个表格、不写分析性文字。所有字段值、命名、描述按 [rules/ts-split.md](../../rules/ts-split.md) 填**最终值**（带前缀、套描述模板）。

后段应严格长成这样：

````markdown
## 平台写入数据

>  本章为固定格式，由提取脚本读取生成平台 JSON，请勿手动改动格式。

### TR

| 字段 | 值 |
|------|-----|
| tr_name | <从 tr_context.json 获取已有TR名称> |
| description | <从 tr_context.json 获取已有TR描述> |
| resolve_description | <从 tr_context.json 获取已有TR解决描述> |
| requirement_ids | <覆盖的全部 SR 编号，英文逗号分隔不含空格> |
| function_numbers | <命令 --function-numbers 值；未传填 <PENDING-coretest-init>> |
| feature_numbers | <留空> |

### TS 清单

| ts_name | ts_type | requirement_ids | description | resolve_description |
|---------|---------|-----------------|-------------|---------------------|
| <TS 名，纯中文> | <scene/function/feature/constraint 四选一> | <本条覆盖的 SR，逗号分隔不含空格> | <按 ts-split.md 第四节模板> | <按 ts-split.md 第四节模板> |
| <按 ts-split.md 第二节拆分原则逐条一行> | | | | |
````

### 编码与中文输出约束

生成 `## 平台写入数据` 章节时，所有中文内容必须以正常可读的 UTF-8 中文输出。

`TR` 表和 `TS 清单` 中的 `tr_name`、description、resolve_description、ts_name 等字段不得出现乱码、错码、混合编码或不可读字符。

如果生成过程中发现字段内容不可读，必须立即重新生成该字段，确保最终落盘内容为正常中文。

生成完成后，需要检查 `## 平台写入数据` 章节，确认 `TR` 表和 `TS 清单` 中所有中文字段均可正常阅读。

## 输出

单产物 `test_specs/<中文需求名>测试规格.md`，含前段分析与后段固定格式的「平台写入数据」章节。

平台 JSON（`tr_ts.json`）由 `/coretest-explore` 阶段 6.5 的 `build_tr_json.py` 从本 md 后段提取生成、并补全 `design_task_id` / `creator`。JSON 结构与字段顺序由脚本写死保证合规，内容全部来自本 md 后段。
