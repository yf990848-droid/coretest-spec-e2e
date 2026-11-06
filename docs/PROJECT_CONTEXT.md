# coretest-spec-e2e 项目上下文

> 最后核对：2026-11-06
> 仓库扩展版本元数据：`0.2.9`
> 当前开发分支：`develop`  
> 稳定分支：`main`  
> 最新 MCP 现场结论：2026-11-02 用户确认 Python 3.10 旧虚拟环境导致的 StrEnum 导入问题已解决；通过 Python 3.12 重建环境并从项目根目录 requirements.txt 安装依赖，见第 16 节。  
> 用例卡片现场结论：用例卡片调用约束修复已于 2026-10-31 由用户确认验证成功。最终采用 Agent 原生 Shell、优先 workdir 设置脚本目录，不强制 CMD；见第 15 节。第 14 节的 Portal 切换模型恢复属于另一轮历史排查。  
> 代码仓归档状态：2026-11-06 用户确认 0.2.9 已合入 CodeHub `CoreTestClaw_G/CoreTestClaw` 的 `coretest-spec-e2e` 分支；Python 新增 458 行，未拆分 MR，详见第 20 节。该结果不代表 GitHub main 合并或正式发布。  
> 版本与发布状态：0.2.9 CLI 主流程已由用户确认验证通过，版本配置、README 和指导教程已更新至 develop；本次对话未执行 main 合并、Release 创建或安装包发布。最新结论及证据见第 19 节。
> 阅读提示：第 13～17 节为历史记录；当前 CLI、Bash、TC 标识及发布状态以第 18～20 节和当前源码为准。

## 1. 项目目标

`coretest-spec-e2e` 是基于 TestAgent 的 E2E 测试设计扩展。正式链路围绕平台已有设计任务和 TR：

```text
/coretest-init
→ /coretest-explore <tr_id>
→ 普通/DFX 测试规格 + ts_catalog.json
→ 可选归档全部 Explore 普通 TS
→ /coretest-design <tr_id|TR_tr_id> [TS选择器...]
→ TP/TC、JSON、测试用例卡片
→ /coretest-archive <tr_id> <目标...>
→ 对象归档 + 在线文档 + Portal

Portal 卡片也可从 TR/TS 节点直接触发 Explore/Design。
```

核心原则：

- `tr_info.json.requirements[]` 是当前 TR 直接关联需求的唯一权威范围；
- SR 用于内容拆分和覆盖审计，不直接替代平台 `requirement_ids`；
- 平台 DFX TS 与 Explore 普通 TS 使用统一稳定编号；
- DFX 已存在，Explore 不归档；正式 Archive 只复用其平台 ID；
- 普通 TS 可以在 Explore 末尾提前归档并保存真实 ID；
- Object、Document、Portal 三类结果分别记录；
- 脆弱的计划生成和在线文档写入由确定性脚本完成；
- 卡片只负责转发节点上下文和生成命令，不改变 Explore/Design 的业务契约。

## 2. 当前开发基线

0.2.4 功能基线于 2026-09-01 合入 `main`（提交 `bec90e8`）。0.2.5 完成 TS/TP 因子检索、因子计划与 Archive 关联的现场闭环。0.2.6 只进行新版测试用例卡片 `webapps` 适配，卡片加载与 Design 卡片链路已经用户验证。0.2.7 仅修复 MCP 启动时的 Python 选择、依赖导入检查及 Windows 批处理文件格式。0.2.8 修正用例卡片执行约束、清理旧 Skill 流程并更新用户教程，用户已确认验证成功。当前以 GitHub `develop` 实际文件为准；2026-11-06 用户确认 0.2.9 CodeHub 归档分支已合入 `coretest-spec-e2e`（第 20 节）。GitHub main 与 develop 的历史分叉状态仍须在合并前重新核对。

当前已完成：

1. Explore 查询平台 TS，识别 DFX 并生成独立 DFX 测试规格；
2. `platform_ts.json + tr_ts.json → ts_catalog.json` 统一编号；
3. Explore 末尾增加“跳过/归档全部普通 TS”的阻塞式确认；
4. `build_ts_archive_request.py` 从 catalog 确定性生成普通 TS-only 文件计划；
5. DFX 不进入 Explore 归档计划；
6. Design 同时支持稳定 TS 编号和真实平台 TS ID；
7. 修复 `ts-split.md` 与已有 TR 契约冲突；
8. Archive 拆分对象、在线文档和 Portal 编排；
9. 设计任务的 7 个叶子章节分别写入对应 topic；
10. Archive 最新现场回归成功；
11. `webapps/default/index.html` 支持 Portal 卡片与 TestAgent 双向通信，从 TR 节点触发 Explore、从 TS 节点触发 Design；
12. Design 已实现 TS/TP TestFactor 检索，scene TS 同时检索 SceneFactor，并生成候选证据与因子计划；
13. Archive 已实现 TS 因子同步和新 TP 创建时原子关联因子，现场闭环验证成功；
14. 0.2.6 采用仅替换 `webapps` 的新版测试用例卡片适配方案，保留原有 Init / Explore / Design / Archive 和 Markdown/JSON 数据契约；用户已确认验证成功。

关键提交：

- `cbd942d`：Explore TS 归档入口、真实 ID Design、叶子 topic 写入；
- `d9f4574`：确定性普通 TS-only 计划、DFX 排除、`ts-split.md` 修复；
- `f9a12c0`：新增全量测试设计 Portal 卡片入口与 `aiAnalyse` 消息转发；
- `bec90e8`：更新 0.2.4 版本元数据和 README，并同步至 `main`；
- `472e97b`：兼容 CoreTool CLI 空列表返回 `total=0,page_size=0`；
- `c0eac20`：在 Archive CLI 边界将 TestFactor `type` 从字符串转换为 int，并补回归测试；
- `a6bb74c`：更新 0.2.5 版本元数据和 README；
- `a89464a`：将 0.2.6 范围收敛为仅替换新版测试用例卡片 `webapps`；
- `9b6f203`：更新 0.2.6 版本元数据与 README；
- `9ad7df1`：指导教程更新并重命名为 `coretest-spec-e2e 0.2.6 指导教程.md`。

根目录版本当前为：

```text
coretest-spec-e2e 0.2.9
```

0.2.7 相关提交：

- `a4d9770`：修复 Python 版本选择和 FastMCP 实际导入检查；
- `0d1b55c`：启动脚本统一 CRLF 换行和 ASCII 注释；
- `56cdb80`、`e5810af`：更新版本元数据和 README；
- `02fcff1`、`df1e95e`：指导教程更新并重命名为 0.2.7。

## 3. 快速命令

### Portal 卡片触发（0.2.4）

在全量测试设计 Portal 卡片中对节点执行“AI分析”：

```text
TR 节点 → /coretest-explore <TR ID>
TS 节点 → /coretest-design <TS ID>
```

卡片自动透传节点类型、节点 ID、IDP 文档 ID、活动名称、版本 PBI 和当前用户信息。手工命令入口继续保留。

### Init

```text
/coretest-init "UPCF 27.0.0"
```

### Explore

```text
/coretest-explore <tr_id>
/coretest-explore <tr_id> --skip-clarify
```

普通模式最后必须让用户选择：

```text
1. 跳过 TS 归档
2. 直接归档全部 Explore 普通 TS
```

`--skip-clarify` 默认跳过归档。DFX 不进入 Explore 归档计划。

### Design

全部 TS：

```text
/coretest-design <tr_id>
```

稳定编号：

```text
/coretest-design 4029 TS_11 TS_12
```

真实平台 ID：

