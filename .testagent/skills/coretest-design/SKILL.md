---
description: Test design generation - reads test_specs, initializes TS working cards,
  invokes test-design-agent per TS in parallel, and lets each TS agent complete
  markdown, JSON extraction, and card update.
license: MIT
metadata:
  author: corespec
  generatedBy: manual
  version: 1.5.0
name: coretest-design
---

# CoreTest Design Skill

测试设计生成流程：

    coretest-explore
            |
            v
    测试规格
            |
            v
    coretest-design
            |
            v
    初始化TS级working卡片
            |
            v
    .design_output/<design_task_id>/TR_<tr_id>/test_design
            |
            v
    并行调用test-design-agent
            |
            v
    每个TS独立完成：TP/TC设计 -> JSON提取 -> 测试用例卡片completed

## Input

-   TR ID：必选第一个位置参数，如 `3863`
-   TS 列表：可选后续位置参数，如 `TS_01 TS_02 TS_03`
-   完整命令格式：`/coretest-design <tr_id> [TS列表]`
-   不传 TS 时，默认处理当前 `ts_catalog.json` 中的全部 TS（平台 DFX + Explore 普通 TS）
-   TS 编号大小写不敏感，统一标准化为 `TS_<NN>`，去重后保持输入顺序

## Execution Flow

### Phase 0: Gather Context

