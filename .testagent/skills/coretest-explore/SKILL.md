---
description: 以 init 生成的已有 TR 上下文为入口，汇总需求文档并生成测试规格；查询平台既有 DFX TS，与普通 TS 合并生成稳定编号目录 ts_catalog.json。
license: MIT
metadata:
  author: corespec
  generatedBy: manual
  version: 0.5.0
name: coretest-explore
---

# CoreTest Explore

## 1. 职责与边界

正式流程以 init 已生成的 `TR_<tr_id>/tr_info.json` 为唯一权威上下文：

```text
/coretest-explore <tr_id>
        ↓
.design_output/<design_task_id>/TR_<tr_id>/tr_info.json
        ↓
全部直接关联需求 → 全部唯一文档 → 一套 SR 规格 → 一套 TR 测试规格
```

本 Skill：

- 处理当前已有 TR，不创建 TR；
- 只使用 `tr_info.json.requirements[]` 确定分析范围；
- 汇总所有有效 Word 文档，并按 `DOC_TYPE:doc_id` 去重；
- 每个下游 Skill 只调用一次；
- 所有产物写入当前 `TR_<tr_id>/`。

不得从 `design_task_info.json`、其他 TR、任务级功能或特性补充需求，不再生成 `tr_context.json`，不调用 `create-tr`。

## 2. 输入

正式入口：

```text
/coretest-explore <tr_id> [--skip-clarify]
```

例如：

```text
/coretest-explore 3863
```

第一位置参数为纯数字时必须解释为 `tr_id`，不能解释为 `design_task_id`。

需求编号和本地 `.docx` 仅作为独立兼容分析模式；兼容模式不得生成可进入 Design/Archive 的正式 `tr_ts.json`。

## 3. 正式流程

执行时使用 `todowrite` 跟踪以下阶段。

### 阶段 0：启动检查

1. 读取仓库约束文件（若存在）。
2. 执行 `pandoc --version`，并按 `coretool` Skill 检查 `coretool` 可用且已登录。
3. 校验输入为纯数字 TR ID。
4. 搜索：

   ```text
   .design_output/*/TR_<tr_id>/tr_info.json
   ```

定位规则：

- 仅一处匹配：使用该目录；
- 多处匹配：列出候选并停止；
- 未匹配：提示先执行或重新执行 init；
- 不从任务级文件重新组装 TR。

将匹配目录记为 `<tr_dir>`，其父级名称即 `design_task_id`。

### 阶段 1：读取并校验 TR 上下文

读取：

```text
<tr_dir>/tr_info.json
<tr_dir>/cida_info.json
```

校验：

- 目录名 `TR_<tr_id>` 与 `tr_info.tr_id` 一致；
- `tr_info.design_task_id` 与父目录一致；
- `requirements[]` 非空；
- 每条需求具有 `requirement_number`；
- 按 `requirement_number` 去重，保留首次出现顺序；
- `cida_info.json` 仅用于准入与旧接口兼容，不代表完整分析范围。

以下当前 TR 字段供测试规格阶段直接复用：`tr_id`、`tr_no`、`tr_name`、`description`、`resolve_description`、`creator`、`tr_resource_type`、`relation_function`、`relation_feature`、`scene_list`、`function_list`、`feature_list`。

### 阶段 2：查询全部需求并建立文档清单

对去重后的每个 `requirement_number` 分别执行：

```bash
python .testagent/skills/coretest-explore/scripts/corealm_api.py \
  --id "<requirement_number>" \
  --user "<tr_info.creator>"
```

先查询全部需求，再汇总 `doc_info[]`，禁止边查询边挑选单个文档。

有效文档满足：

- `doc_id` 非空；
- `doc_type` 转大写后为 `IDP` 或 `DBOX`。

唯一键：

```text
upper(doc_type) + ":" + doc_id
```

规则：

