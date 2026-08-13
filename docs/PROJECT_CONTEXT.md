# coretest-spec-e2e 项目上下文

> 最后更新：2026-08-13  
> 当前定稿版本：`0.2.1`  
> 默认分支：`main`

## 1. 项目目标

`coretest-spec-e2e` 是基于 TestAgent 的 E2E 测试设计能力扩展，用于完成从产品与需求上下文初始化、需求探索、测试规格生成、TS 级测试设计，到 TS/TP/TC 平台归档和 Portal 卡片刷新的自动化闭环。

当前正式流程以平台已有 TR 为主上下文：

```text
/coretest-init
      ↓
拉取设计任务、已有 TR 及其直接关联需求
      ↓
/coretest-explore <tr_id>
      ↓
生成当前 TR 唯一一套需求分析与测试规格
      ↓
/coretest-design <tr_id> [TS列表]
      ↓
按 TS 生成 TP/TC、JSON 和测试用例卡片
      ↓
/coretest-archive <tr_id> <TS|TP|TC|指定对象...>
      ↓
复用已有 TR，归档 TS、TP、TC
```

项目目标：

- 减少人工需求分析和测试设计工作量；
- 基于 TR 直接关联需求生成测试规格、测试点和测试用例；
- 实现 TS、TP、TC 精确归档和断点续跑；
- 建立需求、TR、TS、TP、TC 的端到端追踪链路；
- 通过 Portal 卡片展示设计与归档进度。

## 2. 当前版本状态

当前版本：

```text
coretest-spec-e2e 0.2.1
```

0.2.1 已完成并验证以下定稿能力：

- Init 拉取并保存平台已有 TR 的完整信息；
- Explore、Design、Archive 全部适配 `TR_<tr_id>` 目录；
- Explore 按 TR 的全部直接关联需求生成唯一一套测试规格；
- Design 支持处理当前 TR 的全部 TS 或指定 TS；
- Archive 不创建、不归档 TR，仅复用已有 TR 归档 TS、TP、TC；
- Archive 使用文件方式持久化权威执行计划，避免 PowerShell JSON 参数转义和长度问题；
- Archive 严格按状态文件中的执行计划执行，并支持对象状态保存与断点续跑。

版本演进：

| 版本 | 主要能力 |
|---|---|
| 0.1.x | 打通 Init、Explore、Design、卡片和 Archive 基础链路 |
| 0.2.0 | 完善 E2E 测试设计与 TR/TS/TP/TC 自动化处理 |
| 0.2.1 | 完成 TR 级全流程适配，Archive 改为复用已有 TR 并仅归档 TS/TP/TC |

## 3. 快速使用

以下以产品版本 `UPCF 27.0.0`、TR ID `3863` 为例。

### 3.1 初始化

```text
/coretest-init "UPCF 27.0.0"
```

Init 查询产品版本对应的 PBI、设计任务、已有 TR 及其直接关联需求，并生成 TR 级上下文。

如需在平台新增 TR，应先在右侧卡片中完成创建，再回复：

```text
TR已创建
```

系统随后重新执行一轮 Init，拉取最新 TR 信息。后续流程只使用本轮 Init 生成的 TR 上下文。

### 3.2 需求探索与测试规格生成

```text
/coretest-explore 3863
```

跳过中途确认：

```text
/coretest-explore 3863 --skip-clarify
```

### 3.3 测试设计

处理全部 TS：

```text
/coretest-design 3863
```

处理指定 TS：

```text
/coretest-design 3863 TS_01 TS_02
```

### 3.4 测试资产归档

归档全部 TS：

```text
/coretest-archive 3863 TS
```

归档指定 TS：

```text
/coretest-archive 3863 TS_01 TS_02
```

归档全部 TP 或全部 TC，并自动向上补齐父级依赖：

```text
/coretest-archive 3863 TP
/coretest-archive 3863 TC
```

归档指定 TP：

```text
/coretest-archive 3863 TS_01/TP.01.03.01
```

Archive 不支持 `TR` 目标。

## 4. 核心组件现状