```text
/coretest-design TR_4029 TS_35807
```

真实 ID 映射：

- DFX：`ts_catalog.items[].platform_ts_id`；
- 普通 TS：`archive_state.json.ts[TS_<NN>].platform_id`；
- 解析后始终使用稳定 `ts_key` 生成卡片和文件。

### Archive

```text
/coretest-archive <tr_id> TR
/coretest-archive <tr_id> TS
/coretest-archive <tr_id> TS_<NN>
/coretest-archive <tr_id> TP
/coretest-archive <tr_id> TS_<NN>/TP.xxx
/coretest-archive <tr_id> TC
```

`TR` 只复用并同步任务/TR 文档，绝不调用 `create_tr`。

## 4. 关键数据契约

### 4.1 TR 和需求

- 正式目录：`.design_output/<design_task_id>/TR_<tr_id>/`；
- TR 元数据直接来自 `tr_info.json`；
- TR `requirement_ids` 等于 `requirements[].requirement_number` 去重全集；
- 普通/DFX TS `requirement_ids` 是上述全集的非空子集；
- `tr_name/description/resolve_description` 不得重新总结；
- `function_numbers/feature_numbers` 分别来自 `relation_function/relation_feature`。

### 4.2 TS catalog

`ts_catalog.json` 是 Design 和 Archive 的稳定快照：

- DFX：`source=platform_dfx`，保存 `platform_ts_id`；
- 普通：`source=explore`，保存 `tr_ts_index`；
- DFX 从 `TS_01` 起，普通 TS 接续；
- 不重新查询平台改变已有编号。

TR_4029 的一次现场样例：

- 10 条 DFX；
- 8 条普通 TS；
- 共 18 条；
- DFX 为 `TS_01～TS_10`，普通 TS 为 `TS_11～TS_18`。

### 4.3 Explore 普通 TS-only 归档

固定流程：

```text
ts_catalog.json
→ build_ts_archive_request.py
→ archive/request_plan.json
→ archive_state.py init
→ archive_state.py record-plan --request-file
→ 回读并核对状态计划
→ coretest-object-archive(explore_ts_only)
```

规则：

- 计划只包含全部 `source=explore`；
- `source=platform_dfx` 只计入跳过数量；
- `tr/tp/tc` 计划为空；
- 禁止手工枚举 TS；
- 禁止使用内联 JSON；
- 计划失败或回读不一致时禁止创建对象；
- 本阶段不执行在线文档、Portal、TP 或 TC；
- 单个普通 TS 失败后继续，允许部分成功。

### 4.4 Design

- 每批最多 3 个 TS Agent；
- 主流程从 catalog 精确提取单 TS 规格；
- DFX 使用 `platform_ts_id` 定位 DFX 规格；
- 普通 TS 使用 `tr_ts_index` 定位 `tr_ts.json.test_specs[]`；
- 每个 TS 独立生成 Markdown、TP/TC JSON、因子候选、因子计划和 completed 卡片；
- TestFactor 对所有 TS 查询；scene TS 同时查询 SceneFactor；
- 候选证据保存为 `ts_<NN>_factor_candidates.json`，最终计划保存为 `ts_<NN>_factor_plan.json`；
- 图谱无匹配因子时允许空因子计划继续；
- 卡片 key 仍为 `<requirement_id>_<ts_key>`。

### 4.4.1 用例卡片执行约束（0.2.8 历史基线）

0.2.9 终端指令统一为 Bash，保留以下 workdir、单 TS 独立调用和返回结果判定；历史 PowerShell 示例不作为当前执行指令。

- 在 Agent 终端工具内执行，使用工具原生 Shell；不得仅凭工具名判断实际 Shell，不强制 CMD，不嵌套启动其他 Shell。
- 优先将工具 workdir 设置为 test-case-card/scripts；不支持时按实际 Shell 语法切换目录，失败立即停止。在该目录直接调用 Python 和相对文件名 card_generate.py。
- PowerShell 调用带引号的解释器绝对路径允许使用 &；不得在 PowerShell 中使用 CMD 的 cd /d。
- 每个 TS 独立调用，保留原始输出，禁止循环、批量包装和输出捕获；现有最多 3 个 TS Agent 并发不变。
- 复用 adapter 生成的单 TS JSON；检查初始化 card_id 文件存在且非空，第四个参数与初始化 key 完全一致。
- 退出码为 0、success=true 且 data.card_cache_id 非空，才能判定缓存更新调用成功；页面实际显示另行确认。卡片阶段沿用上层最多一次重试。
- 本次修改提示词约束，未修改 Python、前端、因子或归档逻辑。

### 4.5 Archive

对象范围：

```text
TR        → 空对象计划，仅复用 TR
TS        → 全部 TS
TS_<NN>   → 指定 TS
TP        → 全部 TS + TP
指定 TP   → 所属 TS + 指定 TP
TC        → 全部 TS + TP + TC
指定 TC   → 所属 TS + TP + 指定 TC
```

对象规则：

- DFX 在正式 Archive 中复用 `platform_ts_id`；
- 普通 TS 通过 `create_ts` 创建或从状态复用；
- TP/TC 只按锁定计划执行；
- 正式 Archive 在 TS 创建/复用后按因子计划执行 TS 因子同步；
- 新 TP 通过 CoreTool CLI `tp create --relations` 原子关联 TestFactor/SceneFactor；旧成功 TP 只复用、不补录因子；
- TestFactor 使用 `test_factor_id` UUID，SceneFactor 使用因子编码；
- CLI 边界将 TestFactor `type` 规范化为 int，不修改原始因子计划；
- 成功对象即时保存；
- TS/TP 需要有效平台 ID；
- 0.2.9 新建 TC 创建后查询确认并保存真实平台 ID；历史已成功但未记录 ID 的 TC 兼容复用；
- 文档失败不回滚对象。

固定编排：

```text
coretest-archive-agent
→ coretest-object-archive
→ coretest-document-sync-agent
→ test-portal-card
→ 汇总
```

### 4.6 在线文档

同步范围：

```text
TR    → 任务 + TR
TS    → 任务 + TR + TS
TP/TC → 任务 + TR + 所属 TS
```

任务级叶子 topic：

```text
被测对象概述
测试方案概述
特性风险分析（RBT）
测试重点难点分析
分层测试策略
底层硬件/组网差异测试策略分析
网元形态差异测试策略分析
```

TR topic：

```text
场景分析
测试类型分析
特性交互分析
功能交互分析
设计约束分析
```

TS topic 根据类型选择功能、场景、DFX 和内部实现章节。所有 topic 按名称完全相等、有效 ID、`deleted=0` 精确匹配。

`source-data write` 成功条件：

- 退出码为 0；
- 输出包含 `Successfully wrote source data to topic <topic_id>`。

### 4.7 Portal 卡片通信

消息流：

```text
TestAgent → type=chat → webapps/default/index.html → Portal iframe
Portal iframe → event=aiAnalyse → webapps/default/index.html → type=chat → TestAgent
```

契约：

- 卡片加载后发送 `iframeReady`，等待 TestAgent 下发版本和节点参数；
- Portal 以 `aiAnalyse` 上报 `nodeType/nodeId/idpDocId/activityName`；
- TR 节点生成 `/coretest-explore <nodeId>`；
- TS 节点生成 `/coretest-design <nodeId>`；
- 转发数据补充 `versionPbi` 和 `userId`；
- Portal URL 固定携带 `isAgentMode=true`；
- 卡片触发与手工输入使用相同命令，不新增独立业务流程。

### 4.8 0.2.6 新版测试用例卡片

