# coretest-spec-e2e

`coretest-spec-e2e` 是面向 E2E 测试设计的 TestAgent 扩展包，围绕平台已有设计任务和 TR，完成需求探索、普通/DFX 测试规格、TS 级 TP/TC 设计、测试用例卡片、平台对象归档、在线文档同步和 Portal 刷新。

当前扩展版本：`0.2.4`
当前开发分支：`develop`

## 流程概览

```text
/coretest-init
→ 拉取设计任务、已有 TR 和直接关联需求
→ /coretest-explore <tr_id>
→ 生成普通/DFX 测试规格和统一 ts_catalog.json
→ 可选：只归档 Explore 生成的全部普通 TS
→ /coretest-design <tr_id|TR_tr_id> [TS选择器...]
→ 按 TS 生成 Markdown、TP/TC JSON 和测试用例卡片
→ /coretest-archive <tr_id> <TR|TS|TP|TC|指定对象...>
→ 创建或复用 TS、TP、TC
→ 同步任务、TR、相关 TS 在线文档
→ 刷新 Portal 卡片
```

所有正式阶段共享同一个目录：

```text
.design_output/<design_task_id>/TR_<tr_id>/
```

## 卡片触发（0.2.4）

全量测试设计 Portal 卡片支持通过“AI分析”直接触发 TestAgent 流程：

| 卡片节点 | 自动生成的指令 |
|---|---|
| TR | `/coretest-explore <TR ID>` |
| TS | `/coretest-design <TS ID>` |

卡片会将节点类型、节点 ID、IDP 文档 ID、活动名称、版本 PBI 和当前用户信息传递给 TestAgent。用户仍可继续在对话框中手工输入相同指令。

## 使用前准备

- TestAgent 已加载当前扩展包；
- `core_test_design_mcp` 可用，地址通常为 `127.0.0.1:8765`（SSE）；
- 当前账号可访问对应产品版本、测试设计任务和 Portal；
- Python 可用；
- Pandoc 可通过 `pandoc --version` 检查；
- CoreTool 优先使用扩展包内置绝对路径，且已完成认证；
- 当前 TR 至少直接关联一个有效 IR/SR/US。

## 快速开始

### 1. 初始化

```text
/coretest-init "UPCF 27.0.0"
```

Init 查询 PBI、设计任务、平台已有 TR 和直接关联需求，生成：

```text
.design_output/design_task_info.json
.design_output/<design_task_id>/TR_<tr_id>/tr_info.json
.design_output/<design_task_id>/TR_<tr_id>/cida_info.json
```

后续阶段复用已有 TR，不自行创建 TR。

### 2. Explore

```text
/coretest-explore <tr_id>
```

例如：

```text
/coretest-explore 4029
```

Explore 会：

- 以 `tr_info.json.requirements[]` 为直接需求全集；
- 下载并解析全部唯一 IDP/DBOX 文档；
- 生成系统需求、功能设计和 `sr_specs`；
- 查询平台已有 TS，识别 DFX；
- 生成普通/DFX 测试规格；
- 生成 `tr_ts.json` 和稳定统一编号 `ts_catalog.json`；
- 最后询问：
  1. 跳过 TS 归档；
  2. 直接归档全部 Explore 普通 TS。

平台 DFX TS 已存在，不进入 Explore TS-only 归档计划，也不调用 `create_ts`。选择直接归档时，确定性脚本从 catalog 选取全部 `source=explore` 条目并生成文件式计划：

```text
archive/request_plan.json
```

`--skip-clarify` 会跳过交互并明确记录“不归档 TS”：

```text
/coretest-explore <tr_id> --skip-clarify
```

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

需求关系规则：

- SR 用于测试内容拆分和覆盖审计；
- TR、普通 TS 和 DFX TS 的平台 `requirement_ids` 使用当前 TR 直接关联需求的全集或非空子集；
- TR 元数据原样来自 `tr_info.json`，不得重新总结。

### 3. Design

处理 catalog 中全部 TS：

```text
/coretest-design <tr_id>
```

使用稳定编号处理指定 TS：

```text
/coretest-design 4029 TS_11 TS_12
```

若 TS 已有真实平台 ID，也可使用：

```text
/coretest-design TR_4029 TS_35807
```

选择器解析规则：

1. 优先精确匹配 `ts_catalog.items[].ts_key`；
2. DFX 真实 ID 匹配 catalog 的 `platform_ts_id`；
3. 普通 TS 真实 ID 匹配 `archive_state.json.ts[].platform_id`；
4. 最终统一转换为稳定 `TS_<NN>`，因此卡片 key 和文件名不变。

Design 每批最多并行 3 个 TS，每个 TS 独立完成：

```text
test_design/ts_<NN>_test_design.md
test_design/ts_<NN>_test_cases.md
test_design/ts_<NN>_tp.json
test_design/ts_<NN>_tc.json
ts_<NN>_test_case.json
```

### 4. Archive

```text
/coretest-archive <tr_id> <目标...>
```

常用示例：

```text
/coretest-archive 4029 TR
/coretest-archive 4029 TS
/coretest-archive 4029 TS_11
/coretest-archive 4029 TP
/coretest-archive 4029 TS_11/TP.01.03.01
/coretest-archive 4029 TC
```