- 一个需求关联多份有效文档：全部保留；
- 多个需求共享同一唯一键：仅下载一次，将需求编号追加到 `source_requirements`；
- 相同 `doc_id`、不同 `doc_type`：视为不同文档；
- 文件名前缀使用首次遇到该文档的需求编号；
- 任一直接关联需求没有有效文档：停止并报告，避免不完整分析；
- 非法 `doc_type` 写入清单审计并停止，不得静默忽略。

创建 `<tr_dir>/design_doc/document_manifest.json`。清单至少包含：

```json
{
  "tr_id": 3863,
  "documents": [
    {
      "doc_key": "IDP:123456",
      "doc_id": "123456",
      "doc_type": "IDP",
      "file_name": "IR20251206000098_IDP_123456.docx",
      "file_path": "/absolute/path/IR20251206000098_IDP_123456.docx",
      "source_requirements": ["IR20251206000098", "SR20260124957076"],
      "status": "downloaded"
    }
  ]
}
```

清单按需求顺序、文档出现顺序稳定生成；重复执行须保持顺序和文件名不变。

### 阶段 3：下载全部唯一文档

每个唯一文档调用一次：

```bash
python .testagent/skills/coretest-explore/scripts/file_download.py \
  --doc-id "<doc_id>" \
  --doc-type "<doc_type>" \
  --output-dir "<tr_dir>/design_doc" \
  --us-num "<首次关联需求编号>"
```

目标文件名固定为：

```text
<首次关联需求编号>_<DOC_TYPE>_<doc_id>.docx
```

读取命令最后一行 JSON；只有 `success=true` 且 `file_path` 为非空文件时才更新清单并继续。失败时保留清单中的失败状态，展示错误并停止。

### 阶段 4：调用 spec-extractor

只调用一次，传入：

```yaml
docx_paths:
  - <全部 document_manifest.documents[].file_path>
document_manifest: <tr_dir>/design_doc/document_manifest.json
output_dir: <tr_dir>
source_ids:
  - <全部去重后的 requirement_number>
author: <tr_info.creator>(via spec-extractor)
```

只生成一份 `<tr_dir>/系统需求.md` 和一份 `<tr_dir>/功能设计.md`。

### 阶段 5：调用 requirement-parser

只调用一次，参数同一文档集合、清单和 `<tr_dir>`。全部 Word 共同构成权威输入；`系统需求.md`、`功能设计.md` 为辅助输入。

输出唯一一套：

```text
<tr_dir>/sr_specs/
```

相同 SR 编号只生成一个文件，多文档内容合并；字段冲突写入 `_index.md` 的“合并冲突与解析审计”。

默认停顿并展示需求结构、SR 数量、来源覆盖和冲突数量。`--skip-clarify` 可跳过确认。

### 阶段 6：调用 test-spec-analysis

只调用一次，明确传入：

```yaml
tr_info: <tr_dir>/tr_info.json
sr_specs: <tr_dir>/sr_specs/
output_dir: <tr_dir>/test_specs/
```

要求：

- 使用已有 TR；
- TR 的 `requirement_ids` 等于 `tr_info.requirements[]` 的去重全集；
- 每条 TS 的 `requirement_ids` 是该集合的子集；
- TR 元数据直接来自 `tr_info.json`；
- 不创建 TR，不追加平台已有的质量属性 TS。

输出一份 `<tr_dir>/test_specs/<TR名称>测试规格.md`。默认展示并等待确认；`--skip-clarify` 可跳过。

### 阶段 6.5：生成 tr_ts.json

确认 Markdown 后执行：

```bash
python .testagent/skills/test-spec-analysis/scripts/build_tr_json.py \
  "<tr_dir>/test_specs/<TR名称>测试规格.md" \
  --tr-info "<tr_dir>/tr_info.json"
```

脚本只生成已有 TR 模式 JSON，不调用任何 MCP。验证：

- `_meta.tr_mode == "existing"`；
- `tr.tr_id` 与输入 TR 一致；
- TR 需求全集一致；
- 所有 TS 需求均属于当前 TR；
- 未追加质量属性 TS。