- 仅替换新版测试用例卡片 `webapps`，不改 Skill、Agent、Rule 或归档脚本；
- 保留现有卡片初始化、Design 完成卡片与 Portal 通信入口；
- 保持现有 TS/TP/TC Markdown、JSON 产物及目录不变；
- 0.2.6 不包含在线文档新版适配，已有文档同步逻辑不变；
- 用户已确认新版卡片替换后验证成功，README 与 `codeagent-extension.json` 同步为 0.2.6。

## 5. 组件版本

| 组件 | 版本/状态 |
|---|---:|
| `coretest-init` | 1.2.1 |
| `coretest-explore` | 0.7.0 |
| `coretest-design` | 1.6.0 |
| `coretest-archive` | 2.9.0 |
| `coretest-archive-agent` | 1.12.0 |
| `coretest-document-sync-agent` | 1.0.0 |
| `build_ts_archive_request.py` | develop 新增 |
| `webapps/default/index.html` | 0.2.4 Portal 卡片入口，0.2.6 保持通信契约 |
| 新版测试用例卡片 `webapps` | 0.2.6 适配，用户已验证 |

## 6. 标准目录

```text
.design_output/
├── design_task_info.json
└── <design_task_id>/
    └── TR_<tr_id>/
        ├── tr_info.json
        ├── cida_info.json
        ├── design_doc/document_manifest.json
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

## 7. 已验证

0.2.4 功能基线截至 2026-09-01 的验证：

- Init 可拉取已有任务、TR 和直接需求；
- Explore 可生成 SR、普通/DFX 规格、`tr_ts.json` 和统一 catalog；
- `build_tr_json.py` 可校验已有 TR 元数据和需求关系；
- 普通 TS-only 计划可从 catalog 确定性生成，DFX 被排除；
- 普通 TS 可写回平台并保存真实 ID；
- Design 可处理 DFX、普通 TS、稳定编号和真实平台 ID；
- Archive 的对象、在线文档、Portal 闭环现场验证成功；
- 新版 CLI `source-data write` 与现有成功判断兼容；
- 任务级 7 个叶子 topic 可独立写入；
- 对象失败/文档失败隔离和状态持久化逻辑已验证；
- 0.2.4 卡片的 TR/TS 指令映射、上下文透传和 iframe 通信实现已完成代码核对。

0.2.5 截至 2026-09-23 的发布前验证：

- `/coretest-design 4029 TS_18` 成功闭环：1 个 scene TS，6 TP、6 TC，TP→TC 覆盖率 100%；
- `ts_18_factor_candidates.json` 完成 TS + 6 TP 的 TestFactor/SceneFactor 查询，共 14 次查询，全部 `ok=true`；
- `ts_18_factor_plan.json` 校验成功：4 个 TestFactor、0 个 SceneFactor、6 个 TP 全覆盖；
- `/coretest-archive 4029 TS_18/TP.18.01` 最终成功：TS_18 平台 ID=`40152`，TP.18.01 平台 ID=`26313`；
- TS_18 的 4 个 TestFactor 关系全部 `succeeded`；
- 在线文档同步全部成功：任务 7 个叶子章节、TR 5 个分析章节、TS_18 2 个设计章节；
- Portal 卡片成功跳转 TP.18.01（analyseId=`26313`）；
- `test_factor_archive.py -v` 与 `py_compile` 发布前检查通过；
- 现场暴露并修复两项 CLI 兼容性：空列表 `page_size=0`、TestFactor `type="0"` 到 int 的边界转换。

2026-09 的本地 CLI 现场验证：

| 对象 | 因子 | 现场结果 |
|---|---|---|
| scene TS `38490` | TestFactor `Flow_03_01` | 首次 `created=1`、重复 `created=0`；查询关系 ID `28880`，总数保持 1 |
| function TS `38489` | TestFactor `Insp_01_01` | 首次 `created=1`、重复 `created=0`；查询关系 ID `28881`，总数保持 1 |
| constraint TS `38485` | TestFactor `Mtn_02_01` | `created=1`，查询关系 ID `28883` |
| performance/DFX TS `38058` | TestFactor `Info_02_01` | 列表查到关系 ID `28882`；同 TS 原有 `CLI_TEST_002`，总数 2；未进行重复写入 |
| scene TS `38490` | SceneFactor「产品环境IP类型」 | CLI `scene-factor list` 查询到关系 ID `23151`，页面可见；返回 `number` 为空 |

早期 TP `24891` 传入了 TS 关系数字 ID，页面未显示 TestFactor。新 CLI
现场对照确认 `testFactorId` 必须使用因子 UUID：scene TP 双因子、function、
constraint、DFX TP 的名称和编码均已在页面显示。Feature TS 尚未现场验证，
按现有约定不阻断 0.2.5，但须做契约测试。

0.2.6 新版测试用例卡片验证（用户反馈）：

- 已完成新版测试用例卡片 `webapps` 替换并确认验证成功；
- 版本元数据和 README 已提升至 0.2.6，指导教程已更新为 0.2.6；
- 该版本不修改 Init、Explore、Design、Archive 主业务实现，也不纳入在线文档适配。

0.2.8 用例卡片验证（2026-10-31 用户反馈）：

- 用户在最终原生 Shell / workdir 约束修正后反馈“验证成功了”，随后要求准备 0.2.8；
- 本轮验证范围为 Design 卡片调用和页面刷新，不代表重新完成 Archive 全链路回归；
- 10 月 30 日曾出现卡片刷新成功但命令报错，不能与最终修正后的验证混淆，详见第 15 节。

## 8. 已知事项

1. `build_tp_tc_json.py --ts` 仍可能在过滤目标前扫描其他 TS，产生无关缺失配对警告；不代表目标 TS 失败。
2. 卡片缓存成功不等于界面已展示。2026-10-22 现场曾在参数正确、缓存成功后仍不显示，用户于 2026-10-26 确认切换模型后恢复；不能简单归因于页面延迟，详见第 14 节。
3. 需要继续补充多需求 TR、多 TR 同需求、指定对象和断点续跑回归。
4. 已错误写入父 topic 的历史聚合数据不会因新逻辑自动删除，需要在平台上一次性清理。
5. Portal TR/TS 节点【AI分析】触发 Explore/Design 的独立实机回归仍建议保留；不要将新版测试用例卡片的验证直接等同于所有 Portal 交互路径的回归。
6. 发布 0.2.9 安装包时，扩展目录与 `codeagent-extension.json.version` 应一致，并提供内置 CoreTool CLI；本扩展已移除 MCP 服务。不能从 CLI 版本推断扩展包版本。
7. 因子选择规则和归档适配已改为显式 ID 计划；scene TS/TP 可同时选两类因子，其他 TS 类型只选 TestFactor。scene TS 的完整扩展包闭环已现场验证。
8. 旧 TP 不做因子补录；只有新 TP 在创建时原子关联。平台已有但本地无成功状态的同名 TP 需人工核对。
9. 0.2.5 的 Design/Archive 主链路已完成内网现场回归；非 scene TS 的完整扩展包端到端类型覆盖可作为后续增强验证，不阻塞本次发布。

## 9. 新窗口继续工作的读取顺序

1. 读取本文件；
2. 读取 [`0.2.5 及后续版本开发计划`](0.2.5_AND_FOLLOWUP_DEVELOPMENT_PLAN.md)；需保留 TS/TP/TC 产物格式时读取 [`Markdown 产物契约`](TS_TP_TC_MARKDOWN_CONTRACT.md)；
3. 读取根目录 `README.md`；
4. 根据任务读取对应 Skill：
   - Explore：`.testagent/skills/coretest-explore/SKILL.md`
   - Design：`.testagent/skills/coretest-design/SKILL.md`
   - Archive：`.testagent/skills/coretest-archive/SKILL.md`
5. 涉及对象状态时读取：
   - `.testagent/skills/coretest-object-archive/SKILL.md`
   - `.testagent/skills/coretest-archive/scripts/archive_state.py`
6. 涉及在线文档时读取：
   - `.testagent/skills/coretest-document-sync/SKILL.md`
   - `.testagent/skills/coretest-document-sync/scripts/document_sync.py`
7. 涉及因子接口时读取 `.testagent/skills/coretool-cli/references/coretest.md`、`.testagent/skills/coretool-cli/SKILL.md`，并在本地核对实际 `coretool-cli --help`；文档与 CLI 版本可能不同。

以 `develop` 实际源码为最终依据。2026-10-19 核对时 `main` 与 `develop` 已分叉（`develop` 相对 `main` ahead 1、behind 1），不要将任一分支状态推定为另一个分支的版本；后续若需要合并须先核对实际差异。

当前用户指导教程：`docs/coretest-spec-e2e 0.2.9 指导教程.md`。教程面向使用者，终端示例使用 Bash；平台访问使用内置 CoreTool CLI，使用前完成登录。README 和教程不引用 GitHub 网页；当前两者使用仓库内相对链接互相引用。

## 10. 接手后的下一步

0.2.9 已完成本轮“打通流程”的验收，版本配置、README 和指导教程已提交 develop。2026-11-06 用户确认 0.2.9 CodeHub 代码仓归档已合并（第 20 节），不再作为待执行归档任务。无需仅为发布准备重复执行已通过的 Archive；业务设计质量与其他扩展验证按后续目标单独安排。

1. 若用户要求合并到 main，先核对最新分支差异，再执行合并；本次对话没有 main 合并、Release 或安装包发布记录，不沿用历史 ahead/behind 数值。
2. 发布包保持版本 0.2.9，包含与 CLI 1.0.6 接口兼容的内置可执行文件；用户完成 CLI 登录并准备 Python、Pandoc 环境。旧 MCP 启动及依赖排障仅作为历史参考。
3. 本轮未以重复运行验证幂等性，未验证业务设计质量或页面实际展示；不将接口成功扩展为这些结论。用户当前只要求流程打通，不追加阻塞性验收步骤。
4. 历史本地产物和状态不自动迁移。重新 Explore 后，同一稳定 TS 编号可能指向不同对象；旧 TP/TC/因子状态应与其原始父对象一并核对，不能只改父级 ID。
5. Init 全量需求功能/特性关系、DFX 设计准则匹配、Explore TR 分组、流程策略配置和在线文档新版适配仍按后续计划独立推进。

## 11. 0.2.5 develop 实施增量（已验证）

- Design 每 TS 先通过 `factor_candidates.py` 调用图谱查询并保存
  `test_design/ts_<NN>_factor_candidates.json`；查询成功后生成
  `test_design/ts_<NN>_factor_plan.json`，经
  `.testagent/skills/coretest-design/scripts/factor_plan.py` 校验；TP/TC Markdown
  固定表格与 JSON 继续保持原结构。无匹配因子明确保存空数组。
- 正式 Archive 的 TS 创建/复用后运行 `factor_archive.py sync-ts`，逐因子
  查询、必要时写入、再查询；独立结果保存在 `archive_state.json.factor`。
  Explore TS-only 归档不提前读取 Design 产物。
- 新 TP 通过 `factor_archive.py create-tp` 调用 CLI `--relations`；
  TestFactor 使用 `test_factor_id` UUID，SceneFactor 使用编码。旧 TP 复用，
  本版不补录。CLI 原始响应和请求保存在 `archive/responses/`。
- scene 双因子、function、constraint、DFX 的手工 CLI 页面验证已通过；
  scene TS 的扩展包 Design/Archive 端到端已完成现场回归：TS_18=`40152`、
  TP.18.01=`26313`、4 个 TestFactor 全部关联成功，文档与 Portal 均成功。
- 现场修复 `factor_archive.py` 对 CLI 空列表 `page_size=0` 的兼容，以及
  TestFactor `type` 字段从字符串到 int 的 CLI 边界转换；对应回归测试与语法检查均通过。
- 0.2.5 因子闭环现场验证完成；后续 0.2.6 仅调整新版测试用例卡片 WebApp，因子相关实现保持不变。

## 12. 0.2.6 状态更新（2026-10-19 核对）

- 范围：仅替换新版测试用例卡片 `webapps`，不更改其他业务链路；本版不包含新版在线文档适配。
- 验证：用户已反馈替换成功并完成验证；保留 0.2.5 因子与归档闭环验证结果。
- 元数据：`codeagent-extension.json` 与 README 已更新为 `0.2.6`。
- 教程：`docs/coretest-spec-e2e 0.2.6 指导教程.md` 已提交至 `develop`。
- 历史说明：以上为 2026-10-19 的 0.2.6 状态快照；当前版本和后续安排以第 10、15 节为准。

## 13. 0.2.7 MCP 启动修复与验证（2026-10-20～2026-10-22）

### 问题与定位

- 首次启动使用 Python 3.10.11 创建虚拟环境，依赖安装成功，但 griffe 导入 `enum.StrEnum` 失败；StrEnum 需要 Python 3.11 或以上。
- 最后的 `FastMCP server support is not installed` 是包装后的错误，本次实际根因是依赖与 Python 3.10 不兼容。
- 原启动脚本优先执行 `py -3.10`，即使本机同时安装 3.12、3.13 仍会选中 3.10；已有虚拟环境也缺少版本检查。
- 首轮脚本修改后出现 `'?' 不是内部或外部命令`、`%~fI` 路径替换语法错误，发生于批处理解析阶段。仓库脚本当时使用 LF 换行和中文注释；统一 CRLF 与 ASCII 注释后，用户反馈“现在好了”。未取得当时本地脚本字节，换行/编码为疑似原因，不将其表述为已完成逐字节复现。

### 实际改动范围

- 运行代码仅修改 `.testagent/mcp/core_test_design_mcp/start_mcp.bat`：
  - 优先选择 Python 3.12；其他候选要求至少 3.11；
  - 复用已有 `.venv` 前检查版本，不兼容时停止并提示备份、重建；
  - 实际执行 `from fastmcp import FastMCP` 检查，而非仅 `import fastmcp`；
  - 依赖安装后再验证导入，失败即停止；
  - 使用 Windows CRLF 换行和 ASCII 注释。
- `codeagent-extension.json` 版本升至 0.2.7，更新说明仅包含 MCP 启动修复。
- README 明确提醒提前安装 Python ≥3.11，推荐已验证的 Python 3.12，并补充启动、版本检查及旧虚拟环境重建指引。
- 教程重命名为 `docs/coretest-spec-e2e 0.2.7 指导教程.md`，同步上述使用指引；旧 0.2.6 文件名已移除。
- 本次未修改业务流程、产物契约、因子规则、MCP 服务接口或依赖版本。

### 用户侧验证及边界

- 使用 Python 3.12 重建环境后，服务输出 `Application startup complete`，监听 `http://127.0.0.1:8765`。
- 日志显示 `GET /sse` 返回 200、`POST /messages/` 返回 202，说明 SSE 连接建立且消息请求被接受；不将其等同于全部业务工具调用回归。
- 首个 `POST /sse` 返回 405 后仍能连接，推测为客户端协议探测/回退，未因此修改服务端。
- CRLF/ASCII 修复后，用户在 0.2.7 本地目录确认启动成功。代理侧未在 Windows 实跑，验证依据为用户反馈。
- 仅安装新版 Python 不会改变已有 `.venv` 的解释器，需要按 README/教程备份并重建。
- 发布待办见第 10 节；不得在上下文中复制认证令牌或将待办记为已完成。


