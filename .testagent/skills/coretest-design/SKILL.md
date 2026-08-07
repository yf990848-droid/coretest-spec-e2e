---
compatibility: Works without npm - depends on downstream skills
description: Test design generation - reads test_specs, initializes TS working cards,
  invokes test-design-agent per TS in parallel, and lets each TS agent complete
  markdown, JSON extraction, and card update.
license: MIT
metadata:
  author: corespec
  generatedBy: manual
  version: 1.3
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
    .design_output/<design_task_id>/<IR>/test_design
            |
            v
    并行调用test-design-agent
            |
            v
    每个TS独立完成：TP/TC设计 -> JSON提取 -> 测试用例卡片completed

## Input

-   TS 列表：可选位置参数，如 `TS_01 TS_02 TS_03`
-   不传 TS 时，默认处理当前 `tr_ts.json` 中的全部 TS
-   TS 编号大小写不敏感，统一标准化为 `TS_<NN>`，去重后保持输入顺序

## Execution Flow

### Phase 0: Gather Context

从 `.design_output/` 下定位已完成 explore 的上下文目录：

    .design_output/<design_task_id>/<IR>/

必须存在：

    cida_info.json
    test_specs/<需求名>测试规格.md
    test_specs/tr_ts.json

其中：

-   如果只找到一个有效上下文，直接使用；
-   如果找到多个有效上下文，停止执行并列出候选 `<design_task_id>/<IR>`，不得静默选择；
-   `cida_info.json` 必须使用 init 阶段已经生成并由 explore 阶段落入当前上下文目录的文件，只读，不得重新生成或覆盖；
-   从 `cida_info.json` 及其所属目录获取并校验 `design_task_id` 和 IR；
-   将完整 CIDA 上下文传给每个 `test-design-agent`；
-   当前 TS JSON 提取所需的 `design-task-id` 来自该上下文，不再要求用户传入；
-   TS完整列表必须来自 `tr_ts.json`；
-   测试规格文档提供TR级背景信息。

### Phase 1: TS Filtering

根据位置参数中的 TS 列表筛选目标 TS。

未指定时处理全部 TS。

规则：

-   所有 TS 参数统一标准化为 `TS_<NN>`；
-   对重复 TS 去重并保持用户输入顺序；
-   所有目标 TS 必须存在于 `tr_ts.json`；
-   任一 TS 不存在时，在初始化卡片和启动 Agent 前停止并报告。

### Phase 1.5: Initialize TS Working Cards

目标 TS 按每批最多 3 个分批处理。每批启动 TS 设计 SubAgent 之前，必须先为当前批次初始化 working 卡片。

规则：

-   一个 TS 对应一个 working 卡片；
-   初始化 key 必须使用 `<IR>_<ts-id>`；
-   示例：`IR20251206000098_ts_01`；
-   初始化脚本必须使用原始 card-initializer 脚本；
-   card_id 文件保留在初始化脚本目录，不复制到 `.design_output/<design_task_id>/<IR>/cards/`；
-   每个 TS 必须使用一次独立的 bash 工具调用，不得在同一次 bash 调用中串联多个 `card_generate.py`；
-   当前批次最多同时发起 3 个独立的卡片初始化调用；
-   当前批次初始化完成后立即进入该批次的并行测试设计阶段；
-   当前批次所有卡片均验证成功后才能启动本批 `test-design-agent`；
-   任一卡片初始化失败时，不得启动当前批次的任何 `test-design-agent`，避免后续 completed 卡片无法关联。

每个 TS 的独立工具调用必须遵循以下格式：

```bash
cd "<root>/.testagent/skills/card-initializer/scripts/test_case"; python -u card_generate.py <IR>_<ts-id>
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

    <root>/.testagent/skills/card-initializer/scripts/test_case/<IR>_<ts-id>_card_id.txt

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

1.  IR 编号；
2.  当前 TS 编号（如 `ts_01` 或 `01`）；
3.  当前负责生成的 TS 信息；
4.  当前 TR 信息；
5.  TR级背景测试规格；
6.  当前 TR 下完整 TS 清单；
7.  输出目录；
8.  测试规格文件路径；
9.  `design-task-id`；
10. 完整 `cida_info.json` 上下文。

`coretest-design` 不再在主流程中统一调用 `build_tp_tc_json.py`，也不再统一调用 `test-case-card-agent`。JSON 提取和卡片更新已经下沉到每个 `test-design-agent` 内部。

## TS边界约束（必须遵守）

并行生成时，不允许只给 SubAgent 单独 TS 信息。

每个 SubAgent 必须知道：

    当前TR全部TS列表

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

    .design_output/<design_task_id>/<IR>/test_design/

每批输出：

    .design_output/<design_task_id>/<IR>/test_design/

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
  cida_info.json 缺失          退出
  找到多个有效上下文           列出候选并退出
  用户指定的TS不存在           初始化卡片前退出
  卡片初始化失败               停止流程
  test-design-agent 调用失败   记录失败TS并继续其他已启动TS
  单TS设计失败                 由 test-design-agent 返回失败，不生成该TS JSON和卡片
  单TS JSON生成失败            由 test-design-agent 返回失败，不生成该TS卡片
  单TS卡片失败                 由 test-design-agent 返回失败，不影响其他TS
  汇总阶段发现失败TS           列出失败阶段和失败原因

## Guardrails

-   不生成测试脚本；
-   不跳过校验；
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
-   每个 `test-design-agent` 必须接收完整 CIDA 上下文；
-   不得重新生成或覆盖 init 阶段生成的 `cida_info.json`；
-   不等待全部 TS markdown 生成完成后再统一提取 JSON；
-   不等待全部 JSON 生成完成后再统一生成卡片；
-   主流程不统一调用 `build_tp_tc_json.py`；
-   主流程不统一调用 `test-case-card-agent`；
-   不调用 `run_card_flow.py`；
-   一个TS对应一个卡片；
-   禁止SubAgent生成非目标TS的TP/TC；
-   TS之间必须保持测试职责边界，避免重复覆盖。
