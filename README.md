# coretest-spec-e2e

`coretest-spec-e2e` 是面向 E2E 测试设计的 TestAgent 扩展包，覆盖从产品版本初始化、需求探索、测试规格分析、测试用例设计，到 TS、TP、TC 归档和 Portal 卡片刷新的完整流程。

当前版本：`0.2.1`

## 能力概览

完整流程如下：

```text
/coretest-init
      ↓
获取设计任务和平台已有 TR
      ↓
/coretest-explore
      ↓
解析 TR 直接关联需求，生成测试规格
      ↓
/coretest-design
      ↓
按 TS 生成 TP/TC、JSON 和测试用例卡片
      ↓
/coretest-archive
      ↓
复用已有 TR，归档 TS、TP、TC
```

0.2.1 使用 TR 作为流程主上下文，所有阶段产物统一保存在：

```text
.design_output/<design_task_id>/TR_<tr_id>/
```

## 使用前准备

开始前请确认：

- 已在 TestAgent 中加载本扩展包；
- `core_test_design_mcp` 已配置并可以正常调用；
- 当前账号有权访问对应产品版本、设计任务和 Portal；
- 本机可使用 Python；
- 执行 Explore 前已安装 Pandoc，并可通过 `pandoc --version` 检查；
- TR 已直接关联至少一个信息完整的 IR 或 SR。

## 快速开始

以下以产品版本 `UPCF 27.0.0`、TR ID `3863` 为例。

### 1. 初始化产品和 TR 上下文

```text
/coretest-init "UPCF 27.0.0"
```

Init 会：

- 查询产品版本对应的 PBI、设计任务和平台已有 TR；
- 创建全量测试设计 working 卡片；
- 保存完整初始化结果；
- 为每个有效 TR 生成独立上下文。

主要产物：

```text
.design_output/design_task_info.json
.design_output/<design_task_id>/TR_<tr_id>/tr_info.json
.design_output/<design_task_id>/TR_<tr_id>/cida_info.json
```

执行后，请在右侧“全量测试设计”卡片中确认是否需要新增 TR：

- 如需新增，在卡片中完成 TR 创建；
- 如已有 TR 可直接使用，确认无需新增；
- 操作完成后回复：

```text
TR已创建
```

系统会重新执行一次 Init，拉取最新 TR 信息。后续流程只使用本次 Init 生成的 `tr_info.json`，不会自行创建 TR。

### 2. 探索需求并生成测试规格

```text
/coretest-explore 3863
```

如需跳过中途确认：

```text
/coretest-explore 3863 --skip-clarify
```

Explore 会：

- 读取当前 TR 的全部直接关联需求；
- 查询并下载所有唯一 IDP/DBOX 文档；
- 提取系统需求和功能设计；
- 生成 SR 规格；
- 生成当前 TR 的测试规格和 `tr_ts.json`；
- 输出可供 Design 使用的 TS 编号列表。

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

### 3. 生成 TP/TC 测试设计

处理当前 TR 的全部 TS：

```text
/coretest-design 3863
```

只处理指定 TS：

```text
/coretest-design 3863 TS_01 TS_02
```

说明：

- TS 编号来自 `tr_ts.json.test_specs[]` 的顺序；
- 第 1 条对应 `TS_01`，第 2 条对应 `TS_02`；
- 不传 TS 时默认处理全部 TS；
- 每批最多并行处理 3 个 TS；
- 每个 TS 独立完成 Markdown、TP/TC JSON 和测试用例卡片更新。

主要产物：

```text
TR_<tr_id>/
├── test_design/
│   ├── ts_01_test_design.md
│   ├── ts_01_test_cases.md
│   ├── ts_01_tp.json
│   └── ts_01_tc.json
└── ts_01_test_case.json
```

### 4. 归档 TS、TP、TC

Archive 复用 Init 拉取的平台既有 TR，只归档 TS、TP、TC，不创建或归档 TR。

归档全部 TS：

```text
/coretest-archive 3863 TS
```

归档指定 TS：

```text
/coretest-archive 3863 TS_01 TS_02
```

归档全部 TP，自动补齐所属 TS：

```text
/coretest-archive 3863 TP
```

归档指定 TP：

```text
/coretest-archive 3863 TS_01/TP.01.03.01
```

归档全部 TC，自动补齐所属 TS 和 TP：

```text
/coretest-archive 3863 TC
```

指定对象只会向上补齐父级依赖，不会向下展开子级。例如：

```text
/coretest-archive 3863 TS_01
```

只归档 `TS_01`，不会归档其下 TP 或 TC。

归档状态保存在：

```text
.design_output/<design_task_id>/TR_<tr_id>/archive/archive_state.json
```

Archive 支持断点续跑：已成功的 TS、TP、TC 会直接复用，避免重复创建。

## 完整示例

```text
/coretest-init "UPCF 27.0.0"
```

在全量测试设计卡片中完成 TR 操作或确认无需新增，然后回复：

```text
TR已创建
```

继续执行：

```text
/coretest-explore 3863
/coretest-design 3863
/coretest-archive 3863 TC
```

如果只想设计并归档部分对象：

```text
/coretest-design 3863 TS_01 TS_02
/coretest-archive 3863 TS_01 TS_02
```

## 目录结构

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

## 使用约束

- 后续命令中的第一个数字参数均为 `tr_id`，不是 `design_task_id`；
- Explore、Design、Archive 必须使用同一个 `TR_<tr_id>` 上下文；
- 不要手工修改 `tr_info.json`、`tr_ts.json`、TP JSON、TC JSON 或归档状态中的平台 ID；
- Archive 不支持 `TR` 目标；
- TP 的 `tpSourceType` 为空时，该 TP 会标记为 `skipped`，其下 TC 会标记为 `blocked`；
- Portal 当前不支持直接跳转到 TC，TC 归档完成后会跳转到所属 TP；
- 同一需求下不同 TR 若存在相同 TS 编号，卡片 key 可能相同。建议同一需求同一时间只执行一个 TR 的 Design。

## 常见问题

### 找不到 TR 上下文

确认已执行 Init，并在创建或确认 TR 后回复过：

```text
TR已创建
```

然后检查：

```text
.design_output/<design_task_id>/TR_<tr_id>/tr_info.json
```

是否存在。

### TR 无法进入 Explore

确认 TR 已直接关联 IR 或 SR，且第一条直接关联需求包含完整的 `requirement_id`。补齐平台关联后重新执行 Init。

### Explore 提示 Pandoc 不可用

安装 Pandoc，并确认以下命令执行成功：

```bash
pandoc --version
```

### Design 指定 TS 越界

TS 编号按 `test_specs/tr_ts.json` 中 `test_specs[]` 的顺序生成。先查看 Explore 汇总输出，再使用有效的 `TS_<NN>`。

### Archive 中断后如何继续

使用相同 TR ID 和相同归档目标重新执行 Archive。流程会读取 `archive/archive_state.json`，复用已经成功的对象并继续未完成部分。

## 版本说明

### 0.2.1

完成端到端流程的 TR 级适配。Init 支持拉取并保存平台已有 TR 信息；Explore、Design、Archive 统一使用 `TR_<tr_id>` 目录；Design 支持按 TR 生成指定或全部 TS 用例；Archive 复用已有 TR，仅归档 TS、TP、TC，并优化执行计划持久化与断点状态管理，确保计划范围与实际归档结果一致。