## 14. 全量测试设计卡片不显示排查（2026-10-22～2026-10-26）

### 现场范围与最终结果

- 现场安装目录为 `D:\工具\Testagent\templates\coretest-spec-e2e@0.2.6\coretest-spec-e2e`，PBI 为 `268877136`，工号为 `l30012808`（首字符是小写字母 l，不是数字 1）。
- Init MCP 已成功返回，`data[0].tr_list` 为空。无 TR 只解释没有 TR 上下文目录，不应阻止展示全量测试设计首页供用户创建 TR。
- 起初脚本被描述为“静默退出”，无卡片、无 `card_generate.log`。后续依次排查执行环境、参数传递、缓存接口和展示链路。
- 2026-10-26 用户明确反馈“最后通过切换模型解决了”。现场问题已恢复；没有提供切换前后模型名称，也未取得平台展示链路的完整诊断证据，不能确定是模型行为、工具结果处理还是会话状态恢复导致。
- 用户在排查期间上传了本地 `test-portal-card/SKILL.md` 和 `scripts/card_generate.py`，随后已读取源码分析。代理未实施卡片脚本、Skill 或前端修复；本次更新仅记录上下文，不变更版本、不合并 main。

### 已确认的问题与证据

| 环节 | 现场证据与结论 |
|---|---|
| Python 依赖 | 本地终端报缺少 `requests`；用户安装后可执行。脚本在初始化日志前执行 `import requests`，因此导入失败时不会创建日志。 |
| 解释器选择 | 对话排查记录指出裸 `python` 指向 Windows Store 占位程序；改用 `py -3` 可输出并执行。MCP 成功不能证明卡片脚本使用的 Python 环境依赖齐全。 |
| 工作目录 | Skill 要求先 cd 到 `test-portal-card/scripts`；现场最初未遵守。但脚本日志、card_id、扩展元数据路径均基于 `__file__`，未确认缺少 cd 是故障根因。不要误用 `test-case-card` 目录。 |
| 空参数 | 现场 PowerShell 调用丢失 `""`，日志显示 `analyseId=fullTestDesign`、`pageType=l30012808`，说明位置参数前移。首页应为 `analyseId=""`、`pageType=fullTestDesign`，不能用虚构 ID 占位。 |
| 缓存接口 | 多次调用 `http://127.0.0.1:38101/digital-test/agent/v1/card/cache` 返回 HTTP 200、`code=0` 和 `data.card_cache_id`。缓存成功不等于当前会话已经展示卡片。 |
| 最终展示 | 参数正确、接口成功后仍未显示，最后用户通过切换模型恢复。具体内部原因未确认。 |