| 组件 | 当前版本 | 当前职责 |
|---|---:|---|
| `coretest-init` | 1.2.1 | 解析产品版本并调度 Init Agent，拉取设计任务和已有 TR 上下文 |
| `coretest-explore` | 0.4.1 | 按 TR 的全部直接关联需求生成唯一一套 Explore 产物和 `tr_ts.json` |
| `coretest-design` | 1.4.0 | 按 TR 处理全部或指定 TS，每个 TS 独立完成 Markdown、JSON 和卡片闭环 |
| `coretest-archive` | 2.5.1 | 复用已有 TR，严格按权威计划顺序归档 TS、TP、TC |

### 4.1 Init

正式输入：

```text
/coretest-init "<product_name>"
```

关键产物：

```text
.design_output/design_task_info.json
.design_output/<design_task_id>/TR_<tr_id>/tr_info.json
.design_output/<design_task_id>/TR_<tr_id>/cida_info.json
```

约束：

- 单轮初始化只调用一次 `get_design_task_info_init`；
- 只有用户回复“TR已创建”时才启动新一轮初始化；
- 后续阶段不得自行创建 TR；
- TR 没有有效直接关联需求时，不进入正式 Explore 流程。

### 4.2 Explore

正式输入：

```text
/coretest-explore <tr_id> [--skip-clarify]
```

权威分析范围：

```text
TR_<tr_id>/tr_info.json.requirements[]
```

主要产物：

```text
TR_<tr_id>/
├── design_doc/
├── 系统需求.md
├── 功能设计.md
├── sr_specs/
└── test_specs/
    ├── <TR名称>测试规格.md
    └── tr_ts.json
```

约束：

- 第一位置参数是 `tr_id`，不是 `design_task_id`；
- 处理当前 TR 的全部直接关联需求；
- IDP/DBOX 文档按 `DOC_TYPE:doc_id` 去重；
- 不从其他 TR、设计任务级功能或特性补充分析范围；
- 不创建 TR。

### 4.3 Design

正式输入：

```text
/coretest-design <tr_id> [TS列表]
```

主要产物：

```text
TR_<tr_id>/
├── test_design/
│   ├── ts_<NN>_test_design.md
│   ├── ts_<NN>_test_cases.md
│   ├── ts_<NN>_tp.json
│   └── ts_<NN>_tc.json
└── ts_<NN>_test_case.json
```

规则：

- `tr_ts.json.test_specs[0]` 对应 `TS_01`，依次递增；
- 不传 TS 时默认处理全部 TS；
- 每批最多并行处理 3 个 TS；
- 每个 TS 由一个 `test-design-agent` 独立完成 Markdown、JSON 和卡片更新；
- 一个 TS 对应一个测试用例卡片；
- 卡片 key 保持 `<requirement_id>_<ts-id>`。

已接受的使用约束：

- 同一需求关联多个 TR 且存在相同 TS 编号时，卡片 key 可能冲突；
- 同一需求同一时间只执行一个 TR 的 Design。

### 4.4 Archive

正式输入：

```text
/coretest-archive <tr_id> <TS|TP|TC|指定对象...>
```

归档关系：

```text
既有 TR → TS → TP → TC
```

规则：

- TR 由 Init 从平台拉取，Archive 不创建、不归档 TR；
- `request.execution_plan.tr` 永远为空；
- 指定对象只向上补齐父级依赖，不向下展开子级；
- 主 Skill 生成本次权威计划，但不直接调用状态脚本或创建 MCP；
- Archive Agent 将完整计划写入 `archive/request_plan.json`；
- 状态脚本通过 `--request-file` 一次性记录计划，避免 PowerShell JSON 参数转义问题；
- Agent 回读并校验状态计划后，才允许调用 `create_ts`、`create_tp`、`create_tc`；
- Agent 只能遍历状态文件中的执行计划，禁止从 TP/TC 源 JSON 扩大范围；
- 已成功对象直接复用，避免重复创建；
- `tpSourceType` 为空的 TP 标记为 `skipped`，其下 TC 标记为 `blocked`。

归档状态：

```text
.design_output/<design_task_id>/TR_<tr_id>/archive/
├── request_plan.json
├── archive_state.json
└── responses/
```

`archive_state.json` 使用 `schema_version=2`，完整保存 Init 拉取的 TR 信息，并记录 TS、TP、TC、卡片和原始响应状态。

## 5. 标准目录结构

