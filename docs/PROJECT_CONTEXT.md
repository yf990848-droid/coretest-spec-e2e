# coretest-spec-e2e 项目上下文

> 最后更新：2026-08-26  
> 当前扩展版本：`0.2.3`  
> 当前开发基线：`main`（已包含 0.2.3 之后的 DFX 与文档归档增强）  
> 默认分支：`main`

## 1. 项目目标

`coretest-spec-e2e` 是基于 TestAgent 的 E2E 测试设计扩展，围绕平台已有设计任务和 TR，完成需求探索、测试规格、TS 级 TP/TC 设计、测试用例卡片、平台对象归档、在线文档同步及 Portal 刷新。

当前正式流程：

```text
/coretest-init
→ 拉取设计任务、已有 TR 及直接关联需求
→ /coretest-explore <tr_id>
→ 生成普通/DFX 测试规格和统一 TS 编号目录
→ /coretest-design <tr_id> [TS列表]
→ 按 TS 生成 Markdown、TP/TC JSON 和测试用例卡片
→ /coretest-archive <tr_id> <TR|TS|TP|TC|指定对象...>
→ 复用 TR/平台 DFX TS，创建或复用普通 TS、TP、TC
→ 同步设计任务、TR、相关 TS 在线文档
→ 刷新 Portal 卡片
```

核心目标：

- 以 TR 直接关联需求作为唯一分析范围；
- 对平台 DFX TS 和 Explore 普通 TS 建立稳定统一编号；
- 每个 TS 独立完成测试设计和用例卡片闭环；
- 支持 TR、TS、TP、TC 目标解析、父级补齐、幂等归档和断点续跑；
- 将对象归档、在线文档同步和 Portal 结果分别记录并汇总；
- 避免长上下文导致 Agent 跳步，将脆弱操作收敛到独立 Agent 和确定性脚本。

## 2. 当前版本与主分支状态

根目录 `codeagent-extension.json` 当前仍为：

```text
coretest-spec-e2e 0.2.3
```

0.2.3 已完成并验证测试用例上报字段链路：

- `TestType` 按规则映射，无法识别时默认 `"1"`；
- `AutoType` 自动化为 `"1"`，非自动化或无法识别时为 `"0"`；
- `envtype` 当前为空字符串；
- `DesignNote` 根据测试目的和验证内容生成，不允许为空；
- 字段通过 `tp-tc-output.md → build_tp_tc_json.py → prepare_test_case_card.py → archive_testcase.js` 传递至 CIDA；
- `caseHandler` 当前不处理。

`main` 已在 0.2.3 基础上继续完成：

1. Explore 查询平台已有 TS，识别 DFX 并生成 DFX 测试规格；
2. 使用 `platform_ts.json + tr_ts.json → ts_catalog.json` 建立统一编号；
3. Design 按 `source=platform_dfx/explore` 精确取得单 TS 规格，禁止目录扫描补偿；
4. 修复叙述区标题、TP 表 `dimension` 与 `tpSourceType` 混用；
5. Archive 支持 `TR` 目标，但只复用 TR、不创建 TR；
6. 将对象归档和在线文档同步拆为独立能力；
7. 在线文档同步通过独立 Agent 隔离上下文，并由脚本确定性执行；
8. 修复 IDP topic 查询返回“父 topic + 子 topic”时的父节点匹配问题。

版本演进：

| 版本/阶段 | 主要能力 |
|---|---|
| 0.1.x | 打通 Init、Explore、Design、卡片和 Archive 基础链路 |
| 0.2.0 | 完善 E2E 测试设计与 TR/TS/TP/TC 自动化处理 |
| 0.2.1 | 完成 TR 级目录适配、已有 TR 复用和文件化归档计划 |
| 0.2.2 | 增强 CIDA 卡片字段，并修复扩展版本未同步导致旧卡片被加载的问题 |
| 0.2.3 | 完成 TestType、AutoType、envtype、DesignNote 的规则化生成和端到端透传 |
| 当前 `main` | 增加 DFX 规格/统一编号、Design 精确输入、归档能力拆分及确定性在线文档同步 |

## 3. 快速使用

以下命令中的第一位置参数均为平台 `tr_id`。

### 3.1 初始化

```text
/coretest-init "UPCF 27.0.0"
```

Init 查询 PBI、设计任务、已有 TR 和直接关联需求，并生成 TR 级上下文。后续阶段不得自行创建 TR。

### 3.2 Explore

```text
/coretest-explore <tr_id>
/coretest-explore <tr_id> --skip-clarify
```

### 3.3 Design

处理 catalog 中全部 TS：

```text
/coretest-design <tr_id>
```

处理指定 TS：