2026-10-22 的关键日志：

| 时间 | 状态 | 参数 | 缓存 ID |
|---|---|---|---|
| 16:24:54 | working | 仍错位，不能记为已修正 | `abac9773-261e-4963-8079-61fe79c8669f` |
| 16:33:13 | completed | 正确，analyseId 为空 | `fec6ab19-eac7-4706-a428-49f3671c0812` |
| 16:40:07 | working | 正确，analyseId 为空 | `7910e993-4659-4cab-a52c-9f8ee509f32e` |
| 16:41:53 | working | 再次错位 | `d4cbddc0-1b88-4d6c-a638-1a8705763ff9` |

正确请求的 `userId=l30012808`，`subTitleLink=/digital-test/agent/v1/static/coretest-spec-e2e@0.2.6/webapps/default/index.html`。各次复用同一 card_id；不将 card_id 文件存在视为发送成功，因为脚本先保存 ID，再请求缓存接口。

### 结果判断与尚未实施的加固

- `generate_tr_context.py` 即使没有 TR，也会打印 `TR contexts generated: 0; ...` 摘要。“没有 TR，所以没有输出正常”的判断错误；原始 JSON 文件存在也不能证明脚本已执行。
- 卡片脚本正常成功/失败路径都会打印 JSON。参数错误、接口失败等分支未设置非零退出码，退出码 0 不能单独证明成功，应检查 `success=true` 和非空 `card_cache_id`。
- 无输出、无新增日志时，先核对实际解释器及依赖，不能宣称“stdout 被吞掉”或“初始化完成”。外部终端执行成功与 TestAgent 会话消费工具结果要分开验证。
- Init Agent 文字称 working，但原命令使用 completed；本次两种状态均测试过，未证明状态切换能解决展示问题，不应凭推测修改状态契约。
- 16:41:53 平台引擎另有 `session.error / QueueRetryError`，状态码 429，`isRetryable=true`、`retryAfter=8`。可能影响后续会话处理，但没有确认实际重试结果或与展示的因果关系，不能作为已证实根因。
- 本次曾提供 CMD 原生空参数调用、Windows PowerShell `--%`、Python 内部构造 `sys.argv` 的诊断方式。日志已证明存在正确传参的执行，但不能将某一种命令写法宣称为最终展示恢复原因；最终恢复依据是用户切换模型后的反馈。
- 后续若再次复现，围绕同一次参数正确的工具调用，保留原始输出、日志时间、card_cache_id 和会话标识，检查平台是否识别结果并发送展示事件；避免反复调用 MCP 或仅因拿到缓存 ID 就宣称右侧已更新。

## 15. 0.2.8 用例卡片修复与发布准备（2026-10-26～2026-10-31）

### 现场经过与最终判断

- 初始现场为 TR_4090、设计任务 2702、需求 SR20260511983576，批量更新 13 个 TS（ts_01～ts_11、ts_13、ts_14）；规格文件名为“NWDAF原子能力编排测试规格.md”，NWDAF 全大写。
- 原批量命令出现 PowerShell Profile 被执行策略阻止，贴出的 foreach 命令也存在闭合不完整疑点；没有充分证据确认唯一根因。
- 单卡脚本返回 success=true、card_cache_id 非空和退出码 0；用户随后明确在 Agent 内先切换目录、再直接运行 Python 可以执行。外部终端缓存成功不能代替 Agent 页面展示验证。
- 用户上传 test-case-card/SKILL.md 和 scripts/card_generate.py 后，确认底层 Skill 仍描述旧的需求级 JSON 生成、修复及 Excel 导出流程，且只说明三个参数；实际脚本支持第四个 TS key。
- 脚本日志、card_id、扩展配置路径基于 __file__，不能断言没有 cd 就是展示失败根因。失败分支可能退出码仍为 0；card_id 缺失或为空时会生成新 UUID。这些脚本行为本轮未修改。
- 曾把执行约束收紧为“必须 CMD”。10 月 30 日用户在 TR_5192 / ts_12 验证时，cmd /c 包装命令被平台拦截；日志未说明具体拦截规则。随后 cd /d 实际进入 PowerShell，产生 Set-Location 参数错误，但后续 Python 仍执行并刷新卡片，返回 card_cache_id=c9da0bbf-c877-4502-9e27-bd88f3298702。
- Agent 描述该次工具已设置正确 workdir，但贴出的命令未展示工具参数，因此这只是当时成功原因的合理解释。可以确认 PowerShell 本身并非必然导致刷新失败；强制 CMD 的约束不适配工具环境。
- 最终修正为第 4.4.1 节的原生 Shell / workdir 规则。用户于 2026-10-31 确认验证成功，不再沿用“禁止 PowerShell”或“必须手动 cd”的过时要求。

### 实际修改与提交