### 阶段 6.6：生成统一 TS 编号目录

调用 `coretool` Skill 查询当前 TR 的平台 TS，并将 JSON 通过 stdin 交给固定脚本：

```bash
coretool coretest testdesign ts query-by-type --tr-id <tr_id> --output json | \
python .testagent/skills/coretest-explore/scripts/build_ts_catalog.py \
  --platform-json - \
  --tr-ts-json "<tr_dir>/test_specs/tr_ts.json" \
  --output "<tr_dir>/test_specs/ts_catalog.json"
```

必须检查脚本最后输出 `success=true`。编号规则由脚本固定执行：

- 平台返回中 `scene`、`function`、`feature`、`constraint` 属于普通类型并过滤；
- 其他平台返回项全部视为 DFX，不维护 DFX 类型白名单；
- DFX 按过滤后的 `items[]` 返回顺序从 `TS_01` 开始编号；
- 同一 `ts_type` 返回多条时逐条保留；
- DFX 数量为 N 时，`tr_ts.json.test_specs[0]` 从 `TS_<N+1>` 开始；
- 编号至少两位，超过 99 时自然扩展；
- DFX 条目保存真实 `platform_ts_id`，普通条目保存 `tr_ts_index`；
- `ts_catalog.json` 是 Design 和 Archive 的稳定编号快照，后续不得重新查询并改变编号。

平台查询失败、JSON 非法、DFX 条目缺少平台 ID 或平台 ID 重复时停止，不得进入 Design。平台没有 DFX 时允许继续，普通 TS 从 `TS_01` 开始。

### 阶段 7：汇总

输出：TR、直接需求数、唯一文档数、SR 数、TS 数、冲突审计数量及所有产物路径。

读取：

```text
<tr_dir>/test_specs/ts_catalog.json
```

按 `items[]` 的稳定顺序展示全部 TS：

| 编号 | 名称 | 类型 | 来源 |
|---|---|---|---|
| TS_01 | `<ts_name>` | `<ts_type>` | DFX |
| TS_02 | `<ts_name>` | `<ts_type>` | 测试规格 |

汇总末尾输出下一步提示。

处理全部 TS：

```text
/coretest-design <tr_id>
```

处理指定 TS：

```text
/coretest-design <tr_id> TS_01 TS_02
```

## 4. 输出结构

```text
.design_output/<design_task_id>/TR_<tr_id>/
├── tr_info.json
├── cida_info.json
├── design_doc/
│   ├── <需求编号>_<DOC_TYPE>_<doc_id>.docx
│   └── document_manifest.json
├── 系统需求.md
├── 功能设计.md
├── sr_specs/
│   ├── _index.md
│   └── SR<编号>.md
└── test_specs/
    ├── <TR名称>测试规格.md
    ├── tr_ts.json
    └── ts_catalog.json
```

不得创建 `.design_output/<design_task_id>/<requirement_id>/` 或 `tr_context.json`。

## 5. 下游契约

| Skill | 输入 | 输出 |
|---|---|---|
| `spec-extractor` | 全部 `docx_paths`、清单、`<tr_dir>` | 一份系统需求、一份功能设计 |
| `requirement-parser` | 同一权威文档集合及辅助文件 | 一套 `sr_specs/` |
| `test-spec-analysis` | `tr_info.json`、整套 `sr_specs/` | 一份已有 TR 测试规格 |
| `coretool` | 当前 `tr_id` | 平台已有 TS 查询结果 |
| `build_ts_catalog.py` | 平台 TS JSON、`tr_ts.json` | 稳定编号的 `ts_catalog.json` |

## 6. 兼容模式

单个 `docx_path`、需求编号和自由描述入口可以继续用于独立需求分析；必须明确标记为兼容模式，并满足：

- 不伪造 `tr_info.json`；
- 不生成正式 `tr_ts.json`；
- 不提示可直接进入 Design 或 Archive；
- 若用户需要完整链路，提示先执行 init，再以 TR ID 调用本 Skill。