```text
/coretest-design <tr_id> TS_01 TS_11
```

### 3.4 Archive

```text
/coretest-archive <tr_id> TR
/coretest-archive <tr_id> TS
/coretest-archive <tr_id> TS_01 TS_11
/coretest-archive <tr_id> TP
/coretest-archive <tr_id> TS_01/TP.01.03.01
/coretest-archive <tr_id> TC
```

`TR` 目标只复用现有 TR 并同步设计任务/TR 文档，绝不调用 `create_tr`。`--document` 已废弃，传入时按未知参数报错。

## 4. 核心组件

| 组件 | 当前版本 | 职责 |
|---|---:|---|
| `coretest-init` | 1.2.1 | 拉取设计任务、已有 TR 和直接关联需求 |
| `coretest-explore` | 0.5.0 | 生成普通/DFX 测试规格、`tr_ts.json` 和统一 `ts_catalog.json` |
| `coretest-design` | 1.5.0 | 按 catalog 处理全部或指定 TS，完成 Markdown、JSON 和卡片闭环 |
| `coretest-archive` | 2.9.0 | 解析对象计划和文档范围，调度 Archive Agent |
| `coretest-archive-agent` | 1.12.0 | 编排对象 Skill、文档 Agent、Portal 和最终汇总 |
| `coretest-object-archive` | — | 串行创建或复用 TS、TP、TC，并即时保存状态 |
| `coretest-document-sync-agent` | 1.0.0 | 以独立上下文调用文档同步 Skill 和脚本 |
| `coretest-document-sync` | — | 定义文档输入、CLI 返回和终态门禁契约 |

## 5. 阶段契约

### 5.1 Init

关键产物：

```text
.design_output/design_task_info.json
.design_output/<design_task_id>/TR_<tr_id>/tr_info.json
.design_output/<design_task_id>/TR_<tr_id>/cida_info.json
```

约束：

- 单轮初始化只调用一次平台 Init 查询；
- `tr_info.json.requirements[]` 是 Explore 的权威需求范围；
- TR 没有有效直接关联需求时，不进入正式 Explore；
- 后续阶段不创建 TR。

### 5.2 Explore

正式输入：

```text
/coretest-explore <tr_id> [--skip-clarify]
```

核心流程：

```text
tr_info.json.requirements[]
→ 查询全部需求并建立 document_manifest.json
→ 下载并解析全部唯一 IDP/DBOX 文档
→ 查询平台已有 TS，保存 platform_ts.json
→ 一次 test-spec-analysis 生成普通与 DFX 测试规格
→ build_tr_json.py 仅生成普通 tr_ts.json.test_specs[]
→ build_ts_catalog.py 合并 DFX 与普通 TS
```

统一编号规则：

- 平台 `scene/function/feature/constraint` 不是 DFX，不进入平台 DFX 清单；
- 其他平台 TS 作为 DFX，保留唯一 `platform_ts_id`；
- DFX 从 `TS_01` 起按平台查询顺序编号；
- Explore 普通 TS 接在 DFX 之后；
- DFX 不进入 `tr_ts.json.test_specs[]`，避免 Archive 重复创建；
- DFX 规格写入测试规格 Markdown 的独立章节，并通过 `platform_ts_id` 唯一定位；
- 同一轮 Explore 只查询一次平台 TS，规格生成和 catalog 共用 `platform_ts.json`。

主要产物：

```text
TR_<tr_id>/
├── design_doc/document_manifest.json
├── 系统需求.md
├── 功能设计.md
├── sr_specs/
└── test_specs/
    ├── <TR名称>测试规格.md
    ├── platform_ts.json
    ├── tr_ts.json
    └── ts_catalog.json
```

### 5.3 Design

正式输入：

```text
/coretest-design <tr_id> [TS列表]
```

规则：

- TS 完整列表和稳定编号只来自 `ts_catalog.json.items[]`；
- 不传 TS 时处理全部 catalog 项；指定时按 `ts_key` 精确匹配；
- 每批最多并行 3 个 TS Agent；
- `source=platform_dfx` 根据 `platform_ts_id` 从 DFX 规格章节取得唯一规格，不查找 `tr_ts_index`；
- `source=explore` 根据 `tr_ts_index` 读取 `tr_ts.json.test_specs[]`；
- 主流程向单 TS Agent 传入精确规格，不传目录供 Agent 自行搜索；
- Agent 不扫描其他 TS 产物、历史样例或不存在的 references 目录；
- 一个 TS 对应一个测试用例卡片，key 为 `<requirement_id>_<ts-id>`。

主要产物：

```text
TR_<tr_id>/test_design/
├── ts_<NN>_test_design.md
├── ts_<NN>_test_cases.md
├── ts_<NN>_tp.json
└── ts_<NN>_tc.json
```