| 提交 | 内容 |
|---|---|
| c6e96a4 | 四个提示词文件增加单 TS 独立更新约束、已有 JSON 入口、返回结果检查及统一重试规则 |
| 7916211 | 删除底层 Skill 旧的 JSON 重建、修复和 Excel 导出说明，清理 adapter 引用 |
| 4868001 | 曾统一为 CMD 示例；该限制后来被 6b726d6 修正，不是最终规范 |
| 6b726d6 | 使用原生 Shell，优先 workdir；切目录失败停止，允许 PowerShell 的 & 解释器调用 |
| 3f7e4f5 | README、codeagent-extension.json 更新为 0.2.8，教程由 0.2.7 重命名为 0.2.8 |
| 3e9b841 | README 和教程的文档引用改为直接写文件名 |
| 56d30d8 | 教程精简为用户操作指南，明确 MCP 自动启动，删除手动启动及内部实现说明 |

提示词修改涉及：

- .testagent/skills/test-case-card/SKILL.md
- .testagent/skills/test-case-card-adapter/SKILL.md
- .testagent/agents/test-design-agent.md
- .testagent/skills/coretest-design/SKILL.md

Python 脚本、前端、每批最多 3 个 TS 的并发数量、因子规则和 Archive 行为未因本轮修复而改变。

### 用户文档要求与当前状态

- 当前版本为 0.2.8，用户教程为 coretest-spec-e2e 0.2.8 指导教程.md。
- README 和用户教程引用文档时直接写文件名，不使用 GitHub 或相对文件超链接。
- 教程面向用户，仅保留环境准备、CoreTool 登录、Init / Explore / Design / Archive 操作、结果检查和常见问题；不要加入 Shell 包装、workdir、缓存 ID、脚本参数等实现细节。
- 用户明确 MCP 由工具自动启动，无需手动执行启动脚本或保持独立终端。Python 安装要求仍保留：至少 3.11，推荐 3.12。
- 最新一次精简只修改教程；README 仍保留此前的手动 MCP 启动检查段落，尚未按“自动启动”的用户文档口径同步，后续若更新 README 应一并统一。
- 本轮已完成版本和文档准备，但没有 main 合并、GitHub Release 创建或安装包正式发布的执行记录；发布状态需后续按实际操作更新。

## 16. 用户现场 MCP Python 3.10 兼容问题恢复（2026-11-02）

### 现场与根因

- 用户本地扩展目录为 `D:\AI test\testagent\templates\coretest-spec-e2e-jjfa@0.2.0\coretest-spec-e2e-jjfa`。这是现场包目录名称，不据此修改仓库 `0.2.8` 版本元数据。
- 启动输出 `[MCP] Using existing venv`，随后 griffe 在 `from enum import StrEnum` 处失败；标准库路径指向 `Python310\lib\enum.py`，说明复用的虚拟环境仍使用 Python 3.10。
- StrEnum 从 Python 3.11 起提供，当前安装的 griffe 代码与 Python 3.10 不兼容。后续 `FastMCP server support is not installed` 是导入异常包装提示，不能据此判断只是缺少 server 包。
- 用户已安装 Python 3.12，但安装新版不会自动切换原有 `.venv`。无需先修改 PATH，可以使用解释器完整路径重建环境。
- 用户最后提供的解释器位置为 `D:\Python312\Scripts\python.exe`（早先只提供 Scripts 目录）。实际操作先用 `--version` 验证，不能仅凭目录名判断版本。

### 解决步骤与路径纠正

以下为本次提供的 CMD 排障步骤；已经完成的备份与重建不重复执行。若备份目录已存在，应保留它并另选备份名称。

```bat
"D:\Python312\Scripts\python.exe" --version
cd /d "D:\AI test\testagent\templates\coretest-spec-e2e-jjfa@0.2.0\coretest-spec-e2e-jjfa"
ren .venv .venv_py310_backup
"D:\Python312\Scripts\python.exe" -m venv .venv
".venv\Scripts\python.exe" --version
".venv\Scripts\python.exe" -m pip install -r "requirements.txt" -i http://cmc-cd-mirror.rnd.huawei.com/pypi/simple/ --trusted-host cmc-cd-mirror.rnd.huawei.com
.\.testagent\mcp\core_test_design_mcp\start_mcp.bat
```

- 两次版本检查均应确认 Python 3.12.x，依赖安装成功后再启动；任一步失败先处理该错误。
- 对话早期曾误给 `.testagent/mcp/core_test_design_mcp/requirements.txt`。经读取 develop 源码确认，正确位置是**项目根目录 `requirements.txt`**；启动脚本也使用 `%ROOT_DIR%\requirements.txt`，不要沿用错误路径。
- 本次核对根目录依赖为 `fastmcp==3.4.3`、`fastmcp-slim==3.4.3`、`requests==2.34.2`、`cryptography==49.0.0`，未修改版本。
- develop 当前启动脚本已具备 Python ≥3.11 校验、优先选择 3.12、实际 FastMCP 导入检查和缺失依赖安装逻辑。现场旧包不能直接视为已包含该脚本。
- 上述手动启动仅用于本次故障定位与验证；正常使用仍由工具自动启动 MCP，不改变用户教程口径。

### 验证结果与边界

- 用户在纠正依赖路径并给出安装、启动命令后明确反馈“解决了”，本次现场故障已关闭。
- 未提供修复后的完整启动日志或业务工具调用记录；按用户反馈记录恢复，不将其扩展为 Init / Explore / Design / Archive 全链路回归通过。
- 本轮仅更新项目上下文文档，未修改启动脚本、业务代码、依赖、版本元数据，也未执行 main 合并或发布。


## 17. 0.2.8 代码仓归档完成（2026-11-02）

### 归档来源与目标

- 源模板：`D:\TestAgent\templates\coretest-spec-e2e@0.2.8\coretest-spec-e2e`；现场读取扩展清单确认 name 为 coretest-spec-e2e、version 为 0.2.8。
- 本地归档仓：`D:\CoreTestClaw_new`。
- origin：`https://szv-open.codehub.huawei.com/innersource/CoreTestClaw_G/CoreTestClaw.git`。
- 目标分支：`coretest-spec-e2e`；本次源分支：`personal/c00959281/coretest-spec-e2e-028`。
- 从旧的 026-mr2 分支切换到目标分支时，本地落后远端 4 个提交；同步后已成功创建本次 028 分支。拉取输出中的 WebApp 资源重命名属于目标分支已有更新，不是本次 0.2.8 新归档内容。

### 本次归档范围

现场暂存清单仅包含以下 7 个修改文件：

| 文件 | 归档内容 |
|---|---|
| `.testagent/mcp/core_test_design_mcp/start_mcp.bat` | 纳入 0.2.7 MCP 启动修复 |
| `.testagent/agents/test-design-agent.md` | 用例卡片调用约束 |
| `.testagent/skills/coretest-design/SKILL.md` | Design 卡片执行约束 |
| `.testagent/skills/test-case-card-adapter/SKILL.md` | 单 TS 数据复用及卡片调用约束 |
| `.testagent/skills/test-case-card/SKILL.md` | 原生 Shell / workdir、四参数、返回检查及旧流程清理 |
| `README.md` | 0.2.7 / 0.2.8 更新与使用说明 |
| `codeagent-extension.json` | 版本从 0.2.6 更新到 0.2.8 |

