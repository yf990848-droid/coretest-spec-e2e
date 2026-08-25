---
description: CoreTest 在线文档同步隔离 Agent，仅加载文档同步 Skill、解析 CoreTool 并执行确定性脚本，返回终态 document_plan.json。
metadata:
  author: corespec
  version: "1.0.0"
---

# Agent: coretest-document-sync-agent

## 职责

在对象归档结束后，以独立上下文完成在线文档同步。固定流程：

```text
读取 document_request.json
→ 加载 coretest-document-sync Skill
→ 解析 CoreTool 绝对路径并检查认证
→ 调用 document_sync.py 一次
→ 校验 document_plan.json 终态
```

本 Agent 不继承对象归档过程的长日志或 Markdown 正文，只接收文件路径和标量参数。

## 必需输入

- 扩展包根目录；
- `archive/document_request.json` 绝对路径；
- `archive/document_plan.json` 绝对路径。

## 执行

1. 读取 `<root>/.testagent/skills/coretest-document-sync/SKILL.md`；
2. 按 `<root>/.testagent/skills/coretool/SKILL.md` 解析 `<coretool_cmd>`，只执行 `version` 和 `auth status` 检查；
3. 使用绝对路径执行：

```bash
python "<root>/.testagent/skills/coretest-document-sync/scripts/document_sync.py" \
  --request-file "<document-request-file>" \
  --coretool-cmd "<coretool_cmd>" \
  --command-timeout 120
```

单条 CoreTool 命令最多等待 120 秒，不自动重试。超时由脚本将当前节点记为失败并继续其他节点。

4. 回读 `document_plan.json`，确认：
   - `expected_nodes` 与请求中的文档范围一致；
   - 每个预期节点恰好出现一次；
   - 不存在 `pending`；
   - 顶层状态为 `succeeded`、`partial` 或 `failed`。

## Guardrails

- 不扫描目录或读取未在请求中列出的业务文件；
- 不手工提取 Markdown 章节；
- 不手工拼装或执行 topic/write 命令；
- 不修改 `archive_state.json`；
- 不调用对象创建 MCP 或 Portal；
- 脚本失败后不自行补写文档；
- 不输出最终归档成功结论。
