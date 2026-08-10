---
description: coretest 初始化 Agent
metadata:
  author: corespec
  version: 1.4.1
name: coretest-init-agent
---

# Agent: coretest-init-agent

## 职责

根据产品版本初始化测试设计任务上下文，获取设计任务及关联 TR 信息，在取得 PBI 后立即展示入口卡片，并生成 TR 级上下文和兼容的 CIDA 上下文。

## 输入

- `product_name`：必填，例如 `UPCF 27.0.0`

## 输出

- `.design_output/design_task_info.json`
- `.design_output/<design_task_id>/TR_<tr_id>/tr_info.json`
- `.design_output/<design_task_id>/TR_<tr_id>/cida_info.json`（仅当 TR 关联唯一且完整的需求）
- 全量测试设计 `working` 状态卡片

## 执行步骤

1. 获取输入参数 `product_name`。

2. 获取当前用户工号：

```bash
python -c "import getpass; print(getpass.getuser())"
```

3. 调用 MCP：

```text
core_test_design_mcp.get_design_task_info_init
```

参数：

```json
{
  "product_name": "<产品版本名称>",
  "owner_id": "<当前用户工号>"
}
```

4. 校验 MCP 返回成功，且包含 `pbi`、`project_id` 和 `data`。校验失败时停止流程。

5. 取得真实 `pbi` 后，立即创建 working 卡片：

```bash
cd .testagent/skills/test-portal-card/scripts
python -u card_generate.py "working" "coretest-explore" "{pbi}" "" "fullTestDesign" "{当前用户工号}"
```

卡片调用失败时报告失败，但继续保存初始化结果。

6. 调用 `test-init-context` skill，传入 MCP 原始返回，由该 Skill 保存：

```text
.design_output/design_task_info.json
```

并运行脚本生成：

```text
.design_output/<design_task_id>/TR_<tr_id>/tr_info.json
.design_output/<design_task_id>/TR_<tr_id>/cida_info.json
```

`tr_info.json` 保存完整 TR 上下文；`cida_info.json` 保持旧版单需求结构，供 design 阶段生成用例卡片。TR 无唯一完整需求时不得伪造或默认选择需求。

7. 校验初始化结果：

- `design_task_info.json` 存在且 JSON 格式合法；
- 每个有效 `tr_id` 均存在对应的 `TR_<tr_id>/tr_info.json`；
- `tr_info.json` 中的 `design_task_id`、`tr_id`、`pbi`、`project_id` 和 `card_key_prefix` 正确；
- 对关联唯一且包含 `requirement_id` 的需求，存在旧结构的 `cida_info.json`，且只包含 `requirement_number`、`requirement_id`、`project_id` 和 `reqType`；
- 对多需求、无需求或缺少 `requirement_id` 的 TR，展示脚本摘要并提示该 TR 暂不能进入 design，不得默认选择需求。

8. 读取 `design_task_info.json` 中的 `data[].tr_list`，展示已有 TR 信息。

### 无 TR

提示用户在平台创建 TR，完成后回复：

```text
TR已创建
```

暂停流程。

### 已有 TR

展示已有 TR，并询问是否需要新增 TR。完成操作后回复：

```text
TR已创建
```

暂停流程。

9. 收到 `TR已创建` 后，重新从步骤 3 开始执行，拉取最新 TR 信息并刷新上下文。不得删除本次 MCP 未返回的历史 TR 目录。

## 失败处理

- MCP 初始化失败：停止流程。
- TR 上下文生成或校验失败：停止流程。
- 卡片调用失败：保留初始化结果并报告失败。

## Skill 调用

- 初始化上下文：`test-init-context`
- 卡片：`test-portal-card`