设计维度必须区分三套名称：

| 用途 | 内部实现类正确值 |
|---|---|
| 叙述区标题 | `基于业务内部实现的设计` |
| TP 表 `dimension` | `基于业务内部实现` |
| `tpSourceType` | `基于业务内部实现设计—测试因子` |

`dimension` 只允许：

```text
基于业务场景
基于业务内部实现
功能交互设计
测试类型交互设计
```

当前 `build_tp_tc_json.py --ts <NN>` 会在过滤目标前扫描全部设计文件，因此可能对其他 TS 输出无关的缺失配对警告；该警告不代表目标 TS 处理失败，过滤时机仍待最小修复。

### 5.4 Archive

正式输入：

```text
/coretest-archive <tr_id> <TR|TS|TP|TC|指定对象...>
```

对象范围：

```text
TR           → 空对象计划，只复用 TR
TS_01        → 指定 TS
TS           → 全部 TS
指定 TP      → 所属 TS + 指定 TP
TP           → 全部 TS + 全部 TP
指定 TC      → 所属 TS + 所属 TP + 指定 TC
TC           → 全部 TS + 全部 TP + 全部 TC
```

文档范围：

```text
TR           → 设计任务 + TR
TS           → 设计任务 + TR + 相关 TS
TP/TC        → 设计任务 + TR + 所属 TS
```

TP、TC 自身文档暂不同步。混合目标取并集，TS 按 catalog 顺序去重。

固定编排：

```text
coretest-archive-agent
→ 初始化 archive_state.json 并锁定 request_plan.json
→ coretest-object-archive（一次调用，串行处理全部对象）
→ 对象终态校验
→ 生成 document_request.json
→ coretest-document-sync-agent（独立上下文，一次调用）
→ document_plan.json 终态校验
→ test-portal-card
→ 汇总
```

对象规则：

- TR 永远只复用，`execution_plan.tr=[]`；
- DFX TS 复用 catalog 的 `platform_ts_id`，不调用 `create_ts`；
- 普通 TS 通过 `tr_ts_index` 创建或复用；
- 对象只能按已锁定计划执行，禁止从源 JSON 扩大范围；
- 成功对象立即保存真实 ID 和原始响应；
- 已成功对象重跑时直接复用；
- TP 的 `tpSourceType` 必须在调用 Agent 前非空且合法，不允许运行时猜测或补写；
- TC 以平台返回 `success=true` 为成功，不要求 `tcId/platform_id`。

结果语义：

- 对象全部成功或复用、文档全部成功：`成功`；
- 对象全部成功或复用、任一文档失败：`部分成功`；
- 对象失败或 blocked：沿用对象失败规则，并同时报告文档实际结果；
- 文档失败不回滚对象；Portal 成功不能掩盖对象或文档失败。

### 5.5 在线文档同步

文档同步不在 Archive Agent 的长上下文内展开，而由独立 `coretest-document-sync-agent` 执行：

```text
读取 document_request.json
→ 加载 coretest-document-sync
→ 解析 CoreTool 绝对路径并检查认证
→ 调用 document_sync.py 一次
→ 回读 document_plan.json
```

脚本固定完成：

- 在外部命令前初始化全部 TASK/TR/TS 节点；
- 精确提取测试规格和 TS 设计 Markdown 章节；
- 查询或复用设计任务 `idp_doc_id`；
- 查询活动 topic；
- 使用 URL namespace UUIDv5 生成稳定 `source_value_uuid`；
- 生成 UTF-8 无 BOM payload；
- 调用 `source-data write`；
- 保存命令、stdout、stderr、退出码和超时状态；
- 单节点失败后继续其他节点；
- 返回前关闭全部 `pending`。

CoreTool 契约：

- 所有命令使用已解析的绝对路径，禁止裸 `coretool`；
- 单条命令超时 120 秒，自动重试 0 次；
- `task list` 在 `items[]` 中按 `id == design_task_id` 唯一匹配；
- TR topic 的父名称使用 `tr_info.json.tr_name`，不能使用设计任务名称；
- `topic list` 可能返回目标 topic 及子 topic；只接受 `topic_name` 完全相等、`topic_id` 非空、`deleted=0` 的唯一精确项；
- 不要求整个 `items` 或 `pagination.total` 等于 1；
- `source-data write` 返回成功文本，不按 JSON 解析；
- 文档节点状态相互隔离，失败节点不阻塞其他节点。

文档终态门禁只表示所有节点均已结束，不表示全部成功。`document_plan.status=partial` 时仍可刷新 Portal，但最终归档结果必须为“部分成功”。

## 6. 标准目录结构

