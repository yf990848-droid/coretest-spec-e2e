# coretest-spec-e2e 项目上下文

> 最后更新：2026-08-28  
> 当前扩展版本：`0.2.3`  
> 当前开发分支：`develop`  
> 稳定分支：`main`  
> 最新状态：Archive 现场验证成功

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
```

核心原则：

- `tr_info.json.requirements[]` 是当前 TR 直接关联需求的唯一权威范围；
- SR 用于内容拆分和覆盖审计，不直接替代平台 `requirement_ids`；
- 平台 DFX TS 与 Explore 普通 TS 使用统一稳定编号；
- DFX 已存在，Explore 不归档；正式 Archive 只复用其平台 ID；
- 普通 TS 可以在 Explore 末尾提前归档并保存真实 ID；
- Object、Document、Portal 三类结果分别记录；
- 脆弱的计划生成和在线文档写入由确定性脚本完成。

## 2. 当前开发基线

`develop` 在 `main` 基础上已经完成：

1. Explore 查询平台 TS，识别 DFX 并生成独立 DFX 测试规格；
2. `platform_ts.json + tr_ts.json → ts_catalog.json` 统一编号；
3. Explore 末尾增加“跳过/归档全部普通 TS”的阻塞式确认；
4. `build_ts_archive_request.py` 从 catalog 确定性生成普通 TS-only 文件计划；
5. DFX 不进入 Explore 归档计划；
6. Design 同时支持稳定 TS 编号和真实平台 TS ID；
7. 修复 `ts-split.md` 与已有 TR 契约冲突；
8. Archive 拆分对象、在线文档和 Portal 编排；
9. 设计任务的 7 个叶子章节分别写入对应 topic；
10. Archive 最新现场回归成功。

关键提交：

- `cbd942d`：Explore TS 归档入口、真实 ID Design、叶子 topic 写入；
- `d9f4574`：确定性普通 TS-only 计划、DFX 排除、`ts-split.md` 修复。

根目录版本仍为：

```text
coretest-spec-e2e 0.2.3
```

## 3. 快速命令

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
- 每个 TS 独立生成 Markdown、TP/TC JSON 和 completed 卡片；
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

截至 2026-08-28：

- Init 可拉取已有任务、TR 和直接需求；
- Explore 可生成 SR、普通/DFX 规格、`tr_ts.json` 和统一 catalog；
- `build_tr_json.py` 可校验已有 TR 元数据和需求关系；
- 普通 TS-only 计划可从 catalog 确定性生成，DFX 被排除；
- 普通 TS 可写回平台并保存真实 ID；
- Design 可处理 DFX、普通 TS、稳定编号和真实平台 ID；
- Archive 的对象、在线文档、Portal 闭环现场验证成功；
- 新版 CLI `source-data write` 与现有成功判断兼容；
- 任务级 7 个叶子 topic 可独立写入；
- 对象失败/文档失败隔离和状态持久化逻辑已验证。

## 8. 已知事项

1. `build_tp_tc_json.py --ts` 仍可能在过滤目标前扫描其他 TS，产生无关缺失配对警告；不代表目标 TS 失败。
2. 部分环境中卡片缓存成功但 Portal 页面展示仍可能延迟，需要结合实际页面继续观察。
3. 需要继续补充多需求 TR、多 TR 同需求、指定对象和断点续跑回归。
4. 已错误写入父 topic 的历史聚合数据不会因新逻辑自动删除，需要在平台上一次性清理。
5. 扩展仍标记为 `0.2.3`；定稿新版本时需要同步更新 `codeagent-extension.json`、扩展目录和 WebApp。

## 9. 新窗口继续工作的读取顺序

1. 读取本文件；
2. 读取根目录 `README.md`；
3. 根据任务读取对应 Skill：
   - Explore：`.testagent/skills/coretest-explore/SKILL.md`
   - Design：`.testagent/skills/coretest-design/SKILL.md`
   - Archive：`.testagent/skills/coretest-archive/SKILL.md`
4. 涉及对象状态时读取：
   - `.testagent/skills/coretest-object-archive/SKILL.md`
   - `.testagent/skills/coretest-archive/scripts/archive_state.py`
5. 涉及在线文档时读取：
   - `.testagent/skills/coretest-document-sync/SKILL.md`
   - `.testagent/skills/coretest-document-sync/scripts/document_sync.py`

以 `develop` 实际源码为最终依据；`main` 尚未包含本轮全部增强。
