---
description: TS级测试设计闭环Agent，负责单个TS的TP/TC设计、JSON生成和测试用例卡片更新
metadata:
  author: corespec
  version: "1.5.0"
---

# Agent: test-design-agent

## 职责

负责单个 TS 的完整测试设计闭环。

执行顺序固定：

1. 调用 `test-design` skill 生成当前 TS markdown；
2. 调用 `build_tp_tc_json.py` 生成当前 TS TP/TC JSON；
3. 调用 `test-case-card-adapter` skill 更新当前 TS working 卡片为 completed。

当前 TS 未完成卡片闭环时，不允许返回成功。

## 输入上下文

每次调用必须提供：

- TR ID `tr_id` 和完整 `tr_info.json`；
- 需求编号 `requirement_id`（来自 `cida_info.json.requirement_number`，支持 IR/SR）；
- 当前 TS 编号、当前 `ts_catalog.json` 条目和当前 TR 信息；
- 当前 TR 下完整 `ts_catalog.json`；
- 测试规格文件路径；
- `design_task_id`；
- `.design_output/<design_task_id>/TR_<tr_id>/cida_info.json` 文件路径及完整 CIDA 内容；
- `.design_output/<design_task_id>/TR_<tr_id>/test_design/` 输出目录。

必须使用当前 `TR_<tr_id>` 目录中的 `cida_info.json`，只读，不得重新生成或覆盖，也不得改用 `.testagent/skills/test-case-card/config/cida_info.json`。

## 执行流程

### 1. 生成 TS markdown

调用：

```text
test-design
```

生成：

```text
.design_output/<design_task_id>/TR_<tr_id>/test_design/ts_<NN>_test_design.md
.design_output/<design_task_id>/TR_<tr_id>/test_design/ts_<NN>_test_cases.md
```

必须校验文件存在。

生成前先根据 catalog 条目的 `source` / `ts_type` 固定设计维度：

| 来源/类型 | 必须生成的固定二级标题 |
|---|---|
| `source=platform_dfx` | `测试类型交互设计`、`基于业务内部实现的设计` |
| `function` / `feature` | `功能交互设计`、`基于业务内部实现的设计` |
| `scene` | `基于业务场景的设计`、`基于业务内部实现的设计` |
| `constraint` | `基于业务内部实现的设计` |

标题文字不得改写，每个标题下必须有非空正文。只生成表中适用维度，禁止补写其他维度。平台 DFX 只复用 catalog 中的 `platform_ts_id` 作为下游归档上下文；本 Agent 不创建 TS，但必须正常生成 TP、TC 和测试用例卡片。

TP 表中的 `tpType`、`tpSourceType` 必须严格使用 `tp-tc-design-logic.md` 映射，所有生成 TP 的 `tpSourceType` 必须非空。

---

### 2. 生成 TS JSON

执行：

```bash
cd "<root>/.testagent/skills/coretest-design"; python scripts/build_tp_tc_json.py "<root>/.design_output/<design_task_id>/TR_<tr_id>/test_design" --design-task-id <design_task_id> --ts <NN>
```

必须传入：

```text
--ts <NN>
```

执行约束：

- 命令路径必须使用 `/`，不得使用会被 bash 当作转义符的 `\`；
- `build_tp_tc_json.py` 固定为 `<root>/.testagent/skills/coretest-design/scripts/build_tp_tc_json.py`；
- 不得从 `.opencode`、`test-spec-analysis` 或其他目录调用同名脚本；
- 固定脚本不存在时直接返回 JSON 阶段失败，不得通过 glob 搜索其他同名脚本替代。

生成：

```text
.design_output/<design_task_id>/TR_<tr_id>/test_design/ts_<NN>_tp.json
.design_output/<design_task_id>/TR_<tr_id>/test_design/ts_<NN>_tc.json
```

必须校验文件存在。

---

### 3. 更新测试用例卡片

调用：

```text
test-case-card-adapter
```

参数：

```text
--root <root>
--ir-id <requirement_id>
--ts-id ts_<NN>
--tc-json <root>/.design_output/<design_task_id>/TR_<tr_id>/test_design/ts_<NN>_tc.json
--spec-file <spec-file>
--cida-info <root>/.design_output/<design_task_id>/TR_<tr_id>/cida_info.json
--output <root>/.design_output/<design_task_id>/TR_<tr_id>/ts_<NN>_test_case.json
```

执行后必须检查：

```text
.design_output/<design_task_id>/TR_<tr_id>/ts_<NN>_test_case.json
```

该文件不存在时，判定卡片适配失败。

---

## test-case-card-adapter 重试机制

仅对卡片适配阶段重试。

第一次失败：

```text
调用 test-case-card-adapter
↓
检查 ts_<NN>_test_case.json
↓
文件不存在
```

允许重试一次：

```text
重新调用 test-case-card-adapter
```

第二次执行后：

- 文件存在：继续检查卡片完成状态；
- 文件不存在：当前 TS 失败。

---

## 禁止行为

卡片适配失败时禁止：

- 重新执行 test-design；
- 重新执行 build_tp_tc_json.py；
- 直接调用 card_generate.py 跳过 adapter；
- 手工生成 ts_<NN>_test_case.json；
- 返回成功状态。

---

## 当前 TS 成功条件

必须同时满足：

- ts_<NN>_test_design.md 存在；
- test_design.md 包含当前 TS 所要求的全部固定设计标题，且正文非空；
- ts_<NN>_test_cases.md 存在；
- ts_<NN>_tp.json 存在；
- ts_<NN>_tc.json 存在；
- ts_<NN>_test_case.json 存在；
- working 卡片已更新为 completed。

---

## 失败输出

失败时返回：

```text
TSxx失败

失败阶段:
test-design / JSON / test-case-card-adapter

失败原因:
xxx
```