```text
.design_output/
├── design_task_info.json
└── <design_task_id>/
    └── TR_<tr_id>/
        ├── tr_info.json
        ├── cida_info.json
        ├── design_doc/
        ├── 系统需求.md
        ├── 功能设计.md
        ├── sr_specs/
        ├── test_specs/
        │   ├── <TR名称>测试规格.md
        │   └── tr_ts.json
        ├── test_design/
        │   ├── ts_<NN>_test_design.md
        │   ├── ts_<NN>_test_cases.md
        │   ├── ts_<NN>_tp.json
        │   └── ts_<NN>_tc.json
        ├── ts_<NN>_test_case.json
        └── archive/
            ├── request_plan.json
            ├── archive_state.json
            └── responses/
```

## 6. 当前验证状态

0.2.1 正式链路已验证通过：

- Init：可拉取设计任务、已有 TR、IR/SR 关联并生成 TR 级上下文；
- Explore：以 `TR_3863` 为上下文完成全部关联需求分析并生成测试规格；
- Design：指定 TS 和全量 TS 流程均可执行，已验证 2 个 TS 完成 Markdown、TP/TC JSON 和卡片闭环；
- Archive：复用已有 TR，仅归档 TS、TP、TC；
- Archive 计划持久化：已验证 `request_plan.json → --request-file → archive_state.json` 链路；
- Archive 一致性：已验证状态中的计划范围与实际归档范围一致；
- 断点状态：重复初始化和重复归档可保留、复用已成功的下游平台对象。

代表性归档验证中：

- TS：2 个进入计划并完成处理；
- TP：24 个进入计划，其中 10 个成功、14 个因 `tpSourceType` 为空而 skipped；
- TC：29 个进入计划，其中 14 个成功、15 个因父 TP skipped 而 blocked。

上述 skipped/blocked 属于既定数据规则，不代表归档流程失败。

## 7. 关键工程约束

- MCP 地址：`127.0.0.1:8765`；
- MCP 协议：SSE；
- Design 同一时间最多运行 3 个 TS Agent；
- Archive 一次只运行一个 Archive Agent，父子依赖顺序处理；
- 禁止使用旧的 `test-create-tr/ts/tp/tc` Skill，平台对象通过统一 MCP 调用；
- 不手工修改 `tr_info.json`、`tr_ts.json`、TP JSON、TC JSON 或归档状态中的平台 ID；
- Explore、Design、Archive 必须使用同一个 `TR_<tr_id>` 上下文；
- Portal 当前不支持直接跳转到 TC，TC 完成后跳转到所属 TP；
- 修改核心流程前必须核对上下游输入、输出和状态契约。

## 8. 已知问题与后续方向

### 8.1 Portal 卡片展示

历史现象：

- 卡片缓存接口调用成功并返回 `card_cache_id`；
- 部分场景下 Portal 页面未展示对应卡片。

后续需要继续核查：

- 卡片缓存数据落库；
- Portal 查询条件；
- 页面刷新机制。

该问题不影响 TP/TC 文件生成和平台归档主链路。

### 8.2 测试因子自动关联

目标是建设独立因子关联能力：

```text
factor_code → factor resolver → 平台树路径/节点 → TS 关联
```

当前约束：

- 平台没有直接通过叶子 `factor_id` 关联的接口；
- 页面操作需要逐层选择树节点；
- 图谱可提供因子信息，但平台写入仍需树形路径适配。

后续方向：

- 建设独立因子解析与关联工具；
- 以因子编码作为稳定输入；
- 缓存产品因子树或维护编码到路径的索引；
- 将平台树遍历和选择逻辑封装在单一工具中。

## 9. 下一步优先级

1. 持续排查 Portal 卡片缓存成功但页面未展示的问题；
2. 设计并验证测试因子编码到平台树节点的自动关联工具；
3. 补充 0.2.1 的回归用例，覆盖多需求 TR、多 TR 同需求、指定对象归档和断点续跑；
4. 后续功能演进继续保持 TR 级目录和既有 TR 复用原则。

## 10. 新任务开始前的读取顺序

处理本项目的新需求时，优先读取：

1. `docs/PROJECT_CONTEXT.md`；
2. 根目录 `readme.md`；
3. 目标阶段对应的 `.testagent/skills/<skill>/SKILL.md`；
4. 相关 Agent、脚本和 MCP 源码。

以仓库 `main` 的实际文件为最终依据；本文用于快速建立项目全局上下文。
