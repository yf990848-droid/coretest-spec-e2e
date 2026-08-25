---
name: coretest-archive
description: 按 TR、TS、TP 或 TC 目标归档测试设计产物，复用既有 TR 和平台 DFX TS，并在全部对象处理完成后自动同步任务、TR 和 TS 在线文档。
metadata:
  author: corespec
  version: "2.8.0"
---

# CoreTest Archive Skill

## 目标

解析归档目标并定位 `.design_output/<design_task_id>/TR_<tr_id>/` 上下文，生成对象执行计划和文档范围，然后调用一个 `coretest-archive-agent` 完成闭环。

内部顺序固定为：

```text
coretest-archive-agent
→ coretest-object-archive（完整 TS/TP/TC）
→ coretest-document-sync
→ test-portal-card
→ 汇总
```

本 Skill 只负责入口解析、上下文定位、输入校验和 Agent 调度，不直接调用创建 MCP、CoreTool 文档命令或 Portal。

## 使用方式

```text
/coretest-archive <tr_id> <归档目标...>
```

示例：

```text
/coretest-archive 3863 TR
/coretest-archive 3863 TS
/coretest-archive 3863 TS_01 TS_02
/coretest-archive 3863 TP
/coretest-archive 3863 TS_01/TP.01.03.01
/coretest-archive 3863 TC
```

| 输入 | 对象归档范围 |
|---|---|
| `TR` | 复用既有 TR，不创建平台对象 |
| `TS` | 全部 TS |
| `TP` | 全部 TS 和全部 TP |
| `TC` | 全部 TS、全部 TP 和全部 TC |

每个有效目标自动同步父级文档：设计任务和 TR 始终同步；TS、TP、TC 目标还同步目标或所属 TS 文档。TP、TC 自身文档暂不写入。

## Phase 0：解析输入

1. 第一个位置参数必须是纯数字 `tr_id`；
2. 其后至少提供一个归档目标；
3. 识别 `TR`、`TS`、`TP`、`TC` 层级关键字；
4. 其他参数作为指定对象标识精确匹配；
5. 重复目标去重但保持输入顺序；
6. 拒绝已废弃的 `--document` 参数。

指定对象规则：

- TS 编号和来源只从 `ts_catalog.json.items[]` 读取；
- DFX TS 复用 `platform_ts_id`；
- 普通 TS 使用现有创建或状态复用逻辑；
- TP 推荐使用 `TS_<NN>/<tp_id_temp>`；裸标识仅在全部 TP JSON 中唯一时允许；
- TC 推荐使用 `TS_<NN>/<tc_id_temp>`；裸标识或 `case_id` 仅在全部 TC JSON 中唯一时允许；
- 指定对象只向上补齐父级依赖，绝不向下展开；
- `TS_01` 不包含其下 TP/TC。

## Phase 1：定位上下文

只使用以下文件匹配定位：

```text
.design_output/*/TR_<tr_id>/tr_info.json
```

必须得到唯一上下文，并按当前目标检查：

```text
tr_info.json
cida_info.json
test_specs/tr_ts.json
test_specs/ts_catalog.json
测试规格 Markdown
test_design/ts_*_test_design.md
test_design/ts_*_tp.json（计划需要时）
test_design/ts_*_tc.json（计划需要时）
.design_output/design_task_info.json
archive/archive_state.json
```

TS-only 不读取 TP/TC JSON；指定 TP 不读取 TC JSON。不得读取或写入 `corespec/changes/`。

## Phase 2：生成对象执行计划

计划固定结构：

```json
{
  "tr": [],
  "ts": ["TS_01"],
  "tp": [],
  "tc": []
}
```

范围规则：

```text
TR              → 不创建对象，四层计划可全空
TS_01           → TS_01
TS              → 全部 TS
TS_01/TP.xxx    → 所属 TS + 指定 TP
TP              → 全部 TS + 全部 TP
TS_01/TC.xxx    → 所属 TS + 所属 TP + 指定 TC
TC              → 全部 TS + 全部 TP + 全部 TC
```

