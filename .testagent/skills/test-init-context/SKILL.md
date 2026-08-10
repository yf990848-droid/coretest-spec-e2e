---
description: 保存初始化 MCP 返回，并按真实 TR ID 生成测试设计任务上下文和 cida_info.json。
metadata:
  author: corespec
  version: 1.3.0
name: test-init-context
---

# test-init-context

保存 `core_test_design_mcp.get_design_task_info_init` 的完整返回，并生成 TR 级初始化上下文。

## 输入

- `init_result`：必填，初始化 MCP 的完整原始返回。

## 输出

```text
.design_output/design_task_info.json
.design_output/<design_task_id>/TR_<tr_id>/cida_info.json
```

## 执行步骤

1. 校验 `init_result` 调用成功，且包含 `pbi`、`project_id` 和 `data`。
2. 创建 `.design_output`，将 `init_result` 完整保存到 `.design_output/design_task_info.json`：
   - UTF-8 编码；
   - 保留中文；
   - JSON 格式化；
   - 不修改原始数据结构。
3. 执行：

```bash
python -u .testagent/skills/test-init-context/scripts/generate_tr_context.py \
  --design-task-info ".design_output/design_task_info.json" \
  --output-root ".design_output"
```

4. 检查脚本退出码和输出摘要；失败时停止流程。

## TR 上下文规则

- 遍历 `data[].tr_list[]`，仅处理存在 `design_task_id` 和 `tr_id` 的 TR。
- 目录固定为 `.design_output/<design_task_id>/TR_<tr_id>/`。
- `requirements` 完整保存 `ir_list` 中关联的 IR/SR，并按需求编号去重。
- `card_key_prefix` 固定为 `TR_<tr_id>`，不得把 TR ID 写入 `requirement_number`。
- TR 无关联需求时仍生成上下文，`requirements` 为空数组。
- 重复执行只更新 `cida_info.json`，不删除历史 TR 目录，不触碰 `test_specs`、`test_design` 和 `archive`。

## `cida_info.json` 结构

```json
{
  "design_task_id": "2470",
  "tr_id": 3867,
  "tr_no": "TR2026...",
  "tr_name": "软参及信元描述刷新",
  "pbi": "266926538",
  "project_id": "2b88f0b325154c7582a71fa02b8cd322",
  "card_key_prefix": "TR_3867",
  "requirements": [
    {
      "requirement_number": "SR20260124957173",
      "requirement_id": "2094163417",
      "requirement_type": "SR",
      "reqType": "cloudalm"
    }
  ]
}
```

缺失的可选需求字段不伪造；`requirement_number` 必须保留真实 IR/SR 编号。

## 成功准则

1. `design_task_info.json` 与 MCP 原始返回一致。
2. 每个有效 TR 均生成 `TR_<tr_id>/cida_info.json`。
3. 脚本可重复执行，且不覆盖其他阶段产物。