```text
.design_output/
├── design_task_info.json
└── <design_task_id>/
    └── TR_<tr_id>/
        ├── tr_info.json
        ├── cida_info.json
        ├── design_doc/
        │   └── document_manifest.json
        ├── 系统需求.md
        ├── 功能设计.md
        ├── sr_specs/
        ├── test_specs/
        │   ├── <TR名称>测试规格.md
        │   ├── platform_ts.json
        │   ├── tr_ts.json
        │   └── ts_catalog.json
        ├── test_design/
        │   ├── ts_<NN>_test_design.md
        │   ├── ts_<NN>_test_cases.md
        │   ├── ts_<NN>_tp.json
        │   └── ts_<NN>_tc.json
        ├── ts_<NN>_test_case.json
        └── archive/
            ├── request_plan.json
            ├── archive_state.json
            ├── document_request.json
            ├── document_plan.json
            ├── document_payloads/
            └── responses/
```

## 7. 当前验证状态

### 7.1 已验证

- Init 可拉取设计任务、已有 TR 和直接关联需求；
- Explore 可在 TR 上下文内生成普通测试规格，并查询平台 DFX TS；
- 实际平台查询曾返回 10 条 DFX TS，均具有唯一非空 `platform_ts_id`；
- DFX 和普通 TS 可生成统一 `ts_catalog.json`，DFX 在前、普通 TS 接续编号；
- Design 可分别处理 DFX 和普通 TS，且不再依赖目录扫描补偿规格；
- `dimension` 标题映射已经在 Agent、Skill、规则和 JSON 脚本中统一；
- TC 上报四字段链路和前端生产构建已验证通过；
- Archive 对象阶段实际完成 2 个 TS（1 个 DFX 复用、1 个普通 TS 创建）、26 个 TP、48 个 TC；
- Portal 卡片刷新调用成功；
- 文档同步的 TS 节点现场写入成功；
- 文档脚本完整成功、写入失败隔离、章节缺失隔离和 UTF-8 无 BOM均已通过离线测试；
- topic 返回父节点及多个子节点的离线场景已验证 TASK/TR/TS 全部成功。

### 7.2 待现场复验

首次现场文档同步中：

- TASK `概述` 返回父 topic 和两个子 topic；
- TR `测试类型分析` 返回父 topic 和十个子 topic；
- 旧判断错误要求整个返回只有一条，导致 TASK/TR 失败、TS 成功，结果为 `partial`。

该问题已在 `main` 修复为精确筛选目标父 topic。需要在实际环境重新执行 Archive，确认 TASK、TR 和 TS 全部写入成功。

## 8. 关键工程约束

- MCP 地址：`127.0.0.1:8765`，协议 SSE；
- Explore、Design、Archive 必须使用同一个 `TR_<tr_id>` 上下文；
- Design 同时最多运行 3 个 TS Agent；
- Archive 一次只运行一个 Archive Agent；
- Object Skill 和 Document Agent 各调用一次；
- 禁止使用旧的 `test-create-tr/ts/tp/tc` Skill，平台对象通过统一 MCP；
- 禁止手工修改设计输入 JSON 或归档状态中的平台 ID；
- Portal 不支持直接跳转到 TC，TC 完成后跳转到所属 TP；
- 核心流程修改前必须核对上下游输入、输出和状态契约；
- CoreTool 首选扩展包内置 CLI，解析后全程使用绝对路径；
- 扩展目录版本、`codeagent-extension.json.version` 和 WebApp 实际加载版本必须一致；
- 测试用例字段以 `.testagent/rules/tp-tc-output.md` 为业务规则单一来源。

## 9. 已知问题与下一步

1. 在实际环境重新运行 Archive，验证 topic 树精确匹配修复和 TASK/TR/TS 全量文档写入；
2. 完成回归后评估将当前 `main` 增强定稿为下一个扩展版本；
3. 持续排查卡片缓存成功但 Portal 页面部分场景未展示的问题；
4. 设计测试因子编码到平台树节点的独立解析和关联工具；
5. 补充多需求 TR、多 TR 同需求、指定对象、断点续跑和文档失败隔离回归。
6. 将 `build_tp_tc_json.py --ts` 的过滤提前到配对检查前，消除其他 TS 的无关缺失告警。

## 10. 新任务读取顺序

处理本项目新任务时优先读取：

1. `docs/PROJECT_CONTEXT.md`；
2. 根目录 `README.md`；
3. 目标阶段对应的 `.testagent/skills/<skill>/SKILL.md`；
4. 相关 Agent、脚本和 MCP 源码。

以仓库 `main` 实际文件为最终依据；本文用于快速恢复全局上下文，不替代具体 Skill 契约。