依赖只向上补齐。保持用户输入或源文件的稳定顺序。计划包含 TP/TC 时，目标 TP 的 `tpSourceType` 必须非空且合法；否则在调用 Agent 前停止。

## Phase 3：生成文档范围

文档范围独立于对象计划：

```json
{
  "task": ["<design_task_id>"],
  "tr": ["<tr_id>"],
  "ts": ["TS_01"]
}
```

- 任一有效目标都加入当前设计任务和 TR；
- TS 目标加入目标 TS；
- TP/TC 目标加入所属 TS；
- 全量目标加入涉及的全部 TS；
- 混合目标取并集，TS 按 catalog 顺序去重；
- TR-only 的 TS 列表为空；
- 不生成 TP/TC 文档节点。

## Phase 4：调用单个 Archive Agent

只启动一个：

```text
agents/coretest-archive-agent
```

提供：

- 扩展包根目录；
- 原始目标、去重目标；
- 本次对象执行计划和文档范围；
- `tr_id`、`design_task_id`、IR、PBI、`task_name`、`creator`；
- 当前 TR 上下文路径；
- `tr_info.json`、`cida_info.json`、测试规格 Markdown；
- `tr_ts.json`、`ts_catalog.json`；
- `test_design/`；
- 仅当计划需要时提供相关 TP/TC JSON；
- `archive_state.json`、`design_task_info.json`；
- 当前 TR 的完整 TS 清单。

Agent 必须依次：

1. 初始化状态并锁定计划；
2. 调用一次 `coretest-object-archive` 完成全部对象；
3. 校验对象终态；
4. 调用 `coretest-document-sync` 并生成终态 `document_plan.json`；
5. 通过文档门禁后调用 `test-portal-card`；
6. 汇总对象、文档和 Portal 结果。

主 Skill 不得在 Agent 返回后补做任何对象、文档或 Portal 写入。

## Phase 5：汇总要求

输出：

- 用户目标和计划 TS/TP/TC 数量；
- 当前计划内对象的成功、失败、复用、blocked 和真实 ID；
- TR Init 复用状态；
- `archive_state.json` 路径；
- 任务、TR、TS 文档节点状态；
- `document_plan.json` 路径；
- Portal 结果和最终跳转对象。

结果语义：

- 对象成功或复用且全部文档节点成功：`成功`；
- 对象成功或复用但任一文档节点失败：`部分成功`；
- 对象失败或 blocked：沿用对象失败规则，同时报告文档结果；
- Portal 成功不能掩盖对象或文档失败。

禁止输出“文档同步需要后续单独执行”。

## 错误处理

| 场景 | 处理 |
|---|---|
| 未提供 `tr_id` 或目标 | 停止并提示格式 |
| `ts_catalog.json` 缺失或非法 | 停止并提示重新执行 Explore |
| 输入 `--document` | 按未知参数停止 |
| 找不到或存在多个 TR 上下文 | 列出候选并停止 |
| 指定对象不存在或不唯一 | 停止，不调用 Agent |
| Object Skill 失败 | 保留即时状态，继续可执行文档节点并报告对象失败 |
| Document Skill 失败 | 生成或保留失败计划，不回滚对象，最终不得返回成功 |
| Portal 失败 | 保留对象和文档结果，不重复写入 |

## Guardrails

- TR 只复用，禁止创建；
- `execution_plan.tr` 必须为空；
- 不修改任何设计输入 JSON；
- 不重新查询或改变 TS 编号；
- 真实平台 ID 只保存到 `archive/`；
- 一次请求只调用一个 Archive Agent；
- Object Skill 只调用一次且先于 Document Skill；
- Document Skill 必须先于 Portal；
- `document_plan.json` 未终态时禁止最终成功；
- 已成功对象不得重复创建。