- 复制清单还包含根目录 requirements.txt，但其内容无差异，未进入暂存清单。
- 现场差异统计为 7 files changed、192 insertions、172 deletions；没有 .py 文件变更，Python 新增行数为 0，满足单个 MR 小于 1000 行的规则，无需拆分 MR。
- 源模板 docs 目录列举命令没有输出，本次未复制或暂存教程及项目上下文文档；不能据此声称 CodeHub 已同步 0.2.8 教程。
- README 仍包含手动启动 MCP、保持窗口运行的历史说明。本次按已验证包归档，未顺带修正文档；后续应与正常使用由工具自动启动 MCP 的口径统一。
- 本次未归档 WebApp 或 Python 业务代码，不改变因子与平台对象归档规则。

### 检查、合并结果与边界

- git diff --check 仅出现 LF 转 CRLF 提示，没有空白错误；未为换行提示批量重写文件。
- 使用明确的 $Files 清单暂存，未使用 git add -A；现场暂存清单已核对。
- 原有 mcp_settings.json、ProjectSkillStatus.txt 修改，以及 .gitignore、.idea、.opencode 下个人文件、.testagent/AGENTS.md、.testagent/testagent.md 和 __pycache__ 等均未进入本次暂存清单，未执行清理或恢复。
- 用户要求一步步指导、只执行必要命令，并在确认暂存清单后明确“不用检查文件内容”；后续不再要求逐文件审查。
- 提供的提交命令使用说明 `chore: archive coretest-spec-e2e 0.2.8`，推送源分支为 personal/c00959281/coretest-spec-e2e-028。用户随后明确反馈“已合并”，据此记录 CodeHub 本次归档已完成。
- 对话未提供提交 SHA、MR 编号或合并后本地拉取输出，不虚构这些标识，也不宣称本地目标分支已再次同步。
- 该合并是 CodeHub 目标分支归档，不代表 GitHub develop → main 合并、GitHub Release 创建、安装包正式发布或新一轮业务全链路回归。


## 18. 0.2.9：平台访问统一切换 CoreTool CLI

本节覆盖历史章节中的本地 MCP 启动及对象调用说明。基线 develop：b25bb3c11f7624215d08cecbf75a71d3f767a453。

- Init 使用 fetch_design_task_info.py，仅查询一次 task tree；原始响应与兼容 success/pbi/project_id/data 快照分开保存。generate_tr_context.py、直接需求选择和历史目录保留规则不变。
- 普通 TS 使用 object_cli.py 调用 ts create-by-name；DFX 仍按现有规则复用。
- TC 使用 tc create，完整 case_id 原值传递；卡片字段与归档字段不混用。CLI 空 message 不作为失败依据，使用 list 查询确认后保存 TC ID；历史无 ID 的 succeeded TC 继续复用。
- 写入前持久化独占请求标记，保留原始调用证据；不确定结果禁止自动重复创建，人工核查后恢复状态。
- factor_archive.py、TS 因子同步、TP --relations 因子 UUID/编码映射、Design JSON、卡片、在线文档同步和归档状态结构保持不变。
- 标准 TC 当前没有关联因子字段。自定义非空 TC 因子字段不得静默丢弃；需要 CLI 支持完整 case_id 与因子一起提交并验证后扩展。本次不宣称覆盖 MCP 所有可选接口。
- 删除本扩展 MCP 配置、服务器及启动器；移除 fastmcp/fastmcp-slim/cryptography 依赖，保留 requests 和 Python 3.11+ 要求。

验证证据：用户在 Windows CLI 1.0.6 实测 task tree、TS 42026、TP 28241，TC 151519（_001）与 155667（_01_02），并确认平台字段一致。新适配代码另做本地离线回归；这是迁移初期的手动接口验证记录；后续完整流程验证已经完成，见第 19 节。

本地回归：新增 CLI 适配测试 13 项、既有因子归档测试 9 项、既有因子候选测试 4 项全部通过（共 26 项）；测试使用离线 mock，不代表平台联调通过。


## 2026-11-04：0.2.9 首轮实测及最小修复（历史快照）

以下待确认项为修复当时状态；后续验收与发布准备以第 19 节为准。

- 实测：Init 上下文生成成功；TR 5192 的 TS_11 创建为 42119 并成功复用；Design 生成 11 TP、37 TC，因子计划及卡片更新调用成功。
- 小范围归档：TP.11.01.01=28760，4 条 TC 平台 ID 为 156538、156539、156542、156545；TS 因子同步报告成功。TP 因子平台回查、TC 标准状态键及重复归档复用仍待确认。
- 命令问题：Bash 收到了 PowerShell 语法及被提前展开的变量。CoreTool 指令统一 Bash、正斜杠绝对路径，直接执行 exe，不嵌套 Shell。
- TC 问题：case_id 被误传给 --tc-id-temp，并写成三级状态键。仅修正入口、Agent 和对象 Skill 指令：参数使用 tc_id_temp，计划/状态使用 TS_<NN>/<tc_id_temp>，平台编号 case_id 原样保留；先查状态、再 mark-in-progress、最后保存同一 key。不新增校验脚本或状态结构。
- 文档问题：本轮规格遗漏 TASK/TR 固定章节且 DFX 格式偏离；解析器又因普通子标题重复拒绝全文。生成说明明确完整前段、DFX 平台 ID 标题及平台表格置末；清理旧 TR/TS 规则和任务章节聚合说明。解析器仅对同步目标标题判重，普通子标题允许重复，目标正文仍须非空。
- 修复范围：版本保持 0.2.9；不修改因子规则、TP/TC 生成逻辑、卡片实现，不新增 Explore 校验或失败节点重试机制。
- 历史本地产物不迁移、不修复；由用户更新扩展后重新跑流程。已成功平台对象不应被当作失败对象重建。
- 本地验证：7 个解析回归场景及 Python 语法检查通过；Windows 内网端到端验证仍待用户执行。

## 19. 0.2.9 流程验收完成与发布准备（2026-11-04；2026-11-06 整理）

### 本轮目标与修改边界

用户明确本轮先打通流程，暂不评价业务设计质量。修改保持最小范围：终端示例只写 Bash，路径用正斜杠并加引号；指令使用简洁正向表述，保留正确调用方式，不增加无必要的校验脚本。历史失败文档由用户重新生成，不做迁移修复。

首轮 Bash、TC 标识及文档解析修复后，又完成两项指令修正：

| 问题 | 修正 | 文件 |
|---|---|---|
| 误用原始平台响应的 platform_ts_id，导致先报 DFX ID 缺失再纠正 | 原始 platform_ts.json 保留 CLI 响应，取 items[].id，字段不存在时兼容 ts_id；映射到规格及 catalog 的 platform_ts_id | coretest-explore/SKILL.md、test-spec-analysis/SKILL.md |
| Agent 探测 test-design/scripts 和 coretest-design/scripts，且输出目录尚未创建 | 主流程传入解释器及四个脚本绝对路径，提前 mkdir -p 创建输出目录；Agent 直接使用传入路径执行 | coretest-design/SKILL.md、agents/test-design-agent.md |

上述三个 Skill 均位于 .testagent/skills/，Agent 位于 .testagent/agents/。脚本路径固定为 coretest-design/scripts 下的 build_tp_tc_json.py、factor_candidates.py、factor_plan.py，以及 test-graph/scripts/query.py。test-design 负责 Markdown 生成；本次没有发现源码写死错误的 test-design/scripts 路径，修正的是调用方与 Agent 的路径传递契约。

这两项仅修改 4 个 Markdown 文件，未修改 Python、因子选择规则、卡片实现或 Archive 逻辑。检查 Bash 示例语法并回读远端确认一致。TC 参数继续使用 tc_id_temp，标准计划/状态键为 TS_<NN>/<tc_id_temp>，case_id 作为平台业务编号原值保留。

### 现场验证结果

