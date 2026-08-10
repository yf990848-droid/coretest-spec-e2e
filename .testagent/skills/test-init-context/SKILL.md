---
description: 根据产品版本初始化测试设计任务上下文，查询并保存
  PBI、项目ID、全量测试设计任务及关联TR信息，并生成对应需求的
  cida_info.json。
metadata:
  author: corespec
  version: 1.2.1
name: test-init-context
---

# test-init-context

根据产品版本名称初始化测试设计任务上下文。

此技能直接调用 `core_test_design_mcp`，获取产品版本下的
PBI、项目ID、全量测试设计任务信息及关联TR信息，并完成：

1.  保存 MCP 原始返回完整 JSON；
2.  根据 TR 关联需求信息生成对应的 cida_info.json。

------------------------------------------------------------------------

# 核心职责

此技能负责：

1.  根据产品版本名称和用户工号查询测试设计任务信息。
2.  调用 MCP 工具 `core_test_design_mcp.get_design_task_info_init`。
3.  将 MCP 原始返回 JSON 完整保存到：

``` text
.design_output/design_task_info.json
```

4.  根据 MCP 返回数据中的：

``` text
design_task_id
tr_list
```

获取 TR 关联需求信息，并生成：

``` text
.design_output/<design_task_id>/<需求编号>/cida_info.json
```

------------------------------------------------------------------------

# 输入信息

-   `产品版本名称`：必填，例如：

``` text
UPCF 27.0.0
```

-   `用户工号`：必填，由调用方获取并传入。

------------------------------------------------------------------------

# MCP调用

调用 MCP：

``` text
core_test_design_mcp
```

工具：

``` text
get_design_task_info_init
```

参数：

``` json
{
  "product_name": "<产品版本名称>",
  "owner_id": "<用户工号>"
}
```

------------------------------------------------------------------------

# 执行步骤

## 步骤一：检查输入

确认：

1.  product_name
2.  owner_id

缺失时停止执行。

------------------------------------------------------------------------

## 步骤二：调用 MCP

调用：

``` text
core_test_design_mcp.get_design_task_info_init
```

如果：

``` json
success=false
```

打印错误并停止。

------------------------------------------------------------------------

## 步骤三：保存 MCP 原始返回

创建：

``` text
.design_output
```

保存：

``` text
.design_output/design_task_info.json
```

要求：

1.  UTF-8编码；
2.  保留中文；
3.  JSON格式化；
4.  保留 MCP 返回全部字段；
5.  不修改原始数据结构。

------------------------------------------------------------------------

## 步骤四：生成 cida_info.json

遍历 MCP 返回：

``` text
data[]
```

对于每个：

``` text
design_task_id
```

遍历：

``` text
tr_list
```

获取每个 TR 下：

``` text
ir_list
```

中的关联需求信息。

根据需求信息生成：

``` text
.design_output/<design_task_id>/<需求编号>/
```

生成文件：

``` text
cida_info.json
```

规则：

-   仅处理 TR `ir_list` 中存在的需求；
-   支持 `requirement_type` 为 IR 或 SR；
-   根据 `requirementAlmId` 对重复需求去重。

内容：

``` json
{
    "requirement_number": "<IR或SR>",
    "requirement_id": "<requirementAlmId>",
    "project_id": "<project_id>",
    "reqType": "cloudalm"
}
```

字段来源：

  字段                 来源
  -------------------- -----------------------------
  requirement_number   tr.ir_list.requirement_id
  requirement_id       tr.ir_list.requirementAlmId
  project_id           MCP顶层project_id
  reqType              固定cloudalm

------------------------------------------------------------------------

## 步骤五：打印初始化信息

输出：

-   产品版本；
-   用户工号；
-   PBI；
-   项目ID；
-   设计任务数量；
-   设计任务总览；
-   TR列表；
-   IR/SR列表；
-   特性；
-   功能。

------------------------------------------------------------------------

# 成功准则

技能成功完成：

1.  MCP调用成功；
2.  存在：

``` text
.design_output/design_task_info.json
```

3.  文件内容为 MCP 原始返回；
4.  每个存在 TR 关联需求的 design_task 均生成：

``` text
.design_output/<design_task_id>/<需求编号>/cida_info.json
```

5.  cida_info.json字段正确。

------------------------------------------------------------------------

# 注意事项

1.  此技能只负责初始化上下文。
2.  TR创建确认及用户交互由调用方 Agent 负责。
3.  design_task_info.json 保留 MCP 原始返回结构，不新增额外上下文文件。
4.  explore 阶段读取：

``` text
.design_output/design_task_info.json
```

根据用户输入的 tr_id 查找对应 TR 信息。 5. card 流程后续读取：

``` text
.design_output/<design_task_id>/<IR或SR>/cida_info.json
```
