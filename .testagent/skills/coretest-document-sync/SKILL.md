---
name: coretest-document-sync
description: 在 CoreTest 对象归档结束后，由隔离的 coretest-document-sync-agent 调用确定性脚本，同步设计任务、TR 和 TS 在线文档并生成终态 document_plan.json。用于 Archive 的文档阶段，不创建测试对象、不写 TP/TC 文档。
---

# CoreTest Document Sync

## 职责

仅由 `coretest-document-sync-agent` 在对象归档完成后、Portal 刷新前调用。固定同步顺序：

```text
设计任务 → TR → 文档范围中的 TS
```

文档失败不得回滚对象状态；节点之间相互隔离。

## 输入契约

调用方提供 `archive/document_request.json`，且只能传路径与标量数据：

```json
{
  "extension_root": "<绝对路径>",
  "design_task_id": "2470",
  "pbi": "266926538",
  "user_id": "c00959281",
  "tr_id": "4029",
  "tr_info_file": "<tr_info.json>",
  "design_task_info_file": "<design_task_info.json>",
  "test_spec_file": "<测试规格.md>",
  "ts_catalog_file": "<ts_catalog.json>",
  "test_design_dir": "<test_design目录>",
  "archive_state_file": "<archive_state.json>",
  "document_plan_file": "<document_plan.json>",
  "document_scope": {
    "task": ["2470"],
    "tr": ["4029"],
    "ts": ["TS_01"]
  }
}
```

任一有效请求必须且只能包含当前任务和当前 TR。TS 按 catalog 顺序去重；TR-only 的 `ts` 为空。

## 唯一执行方式

先按 CoreTool Skill 解析并校验绝对路径 `<coretool_cmd>`，再调用一次：

```bash
python "<root>/.testagent/skills/coretest-document-sync/scripts/document_sync.py" \
  --request-file "<document-request-file>" \
  --coretool-cmd "<coretool_cmd>" \
  --command-timeout 120
```

脚本固定完成：

- 初始化并持续保存 `document_plan.json`；
- 精确提取任务、TR、TS 章节；
- 查询 `idp_doc_id` 和唯一 topic；
- 生成 UUIDv5 与无 BOM UTF-8 payload；
- 调用 source-data write 并保存 stdout、stderr、退出码；
- 单节点失败后继续其他节点；
- 返回前关闭全部 `pending`。

不得由 Agent 手工替代脚本中的任何步骤。

## CoreTool 返回契约

- `task list --output json`：在 `items[]` 中按 `id == design_task_id` 唯一匹配，并读取非空 `idp_doc_id`；
- `idp topic list --output json`：要求退出码为 0、`items` 恰好一项、`pagination.total == 1`、`topic_id` 非空且 `topic_name` 等于活动名；
- TR topic 的 `parent-activity-name` 必须使用 `tr_info.json.tr_name`；
- `source-data write` 返回文本而非 JSON：要求退出码为 0，且 stdout/stderr 中包含 `Successfully wrote source data to topic <topic_id>`；
- CLI 字节按 UTF-8 解码，写入 JSON 使用 UTF-8 无 BOM。

每条 CoreTool 命令超时 120 秒，自动重试 0 次。超时只使当前节点失败，并继续其他节点。

## 返回门禁

`document_plan.json` 必须满足：

- `expected_nodes` 与输入范围完全一致；
- 每个预期节点恰好出现一次；
- 不存在 `pending`；
- 节点状态只为 `succeeded`、`failed` 或 `not_executed`；
- 顶层状态只为 `succeeded`、`partial` 或 `failed`。

## Guardrails

- 不调用 `create_tr/create_ts/create_tp/create_tc`；
- 不修改 `archive_state.json` 或任何设计输入；
- 不扫描范围外 TS；
- 不写 TP/TC 文档；
- 不因单节点失败停止全部文档；
- 不调用 Portal；
- 不输出最终归档成功结论。