验证环境为 Windows、CoreTool CLI 1.0.6、设计任务 2470、PBI 266926538；依据为用户提供的执行报告。

| 环节 | 结果与证据 |
|---|---|
| Init | CLI 获取任务及已有 TR 上下文成功 |
| TR 5192 Explore | 10 个 DFX + 5 个普通 TS，普通 TS_11～TS_15 平台 ID 为 42149～42153；DFX 41534～41543 复用 |
| TR 5192 Design | TS_11 为 scene，6 TP、6 TC；14 次因子查询，选用 1 TestFactor + 2 SceneFactor，计划校验及 completed 卡片调用成功 |
| TR 5192 Archive | TS_11 复用 42149；TP.11.03 新建 28790；TC.11.03（case_id=PCF_N23N5_REBUILD_11_03）新建 156649；3 个 TS 因子全部 succeeded |
| 文档同步 | document_plan.json=succeeded；TASK:2470 的 7 个叶子章节、TR:5192 的 5 个章节、TS:TS_11 的 2 个章节全部成功 |
| Portal | 跳转 TP.11.03，analyseId=28790，pageType=TP；card_cache_id=e01373e8-9836-488f-b07f-563b7692e558 |
| 后续 TR 5175 Design | TS_11 为 function，4 TP、9 TC；5 次查询全部成功，8 个 TestFactor 候选，选用 3 个，SceneFactor=0；因子计划及 completed 卡片成功，card_cache_id=28463ecb-b36f-4a68-aeb1-eb8a09f4fa52 |

TR 5175 的 3 个 TestFactor 为 Insp_01_01、Protocol_05_01、License_02_01，均来自候选，每个 TP 不超过 2 个，所有选中 TS 因子均被 TP 使用。这里只记录流程与结构校验，不据此证明因子与业务的相关性。

用户在 TR 5192 Archive 后明确“全部验证通过”，随后提供 TR 5175 Design 成功报告。本轮结论为 **0.2.9 流程及接口调用验收完成，可进入发布准备**。报告未逐行展示最终两项指令修正后的执行日志，不额外声称已独立核实全过程没有任何探测或纠正动作。页面实际展示、业务质量、重复执行幂等性不属于本轮已验证结论。

### 旧状态混用的现场提醒

TR 5192 首轮 TS_11 是 feature“CLI迁移验证”，平台 ID 42119；重新 Explore 后 TS_11 变为 scene，平台 ID 42149。用户曾贴出的 archive_state.json 已更新 TS 父对象，却仍保留 parent_id=42119 的旧 TP、因子及旧卡片记录。这些旧 succeeded 不能证明新 TS 下对象成功，也不能仅将 parent_id 改成新值。后续成功证据以 TP 28790、TC 156649 为准；本次没有提供旧平台对象删除或历史状态全部清理的证据。

### develop 提交与发布文档

| 提交 | 内容 |
|---|---|
| 0447795 | CoreTool Bash 指令改为简洁正向表述 |
| b37812e、654f420 | Explore / test-spec-analysis 原始平台 ID 映射说明 |
| 149bf02、3116dfe | Design 传递解释器及绝对脚本路径、创建输出目录、Agent 使用传入路径 |
| 67cbbac | codeagent-extension.json 保持 0.2.9，补齐本轮修复与验证说明 |
| 3172eeb | README 更新流程验收结果、发布说明和 Bash 环境准备命令 |
| 85ba623 | docs/coretest-spec-e2e 0.2.9 指导教程.md 更新 Bash 登录、准备事项及 TC 标识说明 |

发布文档仅修改 codeagent-extension.json、README.md、docs/coretest-spec-e2e 0.2.9 指导教程.md 三个文件；JSON 与 Bash 示例检查通过，提交后已回读 develop 确认一致。教程保持用户操作指南，未变更业务代码。此次对话没有执行 develop → main 合并、GitHub Release 创建或安装包发布。

## 20. 0.2.9 代码仓归档完成（2026-11-06）

### 来源、目标与基线

- 源模板：`D:\TestAgent\templates\coretest-spec-e2e@0.2.9\coretest-spec-e2e`；现场读取 codeagent-extension.json 确认 name=coretest-spec-e2e、version=0.2.9。
- 本地归档仓：`D:\CoreTestClaw_new`；origin 为 `https://szv-open.codehub.huawei.com/innersource/CoreTestClaw_G/CoreTestClaw.git`。
- 目标分支：`coretest-spec-e2e`；本次源分支：`personal/c00959281/coretest-spec-e2e-029`。
- 从 028 分支切换到目标分支后，执行 pull --ff-only，从 `6318286` 快进至 `8e8faf8`，再成功创建 029 分支。拉取显示的 7 文件、192 新增、172 删除属于前次 0.2.8 已合入内容，不是本次 0.2.9 的变更统计。

### 归档范围与本地文件处理

按 GitHub develop 的 0.2.9 基线差异整理明确清单，从已验证的本地模板复制 24 个文件，现场 status 已显示对应修改及新增文件：

- 4 个 Agent：coretest-archive-agent、coretest-document-sync-agent、coretest-init-agent、test-design-agent。
- 规则：.testagent/rules/analysis-guide.md。
- 8 个 Skill 的 SKILL.md：coretest-archive、coretest-design、coretest-explore、coretest-init、coretest-object-archive、coretool-cli、test-init-context、test-spec-analysis；另含 coretool-cli/references/coretest.md。
- 7 个 Python 文件：archive_state.py、build_tp_tc_json.py、document_sync.py、object_cli.py、test_cli_migration.py、fetch_design_task_info.py、generate_tr_context.py；其中 object_cli.py、test_cli_migration.py、fetch_design_task_info.py 为新增。
- 根目录 README.md、codeagent-extension.json、requirements.txt。

旧 MCP 移除按明确路径执行：mcp_server.py、start_mcp.bat、mcp.yaml 使用 git rm；已有本地修改的 .testagent/mcp/mcp_settings.json 使用 git rm --cached，仅移除仓库跟踪、保留磁盘文件，不提交其中的个人配置。

源模板 docs 列举命令无输出，本轮未复制或暂存教程、PROJECT_CONTEXT.md；不据此声称 CodeHub 已同步 0.2.9 教程。本次没有复制 WebApp 或 CLI 可执行文件。ProjectSkillStatus.txt、.gitignore、.idea/、.opencode/、.testagent/AGENTS.md、.testagent/testagent.md、__pycache__/ 等本地修改或未跟踪文件未纳入明确暂存清单，未要求清理或恢复。

### 检查与合并结果

- 使用 git add -- $Files 精确暂存；现场统计 Python 新增行数为 **458**，满足单个 MR 的 .py 新增行数小于 1000 的规则，无需拆分 MR；删除行及非 Python 文件不计入该限制。
- 要求核对暂存文件清单和 git diff --cached --check 后，用户回复“确认”。对话未贴出这两项完整输出，因此记录为用户确认，不声称已独立逐项复核。
- 提供提交说明 `chore: archive coretest-spec-e2e 0.2.9` 及推送 029 分支的命令后，用户明确反馈“已合并”，据此记录本次 CodeHub 归档完成。
- 未提供本次提交 SHA、MR 编号、最终总文件数和增删行统计，也未提供合并后本地拉取结果；`8e8faf8` 仅为归档前同步基线，不是本次合并提交。
- 本轮未重新执行业务测试；此前 CLI 流程验收见第 19 节。本次 CodeHub 合并不等同于 GitHub develop → main 合并、Release 创建或安装包正式发布。
- 用户要求逐步指导、只进行必要步骤；后续同类归档沿用明确文件清单、必要检查和单 MR 优先的方式。