根据输入的 `tr_id` 定位已完成 explore 的 TR 目录：

    .design_output/*/TR_<tr_id>/

必须存在：

    tr_info.json
    cida_info.json
    test_specs/<TR名称>测试规格.md
    test_specs/tr_ts.json
    test_specs/ts_catalog.json

只做以下必要检查：

-   TR 目录存在且只定位到一个；
-   `tr_info.json`、`cida_info.json`、`test_specs/tr_ts.json` 和 `test_specs/ts_catalog.json` 存在；
-   `test_specs/` 下存在测试规格 Markdown；
-   用户指定的 `TS_<NN>` 必须存在于 `ts_catalog.json.items[].ts_key`。

其中：

-   从 TR 目录父级获取 `design_task_id`；
-   从 `cida_info.json.requirement_number` 获取 `requirement_id`（支持 IR/SR），用于卡片关联；
-   `cida_info.json` 只读，不得重新生成或覆盖；
-   `tr_info.json`、完整 CIDA 上下文和完整 TS 清单必须传给每个 `test-design-agent`；
-   TS 完整列表和稳定编号只来自 `ts_catalog.json.items[]`；
-   `source=platform_dfx` 的条目必须包含有效 `platform_ts_id`，并按该 ID 从测试规格 Markdown 的 `## DFX TS 测试规格` 中精确取得唯一规格，不得创建平台 TS，也不得查找 `tr_ts_index`；
-   `source=explore` 的条目必须包含有效 `tr_ts_index`，其唯一规格来自对应的 `tr_ts.json.test_specs[]`；
-   启动 Agent 前由主流程提取当前 TS 的完整规格内容；不得把目录或整份背景材料交给 Agent 自行搜索；
-   所有设计产物写入当前 `TR_<tr_id>` 目录。

### Phase 1: TS Filtering

根据位置参数中的 TS 列表筛选目标 TS。

未指定时处理全部 TS。

规则：

-   所有 TS 参数统一标准化为 `TS_<NN>`，不接受或要求中文名称后缀；
-   对重复 TS 去重并保持用户输入顺序；
-   未指定时按 `ts_catalog.json.items[]` 顺序处理全部 TS；
-   指定时按 `items[].ts_key` 精确匹配；
-   任一编号不存在、重复或条目缺少来源必需字段时，在初始化卡片和启动 Agent 前停止并报告。

### Phase 1.5: Initialize TS Working Cards

目标 TS 按每批最多 3 个分批处理。每批启动 TS 设计 SubAgent 之前，必须先为当前批次初始化 working 卡片。

规则：

-   一个 TS 对应一个 working 卡片；
-   初始化 key 必须使用 `<requirement_id>_<ts-id>`；
-   示例：`IR20251206000098_ts_01`；
-   初始化脚本必须使用原始 card-initializer 脚本；
-   card_id 文件保留在初始化脚本目录，不复制到 `.design_output/<design_task_id>/TR_<tr_id>/cards/`；
-   每个 TS 必须使用一次独立的 bash 工具调用，不得在同一次 bash 调用中串联多个 `card_generate.py`；
-   当前批次最多同时发起 3 个独立的卡片初始化调用；
-   当前批次初始化完成后立即进入该批次的并行测试设计阶段；
-   当前批次所有卡片均验证成功后才能启动本批 `test-design-agent`；
-   任一卡片初始化失败时，不得启动当前批次的任何 `test-design-agent`，避免后续 completed 卡片无法关联。

每个 TS 的独立工具调用必须遵循以下格式：

```bash
cd "<root>/.testagent/skills/card-initializer/scripts/test_case"; python -u card_generate.py <requirement_id>_<ts-id>
```

要求：

-   命令路径必须使用 `/`，不得使用会被 bash 当作转义符的 `\`；
-   必须先 `cd` 到 `card-initializer/scripts/test_case` 目录；
-   必须使用 `python -u card_generate.py` 执行；
-   不要使用绝对路径直接调用 `card_generate.py`；
-   命令间隔必须使用 `;`；
-   不得使用 `&&`；
-   不得执行 `Remove-Item` 或 `rm`，`card_generate.py` 内部已负责覆盖旧 card_id 文件；
-   每个目标 TS 都必须执行一次且仅执行一次独立初始化调用；
-   每次调用必须分别确认输出中 `success` 为 `true` 且存在 `data.card_cache_id`；
-   禁止把当前批次多个 TS 的初始化命令拼接为一条 bash 命令。

初始化后应生成：

    <root>/.testagent/skills/card-initializer/scripts/test_case/<requirement_id>_<ts-id>_card_id.txt

例如：

    <root>/.testagent/skills/card-initializer/scripts/test_case/IR20251206000098_ts_01_card_id.txt

每次调用还必须确认对应 card_id 文件存在。只有当前批次全部 TS 的 `success`、`card_cache_id` 和 card_id 文件均验证成功，才能进入 Phase 2。

### Phase 2: Invoke test-design-agent In Parallel

按 TS 分批并行调用，每批最多 3 个：

    agents/test-design-agent

例如目标 TS 为 `TS_01 TS_02 TS_03 TS_04 TS_05`：

1.  初始化 `TS_01`、`TS_02`、`TS_03` 的 working 卡片；
2.  并行启动这 3 个 `test-design-agent`，等待本批全部结束；
3.  初始化 `TS_04`、`TS_05` 的 working 卡片；
4.  并行启动这 2 个 `test-design-agent`，等待本批全部结束；
5.  汇总全部批次结果。

同一时间运行的 `test-design-agent` 不得超过 3 个。单个 TS 失败不影响同批其他 TS；当前批次全部结束并记录结果后，继续下一批。

`test-design-agent` 是单 TS 闭环 Agent。每个 Agent 调用只处理一个 TS，内部按顺序完成：

1.  调用 `skills/test-design` 生成当前 TS 的 `ts_<NN>_test_design.md` 和 `ts_<NN>_test_cases.md`；
2.  调用 `build_tp_tc_json.py --ts <NN>` 只提取当前 TS 的 JSON；
3.  调用 `skills/test-case-card-adapter` 将当前 TS 已初始化的 working 卡片更新为 completed；
4.  当前 TS 分支结束。

每个 `test-design-agent` 调用时必须同时提供：

1.  TR ID `tr_id` 和完整 `tr_info.json`；
2.  需求编号 `requirement_id`（来自 `cida_info.json.requirement_number`，支持 IR/SR）；
3.  当前 TS 编号（如 `ts_01` 或 `01`）；
4.  当前负责生成的完整 catalog 条目，包括 `source`、`ts_type`、`ts_name`，DFX 还包括 `platform_ts_id`；
5.  当前 TR 信息；
6.  按来源精确提取的当前 TS 完整规格内容：普通 TS 使用 `tr_ts_index`，DFX 使用 `platform_ts_id`；
7.  当前 TR 下完整 TS 清单（仅用于边界判断）；
8.  输出目录；
9.  测试规格文件路径（仅用于来源审计，不允许 Agent 扫描其目录）；
10. `design-task-id`；
11. 完整 `cida_info.json` 上下文；
12. 完整 `ts_catalog.json`，并明确当前 TS 只能按 `tp-tc-design-logic.md` 中对应来源/类型的维度生成设计。

`coretest-design` 不再在主流程中统一调用 `build_tp_tc_json.py`，也不再统一调用 `test-case-card-agent`。JSON 提取和卡片更新已经下沉到每个 `test-design-agent` 内部。

## TS边界约束（必须遵守）

并行生成时，不允许只给 SubAgent 单独 TS 信息。

每个 SubAgent 必须知道：

    当前 TR 的完整 ts_catalog.json

并明确：

-   本次只负责指定 TS；
-   其他 TS 只作为边界参考；
-   不允许生成其他 TS 对应的 TP/TC。

如果发现测试点属于其他 TS 职责范围，不要纳入当前 TS。

目的：

-   避免多个 SubAgent 对同一需求重复发散；
-   减少不同 TS 之间 TP/TC 重复覆盖；
-   保证 TS 职责边界清晰。

## 输出目录约束

所有测试设计产物统一写入：

    .design_output/<design_task_id>/TR_<tr_id>/test_design/

每批输出：

    .design_output/<design_task_id>/TR_<tr_id>/test_design/

    ts_<NN>_test_design.md
    ts_<NN>_test_cases.md

禁止：

-   写入扩展包根目录；
-   写入任何 `corespec/changes/` 目录；
-   写入其他自定义目录。

### Phase 3: Summary

等待所有 `test-design-agent` 分支完成后，只做汇总，不再补做 JSON 或卡片生成。

汇总内容：

-   目标 TS 数量；
-   成功完成闭环的 TS 数量；
-   失败 TS 列表及失败阶段（test-design / JSON / card）；
-   已生成的 TP/TC markdown、TP/TC JSON、测试用例卡片数据。

每个 TS 的产物校验、JSON 提取和卡片更新由对应 `test-design-agent` 在分支内部完成。

禁止在 Phase 3 中输出“Phase 6 需要单独调用 test-case-card-agent”或“当前阶段已完成核心测试设计产物生成”后提前结束。

## Downstream Skills and Agents

  Component                         调用阶段      输出
  --------------------------------- ------------- -------------------
  agents/test-design-agent          Phase 2       单TS闭环：markdown、JSON、卡片completed
  skills/test-design                Agent内部     TS级TP/TC设计文件
  scripts/build_tp_tc_json.py       Agent内部     单TS TP/TC JSON
  skills/test-case-card-adapter     Agent内部     单TS测试用例卡片数据

## Error Handling

  场景                         处理
  ---------------------------- ------------
  测试规格缺失                 退出
  ts_catalog.json 缺失或非法   退出
  cida_info.json 缺失          退出
  找到多个同 ID 的 TR 目录       列出候选并退出
  用户指定的TS编号不存在         初始化卡片前退出
  卡片初始化失败               停止流程
  test-design-agent 调用失败   记录失败TS并继续其他已启动TS
  单TS设计失败                 由 test-design-agent 返回失败，不生成该TS JSON和卡片
  单TS JSON生成失败            由 test-design-agent 返回失败，不生成该TS卡片
  单TS卡片失败                 由 test-design-agent 返回失败，不影响其他TS
  汇总阶段发现失败TS           列出失败阶段和失败原因

## Guardrails

-   Phase 1.5 必须按每批最多 3 个 TS 初始化 working 卡片；
-   每个 TS 必须通过独立的 bash 工具调用初始化，禁止在一次调用中串联多个 `card_generate.py`；
-   当前批次 working 卡片初始化完成后，必须立即运行当前批次，不得预先初始化后续批次；
-   Phase 1.5 必须先 `cd` 到初始化脚本目录，再执行 `python -u card_generate.py`；
-   Phase 1.5 命令间隔必须使用 `;`，不得使用 `&&`；
-   Phase 1.5 的命令路径必须使用 `/`，不得执行 `Remove-Item` 或 `rm`；
-   当前批次所有卡片的 `success`、`card_cache_id` 和 card_id 文件验证成功前，不得启动本批 Agent；
-   Phase 2 必须保持 TS SubAgent 分批并行执行，同一时间最多运行 3 个；
-   Phase 2 必须调用 `agents/test-design-agent`，不得把 `skills/test-design` 当作 subagent_type；
-   `coretest-design` 主流程不得自行读取 test-design 规则文件后串行生成所有 TS；
-   每个 `test-design-agent` 必须只处理一个 TS，并在 Agent 内部完成 markdown、JSON、卡片 completed 闭环；
-   每个 `test-design-agent` 必须接收完整 CIDA 上下文和当前 TS 的精确规格内容；
-   DFX 只能按 `platform_ts_id` 定位 Explore 已生成的规格，禁止扫描 TR、`test_specs`、`test_design` 或历史样例；
-   一个TS对应一个卡片；
-   禁止SubAgent生成非目标TS的TP/TC；
-   TS之间必须保持测试职责边界，避免重复覆盖。
