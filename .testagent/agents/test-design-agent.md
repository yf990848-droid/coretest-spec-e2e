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
3. 用固定脚本检索图谱因子，保存候选证据，再生成并校验本地因子计划；
4. 调用 `test-case-card-adapter` skill 更新当前 TS working 卡片为 completed。

当前 TS 未完成卡片闭环时，不允许返回成功。

## 输入上下文

每次调用必须提供：

- TR ID `tr_id` 和完整 `tr_info.json`；
- 需求编号 `requirement_id`（来自 `cida_info.json.requirement_number`，支持 IR/SR）；
- 当前 TS 编号、当前 `ts_catalog.json` 条目和当前 TR 信息；
- 当前 TR 下完整 `ts_catalog.json`；
- 按来源精确提取的当前 TS 完整规格内容：普通 TS 通过 `tr_ts_index`，DFX 通过 `platform_ts_id`；
- 测试规格文件路径（只用于来源审计）；
- `design_task_id`；
- `.design_output/<design_task_id>/TR_<tr_id>/cida_info.json` 文件路径及完整 CIDA 内容；
- `.design_output/<design_task_id>/TR_<tr_id>/test_design/` 输出目录。
- 当前版本的产品名，用于图谱检索时过滤产品。

必须使用当前 `TR_<tr_id>` 目录中的 `cida_info.json`，只读，不得重新生成或覆盖，也不得改用 `.testagent/skills/test-case-card/config/cida_info.json`。

步骤 1 开始前必须从扩展包仓库根目录精确读取：

- `.testagent/rules/tp-tc-design-logic.md`；
- `.testagent/rules/tp-tc-output.md`。

两个文件均读取成功后才能调用 `test-design`。不得在 `.testagent/skills/test-design/rules/` 下查找，不得使用 glob 搜索替代文件；任一文件不存在或读取失败时，当前 TS 立即失败。

只允许使用调用方传入的当前 TS 规格、当前 catalog 条目、完整 TS 清单和上述两个公共规则文件。DFX 不存在普通 `tr_ts_index`；不得扫描整个 TR、`test_specs`、`test_design` 或 `test-design/references` 目录，不得查找历史设计样例或读取其他 TS 产物。

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

叙述区标题与 TP 表 `dimension` 不是同一套名称，必须按下表转换：

| 叙述区二级标题 | TP 表 `dimension` |
|---|---|
| `基于业务场景的设计` | `基于业务场景` |
| `基于业务内部实现的设计` | `基于业务内部实现` |
| `功能交互设计` | `功能交互设计` |
| `测试类型交互设计` | `测试类型交互设计` |

禁止把标题 `基于业务内部实现的设计` 直接写入 `dimension`。TP 表中的 `tpType`、`tpSourceType` 必须严格使用 `.testagent/rules/tp-tc-design-logic.md` 映射，所有生成 TP 的 `tpSourceType` 必须非空。执行 JSON 脚本前，检查全部 `dimension` 均属于 `.testagent/rules/tp-tc-output.md` 定义的四类合法值。

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

### 3. 生成因子计划（只在本地，不写平台）

先调用固定脚本，使用 `test-graph/scripts/query.py search` 按当前 TS 和每个 TP
检索 TestFactor；仅当 `ts_type=scene` 时同时检索 SceneFactor。产品名使用
当前版本的产品名（例如 `UPCF`），不能由 TS 名称猜测。脚本读取 catalog 与 TP JSON，
把每次查询、原始 JSON 响应和去重候选写入 `ts_<NN>_factor_candidates.json`：

```bash
python "<root>/.testagent/skills/coretest-design/scripts/factor_candidates.py" \
  --catalog-file "<tr_dir>/test_specs/ts_catalog.json" \
  --tp-file "<test-design-dir>/ts_<NN>_tp.json" \
  --graph-script "<root>/.testagent/skills/test-graph/scripts/query.py" \
  --ts-key "TS_<NN>" --ts-type "<catalog.ts_type>" \
  --product "<产品名>" --output "<test-design-dir>/ts_<NN>_factor_candidates.json"
```

脚本返回 `success=false`、产品名无法确定或查询失败时停止当前 TS 的因子计划与卡片完成，
不得用空数组替代查询结果。检索成功后只从证据中实际查到的因子中选择，不按名称
伪造 ID。先选择 TS 因子，再根据生成的 TP 为每个 `tp_id_temp` 选择 TS 因子子集。
测试因子的 `testFactorId` 使用图谱的 `test_factor_id` UUID；平台关系数字 `id`
仅用于 Archive 查询和幂等核验。候选缺少 UUID、编码或名称时不要选入计划。

写入 `test_design/ts_<NN>_factor_plan.json`，结构为：

```json
{
  "ts_key": "TS_17",
  "ts_type": "scene",
  "limits": {"max_ts_factors": 5, "max_tp_factors": 3},
  "test_factors": [{
    "testFactorId": "测试因子UUID", "number": "因子编码", "name": "因子名称",
    "type": 0, "assoActType": "SceneAnalysis",
    "sourceType": "TestFactorLibrary", "factorType": "BusinessInterImplAnalysis",
    "pbi": "版本PBI"
  }],
  "scene_factors": [{
    "factorCode": "场景因子编码", "sceneFactorCode": "场景因子编码",
    "factorName": "场景因子名称", "assoActType": "SceneAnalysis",
    "sourceType": "scene", "pbi": "版本PBI"
  }],
  "tp_factors": {
    "TP.17.01": {
      "test_factor_ids": ["测试因子UUID"],
      "scene_factor_codes": ["场景因子编码"]
    }
  }
}
```

`limits` 可按本次设计策略调整，缺省均采用 5/3；Design 与 Archive 读取同一计划。
`factorType`、`assoActType` 和 `sourceType` 按检索结果与 CLI 的当前 TS 活动契约
选择，禁止把示例值套用到所有 TS。TP key 必须以真实 `tp.json.tps[].tp_id_temp`
为准。每 TS 默认最多 5 个、每 TP 默认最多 3 个因子，未被 TP 使用的 TS 因子
删除；没有候选时两个 TS 数组为空，每个 TP 也必须有两个空数组。

执行确定性校验：

```bash
python "<root>/.testagent/skills/coretest-design/scripts/factor_plan.py" \
  --plan-file "<test-design-dir>/ts_<NN>_factor_plan.json" \
  --tp-file "<test-design-dir>/ts_<NN>_tp.json" \
  --candidates-file "<test-design-dir>/ts_<NN>_factor_candidates.json" \
  --ts-key "TS_<NN>" --ts-type "<catalog.ts_type>"
```

只有检索和校验均输出 `success=true` 才能更新卡片；检索成功而候选不匹配时因子为空也是有效计划。上限写入
`limits`，Archive 按同一计划校验；不得在两个阶段分别设置不一致的值。

---

### 4. 更新测试用例卡片

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
- ts_<NN>_factor_candidates.json 的所有查询成功，ts_<NN>_factor_plan.json 已通过校验；
- ts_<NN>_test_case.json 存在；
- working 卡片已更新为 completed。

---

## 失败输出

失败时返回：

```text
TSxx失败

失败阶段:
test-design / JSON / factor-plan / test-case-card-adapter

失败原因:
xxx
```
