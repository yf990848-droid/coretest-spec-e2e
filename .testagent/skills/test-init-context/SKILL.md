---
description: 保存初始化 MCP 返回，并按真实 TR ID 生成包含当前 TR 元数据、直接关联需求及 CIDA 兼容信息的上下文。
metadata:
  author: corespec
  version: 1.3.3
name: test-init-context
---

# test-init-context

保存 `core_test_design_mcp.get_design_task_info_init` 的完整返回，并生成 TR 级初始化上下文。

## 输入

- `init_result`：必填，初始化 MCP 的完整原始返回。

## 输出

```text
.design_output/design_task_info.json
.design_output/<design_task_id>/TR_<tr_id>/tr_info.json
.design_output/<design_task_id>/TR_<tr_id>/cida_info.json
```

其中 `tr_info.json` 保存当前 TR 自身元数据和全部直接关联需求；`cida_info.json` 保持旧版单需求结构，仅用于兼容和流程准入，不代表当前 TR 的完整分析范围。

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

4. 检查脚本退出码和输出摘要；失败时停止流程。Agent 不得手工补写脚本未生成的上下文文件。

## TR 上下文规则

- 遍历 `data[].tr_list[]`，仅处理存在 `design_task_id` 和 `tr_id` 的 TR。
- 当前 TR 元数据必须直接取自正在遍历的 `data[].tr_list[]` 条目，不得使用设计任务级字段或其他 TR 的字段补充。
- 保存 `description`、`resolve_description`、`creator`、`tr_resource_type`、`relation_function`、`relation_feature`、`scene_list`、`function_list` 和 `feature_list`；缺失的文本字段保存为空字符串，缺失的列表字段保存为空列表。
- 只认当前 TR 的 `relation_requirement` 直接关联，不得通过任务级需求、函数、特性或其他 TR 推导。
- 目录固定为 `.design_output/<design_task_id>/TR_<tr_id>/`。
- 每个有效 TR 均生成 `tr_info.json`。
- `relation_requirement` 支持逗号分隔多个需求；`tr_info.json.requirements` 按原始顺序保存并去重。
- 需求编号按顺序与当前 TR 的 `ir_list[].requirement_alm_id` 配对；不得使用 `requirementParentId` 代替需求自身 ALM ID。
- `tr_info.json.card_key_prefix` 固定为 `TR_<tr_id>`，不得把 TR ID 写入 `requirement_number`。
- 重复执行只更新上下文文件，不删除历史 TR 目录，不触碰 `test_specs`、`test_design` 和 `archive`。

## `tr_info.json` 结构

```json
{
  "design_task_id": "2470",
  "tr_id": 3863,
  "tr_no": "TR20260728000012",
  "tr_name": "0728",
  "description": "0000",
  "resolve_description": "11111",
  "creator": "c00959281",
  "tr_resource_type": "irAndFeature",
  "relation_function": "",
  "relation_feature": "FEA002024032004168177",
  "scene_list": [],
  "function_list": [],
  "feature_list": [],
  "pbi": "266926538",
  "project_id": "2b88f0b325154c7582a71fa02b8cd322",
  "card_key_prefix": "TR_3863",
  "requirements": [
    {
      "requirement_number": "SR20260124957173",
      "requirement_id": "2096516380",
      "requirement_type": "SR",
      "reqType": "cloudalm"
    }
  ]
}
```

## `cida_info.json` 兼容规则

`cida_info.json` 保持原有结构：

```json
{
  "requirement_number": "SR20260124957173",
  "requirement_id": "2096516380",
  "project_id": "2b88f0b325154c7582a71fa02b8cd322",
  "reqType": "cloudalm"
}
```

- TR 直接关联一个需求且存在 `requirement_id`：生成或更新 `cida_info.json`。
- TR 直接关联多个需求：`tr_info.json.requirements[]` 保存全部需求，且是后续 Explore 的完整分析范围；`cida_info.json` 默认选择原始顺序中的第一条。
- TR 的 `relation_requirement` 为空：判定未直接关联需求，不生成 `cida_info.json`，并报告 `missing direct requirement`。
- 第一条直接关联需求缺少 `requirement_id`：不伪造字段，不生成 `cida_info.json`，并报告 `missing requirement_id`。
- 无法生成 CIDA 上下文时，删除该 TR 目录中的旧 `cida_info.json`，避免该 TR 误入后续流程。

## 后续流程准入

- 仅存在结构合法 `cida_info.json` 的 TR 可以进入后续流程。
- 未直接关联需求或第一条需求缺少 `requirement_id` 的 TR 必须停止，提示用户先在平台补齐该 TR 的直接需求关联，再重新执行 init。

## 成功准则

1. `design_task_info.json` 与 MCP 原始返回一致。
2. 每个有效 TR 均生成 `TR_<tr_id>/tr_info.json`，且其中的 TR 元数据直接来自当前 TR。
3. 每个第一条直接关联需求信息完整的 TR 均生成旧结构的 `TR_<tr_id>/cida_info.json`。
4. 脚本可重复执行，且不覆盖其他阶段产物。
