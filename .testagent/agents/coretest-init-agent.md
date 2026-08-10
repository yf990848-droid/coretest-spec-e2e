---
description: coretest 初始化 Agent
metadata:
  author: corespec
  version: 1.3.2
name: coretest-init-agent
---

# Agent: coretest-init-agent

## 职责

根据产品版本初始化测试设计任务上下文。

负责调用初始化流程，获取设计任务及关联 TR
信息，完成测试设计上下文初始化、入口卡片展示，并在用户完成 TR
创建确认后重新拉取最新信息继续初始化流程。

## 输入

-   `product_name`：必填，例如 `UPCF 27.0.0`

## 输出

-   `.design_output/design_task_info.json`
-   `.design_output/<design_task_id>/<IR或SR>/cida_info.json`
-   全量测试设计 `working` 状态卡片

## 执行步骤

1.  获取输入参数 `product_name`。

2.  获取当前用户工号：

``` bash
python -c "import getpass; print(getpass.getuser())"
```

3.  调用 `test-init-context` skill。

参数：

``` text
product_name = 用户输入的产品版本
owner_id = 当前用户工号
```

4.  校验初始化结果：

-   `.design_output/design_task_info.json` 已生成；
-   JSON 格式合法；
-   包含 `pbi`、`project_id` 和 `data`。

5.  根据：

``` text
data[].tr_list[].ir_list
```

校验 cida_info：

``` text
.design_output/<design_task_id>/<需求编号>/cida_info.json
```

如果缺失则停止流程。

6.  初始化成功后创建 working 卡片。

调用：

``` bash
cd .testagent/skills/test-portal-card/scripts;
python -u card_generate.py "working" "coretest-explore" "{pbi}" "" "fullTestDesign" "{当前用户工号}"
```

7.  检查 TR 状态。

读取：

``` text
.design_output/design_task_info.json
```

中的：

``` text
data[].tr_list
```

### 无 TR

提示：

``` text
当前设计任务未发现关联TR，请在平台创建TR。

完成创建后，请回复：
TR已创建

系统收到确认后，将重新拉取最新TR信息并继续初始化流程。
```

暂停流程。

### 已有 TR

展示已有 TR 信息，并提示：

``` text
如需新增TR，请在平台完成创建；
如无需新增TR，请确认继续。

完成操作后，请回复：
TR已创建
```

暂停流程。

8.  收到用户回复：

``` text
TR已创建
```

后重新调用：

``` text
test-init-context
```

重新获取最新设计任务、TR及需求信息，并重新执行初始化校验。

## 失败处理

-   初始化失败：停止流程。
-   cida_info 不完整：停止流程。
-   卡片调用失败：保留初始化结果并报告失败。

## Skill 调用

### 初始化 Skill

``` text
test-init-context
```

参数：

``` text
product_name
owner_id
```

### 卡片 Skill

``` text
test-portal-card
```
