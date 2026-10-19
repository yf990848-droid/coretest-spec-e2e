# coretest-spec-e2e 项目上下文

> 最后核对：2026-10-19  
> 仓库扩展版本元数据：`0.2.6`  
> 当前开发分支：`develop`  
> 稳定分支：`main`  
> 最新状态：0.2.5 因子关联闭环已验证；0.2.6 新版测试用例卡片适配已由用户在本地验证成功，`develop` 版本元数据、README 和指导教程均已更新为 0.2.6。本版仅替换 `webapps`，不改变业务主流程。

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

0.2.4 功能基线于 2026-09-01 合入 `main`（提交 `bec90e8`）。0.2.5 完成 TS/TP 因子检索、因子计划与 Archive 关联的现场闭环。0.2.6 只进行新版测试用例卡片 `webapps` 适配，卡片加载与 Design 卡片链路已经用户验证。当前以 `develop` 实际文件为准；`main` 和 `develop` 分支已有分叉，未在此操作中合并。

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
coretest-spec-e2e 0.2.6
```

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
- TC 以 `success=true` 为成功，不强制平台 ID；
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

## 8. 已知事项

1. `build_tp_tc_json.py --ts` 仍可能在过滤目标前扫描其他 TS，产生无关缺失配对警告；不代表目标 TS 失败。
2. 部分环境中卡片缓存成功但 Portal 页面展示仍可能延迟，需要结合实际页面继续观察。
3. 需要继续补充多需求 TR、多 TR 同需求、指定对象和断点续跑回归。
4. 已错误写入父 topic 的历史聚合数据不会因新逻辑自动删除，需要在平台上一次性清理。
5. Portal TR/TS 节点【AI分析】触发 Explore/Design 的独立实机回归仍建议保留；不要将新版测试用例卡片的验证直接等同于所有 Portal 交互路径的回归。
6. 发布 0.2.6 安装包时，扩展目录、`codeagent-extension.json.version` 和实际加载的新版 `webapps` 应保持同版；不能从本地 CoreTool CLI 版本推断扩展包版本。
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

当前用户指导教程：[`coretest-spec-e2e 0.2.6 指导教程.md`](coretest-spec-e2e%200.2.6%20指导教程.md)。

## 10. 接手后的下一步

0.2.6 新版测试用例卡片已完成用户侧验证及文档/版本元数据更新。后续发布或分支合并前，先核对新版 `webapps` 是否完整纳入目标版本及 `main/develop` 差异，勿将本地验证当作 GitHub 文件已同步的证明。

下一阶段按开发计划推进 0.2.7：Init 获取设计任务全量需求的功能/特性关联关系，以及 DFX 测试设计准则匹配。后续是 0.3.0 Explore 三种 TR 分组与 0.3.1 流程策略配置。在线文档新版适配已从 0.2.6 移出，待单独排期；非 scene TS 的端到端类型覆盖仍可补充回归。

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
- 交接重点：以仓库实际代码和分支差异为准；继续 0.2.7 前先确认是否需要发布/合并 0.2.6。