对象范围：

| 输入 | 对象处理 |
|---|---|
| `TR` | 只复用已有 TR，不创建对象 |
| `TS` | 全部 TS |
| `TS_<NN>` | 指定 TS |
| `TP` | 全部 TS 和 TP |
| 指定 TP | 所属 TS 和指定 TP |
| `TC` | 全部 TS、TP、TC |
| 指定 TC | 所属 TS、TP 和指定 TC |

规则：

- Explore TS-only 阶段不处理 DFX；
- 正式 Archive 遇到 DFX 时复用 catalog 的 `platform_ts_id`，不调用 `create_ts`；
- 普通 TS 创建成功后将真实 ID保存到 `archive_state.json`；
- 指定对象只向上补齐父级，不向下展开；
- 已成功对象重跑时直接复用；
- 对象失败不回滚成功对象；
- 在线文档失败单独记录，最终结果为“部分成功”。

固定编排：

```text
coretest-archive-agent
→ coretest-object-archive
→ coretest-document-sync-agent
→ test-portal-card
→ 最终汇总
```

在线文档同步范围：

- TR 目标：设计任务 + TR；
- TS 目标：设计任务 + TR + 相关 TS；
- TP/TC 目标：设计任务 + TR + 所属 TS；
- TP/TC 自身文档暂不写入。

设计任务的 7 个叶子章节分别写入对应 topic：

```text
被测对象概述
测试方案概述
特性风险分析（RBT）
测试重点难点分析
分层测试策略
底层硬件/组网差异测试策略分析
网元形态差异测试策略分析
```

不再向“概述”和“测试设计策略”父 topic 写入聚合正文。

## 标准目录

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
        │   ├── platform_ts.json
        │   ├── tr_ts.json
        │   └── ts_catalog.json
        ├── test_design/
        ├── ts_<NN>_test_case.json
        └── archive/
            ├── request_plan.json
            ├── archive_state.json
            ├── document_request.json
            ├── document_plan.json
            ├── document_payloads/
            └── responses/
```

## 测试用例字段

归档到 CIDA 时：

- `TestType` 按规则映射，无法识别时为 `"1"`；
- `AutoType` 自动化为 `"1"`，非自动化或无法识别时为 `"0"`；
- `envtype` 当前为空字符串；
- `DesignNote` 根据测试目的和验证内容生成，不允许为空；
- `caseHandler` 当前不处理。

## 当前验证状态

截至 2026-09-01，`develop` 已验证：

- 普通/DFX 测试规格和统一 TS catalog 可生成；
- Explore 可确定性生成普通 TS-only 计划，DFX 不进入计划；
- 普通 TS 可创建并保存真实平台 ID；
- Design 可处理稳定编号和真实平台 TS ID；
- Archive 对象、在线文档和 Portal 闭环验证成功；
- 新版 CoreTool `source-data write` 返回格式与现有脚本兼容；
- 任务级 7 个叶子章节按独立 topic 写入；
- 全量测试设计卡片可从 TR、TS 节点分别触发 Explore、Design。

## 关键约束

- 命令中的 TR 参数是平台 `tr_id`，不是 `design_task_id`；
- Explore、Design、Archive 必须使用同一个 `TR_<tr_id>`；
- 不手工修改 `tr_info.json`、`tr_ts.json`、`ts_catalog.json`、TP/TC JSON 或平台 ID；
- 不使用旧的 `test-create-tr/ts/tp/tc` Skill；
- Archive 一次只运行一个 Archive Agent；
- Object Skill 和 Document Agent 各调用一次；
- Portal 不支持直接跳转到 TC，TC 完成后跳转到所属 TP；
- 扩展目录版本、`codeagent-extension.json.version` 和 WebApp 实际加载版本必须一致。

## 常见问题

### Explore 为什么没有询问是否归档 TS

- 使用 `--skip-clarify` 时会默认跳过；
- 普通模式必须进入阶段 6.7 并等待明确选择；
- 若没有询问，确认本地 Skill 包含“阶段 6.7”，并重新加载扩展或启动新会话。

### 为什么 Explore 不归档 DFX TS

DFX TS 是平台已有对象，catalog 已保存其 `platform_ts_id`。Explore 只创建本轮生成的普通 TS；Design 可直接使用 DFX 的真实 ID。

### 计划 JSON 为什么必须使用文件

Windows PowerShell 调用原生 Python 时，内联 JSON 可能丢失引号。流程固定生成 `request_plan.json`，并通过 `--request-file` 锁定。

### Archive 中断后如何继续

使用相同 TR ID 和目标重新执行。流程读取 `archive_state.json`，复用成功对象并继续未完成部分。

### 卡片仍加载旧版本

确认根目录 `codeagent-extension.json` 与实际扩展目录版本一致，并重新加载当前构建产物。

## 分支说明

- `main`：当前稳定基线；
- `develop`：包含 DFX、统一编号、Explore 普通 TS-only 归档、真实 ID Design、确定性文档同步及卡片触发 Explore/Design 等最新增强。
